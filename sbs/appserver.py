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
from orm import BaseModel
class MainHandler(tornado.web.RequestHandler):
    config = Config()
    @gen.coroutine
    def prepare(self):
        if "X-Http-Method-Override" in self.request.headers:
            self.request.method = self.request.headers["X-Http-Method-Override"].upper()

        user_id = self.request.headers.get("X-SBS-USER-ID", "")
        if user_id:
            self.device = yield Devices.get(user_id)
        else:
            self.device = None

        sbs_id = self.request.headers.get("X-SBS-ID", "")
        if not sbs_id:
            self.set_header("X-Sbs-Status", "403")
            raise HTTPError(403, "No X-SBS-ID in request headers")

        if self.device and self.config.sbs.get("using_wooga", False):
            sbs_admin_id = self.config.sbs.get(sbs_id,{}).get("admin_id", "")
            sbs_admin_password = self.config.sbs.get(sbs_id,{}).get("admin_password", "")
            self.sbs_client = Sbs(sbs_admin_id,  user_id,  self.device.device_id, sbs_admin_password)
        else:
            self.sbs_client  = None

        self.signature = check_request(self)
        if not self.signature:
            self.set_header("X-Sbs-Status", "401")
            raise HTTPError(401, "%s Signature mismatch" % (user_id))

    @gen.coroutine
    def do_request(self):
        status = 200
        result = None
        try:
            api_func = None
            method = self.request.method.lower()
            path_parts   = self.request.path.split("/")

            try:
                mod = __import__("api.%s" %(path_parts[1].lower()), globals(), locals(), [method], -1)
            except ImportError , e:
                mod = __import__("api.bucket", globals(), locals(), [method], -1)
                path_parts.insert(0, "bucket");

            api_func = getattr(mod, method)
            if api_func:
                status, response = yield api_func(self, *path_parts[2:])
                if status != 204:
                    result = tornado.escape.json_encode(response)
            else:
                self.set_header("X-Sbs-Status", "405")
                raise HTTPError(405)

        except SBSError, e:
            status = e.status_code
            result = '{"status":%s,"error":"%s"}' % (status, str(e))
        except HTTPError, e:
            status = e.status_code
            result = '{"status":%s,"error":"%s"}' % (status, str(e))
        except Exception, e:
            logging.exception(str(e))
            status = 500
            result = '{"status":500,"error":"Internal Error"}'
        self.set_status(status)
        self.result = result
        make_response(self)
        if result:
            self.write(result)

    @gen.coroutine
    def get(self):
        yield self.do_request()

    @gen.coroutine
    def post(self):
        yield self.do_request()

    @gen.coroutine
    def delete(self):
        yield self.do_request()

    @gen.coroutine
    def put(self):
        yield self.do_request()

    @gen.coroutine
    def patch(self):
        yield self.do_request()

    @gen.coroutine
    def head(self):
        yield self.do_request()

    @gen.coroutine
    def options(self):
        yield self.do_request()

class Application(BaseApplication):
    def listen(self, port, address="", **kwargs):
        super(Application, self).listen(port, address, **kwargs)

application = Application([(r"/.*", MainHandler),], template_path = os.path.join(os.path.dirname(__file__), "templates"))

def shutdown():
    """ Stop server and add a callback to stop I/O loop"""
    try:
        io_loop = ioloop.IOLoop.instance()
        logging.info("Waiting for running processes to finish..")
        BaseModel.io_executor.shutdown(wait = True)
        io_loop.stop()
        logging.info("server stoped")
    except Exception,e:
        logging.exception(str(e))

def sig_handler(sig,frame):
    """ Catch signals and callback"""
    ioloop.IOLoop.instance().add_callback(shutdown)

define("host",  default="0.0.0.0", help="http server bind address", type=str)
define("port" , default=9090, help="http server listening port", type=int)
define("config" , default="production", help="service mode [production, staging, ci]", type=str)

if __name__ == "__main__":
    parse_command_line()
    current_dir = os.path.dirname(os.path.realpath(__file__))
    MainHandler.config.configure(os.path.join(current_dir, "config", "%s.conf" % (options.config)))
    MainHandler.config.sbs_admin = {}
    for sbs_id in MainHandler.config.sbs:
        if sbs_id == "using_wooga":
            continue
        MainHandler.config.sbs_admin[MainHandler.config.sbs[sbs_id]["admin_id"]] = MainHandler.config.sbs[sbs_id]
    application.listen(options.port, address=options.host ,xheaders=True)
    # add signal handler to stop server
    signal.signal(signal.SIGTERM , sig_handler)
    signal.signal(signal.SIGINT , sig_handler)
    logging.info("server started %s %s" % (options.port, options.host))
    ioloop.IOLoop.instance().start()
