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
import time
import datetime
import copy
from tornado import gen
from tornado.httpclient import *
from distutils.version import LooseVersion

class Service(object):
    @gen.coroutine 
    def do_request(self):
        result = {"status":200,"data":[],"server_time":int(time.time()) * 1000 }
        t_method = self.request.get_argument("method", u"")
        if t_method == "notice":
            result["data"] = self.notice 
            raise gen.Return(result)

        for cnf in self.activity_config:
            if not cnf.get("usable", 0):
                continue

            channels = cnf.get("channels","").split(",")
            versions = cnf.get("minver","0.0.0").split(",")

            if self.channel not in channels:
                continue
            
            version_str = "0.0.0"
            for channel in channels:
                if channel == self.channel:
                    index_channel = channels.index(channel)
                    if index_channel < len(versions):
                        version_str = versions[index_channel]
                        break

            if self.client_version == "":
                self.client_version = "0.0.0"

            if LooseVersion(self.client_version) < LooseVersion(version_str):
                continue                 

            now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
            if now < cnf.get("start_time",now) or now > cnf.get("over_time",now):  
                continue
            acnf = copy.deepcopy(cnf)
            acnf['minver'] = version_str
            acnf['channels'] = self.channel
            result["data"].append(acnf) 
        raise gen.Return(result)
