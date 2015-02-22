class SequenceStream(object):
    def __init__(self, start_seq=-1):
        self._seq = start_seq
        self._stream = list()

    def append(self, item):
        self._stream.append(item)
        self._seq += 1

    def has_sequence(self, seq):
        list_pos = self._seq - seq
        return abs(list_pos) < len(self._stream)

    def get_sequence(self, seq):
        list_pos = self._seq - seq
        val = self._stream[list_pos]
        return {"sequence": seq, "payload": val}

    def del_sequence(self, seq):
        list_pos = self._seq - seq
        del self._stream[list_pos]

    def trim(self, size):
        while len(self._stream) > size:
            self._stream.pop()

class Streamer(object):
    def __init__(self, stream):
        self.stream = stream
        self.pending_jobs = list()

    def in_event(self, job):
        self.stream.append(job.payload)
        job.sendWorkComplete()

    def flush_pending_jobs(self):
        pjobs = self.pending_jobs
        self.pending_jobs = list()
        for pjob in pjobs:
            self.broadcast_event(pjob)

    def broadcast_event(job):
        seq = job.unique
        try:
            seq = int(seq)
        except TypeError as e:
            job.sendWorkException(str(e))
        if self.stream.has_sequence(seq):
            job.sendWorkData(self.stream.get_sequence(seq))
            return
        self.pending_jobs.append(job)
