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
        # XXX: I'm not sure this is an appropriate simplification. -Clint
        if isinstance(val, bytes):
            val = val.decode('utf-8')
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
        self.stream.append(job.arguments)
        job.sendWorkComplete()

    def flush_pending_jobs(self):
        pjobs = self.pending_jobs
        self.pending_jobs = list()
        for pjob in pjobs:
            self.broadcast_event(pjob)

    def broadcast_event(self, job):
        seq = job.unique
        try:
            seq = int(seq)
        except TypeError as e:
            job.sendWorkException(str(e))
        if self.stream.has_sequence(seq):
            job.sendWorkComplete(
                json.dumps(self.stream.get_sequence(seq)).encode('utf-8'))
            return
        self.pending_jobs.append(job)
