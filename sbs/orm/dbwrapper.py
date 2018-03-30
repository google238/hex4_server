# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
import os
import logging
import hashlib
import datetime
import tornado.escape
import zlib
from io import BytesIO
from tornado import gen
from tornado.escape import json_encode
import time

#try:
#    import pylibmc as memcache
#    _pylibmc = True
#except ImportError, e:
#    import memcache
#    _pylibmc = False

import memcache
_pylibmc = False

import MySQLdb
escape_string = MySQLdb._mysql.escape_string
from orm.mysql import Connection as DBConnection
RETRY_TIME = 60

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
        logging.info("process %s memcached servers : %s " %(os.getpid() , servers))
        self._current = memcache.Client(servers.split(';'))
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

def _smart(v):
    t = type(v)
    if t == str:
        return v
    elif t == unicode:
        return force_str(v)
    elif (t == int) or (t == long) or (t == float):
        return str(v)
    elif t == datetime.datetime:
        return v.strftime("%Y-%m-%d %H:%M:%S")
    return str(v)

def _pairtext(k, v):
    if v is None:
        return "%s=null" % k
    return "%s='%s'" % (k, escape_string(_smart(v)))

def _pairnum(k, v):
    if v is None:
        return "%s=0" % k
    return "%s=%s" % (k, v)

def _sqltext(data, delimiter=","):
    sql = delimiter.join([_pairtext(k[0], k[1]) for k in data.items()])
    return sql

class MysqlClient(object):
    def __init__(self, config, backup = False):
        self.config = config
        if backup:
            self.servers = self.config["servers_back"]
        else:
            self.servers = self.config["servers"]
        self.singled = self.config["singled"]
        self.master  = self.config["master"]
        self.sharding = {}
        for i_range in self.config["sharding"]:
            server_index =  self.config["sharding"][i_range]
            for i in range(i_range[0], i_range[1]+1):
                self.sharding[hex(i)[2:].zfill(2)] = server_index
        self.disconnected = {}

    def get(self,pkey):
        return self._select(pkey)

    def add(self, pkey, data):
        self._insert(pkey, data)

    def set(self, pkey, data):
        self._update(pkey, data)

    def set_or_add(self, pkey, data):
        return self._update_or_insert(pkey, data)

    def delete(self, pkey):
        self._delete(pkey)

    def _insert(self, pkey, data):
        conn, table = self._get_connection_info(pkey)
        try:
            sql = "INSERT INTO %s SET %s , %s" % (table, _pairtext("pkey",pkey) , _pairtext("data",data))
            last_id = conn.execute(sql)
            return last_id
        except Exception, e:
            logging.error(str(e))
        finally:
            if conn:
                conn.close()

    def _update(self, pkey, data,):
        conn, table = self._get_connection_info(pkey)
        try:
            sql = "UPDATE %s SET %s WHERE %s" % (table, _pairtext("data",data), _pairtext("pkey",pkey))
            conn.execute(sql)
        except Exception, e:
            logging.error(str(e))
        finally:
            if conn:
                conn.close()

    def _update_or_insert(self, pkey, data):
        conn, table = self._get_connection_info(pkey)
        result = False
        try:
            sql = "INSERT INTO %s SET %s,%s ON DUPLICATE KEY UPDATE %s" % (table, _pairtext("pkey",pkey), _pairtext("data",data), _pairtext("data",data))
            conn.execute(sql)
            result = True
        except Exception, e:
            logging.error(str(e))
        finally:
            if conn:
                conn.close()
        return result

    def _select(self, pkey):
        conn, table = self._get_connection_info(pkey)
        try:
            sql = "SELECT * FROM %s WHERE %s LIMIT 1" % (table,  _pairtext("pkey",pkey) )
            return conn.get(sql), False
        except Exception, e:
            logging.error(str(e))
        finally:
            if conn:
                conn.close()
        return None, conn is None or conn.closed

    def _delete(self, pkey):
        conn, table = self._get_connection_info(pkey)
        try:
            sql = "DELETE FROM %s WHERE %s" % (table, _pairtext("pkey",pkey))
            conn.execute(sql)
        except Exception, e:
            logging.error(str(e) + sql)
        finally:
            if conn:
                conn.close()

    def _get_connection_info(self, pkey):
        tablename = pkey.split("|")[1].split(".")[-1]
        if tablename in self.singled:
            return self._get_master_connection(), tablename

        shard_index, table_index = self._get_shard_info(pkey)
        host, user, passwd, database = self.servers.get(self.sharding[shard_index])
        mysql_host = (host, database, user, passwd)
        table = "%s_%s" % (tablename, table_index)
        retry_time = self.disconnected.get(mysql_host, 0)
        if retry_time > 0:
            if retry_time > int(time.time()):
                return None, table

        conn = DBConnection(host, database, user, passwd)
        if conn.closed:
            self.disconnected[mysql_host] = int(time.time() + RETRY_TIME)
        else:
            self.disconnected[mysql_host] = 0
        return conn, table

    def _get_master_connection(self):
        host, user, passwd, database = self.master
        mysql_host = (host, database, user, passwd)
        retry_time = self.disconnected.get(mysql_host, 0)
        if retry_time > 0:
            if retry_time > int(time.time()):
                return None
        conn = DBConnection(host, database, user, passwd)
        if conn.closed:
            self.disconnected[mysql_host] = int(time.time() + RETRY_TIME)
        else:
            self.disconnected[mysql_host] = 0
        return conn

    def _get_shard_info(self, shard_key):
        m = hashlib.md5()
        m.update(force_str(shard_key))
        digest = m.hexdigest()
        return digest[:2], digest[-1]

    def select_master(self, sql):
        conn = self._get_master_connection()
        try:
            return conn.query(sql), False
        except Exception, e:
            logging.error(str(e))
        finally:
            if conn:
                conn.close()
        return None, conn is None or conn.closed

    def execute_master(self, sql):
        result = False
        conn = self._get_master_connection()
        try:
            conn.execute(sql)
            result = True
        except Exception, e:
            logging.error(str(e))
        finally:
            if conn:
                conn.close()
        return result, conn is None or conn.closed
