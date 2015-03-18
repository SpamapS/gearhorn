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


class GearhornClient(gear.Client):
    '''An example of a client object to use to subscribe to Gearhorn
    broadcasts.'''

    def submitJob(self, job):
        real_name = job.name
        real_arguments = {'topic': real_name, 'payload': job.arguments}
        job.name = worker.GearhornWorker.fanout_name
        job.arguments = bytes(json.dumps(real_arguments).encode('utf-8'))
        return super(GearhornClient, self).submitJob(job)
