#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
import time
import logging
import msgpack
import collections
import os, os.path
from tornado import gen
from tornado.process import cpu_count
from concurrent.futures import ProcessPoolExecutor
from orm.dbwrapper import MysqlClient, MemcacheClient
from tornado.options import define, options, parse_command_line
from utils.config import Config
__all__ = ('BaseModel',)

class SerializerMetaClass(type):
    def __init__(self, name, bases, attrs):
        super(SerializerMetaClass, self).__init__(name, bases, attrs)
        self._get_def_attrs(bases)

    def _get_def_attrs(self, bases):
        if hasattr(self, "def_attrs"):
            def_attrs = dict(getattr(self, "def_attrs"))
            for attr, v in def_attrs.items():
                if v != "adv" and v != "simple":
                    raise ValueError("Invalid field define. Model:%s field:%s value:%s" % (
                        self.__name__, attr, v))
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

    def dumps(self, attrs=None, shallow=False):
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

_memcached = None
_mysql = None
_config = None
_mysql_bak = None
def install_client(config):
    global _memcached
    global _mysql
    global _mysql_bak
    global _config
    current_dir = os.path.dirname(os.path.realpath(__file__))
    app_dir = os.path.dirname(current_dir)
    if not _config:
        _config = Config()
        _config.configure(os.path.join(app_dir, "config", "%s.conf" % (config)))
    if not _memcached:
        _memcached = MemcacheClient(_config.memcached)

    if not _mysql:
        _mysql = MysqlClient(_config.mysql)

    if not _mysql_bak:
        _mysql_bak = MysqlClient(_config.mysql, True)

def get_data(config, cache_key, cache_only = False):
    result = None
    try:
        install_client(config)
        result = _memcached.get(cache_key)
        if not result and not cache_only:
            dbdata, is_disconnected = _mysql.get(cache_key)
            #if is_disconnected:
            #    dbdata, is_disconnected = _mysql_bak.get(cache_key)
            if dbdata is not None:
                result = msgpack.unpackb(dbdata["data"])
                _memcached.set(cache_key, result)
    except:
        logging.exception("get data failed cache_key %s" % (cache_key))
    return result

def delete_data(config, cache_key, cache_only = False):
    try:
        install_client(config)
        _memcached.delete(cache_key)
        if not cache_only:
            _mysql.delete(cache_key)
            #_mysql_bak.delete(cache_key)
    except:
        logging.error("delete data failed cache_key %s" % (cache_key))

def put_data(config, cache_key, data, cache_only = False):
    try:
        install_client(config)
        _memcached.set(cache_key, data)
        if not cache_only:
            value = msgpack.packb(data)
            _mysql.set_or_add(cache_key, value)
            #_mysql_bak.set_or_add(cache_key, value)
    except:
        logging.error("put data failed cache_key %s" % (cache_key))
    
def execute_master(config, sql):
    result = None
    try:
        install_client(config)
        result, is_disconnected= _mysql.execute_master(sql)
        #if is_disconnected:
        #    result, is_disconnected = _mysql_bak.execute_master(sql)
    except:
        logging.error("execute sql  %s" % (sql))
    return result

def select_master(config, sql):
    result = None
    try:
        install_client(config)
        result, is_disconnected = _mysql.select_master(sql)
        #if is_disconnected:
        #    result, is_disconnected = _mysql_bak.select_master(sql)
    except:
        logging.error("select sql  %s" % (sql))
    return result

def cache_get(config, key , default = None):
    result = None
    try:
        install_client(config)
        result = _memcached.get(key, default)
    except:
        logging.error("cache get %s" % (key))
    return result

def cache_set(config, key, value, timeout = 0):
    result = None
    try:
        install_client(config)
        result = _memcached.set(key, value, timeout)
    except:
        logging.error("cache set %s" % (key))
    return result

def cache_delete(config, key):
    result = None
    try:
        install_client(config)
        result = _memcached.delete(key)
    except:
        logging.error("cache delete %s" % (key))
    return result

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    def get(self, key):
        try:
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
        except KeyError:
            return None

    def set(self, key, value):
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value

class BaseModel(Serializer):
    cache_prefix = "SBS"
    _CACHE_ONLY = False
    _loc = LRUCache(10240)
    io_executor = ProcessPoolExecutor(cpu_count())

    def __init__(self):
        super(BaseModel, self).__init__()
        self.need_insert = True
        self.pkey = None

    @classmethod
    def generate_cache_key(cls, pkey):
        return   "%s|%s.%s|%s"  % (cls.cache_prefix, cls.__module__ ,  cls.__name__ , str(pkey))

    def get_cache_key(self):
        pkey = str(self.pkey)
        return self.__class__.generate_cache_key(pkey)

    @classmethod
    @gen.coroutine
    def execute_master(cls, sql):
        result = yield cls.io_executor.submit(execute_master, options.config, sql)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def select_master(cls, sql):
        result = yield cls.io_executor.submit(select_master, options.config, sql)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def cache_get(cls, key, default = None):
        result = yield cls.io_executor.submit(cache_get, options.config, key, default)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def cache_set(cls, key, value , timeout=0):
        result = yield cls.io_executor.submit(cache_set, options.config, key, value, timeout)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def cache_delete(cls, key):
        result = yield cls.io_executor.submit(cache_delete, options.config, key)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def get(cls, pkey, local_first = False):
        cache_key = cls.generate_cache_key(pkey)

        result = None
        if local_first:
            result = cls._loc.get(cache_key)

        if not result:
            result = yield cls.io_executor.submit(get_data, options.config, cache_key, cls._CACHE_ONLY)
            if local_first:
                cls._loc.set(cache_key, result)

        obj = None
        if result:
            obj = cls.loads(result)
            obj.pkey = str(pkey)
            obj.need_insert = False
        raise gen.Return(obj)

    @gen.coroutine
    def put(self):
        cls = self.__class__
        cache_key = self.get_cache_key()
        data = self.dumps()
        yield cls.io_executor.submit(put_data, options.config, cache_key, data, cls._CACHE_ONLY)
        self.need_insert = False

    @gen.coroutine
    def delete(self):
        cls = self.__class__
        cache_key = self.get_cache_key()
        yield cls.io_executor.submit(delete_data, options.config, cache_key, cls._CACHE_ONLY)
