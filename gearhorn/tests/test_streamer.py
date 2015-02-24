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
import testtools

from gearhorn import streamer
from gearhorn.tests import server


class TestSequenceStream(testtools.TestCase):

    def test_sequences(self):
        stream = streamer.SequenceStream()
        self.assertFalse(stream.has_sequence(1))
        self.assertFalse(stream.has_sequence(0))
        self.assertRaises(IndexError, stream.get_sequence, 0)
        stream.append('a thing')
        self.assertTrue(stream.has_sequence(0))
        self.assertEqual(
            {'sequence': 0,
             'payload': 'a thing'}, stream.get_sequence(0))
        self.assertEqual(
            [{'sequence': 0,
             'payload': 'a thing'}], list(stream.since_sequence(-1)))
        stream.trim(0)
        self.assertFalse(stream.has_sequence(0))


class TestStreamer(testtools.TestCase):

    def setUp(self):
        super(TestStreamer, self).setUp()
        self.server = server.TestServer()
        self.addCleanup(self.server.shutdown)
        self.worker = gear.Worker('worker')
        self.addCleanup(self.worker.shutdown)
        self.client = gear.Client('in_client')
        self.addCleanup(self.client.shutdown)
        self.worker.addServer('localhost', self.server.port)
        self.client.addServer('localhost', self.server.port)
        self.client.waitForServer()
        self.worker.waitForServer()

    def test_streamer(self):
        self.worker.registerFunction(b'in')
        self.worker.registerFunction(b'send_broadcasts')
        job = gear.Job(b'in', b'in payload')
        self.client.submitJob(job)
        workerJob = self.worker.getJob()
        self.assertEqual(b'in', workerJob.name)
        seq = streamer.SequenceStream()
        stream = streamer.Streamer(seq)
        stream.in_event(workerJob)
        while not job.complete:
            time.sleep(0.1)

        self.assertTrue(job.complete)
        self.assertTrue(stream.stream.has_sequence(0))
        broadcast_listener = gear.Client()
        self.addCleanup(broadcast_listener.shutdown)
        broadcast_listener.addServer('localhost', self.server.port)
        broadcast_listener.waitForServer()
        broadcasts_0 = gear.Job(b'send_broadcasts', b'', b'0')
        broadcast_listener.submitJob(broadcasts_0)
        workerJob = self.worker.getJob()
        self.assertEqual(b'send_broadcasts', workerJob.name)
        stream.broadcast_event(workerJob)
        while not broadcasts_0.complete:
            time.sleep(0.1)

        self.assertTrue(broadcasts_0.complete)
        self.assertEqual(
            {'sequence': 0,
             'payload': 'in payload'},
            json.loads(b''.join(broadcasts_0.data).decode('utf-8')))
