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

from gearhorn.tests import base
from gearhorn.tests import server
from gearhorn import worker


class TestGearhornWorker(base.TestCase):
    def setUp(self):
        super(TestGearhornWorker, self).setUp()
        self.server = server.TestServer()
        self.addCleanup(self.server.shutdown)
        self.client = gear.Client('in_client')
        self.addCleanup(self.client.shutdown)
        self.client.addServer('localhost', self.server.port)
        self.client.waitForServer()

    def test_worker(self):
        w = worker.GearhornWorker(client_id='test_worker', dsn='sqlite://')
        w._store.initialize_schema()
        self.addCleanup(w.shutdown)
        w.addServer('localhost', self.server.port)
        w.registerSubscriberFunctions()
        w.registerFanoutFunction()
        subw = gear.Worker('test_worker_subw')
        subw.addServer('localhost', self.server.port)
        subw.waitForServer()
        subw.registerFunction('broadcasts_test_receiver')
        subscribe_message = {'client_id': 'test_receiver',
                             'topic': 'broadcasts'}
        subscribe_job = gear.Job(w.subscribe_name,
                                 arguments=json.dumps(
                                     subscribe_message).encode('utf-8'))
        self.client.submitJob(subscribe_job)
        # w should have this message only
        w.work()
        while not subscribe_job.complete:
            time.sleep(0.1)
        fanout_message = {'topic': 'broadcasts',
                          'payload': 'in payload'}
        job = gear.Job(w.fanout_name,
                       json.dumps(fanout_message).encode('utf-8'))
        self.client.submitJob(job)
        # Now we should fanout message
        w.work()
        while not job.complete:
            time.sleep(0.1)
        # And finally subw should have it
        import pdb; pdb.set_trace()
        broadcasted = subw.getJob()
        self.assertEqual('in payload', broadcasted.arguments)
