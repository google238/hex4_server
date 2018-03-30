#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
import tornado
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado import ioloop
from tornado import gen
import hashlib
import hmac
import base64
from email.utils import formatdate
from utils.sign import makeReuestHeader
import logging

class Sbs(object):
    def __init__(self, sbs_id, sbs_user_id, device_id, password):
        self.sbs_id = sbs_id
        self.sbs_user_id = sbs_user_id
        self.device_id = device_id
        self.password = password
        self.httpClient = AsyncHTTPClient()
        self.sbs_url = "https://api.sbs.wooga.com"

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
    def get_social_bind(self, platform,  social_id):
        path = "/social/%s/%s" % (platform, social_id)
        headers =  makeReuestHeader(self.sbs_id, self.device_id, self.sbs_user_id, self.password, "GET", path)
        logging.info("%s%s" % (self.sbs_url, path))
        response = yield self.httpClient.fetch("%s%s" % (self.sbs_url, path), method="GET", headers=headers)
        raise gen.Return(tornado.escape.json_decode(response.body))
