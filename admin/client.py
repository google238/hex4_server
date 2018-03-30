#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
import os
import tornado
from tornado.httpclient import HTTPRequest, HTTPClient
from tornado import ioloop
from tornado import gen
import hashlib
import hmac
import base64
import signal
import code
import time
from tornado import gen
from tornado import ioloop
from tornado.options import define, options, parse_command_line
import logging
import functools
from email.utils import formatdate
import logging
from tornado.httpclient import HTTPRequest, AsyncHTTPClient

REQUEST_SIGN_FORMAT = "%s\n%s\n%s\nx-sbs-date:%s\nx-sbs-id:%s\nx-sbs-user-id:%s\n%s"
RESPONSE_SIGN_FORMAT = "%s\n%s\n%s\nx-sbs-date:%s\n%s"

def makeReuestHeader(sbs_id , device_id, sbs_user_id, password, method, path, content_type = "", content = ""):
    content_md5 = hashlib.md5(content).hexdigest() if content else ""
    sbs_date = formatdate(timeval=None, localtime=False, usegmt=True)

    stringToSign = REQUEST_SIGN_FORMAT % (method.upper(),
                                          content_md5,
                                          content_type,
                                          sbs_date,
                                          sbs_id,
                                          sbs_user_id,
                                          path
                                         )
    signature_hex = hmac.new(str(password), str(stringToSign), hashlib.sha1).digest()
    signature = base64.b64encode(signature_hex)
    headers = {}
    headers["X-SBS-ID"] = sbs_id
    headers["X-SBS-USER-ID"] = sbs_user_id
    headers["X-SBS-DATE"] = sbs_date
    if content_type:
        headers["Content-Type"] = content_type
    headers["Authorization"] = "SBS %s:%s" % (device_id, signature)
    return headers

class Sbs(object):
    def __init__(self, sbs_id, sbs_user_id, device_id, password, url =  "https://sbs.playfun.me"):
        self.sbs_id = sbs_id
        self.sbs_user_id = sbs_user_id
        self.device_id = device_id
        self.password = password
        self.httpClient = AsyncHTTPClient()
        self.sbs_url = url

    @gen.coroutine
    def getUserData(self,  user_id):
        path = "/users/%s" % (user_id)
        headers =  makeReuestHeader(self.sbs_id, self.device_id, self.sbs_user_id, self.password, "GET", path)
        response = yield self.httpClient.fetch("%s%s" % (self.sbs_url, path), method="GET",headers=headers)
        raise gen.Return(tornado.escape.json_decode(response.body))

    @gen.coroutine
    def getUserPaymentsDetails(self,  user_id):
        path = "/users/%s/payments?details=true" % (user_id)
        headers =  makeReuestHeader(self.sbs_id, self.device_id, self.sbs_user_id, self.password, "GET", path)
        response = yield self.httpClient.fetch("%s%s" % (self.sbs_url, path), method="GET",headers=headers)
        raise gen.Return(tornado.escape.json_decode(response.body))

    @gen.coroutine
    def getUserPayments(self,  user_id):
        path = "/users/%s/payments" % (user_id)
        headers =  makeReuestHeader(self.sbs_id, self.device_id, self.sbs_user_id, self.password, "GET", path)
        response = yield self.httpClient.fetch("%s%s" % (self.sbs_url, path), method="GET",headers=headers)
        raise gen.Return(tornado.escape.json_decode(response.body))

    @gen.coroutine
    def getBucketData(self, bucket,  user_id):
        path = "/%s/%s" % (bucket, user_id)
        headers =  makeReuestHeader(self.sbs_id, self.device_id, self.sbs_user_id, self.password, "GET", path)
        headers["Etag"] = "enforce_fresh"
        response = yield self.httpClient.fetch("%s%s" % (self.sbs_url, path), method="GET",headers=headers)
        raise gen.Return(tornado.escape.json_decode(response.body))

    @gen.coroutine
    def setBucketData(self, bucket,  user_id, data):
        path = "/%s/%s" % (bucket, user_id)
        headers =  makeReuestHeader(self.sbs_id, self.device_id, self.sbs_user_id, self.password, "PUT", path,content_type="application/json; charset=utf-8"  ,content=data)
        headers["Etag"] = "enforce_fresh"
        response = yield self.httpClient.fetch("%s%s" % (self.sbs_url, path), method="PUT",headers=headers, body= data)
        raise gen.Return(response.body)

    @gen.coroutine
    def getPayments(self,user_id):
        path = "/%s/%s" % ("payments", user_id)
        headers =  makeReuestHeader(self.sbs_id, self.device_id, self.sbs_user_id, self.password, "GET", path)
        headers["Etag"] = "enforce_fresh"
        response = yield self.httpClient.fetch("%s%s" % (self.sbs_url, path), method="GET",headers=headers)
        raise gen.Return(tornado.escape.json_decode(response.body))

    @gen.coroutine
    def get_social_bind(self, platform,  social_id):
        path = "/social/%s/%s" % (platform, social_id)
        headers =  makeReuestHeader(self.sbs_id, self.device_id, self.sbs_user_id, self.password, "GET", path)
        logging.info("%s%s" % (self.sbs_url, path))
        response = yield self.httpClient.fetch("%s%s" % (self.sbs_url, path), method="GET", headers=headers)
        raise gen.Return(tornado.escape.json_decode(response.body))

@gen.coroutine
def shell():
    sbs_id = "9wf8wrx3bqjbb47sictyzgf3"
    password = "gzrf1vq440k2qq3jrek9z8yaxq6d75l0n1iadoc1lhn1dwl"
    device_id = "adminplatform"
    client = Sbs(sbs_id, "43br56og2zmg", device_id, password)
    result = yield client.getBucketData("userData","43br56og2zmg")
    logging.info(result)

def shutdown():
    """ Stop server and add a callback to stop I/O loop"""
    try:
        io_loop = ioloop.IOLoop.instance()
        logging.info("Will shutdown in 2 seconds ...")
        io_loop.add_timeout(time.time() + 2, io_loop.stop)
    except Exception as e:
        logging.error(str(e))

def sig_handler(sig,frame):
    """ Catch signals and callback"""
    ioloop.IOLoop.instance().add_callback(shutdown)

if __name__ == "__main__":
    parse_command_line()

    # add signal handler to stop server
    signal.signal(signal.SIGTERM , sig_handler)
    signal.signal(signal.SIGINT , sig_handler)
    ioloop.IOLoop.instance().run_sync(shell)
