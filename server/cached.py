# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from __future__ import absolute_import, division, print_function, with_statement
import time
import logging
from collections import OrderedDict
import signal
import tornado.gen
from tornado import gen 
#from tornado import ioloop
from tornado.iostream import IOStream
from tornado.tcpserver import TCPServer
from tornado.options import define, options, parse_command_line
from tornado.process import cpu_count
from lru import LRUCache

import zmq
from zmq.eventloop import ioloop, zmqstream
ioloop.install()

class ConnectionPool(object):
    def __init__(self, create, max_size=None):
        self._create = create
        self._max_size = max_size
        self._size = 0
        self._items = []

    def get(self):
        if not self._items and (self._max_size is None or self._size < self._max_size):
            item = self._create()
            item.connection_pool = self
            self._size += 1
        else:
            if not self._items:
                return None
            item = self._items.pop()
        return item

    def put(self, item):
        self._items.append(item)

class Connection(object):
    def __init__(self):
        self.route = {
            'get': self.handle_get,
            'stats': self.handle_stats,
            'set': self.handle_set,
            'delete': self.handle_delete,
            'flush_all': self.handle_flush,
            'quit': self.handle_quit,
            'exit': self.handle_quit}

    def close(self):
        if self.connection_pool:
            self.connection_pool.put(self)

    def start(self, stream, address):
        self.io_loop = ioloop.IOLoop.instance()
        self.stream = stream
        self.address = address
        self.stream.set_close_callback(self.close)
        self.stream.read_until("\r\n", self.line_received)

    @tornado.gen.coroutine
    def line_received(self, line):
        args = line.split()
        if len(args) <= 0:
            self.stream.read_until("\r\n", self.line_received)
        else:
            data_required = yield self.route.get(args[0].lower(), self.handle_unknown)(*args[1:])
            if not data_required:
                self.stream.read_until("\r\n", self.line_received)

    @tornado.gen.coroutine
    def handle_unknown(self, *args):
        self.stream.write("CLIENT_ERROR bad command line format\r\n")
        raise gen.Return(False)

    @tornado.gen.coroutine
    def handle_set(self, key, flags, exptime, bytes, *args):
        bytes = int(bytes)
        def on_set_data(data):
            swaped = self.server.cache.set(key,(flags ,data[:-2]))
            if swaped:
                try:
                    self.server.ventilator.send_multipart(["set",swaped[0], swaped[1][0], swaped[1][1]],zmq.DONTWAIT)
                except Exception,e:
                    logging.exception(str(e))
            self.stream.write('STORED\r\n')
            self.stream.read_until("\r\n", self.line_received)
        self.stream.read_bytes(bytes + 2, on_set_data)
        raise gen.Return(True)

    def _get_data(self, key):
        return self.server.cache.get(key)

    @tornado.gen.coroutine
    def handle_get(self, *keys):
        for key in keys:
            data  = self._get_data(key)
            if data:
                self.stream.write('VALUE %s %s %d\r\n%s\r\n' % (key, data[0], len(data[1]), data[1]))
        self.stream.write('END\r\n')
        raise gen.Return(False)

    @tornado.gen.coroutine
    def handle_delete(self, key, *args):
        if self.server.cache.delete(key):
            self.stream.write('DELETED\r\n')
        else:
            self.stream.write('NOT_DELETED\r\n')
        try:
            self.server.ventilator.send_multipart(["delete", key, "0", ""],zmq.DONTWAIT)
        except Exception,e:
            logging.exception(str(e))

        raise gen.Return(False)

    @tornado.gen.coroutine
    def handle_flush(self, *args):
        for item in self.server.cache.cache.items():
            try:
                self.server.ventilator.send_multipart(["set",item[0], item[1][0], item[1][1]],zmq.DONTWAIT)
            except Exception,e:
                logging.exception(str(e))

        self.stream.write('OK\r\n')
        raise gen.Return(False)

    @tornado.gen.coroutine
    def handle_stats(self, *args):
        self.stream.write('push_url: %s\r\n' % (options.push_host))
        self.stream.write('memcahed: %s:%s\r\n' % (options.host, options.port))
        self.stream.write('keys: %s\r\n' % (len(self.server.cache.cache)))
        self.stream.write('write_intervals: %s\r\n' % (options.interval))
        self.stream.write('\r\n')
        raise gen.Return(False)

    @tornado.gen.coroutine
    def handle_quit(self, *args):
        self.stream.close()
        raise gen.Return(True)

class MemcacheServer(TCPServer):
    def __init__(self, io_loop=None, ssl_options=None, **kwargs):
        self.cache = LRUCache(options.capacity)
        self.dbw = ioloop.PeriodicCallback(self.dbw_callback, options.interval, io_loop = io_loop)
        self.dbw.start()
        self.connection_pool = ConnectionPool(lambda: Connection(),max_size= options.max_connection)
        TCPServer.__init__(self, io_loop=io_loop, ssl_options=ssl_options, **kwargs)

    def start_pusher(self,push_url):
        self.context = zmq.Context(cpu_count())
        self.ventilator = self.context.socket(zmq.PUSH)
        self.ventilator.bind(push_url)

    def dbw_callback(self):
        if len(self.cache.cache) > 0:
            item = self.cache.cache.popitem(last=False)
            try:
                self.ventilator.send_multipart(["set",item[0], item[1][0], item[1][1]],zmq.DONTWAIT)
            except Exception,e:
                logging.exception(str(e))

    def handle_stream(self, stream, address):
        """ handle new connection from client"""
        stream.set_nodelay(True)
        connection = self.connection_pool.get()
        if not connection:
            stream.close()
        else:
            connection.server = self;
            connection.start(stream, address)

def shutdown():
    """ Stop server and add a callback to stop I/O loop"""
    try:
        io_loop = ioloop.IOLoop.instance()
        logging.info('Stopping mqtt Server')
        io_loop.memcached.stop()
        logging.info('Will shutdown in 2 seconds ...')
        io_loop.add_timeout(time.time() + 2, io_loop.stop)
    except Exception,e:
        logging.exception(str(e))

def sig_handler(sig,frame):
    """ Catch signals and callback"""
    ioloop.IOLoop.instance().add_callback(shutdown)

define("host", default="0.0.0.0", help="server bind host address", type=str)
define("port", default=11211, help="server bind port", type=int)
define("push_host", default="tcp://0.0.0.0:1981", help="data dump push port", type=str)
define("max_connection", default=1024, help="max connections limit", type=int)
define("capacity", default=65536, help="cache max key numbers", type=int)
define("interval", default=50, help="db write intervals in milliseconds each time a key", type=int)

def main():
    io_loop = ioloop.IOLoop.instance()

    # start mqtt server
    io_loop.memcached = MemcacheServer()
    io_loop.memcached.listen(options.port, address=options.host)
    logging.info("server start at %s:%s" % (options.host, options.port))
    io_loop.memcached.start_pusher(options.push_host)
    logging.info("start data push host at %s", options.push_host);
    # add signal handler to stop server
    signal.signal(signal.SIGTERM , sig_handler)
    signal.signal(signal.SIGINT , sig_handler)

    io_loop.start()

if __name__ == '__main__':
    parse_command_line()
    main()
