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

import random
import time

import gear
import testtools

from gearhorn.tests import server
from gearhorn import worker


class TestGearhornWorker(testtools.TestCase):
    def setUp(self):
        super(TestGearhornWorker, self).setUp()
        self.server = server.TestServer()
        self.addCleanup(self.server.shutdown)
        self.client = gear.Client('in_client')
        self.addCleanup(self.client.shutdown)
        self.client.addServer('localhost', self.server.port)
        self.client.waitForServer()

    def test_worker(self):
        w = worker.GearhornWorker()
        job = gear.Job(w.in_name, b'in payload')
        self.client.submitJob(job)
        self.addCleanup(w.shutdown)
        w.addServer('localhost', self.server.port)
        w.work()
        while not job.complete:
            time.sleep(0.1)
        self.assertTrue(w.stream.stream.has_sequence(0))
