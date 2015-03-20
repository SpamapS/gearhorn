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

from gearhorn.tests import base
from gearhorn.tests import server
from gearhorn import subscriber
from gearhorn import worker


class TestGearhornSubscriber(base.TestCase):
    def setUp(self):
        super(TestGearhornSubscriber, self).setUp()
        self.server = server.TestServer()
        self.addCleanup(self.server.shutdown)
        self.client = gear.Client('in_client')
        self.addCleanup(self.client.shutdown)
        self.client.addServer('localhost', self.server.port)
        self.client.waitForServer()

    def test_subscriber(self):
        w = gear.Worker('test_subscriber_worker')
        w.registerFunction(worker.GearhornWorker.subscribe_name)
        self.addCleanup(w.shutdown)
        w.addServer('localhost', self.server.port)
        s = subscriber.GearhornSubscriber('test_subscriber')
        s.addServer('localhost', self.server.port)
        s.waitForServer()
        s.subscribe('a_topic')

        def _assertJob():
            p = json.loads(j.arguments)
            self.assertIsInstance(p, dict)
            self.assertIn('topic', p)
            self.assertIn('client_id', p)
            self.assertEqual('a_topic', p['topic'])
            self.assertEqual('test_subscriber', p['client_id'])

        j = w.getJob()
        _assertJob()
        w.registerFunction(worker.GearhornWorker.unsubscribe_name)
        s.unsubscribe('a_topic')
        j = w.getJob()
        _assertJob()
