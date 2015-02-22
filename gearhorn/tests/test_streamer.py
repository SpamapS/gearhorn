import testtools

from gearhorn import streamer


class TestSequenceStream(testtools.TestCase):
    def test_sequences(self):
        stream = streamer.SequenceStream()
        self.assertFalse(stream.has_sequence(1))
        self.assertFalse(stream.has_sequence(0))
        self.assertRaises(IndexError, stream.get_sequence, 0)
        stream.append("a thing")
        self.assertTrue(stream.has_sequence(0))
        self.assertEquals({"sequence": 0, "payload": "a thing"},
                          stream.get_sequence(0))
        stream.trim(0)
        self.assertFalse(stream.has_sequence(0))
