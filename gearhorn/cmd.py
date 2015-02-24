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

import argparse
import sys

from gearhorn import worker

def main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', '-H', default=['localhost'],
                        help='Gearman server(s)', nargs='*')
    opts = parser.parse_args(argv[1:])
    w = worker.GearhornWorker()
    for host in opts.host:
        w.addServer(host)
    try:
        while True:
            w.work()
    except Exception as e:
        print(str(e))
        return -1
    return 0
