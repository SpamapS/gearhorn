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

import gear

from gearhorn import worker


def get_broadcast_function(client_id, topic):
    return '%s_%s' % (topic, client_id)


class GearhornSubscriber(object):
    '''Subscribe to broadcasts from Gearhorn'''

    def __init__(self, client_id):
        self.client_id = client_id
        self.worker = gear.Worker(client_id=client_id)
        client_client_id = '%s_subscriber' % (client_id)
        self.client = gear.Client(client_id=client_client_id)

    def _make_sub_job(self, name, topic):
        message = {'client_id': self.client_id,
                   'topic': topic}
        return gear.Job(name=name,
                        arguments=bytes(json.dumps(message).encode('utf-8')))

    def addServer(self, host, port=4730, ssl_key=None, ssl_cert=None,
                  ssl_ca=None):
        self.worker.addServer(host, port=port, ssl_key=ssl_key,
                              ssl_cert=ssl_cert, ssl_ca=ssl_ca)
        self.client.addServer(host, port=port, ssl_key=ssl_key,
                              ssl_cert=ssl_cert, ssl_ca=ssl_ca)

    def waitForServer(self):
        self.worker.waitForServer()
        self.client.waitForServer()

    def subscribe(self, topic):
        self.worker.registerFunction(
            get_broadcast_function(self.client_id, topic))
        self.client.submitJob(
            self._make_sub_job(worker.GearhornWorker.subscribe_name, topic))

    def unsubscribe(self, topic):
        self.client.submitJob(
            self._make_sub_job(worker.GearhornWorker.unsubscribe_name, topic))
        self.worker.unRegisterFunction(
            get_broadcast_function(self.client_id, topic))
