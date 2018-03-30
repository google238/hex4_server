#-*- coding: utf-8 -*-
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
import time
import zmq
import logging
import msgpack
import tornado.options
from tornado.options import define, options, parse_command_line
from zmq.eventloop import ioloop, zmqstream

try:
    import cPickle as pickle
except ImportError, e:
    import pickle

from db.dbwrapper import MysqlClient,MemcacheClient

class SerializerMetaClass(type):
    def __init__(self, name, bases, attrs):
        super(SerializerMetaClass, self).__init__(name, bases, attrs)
        self._get_def_attrs(bases)
    
    def _get_def_attrs(self, bases):
        if hasattr(self, "def_attrs"):
            def_attrs = dict(getattr(self, "def_attrs"))
            for attr, v in def_attrs.items():
                if v<>"adv" and v<>"simple":
                    raise ValueError("Invalid field define. Model:%s field:%s value:%s" % (self.__name__, attr, v))
        else:
            def_attrs = {}
        
        if not def_attrs:   # def_attrs is empty dict
            seq_attrs = getattr(self, "seq_attrs", [])
            adv_seq_attrs = getattr(self, "adv_seq_attrs", [])
            if 'pkey' not in seq_attrs:
                seq_attrs.append('pkey')
            
            for attr in seq_attrs:
                if attr in adv_seq_attrs and not def_attrs.has_key(attr):
                    def_attrs[attr] = "adv"
                else:
                    def_attrs[attr] = "simple"
        for base in bases:
            if hasattr(base, "all_def_attrs"):
                base_def_attrs = getattr(base, "all_def_attrs")
                for k, v in base_def_attrs.items():
                    if not def_attrs.has_key(k):
                        def_attrs[k] = v
        setattr(self, "all_def_attrs", def_attrs)
        
class Serializer(object):
    __metaclass__ = SerializerMetaClass

    def __init__(self):
        super(Serializer, self).__init__()

    @classmethod
    def loads(cls, data):
        def_attrs = cls.all_def_attrs
        o = cls()
        for attr in def_attrs:
            if attr in data:
                if def_attrs[attr] == "adv":
                    if data[attr]:
                        setattr(o, attr, msgpack.unpackb(str(data[attr])))
                    else:
                        setattr(o, attr, None)
                else:
                    setattr(o, attr, data[attr])
        return o

    def dumps(self, attrs = None, shallow = False):
        def_attrs = self.all_def_attrs
        if attrs is not None:
            seq_attrs = attrs
        else:
            seq_attrs = def_attrs.keys()
        
        data = {}
        for attr in seq_attrs:
            val = getattr(self, attr)
            if def_attrs[attr] == "adv":
                data[attr] = val if shallow else msgpack.packb(val)
            else:
                data[attr] = val
        return data

class BaseModel(Serializer):    
    cache_prefix = "snowpear"
    _CACHE_ONLY = False
    def __init__(self):
        super(BaseModel, self).__init__()
        self.need_insert = True
        self.pkey = None

    @classmethod
    def generate_cache_key(cls, pkey):
        return cls.cache_prefix + "|" + cls.__module__ + "." + cls.__name__ + '|' + str(pkey)

    def get_cache_key(self):
        pkey = str(self.pkey)
        return self.__class__.generate_cache_key(pkey)

    @classmethod
    def get(cls, pkey, local_first = False):
        #start_time = time.time()
        cache_key = cls.generate_cache_key(pkey)
        result = None
        if local_first:
            result = cls.loc.get(cache_key)
        if not result:
            result = cls.mc.get(cache_key)
            if not result and not cls._CACHE_ONLY:
                result = cls.dbw.get(cache_key)
                if not result:
                    dbdata = cls.db.get(cache_key)
                    if not dbdata:
                        dbdata = cls.db_back.get(cache_key)
                    if dbdata is not None:
                        try:
                            result = cls.mc.parse_value(dbdata["flag"], dbdata["data"])
                            cls.mc.set(cache_key, result)
                        except Exception,e:
                            logging.info(str(e)) 

            if not result:
                return None

            if local_first:
                cls.loc[cache_key] = result

        obj = cls.loads(result)
        obj.pkey = str(pkey);
        obj.need_insert = False
        #logging.info("get %s time %s " % (cache_key,time.time() - start_time))
        return obj

    def put(self, save_db = False):
        #start_time = time.time()
        cls = self.__class__
        cache_key = self.get_cache_key()
        data = self.dumps()
        cls.mc.set(cache_key,data)
        if not cls._CACHE_ONLY:
            cls.dbw.set(cache_key, data)
        self.need_insert = False
        #logging.info("put %s time %s " % (cache_key , time.time() - start_time))

    def delete(self):
        cls = self.__class__
        cache_key = self.get_cache_key()
        cls.mc.delete(cache_key)
        cls.dbw.delete(cache_key)

    @classmethod
    def install(cls,context = None):
        cls.loc = {}
        cls.mc = MemcacheClient(options.memcached, 0)
        cls.dbw = MemcacheClient(options.writecache, 0)
        cls.db = MysqlClient()
        cls.db_back = MysqlClient(True)

define("memcached", default="127.0.0.1:11211", help='memcached server config,servers is a string like "192.168.0.1:9988;192.168.0.1:9989"', type=str)
define("writecache", default="127.0.0.1:11311", help='dbw server config,servers is a string like "192.168.0.1:9988;192.168.0.1:9989"', type=str)
define("db_conf", default="config/db.conf", help="the mysql server config", type=str)

