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

def to_utf8(val):
    '''Returns passed string as bytes encoded in utf-8'''
    if (isinstance(val, str) or isinstance(val, unicode)):
        return val.encode('utf-8')
    elif isinstance(val, bytes):
        return val
    elif val is None:
        return val
    raise TypeError('Expecting string or bytes, got %s' % type(val))
