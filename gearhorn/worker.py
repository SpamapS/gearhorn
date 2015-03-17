# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import time

import gear

from gearstore.store import sqla


class GearhornWorker(gear.Worker):
    subscribe_name = 'subscribe_fanout'
    subscribe_name = 'unsubscribe_fanout'
    fanout_name = 'fanout'
    foreground_timeout = 30

    def __init__(self, client_id=None, worker_id=None, dsn=None):
        super(GearhornWorker, self).__init__(self.client_id, self.worker_id)
        client_client_id = (client_id or worker_id) + '_broadcaster'
        self._servers = []
        self.client = gear.Client(client_id=client_client_id)
        self._store = sqla.Store(dsn)

    def addServer(self, host, port=4730, ssl_key=None, ssl_cert=None,
                  ssl_ca=None):
        super(GearhornWorker, self).addServer(host, port, ssl_key, ssl_cert,
                                              ssl_ca)
        self.client.addServer(host, port, ssl_key, ssl_cert, ssl_ca)

    def registerSubscriberFunctions(self):
        return self.registerFunction(self.subscribe_name)
        return self.registerFunction(self.unsubscribe_name)

    def registerFanoutFunction(self):
        return self.registerFunction(self.fanout_name)

    def work(self):
        job = self.getJob()
        if job.name == self.fanout_name:
            return self.fanout(job)
        elif job.name == self.subscribe_name:
            return self.subscribe(job)
        elif job.name == self.unsubscribe_name:
            return self.unsubscribe(job)
        raise RuntimeError('Unknown job %s' % job.name)

    def subscribe(job):
        self.subunsub(job, self._store.subscribe)

    def unsubscribe(job):
        self.subunsub(job, self._store.unsubscribe)

    def _subunsub(job, action):
        try:
            message = json.loads(job.arguments)
            if not isinstance(message, dict):
                raise ValueError('must be a mapping')
            if ('topic', 'client_id') not in message:
                raise ValueError('must have topic and client_id keys')
        except ValueError as e:
            job.sendWorkException(bytes(str(e).encode('utf-8')))
            return
        try:
            action(client_id=message['client_id'],
                                  topic=message['topic'])
        except Exception as e:
            job.sendWorkException(bytes(str(e).encode('utf-8')))
            return
        job.sendWorkComplete()

    def fanout(job):
        try:
            message = json.loads(job.arguments)
            if not isinstance(message, dict):
                raise ValueError('must be a JSON mapping.')
            if ('topic', 'payload') not in message:
                raise ValueError('must have topic and payload keys')
        except ValueError as e:
            job.sendWorkException(bytes(str(e).encode('utf-8')))
            return
        wait_jobs = []
        for sub in self._store.get_subscribers(messagej['topic']):
            name = '%s_%s' % (message['topic'], sub)
            cj = gear.Job(name, arguments=message['payload'],
                          unique=message.get('unique'))
            try:
                self.client.submitJob(cj, background=message.get('background',
                                                                 False))
                if not message.get('background'):
                    wait_jobs.append((sub, cj))
            except GearmanError as e:
                errors.append((sub, str(e)))
        done = 0
        # Timeout just in case
        before = time.time()
        while done < len(wait_jobs):
            for sub, wj in wait_jobs:
                if wj.complete and wj.failure:
                    if wj.exception:
                        errors.append((sub, wj.exception))
                    else:
                        errors.append((sub, 'Worker failure'))
                elif wj.complete:
                    done += 1
            time.sleep(0.1)
            if time.time() - before > self.foreground_timeout:
                # timed out
                for sub, wj in wait_jobs:
                    if not wj.complete:
                        errors.append((sub, 'Worker timeout'))
                break
        if errors:
            job.sendWorkException(json.dumps(errors))
        else:
            job.sendWorkComplete(done)
        return True
