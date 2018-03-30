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
import os.path
import time
import signal
import logging
import code
import tornado
import hashlib
import urllib
import tornado.escape
from tornado import gen
from tornado import ioloop
from tornado.options import define, options, parse_command_line
from tornado.web import Application as BaseApplication
from db import BaseModel
from api.data.player import DeviceBind
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import PeriodicCallback
from stats import start_stats, stats_log

MAINTEN = 0 
PRIVATE_KEY = "XcdeeeW3DEFDN"

class MainHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ("POST", "GET", "DELETE")
    CLASS_CACHE = {}
    SYSTEM_MAIL = []
    ACTIVITY_CONFIG = []
    APL_CONFIG = []
    ACTIVITY_NOTICE = []
    def check_apl(self):
        cient_version = self.request.headers.get('X-Pitaya-version','')
        channel = self.request.headers.get('X-Pitaya-channel','')
        for apl in MainHandler.APL_CONFIG:
            if "%d" % (apl.get("apl_id")) == channel and cient_version == apl.get("version") and  apl.get("opened") == 1:
                self.set_header("X-Pitaya-APL", "1")

    def oauth(self, api, uid):
        token = self.request.headers.get('X-Pitaya-token','')
        sbs_id = self.request.headers.get('X-Pitaya-uid','')
        device_id = self.request.headers.get('X-Pitaya-device','')
        lang_local = self.request.headers.get('X-Pitaya-Lang','')
        client_version = self.request.headers.get('X-Pitaya-version','')
        channel = self.request.headers.get('X-Pitaya-channel','')
        ts = int(self.get_argument('ts','0'))

        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        now = time.time()
     
        oschannel = "1" if "android" in self.request.headers.get('User-Agent','').lower() else "3"
        #disable timestamp checking
        #if ts > (now + 30) or ts < (now - 30): 
        #    logging.info("client timestamp: %s , server timestamp %s " % ( now, ts))
        #    return False
        args = dict((k, v[-1]) for k, v in self.request.arguments.iteritems())
        url = "/%s/%s/" % (api,uid)
        signature_str = ''
        for key in sorted(args.keys()):
            value = args[key]
            signature_str += '%s=%s'% (key,value) if signature_str == '' else '&%s=%s'% (key,value)
        stats_log(api,"%s %s %s %s %s %s %s %s&ip=%s&os=%s" % (sbs_id , uid , device_id, client_version , lang_local ,channel, api , signature_str, remote_ip, oschannel))
        access_token = hashlib.md5("%s%s?%s"%(PRIVATE_KEY, url, signature_str)).hexdigest() 
        result = False
        if access_token == token:
            result = True
        return result

    @gen.coroutine
    def do_request(self, api , uid):
        if api == "share":
            lang = self.get_argument('lang','jp')
            if not lang:
                lang = 'jp'
            if lang == 'jp':
                self.render("share_jp.html", icode=uid, lang=lang)
            elif lang == 'zh-hant' or lang == 'zh_hant':
                self.render("share_zh_hant.html", icode=uid, lang=lang)
            else:
                self.render("share_en.html", icode=uid, lang=lang)
            raise gen.Return(None) 

        if api == "act":
            code =  self.get_argument('code','')
            ts =    int(self.get_argument('ts',"0"))
            cksum = self.get_argument('cksum','')
            rawstr = "code=%s&ts=%s%s" % (code, ts , PRIVATE_KEY)
            token = hashlib.md5(rawstr).hexdigest()       
            if token != cksum:
                self.set_status(400) 
                self.write('{"status":400 , "content":"bad request"}');
                raise gen.Return(None)

            now = time.time()
            if ts > (now + 1800) or ts < (now - 1800): 
                self.set_status(400) 
                self.write('{"status":400 , "content":"bad request"}');
                raise gen.Return(None)

            from api.data.friends import Friends
            from api.data.regcode import RegCode
            regcode = RegCode.get(code)
            if regcode:
                fid = regcode.uid
            else:
                self.set_status(400) 
                self.write('{"status":400 , "content":"bad request"}');
                raise gen.Return(None)

            friend = Friends.get(fid)
             
            if uid == "gift":
                self.render("invite_gift.html", invite_count = len(friend.invited), invite_type = 1)
            elif uid == "giftinfo":
                self.render("invite_gift.html", invite_count = len(friend.invited), invite_type = 2)
            raise gen.Return(None)

        try:
            if MAINTEN == 1:
                result = '{"status":10001,"data":"maintain"}'
            else: 
                api_obj = None
                if api == "test" or self.oauth(api, uid):
                    api_obj = self.CLASS_CACHE.get(api)
                    if not api_obj:
                        module_name = "api." +api
                        class_name = "Service"
                        mod = __import__(module_name, globals(), locals(), [class_name], -1)
                        myclass = getattr(mod, class_name)
                        api_obj = myclass()
                        self.CLASS_CACHE[api] = api_obj
                if api_obj:
                    api_obj.bind_uid = uid
                    api_obj.sbs_uid = self.request.headers.get('X-Pitaya-uid','') 
                    api_obj.uid = api_obj.sbs_uid
                    api_obj.language_code = self.request.headers.get('X-Pitaya-Lang','')
                    api_obj.client_version = self.request.headers.get('X-Pitaya-version','')
                    api_obj.channel = self.request.headers.get('X-Pitaya-channel','')
                    api_obj.request = self
                    api_obj.system_mails = MainHandler.SYSTEM_MAIL
                    api_obj.activity_config = MainHandler.ACTIVITY_CONFIG
                    api_obj.notice = MainHandler.ACTIVITY_NOTICE
                    device_id = self.request.headers.get('X-Pitaya-device','')
                    api_obj.device_id = device_id
                    login_device_id = self.request.headers.get('X-Pitaya-login','')
                    login_device = ''
                    if api == "player" and uid:
                        self.devicebind = DeviceBind.get(uid)
                        if not self.devicebind:
                            self.devicebind = DeviceBind()
                            self.devicebind.pkey = uid
                            self.devicebind.device_id = device_id
                            self.devicebind.put()
                        elif login_device_id != '':
                            self.devicebind.device_id = device_id
                            self.devicebind.put()
                        login_device = self.devicebind.device_id

                    #if(login_device != "" and device_id != login_device):
                    #    result = '{"status":1001,"data":"device conflict"}'
                    #    self.set_status(200) 
                    #else:
                    if True:
                        response = yield api_obj.do_request()
                        result = tornado.escape.json_encode(response)
                        self.set_status(200) 
                else:
                    self.set_status(400) 
                    result = '{"status":400,"data":"Bad Request"}'
        except Exception,e:
            logging.exception(str(e))
            self.set_status(400) 
            result = '{"status":400,"data":"Bad Request"}'
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.check_apl()
        self.write(result)

    @gen.coroutine
    def get(self, api, uid):
        yield self.do_request(api, uid)

    @gen.coroutine
    def post(self, api, uid):
        yield self.do_request(api, uid)

    @gen.coroutine
    def delete(self, api, uid):
        yield self.do_request(api, uid) 

class Application(BaseApplication):
    def listen(self, port, address="", **kwargs):
        super(Application, self).listen(port, address, **kwargs)

application = Application([
    (r"/api/(.*)/(.*)/", MainHandler),
],template_path = os.path.join(os.path.dirname(__file__), "templates"))

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

define("host",  default="0.0.0.0", help="http server bind address", type=str)
define("base_host",  default="dev.pitaya.jp:10080", help="http server base host name", type=str)
define("port" , default=10080, help="http server listening port", type=int)
define("shell" , default=0, help="start shell mode", type=int)

class XRequest(object):
    def post(self, url, data = {}):
        self.data = data
        token = url.split("/")
        module_name = "api." +token[2]
        self.uid = token[3]
        class_name = "Service"
        mod = __import__(module_name, globals(), locals(), [class_name], -1)
        myclass = getattr(mod, class_name)
        api_obj = myclass()
        api_obj.bind_uid = self.uid
        api_obj.sbs_uid = self.uid
        api_obj.uid = api_obj.sbs_uid
        api_obj.request = self
        api_obj.system_mails = MainHandler.SYSTEM_MAIL
        gen.Task(self.exec_func, api_obj)

    @gen.coroutine
    def exec_func(api_obj, callback = None):
        response = yield api_obj.do_request()
        logging.info(response)

    def get_argument(self, fieldname, value):
        return self.data.get(fieldname, value)

@gen.coroutine
def watchdog():
    try:
        f = open( os.path.join(os.path.dirname(__file__), "config/mainten.txt"))
        f.seek(0)
        data = f.read(1024)
        if int(data) == 1:
            MAINTEN = 1
        else:
            MAINTEN = 0
        f.close()
        logging.info("mainten data %s" % (data))
    except Exception , e:
        logging.info(str(e))

    try:
        f = open( os.path.join(os.path.dirname(__file__), "config/activity.json"))
        f.seek(0)
        data = f.read(1024*64)
        MainHandler.ACTIVITY_CONFIG = tornado.escape.json_decode(data) 
        f.close()
        logging.info("activity config data %s" % (data))
    except Exception , e:
        logging.info(str(e))

    # 定时加载活动通知
    try:
        f = open( os.path.join(os.path.dirname(__file__), "config/activity_notice.json"))
        f.seek(0)
        data = f.read()
        MainHandler.ACTIVITY_NOTICE = tornado.escape.json_decode(data) 
        f.close()
        #logging.info("activity notice data %s" % (data))
    except Exception , e:
        logging.info(str(e))

    try:
        f = open( os.path.join(os.path.dirname(__file__), "config/apl.json"))
        f.seek(0)
        data = f.read(1024*64)
        MainHandler.APL_CONFIG = tornado.escape.json_decode(data) 
        f.close()
        logging.info("apl config data %s" % (data))
    except Exception , e:
        logging.info(str(e))

    from api.data.mail import Mail
    m = Mail.get("ALL_INVOKE")
    if m:
        MainHandler.SYSTEM_MAIL = m.mail
    else:
        MainHandler.SYSTEM_MAIL = []
       
@gen.coroutine
def shell():
    BaseModel.install()
    request = XRequest()
    yield watchdog()
    code.interact(local=locals())


if __name__ == "__main__":
    parse_command_line()

    if options.shell == 1:
        ioloop.IOLoop.instance().run_sync(shell)  
    BaseModel.install()
    start_stats()
    application.listen(options.port, address= options.host,xheaders=True)
    # add signal handler to stop server
    signal.signal(signal.SIGTERM , sig_handler)
    signal.signal(signal.SIGINT , sig_handler)
    logging.info("server started %s %s" % (options.port, options.host))
    PeriodicCallback(watchdog, 10000, io_loop=ioloop.IOLoop.instance()).start()
    ioloop.IOLoop.instance().add_callback(watchdog)
    ioloop.IOLoop.instance().start()
