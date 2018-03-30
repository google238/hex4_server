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
import time
import signal
import zmq
import logging
import sys, traceback
import tornado.escape
import tornado.ioloop
import tornado.options
from zmq.eventloop import ioloop, zmqstream
ioloop.install()

from tornado import gen
from tornado.options import define, options, parse_command_line

from db import BaseModel

define("push_host", default="tcp://127.0.0.1:1981", help="master recieve host", type=str)
define("wid", default=1, help="worker id", type=int)

class Worker(object):
    def __init__(self,wrk_num):
        self.worker_mum = wrk_num
        # Initialize a zeromq context
        self.context = zmq.Context()
        loop = ioloop.IOLoop.instance()

        self.pull = self.context.socket(zmq.PULL)
        for host in options.push_host.split(";"):
           self.pull.connect(host)
 
        self.stream = zmqstream.ZMQStream(self.pull,loop)
        self.stream.on_recv(self.on_message)

        BaseModel.install()
        logging.info("start process : %d", self.worker_mum);
        logging.info("remote push host : %s", options.push_host);

    @gen.coroutine
    def on_message(self,msg):
        try:
            op, key, flg, value = msg
            if op == "set":
                if not BaseModel.db.set_or_add(key,value, flg):
                    logging.info("fail %s %s %s %s "%(op,key,flg,value))
                else:
                    logging.info("sucess %s %s %s %s "%(op,key,flg,value)) 

                if not BaseModel.db_back.set_or_add(key,value, flg):
                    logging.info("fail %s %s %s %s "%(op,key,flg,value))
                else:
                    logging.info("sucess %s %s %s %s "%(op,key,flg,value)) 
            elif op == "delete":
                BaseModel.db.delete(key)
                BaseModel.db_back.delete(key)
        except Exception,e:
            logging.exception(str(e))

    @classmethod
    def start(cls, wrk_num):
        worker = Worker(wrk_num);

def shutdown():
    """ Stop server and add a callback to stop I/O loop"""
    try:
        io_loop = ioloop.IOLoop.instance()
        logging.info('Will shutdown in 2 seconds ...')
        io_loop.add_timeout(time.time() + 2, io_loop.stop)
    except Exception,e:
        logging.exception(str(e))

def sig_handler(sig,frame):
    """ Catch signals and callback"""
    ioloop.IOLoop.instance().add_callback(shutdown)

if __name__ == "__main__":
    parse_command_line()
    Worker.start(options.wid);
    # add signal handler to stop server
    signal.signal(signal.SIGTERM , sig_handler)
    signal.signal(signal.SIGINT , sig_handler)
    ioloop.IOLoop.instance().start()
