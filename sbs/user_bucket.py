# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
import os.path
import time
import signal
import logging
import hashlib
import hmac
import base64
import code
import tornado
import tornado.escape
from tornado import gen
from tornado import ioloop
from tornado.web import HTTPError
from tornado.options import define, options, parse_command_line
from tornado.web import Application as BaseApplication
from utils.config import Config
from api.bucket import get_bucket, put_bucket

def shutdown():
    """ Stop server and add a callback to stop I/O loop"""
    try:
        io_loop = ioloop.IOLoop.instance()
        logging.info("Will shutdown in 2 seconds ...")
        io_loop.add_timeout(time.time() + 2, io_loop.stop)
    except Exception,e:
        logging.exception(str(e))

def sig_handler(sig,frame):
    """ Catch signals and callback"""
    ioloop.IOLoop.instance().add_callback(shutdown)

config = Config()

@gen.coroutine
def main():
    f = open("/data/uids/uids.txt")
    for uid in f:
        if uid.strip():
            result = yield get_bucket("userData", uid.strip())
            if result:
               levelscore = result.get("data",{}).get("eventLevelScores",[])
               if len(levelscore) >=13 and levelscore[11] == 0 and levelscore[12] > 0:
                   logging.info(uid)
            yield gen.sleep(0.01)
    f.close()

define("config" , default="production", help="service mode [production, staging, ci]", type=str)
if __name__ == "__main__":
    parse_command_line()
    current_dir = os.path.dirname(os.path.realpath(__file__))
    config.configure(os.path.join(current_dir, "config", "%s.conf" % (options.config)))
    # add signal handler to stop server
    signal.signal(signal.SIGTERM , sig_handler)
    signal.signal(signal.SIGINT , sig_handler)
    ioloop.IOLoop.instance().run_sync(main)
