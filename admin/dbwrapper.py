# -*- coding: utf-8 -*-
# Copyright 2014 pitaya games
# Licensed under the Pitaya Games License, Version 1.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.pitayagames.com/licenses/LICENSE-1.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import absolute_import, division, print_function, with_statement

import logging
import hashlib
import datetime
import tornado.escape
import zlib
from io import BytesIO
from tornado import options
from tornado.options import define, options, parse_command_line
try:
    import pylibmc as memcache
    _pylibmc = True
except ImportError, e:
    import memcache
    _pylibmc = False

import msgpack
class MsgpackWrapper(object):
    def __init__(self, file, protocol=None):
        self.file = file

    def dump(self, value):
        self.file.write(msgpack.packb(value))

    def load(self):
        return msgpack.unpackb(self.file.read())

def force_str(text, encoding="utf-8", errors='strict'):
    t_type = type(text)
    if t_type == str:
        return text
    elif t_type == unicode:
        return text.encode(encoding, errors)
    return str(text)

def force_unicode(text, encoding="utf-8", errors='strict'):
    t_type = type(text)
    if t_type == str:
        return text.decode(encoding, errors)
    elif t_type == unicode:
        return text
    elif hasattr(text, '__unicode__'):
        return unicode(text)
    return unicode(str(text), encoding, errors)

class MemcacheClient(object):
    def __init__(self, servers, default_timeout=0):
        '''
            servers is a string like "192.168.0.1:9988;192.168.0.1:9989"
        '''
        logging.info("memcached servers :" + servers)
        self._current = memcache.Client(servers.split(';') ,pickler=MsgpackWrapper, unpickler=MsgpackWrapper)
        if _pylibmc:
            self._current.behaviors['distribution'] = 'consistent'
            self._current.behaviors['tcp_nodelay'] = 1
        self.default_timeout = default_timeout

    def add(self, key, value, timeout=0, min_compress=50):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return self._current.add(force_str(key), value, timeout or self.default_timeout, min_compress)

    def get(self, key, default=None):
        try:
            val = self._current.get(force_str(key))
        except:
            val = self._current.get(force_str(key))
        if val is None:
            return default
        return val

    def set(self, key, value, timeout=0, min_compress=50):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        try:
            return self._current.set(force_str(key), value, timeout or self.default_timeout, min_compress)
        except:
            return self._current.set(force_str(key), value, timeout or self.default_timeout, min_compress)

    def delete(self, key):
        try:
            try:
                val = self._current.delete(force_str(key))
            except:
                val = self._current.delete(force_str(key))
            if type(val)==bool:
                val = 1
        except:
            val = 0
        return val

    def get_multi(self, keys):
        return self._current.get_multi(map(force_str, keys))

    def close(self, **kwargs):
        self._current.disconnect_all()

    def incr(self, key, delta=1):
        return self._current.incr(key, delta)

    def decr(self, key, delta=1):
        return self._current.decr(key, delta)

    def current(self):
        return self._current

    def parse_value(self, flags, data):
        buf = data
        if flags & memcache.Client._FLAG_COMPRESSED:
            buf = zlib.decompress(buf)
            flags &= ~memcache.Client._FLAG_COMPRESSED
        if flags == 0:
            val = bug
        elif flags & memcache.Client._FLAG_INTEGER:
            val = int(buf)
        elif flags & memcache.Client._FLAG_LONG:
            val = long(buf)
        elif flags & memcache.Client._FLAG_PICKLE:
            try:
                file = BytesIO(buf)
                unpickler = self._current.unpickler(file)
                if self._current.persistent_load:
                    unpickler.persistent_load = self.self._current.persistent_load
                val = unpickler.load()
            except Exception as e:
                return None
        else:
            raise ValueError('Unknown flags on get: %x' % flags)
        return val
