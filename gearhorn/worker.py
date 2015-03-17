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
    subscribe_name = 'register_fanout_subscriber'
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

    def registerFanoutFunction(self):
        return self.registerFunction(self.fanout_name)

    def work(self):
        j = self.getJob()
        try:
            message = json.loads(j.arguments)
            if not isinstance(message, dict):
                raise ValueError('must be a JSON mapping.')
            if ('topic', 'payload') not in message:
                raise ValueError('must have topic and payload keys')
        except ValueError as e:
            j.sendWorkException(bytes(str(e).encode('utf-8')))
            return False
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
            j.sendWorkException(json.dumps(errors))
        else:
            j.sendWorkComplete(done)
        return True
