# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
import os.path
import time
import signal
import logging
import code
import hashlib
import tornado
import tornado.escape
from tornado import gen
from tornado import ioloop
from tornado.web import HTTPError
from tornado.options import define, options, parse_command_line
from tornado.web import Application as BaseApplication
from model.admin import AdminUser
from collections import OrderedDict

MODULES =  OrderedDict([
    ("系统管理", {
        "mysetting": "我的设置",
        "users": "用户管理"
    }),

    ("运营工具", {
        "maintenance": "停机维护",
        "playermail": "玩家邮件",
        "globalmail": "全服邮件",
        "level": "关卡设置"
    }),

    ("玩家管理", {
        "player": "玩家查询"
    })
])


class TopHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_name = self.get_secure_cookie("pitaya_user")
        return user_name

    @tornado.web.authenticated
    @gen.coroutine
    def get(self):
        yield self.do_request()

    @tornado.web.authenticated
    @gen.coroutine
    def post(self):
        current_module = self.get_argument("module","mysetting")
        func = getattr(self, "post_%s" % (current_module))
        yield func()
        yield self.do_request()

    @gen.coroutine
    def do_request(self):
        user_name = self.get_current_user()
        user = yield AdminUser.get(user_name)
        usermodules = user.permissions
        current_module = self.get_argument("module","mysetting")
        active_menu = self.get_argument("menu","0")

        if user.pkey == u"admin":
            usermodules = []
            for entry_type in MODULES:
                for module in MODULES[entry_type]:
                    usermodules.append(module)

        elif usermodules:
            usermodules = usermodules.split(",")
        else:
            usermodules = []

        if "mysetting" not in usermodules:
            usermodules.append("mysetting")

        if current_module and current_module not in usermodules:
            raise HTTPError(403, "access resused!")

        datas = OrderedDict()
        entrys = OrderedDict()
        for entry_type in MODULES:
            entrys[entry_type] = {}
            for module in MODULES[entry_type]:
                if module in usermodules:
                    entrys[entry_type][module] = MODULES[entry_type][module]

        datas["entrys"] =  entrys
        datas["current_module"] = current_module
        datas["active_menu"] = active_menu
        datas["current_user"] = user
        self.render("%s.html" % (current_module), **datas)

    @gen.coroutine
    def post_mysetting(self):
        user_name = self.get_current_user()
        user = yield AdminUser.get(user_name)
        user.email = self.get_argument("email","")
        password = self.get_argument("password","")
        password_hash = hashlib.md5(tornado.escape.utf8(password)).hexdigest()
        user.password = password_hash
        yield user.put()

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html")

    @gen.coroutine
    def post(self):
        user_name = self.get_argument("user")
        password = self.get_argument("pass","")
        password_hash = hashlib.md5(tornado.escape.utf8(password)).hexdigest()
        user = yield AdminUser.get(user_name)
        if user_name == u"admin" and not user:
            user = AdminUser()
            user.pkey = "admin"
            user.password = hashlib.md5(tornado.escape.utf8("pitaya4108")).hexdigest()
            yield user.put()

        if not user:
            self.render("login.html", error="user not found")
            raise gen.Return(None);
        elif user.password != password_hash:
            self.clear_cookie("pitaya_user")
            self.render("login.html", error="password error")
            raise gen.Return(None)
        logging.info("%s login" % (user_name))
        self.set_secure_cookie("pitaya_user", tornado.escape.utf8(user_name))
        self.redirect(self.get_argument("next", "/"))

class LogoutHandler(tornado.web.RequestHandler):
    def post(self):
        self.do_request()

    def get(self):
        self.do_request()

    def do_request(self):
        self.clear_cookie("pitaya_user")
        self.redirect("/login/")

settings = dict(
                    template_path=os.path.join(os.path.dirname(__file__), "templates"),
                    static_path=os.path.join(os.path.dirname(__file__), "static"),
                    xsrf_cookies=False,
                    cookie_secret="dsfc333cdddW!0de",
                    login_url="/login/"
                )
class Application(BaseApplication):
    def listen(self, port, address="", **kwargs):
        super(Application, self).listen(port, address, **kwargs)

admin = Application([
    (r"/login/", LoginHandler),
    (r"/logout/", LogoutHandler),
    (r"/", TopHandler)
],**settings)

@gen.coroutine
def shell():
    code.interact(local=locals())

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
define("port" , default=8080, help="http server listening port", type=int)

if __name__ == "__main__":
    parse_command_line()

    admin.listen(options.port, address= options.host,xheaders=True)
    # add signal handler to stop server
    signal.signal(signal.SIGTERM , sig_handler)
    signal.signal(signal.SIGINT , sig_handler)
    logging.info("server started %s %s" % (options.port, options.host))
    ioloop.IOLoop.instance().start()
