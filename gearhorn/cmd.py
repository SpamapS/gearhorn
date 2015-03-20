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
import socket

from gearhorn import worker
from gearhorn.store import sqla


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', default=['localhost'],
                        help='Gearman server(s)', nargs='*')
    parser.add_argument('--sqlalchemy-dsn', help='SQLAlchemy DSN for storing'
                        ' matchmaking data')
    opts = parser.parse_args()
    w = worker.GearhornWorker(client_id='gearhorn_%s' % socket.gethostname(),
                              dsn=opts.sqlalchemy_dsn)
    for host in opts.host:
        if '/' in host:
            (host, port) = host.split('/')
            w.addServer(host, port=port)
        else:
            w.addServer(host)
    try:
        while True:
            w.work()
    except Exception as e:
        print(str(e))
        return -1
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sqlalchemy-dsn', help='SQLAlchemy DSN for schema '
                        'to initialize.')
    opts = parser.parse_args()
    s = sqla.Store(opts.sqlalchemy_dsn)
    s.initialize_schema()
