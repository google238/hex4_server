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
from api.data.friends import *
from db.mysql import Connection 
import shortuuid
import subprocess

@gen.coroutine
def stats_friends(target_id):
    f =  Friends.get(target_id)
    if not f:
         f = Friends()

    ff = FacebookFriends.get(target_id)
    if not ff:
         ff = FacebookFriends()
    l1 = len(f.friends)
    l2 = len(ff.friends)
    f.friends.extend(ff.friends)
    fn = set(f.friends)
    print(target_id, len(fn), l1, l2)

@gen.coroutine
def fetch_uids():
    BaseModel.install()
    f = open("/data/uids/201608151807.txt")
    for uid in f:
        if uid.strip():
            yield stats_friends(uid.strip())
            yield gen.sleep(0.01)
    f.close()
   
if __name__ == "__main__":
    parse_command_line()
    ioloop.IOLoop.instance().run_sync(fetch_uids)  
