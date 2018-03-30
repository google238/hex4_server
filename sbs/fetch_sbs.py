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
from email.utils import formatdate
from model.devices import Devices
from utils.config import Config
from utils.error import SBSError
from utils.sign import check_request, make_response
from utils.sbs import Sbs
from model.bucket import Bucket
from utils.sbs import Sbs
from api.bucket import get

from model.devices import Devices
from model.social import GooglePlayBind, GameCenterBind

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

class Handler(object):
    def __init__(self, client):
        self.sbs_client = client
        self.config = config

@gen.coroutine
def main():
    sbs_admin_id = config.sbs.get('mw4y8t7dzbcmomzskakh7n75',{}).get("admin_id", "")
    sbs_admin_password = config.sbs.get('mw4y8t7dzbcmomzskakh7n75',{}).get("admin_password", "")
    f = open("/data/uids/uids.csv")
    for line in f:
        if line.strip():
            user_id , device_id , password,  game_center_id, google_play_id = line.strip().split(",")
            sbs_client = Sbs(sbs_admin_id,  user_id.strip(), device_id , sbs_admin_password)
            handler = Handler(sbs_client)
            result = yield get(handler, "userData", user_id.strip())
            logging.info("%s,%s,%s,%s,%s" % (device_id , user_id , password, google_play_id, game_center_id)) 
            """
            device = yield Devices.get(user_id)
            if not device:
                device = Devices()
                device.pkey = user_id
                device.device_id = device_id
                device.password = password
                device.google_play_id = google_play_id
                device.game_center_id = game_center_id
                yield device.put()
                logging.info("device %s,%s,%s,%s,%s" % (device_id , user_id , password, google_play_id, game_center_id)) 

            if device.google_play_id:
                g = yield GooglePlayBind.get(device.google_play_id)
                if not g:
                    g = GooglePlayBind()
                    g.pkey = device.google_play_id
                    g.user_ids = [device.pkey]
                    yield g.put() 
                    logging.info("google %s,%s,%s,%s,%s" % (device_id , user_id , password, google_play_id, game_center_id)) 
            if device.game_center_id:
                g = yield GameCenterBind.get(device.game_center_id)
                if not g:
                    g = GameCenterBind()
                    g.pkey = device.game_center_id
                    g.user_ids = [device.pkey]
                    logging.info("apple %s,%s,%s,%s,%s" % (device_id , user_id , password, google_play_id, game_center_id)) 
                    yield g.put() 
            """
            yield gen.sleep(0.01)
    f.close()
    shutdown()

define("config" , default="production", help="service mode [production, staging, ci]", type=str)
if __name__ == "__main__":
    parse_command_line()
    current_dir = os.path.dirname(os.path.realpath(__file__))
    config.configure(os.path.join(current_dir, "config", "%s.conf" % (options.config)))
    # add signal handler to stop server
    signal.signal(signal.SIGTERM , sig_handler)
    signal.signal(signal.SIGINT , sig_handler)
    ioloop.IOLoop.instance().run_sync(main)
    ioloop.IOLoop.instance().start()
