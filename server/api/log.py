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
import tornado.escape
from tornado import gen
from tornado.httpclient import *
from stats import stats_log
class Service(object):
    @gen.coroutine 
    def do_request(self):
        args = dict((k, v[-1]) for k, v in self.request.request.arguments.iteritems())
        jsonData = tornado.escape.json_encode(args)
        #stats_log(args.get("type"),jsonData)
        raise gen.Return("")
