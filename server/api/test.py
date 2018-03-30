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
import logging
import tornado
import hashlib
from tornado import gen
from tornado.httpclient import *
liveURL = 'https://buy.itunes.apple.com/verifyReceipt'
sandboxURL = 'https://sandbox.itunes.apple.com/verifyReceipt'

class Service(object):
    @gen.coroutine 
    def do_request(self):
        raise gen.Return({"status":200,"data":"OK"})
"""
    def do_request(self):
        message = self.request.get_argument("data",u"")
        data = message.replace(" ","+")
        if not data:
            raise gen.Return({"status":200,"data":"OK"})
        jsonData = tornado.escape.json_encode({'receipt-data': data})
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(liveURL, method='POST', body=jsonData)
        logging.info("verifyReceipt %s" % (response.body))
        result = tornado.escape.json_decode(response.body) 
        if result.get("status",-1) == 0:
            raise gen.Return(self.get_md5_result(result))
        elif result.get("status",-1) == 21007:
            http_client2 = AsyncHTTPClient()
            response2 = yield http_client2.fetch(sandboxURL, method='POST', body=jsonData)
            logging.info("verifyReceipt %s" % (response2.body))
            result2 = tornado.escape.json_decode(response2.body)
            if result2.get("status",-1) == 0:
                raise gen.Return(self.get_md5_result(result2))
        raise gen.Return("")

    def get_md5_result(self,result):
        try:
            transaction_id  = result.get("receipt",{}).get("in_app",[{}])[0].get("transaction_id","") + "pitaya"
        except:
            transaction_id = "pitaya"
        return hashlib.md5(transaction_id).hexdigest()
"""
