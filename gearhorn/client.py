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


class GearhornClientJob(gear.Job):
    _as_dict = None
    def as_dict(self):
        if not self.complete:
            return None
        if self._as_dict is None:
            self._as_dict = json.loads(b''.join(self.data).decode('utf-8'))
        return self._as_dict


class GearhornClient(gear.Client):
    '''An example of a client object to use to subscribe to Gearhorn
    broadcasts.'''

    last_sequence = -1
    broadcast_queue_name = b'broadcast'
    current_job = None

    def submitJob(self, job):
        self.current_job = job
        return super(GearhornClient, self).submitJob(job)

    def handleWorkComplete(self):
        payload = self.current_job.as_dict()
        self.last_sequence = payload['sequence']
        self.submitNext()
        self.handlePayload(payload)

    def submitNext(self):
        '''Call this to submit the next job.'''
        new_job = GearhornClientJob(self.broadcast_queue_name, b'', b'%d' %
                                    self.last_sequence)
        self.submitJob(new_job)

    def handlePayload(self, payload):
        '''Override this to do something with the notification.'''
        return
