import json
import time

import gear
import testtools

from gearhorn import streamer

class TestSequenceStream(testtools.TestCase):

    def test_sequences(self):
        stream = streamer.SequenceStream()
        self.assertFalse(stream.has_sequence(1))
        self.assertFalse(stream.has_sequence(0))
        self.assertRaises(IndexError, stream.get_sequence, 0)
        stream.append('a thing')
        self.assertTrue(stream.has_sequence(0))
        self.assertEquals({'sequence': 0,
         'payload': 'a thing'}, stream.get_sequence(0))
        stream.trim(0)
        self.assertFalse(stream.has_sequence(0))

class TestStreamer(testtools.TestCase):

    def setUp(self):
        super(TestStreamer, self).setUp()
        self.server = gear.Server()
        self.addCleanup(self.server.shutdown)
        self.worker = gear.Worker('worker')
        self.addCleanup(self.worker.shutdown)
        self.client = gear.Client('in_client')
        self.addCleanup(self.client.shutdown)
        self.worker.addServer('localhost')
        self.client.addServer('localhost')
        self.client.waitForServer()
        self.worker.waitForServer()

    def test_streamer(self):
        self.worker.registerFunction('in')
        self.worker.registerFunction('send_broadcasts')
        job = gear.Job('in', 'in payload')
        self.client.submitJob(job)
        workerJob = self.worker.getJob()
        self.assertEqual('in', workerJob.name)
        seq = streamer.SequenceStream()
        stream = streamer.Streamer(seq)
        stream.in_event(workerJob)
        while not job.complete:
            time.sleep(0.1)

        self.assertTrue(job.complete)
        self.assertTrue(stream.stream.has_sequence(0))
        broadcast_listener = gear.Client()
        self.addCleanup(broadcast_listener.shutdown)
        broadcast_listener.addServer('localhost')
        broadcast_listener.waitForServer()
        broadcasts_0 = gear.Job('send_broadcasts', '', '0')
        broadcast_listener.submitJob(broadcasts_0)
        workerJob = self.worker.getJob()
        self.assertEqual('send_broadcasts', workerJob.name)
        stream.broadcast_event(workerJob)
        while not broadcasts_0.complete:
            time.sleep(0.1)

        self.assertTrue(broadcasts_0.complete)
        self.assertEqual({'sequence': 0,
         'payload': 'in payload'}, json.loads(''.join(broadcasts_0.data)))
