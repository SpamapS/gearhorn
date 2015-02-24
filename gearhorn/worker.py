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
import gear

from gearhorn import streamer


class GearhornWorker(gear.Worker):
    # XXX: these are entirely arbitrary and intended to be tunable
    max_pending_jobs = 10
    max_stream_backlog = 100
    # XXX: These need to be configurable
    broadcast_name = b'broadcast'
    in_name = b'in'
    client_id = b'gearhorn'
    worker_id = None

    def __init__(self, client_id=None, worker_id=None):
        super(GearhornWorker, self).__init__(self.client_id, self.worker_id)
        self.backlog = streamer.SequenceStream(start_seq=-1)
        self.stream = streamer.Streamer(self.backlog)
        self.registerFunction(self.broadcast_name)
        self.registerFunction(self.in_name)

    def work(self):
        ''' do one unit of work and then return '''
        job = self.getJob()
        if job.name == self.broadcast_name:
            self.stream.broadcast_event(job)
        elif job.name == self.in_name:
            self.stream.in_event(job)
        else:
            self.logger.warn('Unknown job received name=%s' % job.name)
        if len(self.stream.pending_jobs) >= self.max_pending_jobs:
            self.stream.flush_pending_jobs()
        self.stream.stream.trim(self.max_stream_backlog)
