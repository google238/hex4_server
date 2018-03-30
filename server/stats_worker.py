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
import os
import time
import datetime
import signal
import zmq
import logging
import sys, traceback
import tornado.escape
import tornado.ioloop
import tornado.options
from zmq.eventloop import ioloop, zmqstream
ioloop.install()
from tornado.log import LogFormatter
from tornado import gen
from tornado.options import define, options, parse_command_line
from logging.handlers import RotatingFileHandler

define("sub_host", default="tcp://172.31.29.68:1998;tcp://172.31.29.68:2998;tcp://172.31.29.68:3998;tcp://172.31.29.68:4998;tcp://172.31.27.253:1998;tcp://172.31.27.253:2998;tcp://172.31.27.253:3998;tcp://172.31.27.253:4998;tcp://172.31.19.118:1998;tcp://172.31.19.118:2998;tcp://172.31.19.118:3998;tcp://172.31.19.118:4998;tcp://172.31.19.119:1998;tcp://172.31.19.119:2998;tcp://172.31.19.119:3998;tcp://172.31.19.119:4998", help="stats clients", type=str)
define("wid", default=1, help="worker id", type=int)

class Worker(object):
    cache_log = []
    def __init__(self,wrk_num):
        self.worker_mum = wrk_num
        # Initialize a zeromq context
        self.context = zmq.Context()
        loop = ioloop.IOLoop.instance()

        self.sub = self.context.socket(zmq.SUB)
        for host in options.sub_host.split(";"):
           self.sub.connect(host)
        self.sub.setsockopt(zmq.SUBSCRIBE, b"snowpear.INFO.log")
        self.stream = zmqstream.ZMQStream(self.sub,loop)
        self.stream.on_recv(self.on_message)
        logging.info("start process : %d", self.worker_mum)
        logging.info("remote push host : %s", options.sub_host)
        self.loggers = {}

    @gen.coroutine
    def on_message(self,msg):
        uid = msg[1].split(" ")[-8]
        data = "sbsuid=%s&%s" % (uid, msg[1].split(" ")[-1])
        try:
            now = datetime.datetime.now()
            timestr = now.strftime("%Y%m%d %H:%M:%S")
            datestr, hours = timestr.split()
            hour = hours.split(":")[0]
            logger = self.loggers.get((datestr,hour), None)
            if not logger:
                for key, logger in self.loggers.items():
                    for h in logger.handlers:
                        h.close()
                self.loggers = {}
                logger = logging.getLogger("%s%s"%(datestr,hour))
                channel = RotatingFileHandler(os.path.join("/data/", "logs", "%s.%s-%s" % ("sumikko", datestr, hour)))
                fm=tornado.log.LogFormatter(fmt=' %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
                channel.setFormatter(fm)
                logger.addHandler(channel)
                self.loggers[(datestr,hour)] = logger
            logger.info('%s %s' % (datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"),data.strip()))
        except Exception, e:
            logging.info(str(e))

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
