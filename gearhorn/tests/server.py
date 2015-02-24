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

import gear

class TestServer(gear.Server):
    ''' Selects a random port to listen on '''
    def __init__(self):
        port = random.randint(30000, 31000)
        while True:
            try:
                super(TestServer, self).__init__(port=port)
                break
            except Exception as e:
                if 'could not open socket' in str(e):
                    print('failed to listen on %d' % port)
                    pass
                raise e
