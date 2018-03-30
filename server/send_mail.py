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
from db.mysql import Connection 
from api.data.mail import Mail
import shortuuid
import subprocess

@gen.coroutine
def msg_send(msg_types, target_id):
    if target_id:
        msgobj = Mail.get(target_id)
        if not msgobj:
            msgobj = Mail()
            msgobj.pkey = target_id

        for msg_type in msg_types:
            msg = {"mid":shortuuid.uuid()[:8],
                   "local_mid": msg_type,
                   "opened":False,
                   "time"  :int(time.time()),
                   "type"  :"reward",
                   "num"   :1,
                   "name"  :"",
                   "fbname"  :"",
                   "avatar":"",
                   "sender":"gmuser"
                   }
            msgobj.delete_old()
            msgobj.mail.insert(0,msg)
            logging.info("target_id: %s %s" % (target_id, msg))

        msgobj.put()   

@gen.coroutine
def fetch_uids():
    BaseModel.install()
    msg_type1= ["cat_cos_icon188"]
    msg_type2= ["cat_cos_icon191_1","cat_cos_icon191_2","cat_cos_icon191_3"]
    msg_type3= ["cat_coa_icon_192_1","cat_coa_icon_192_2"]
    f = open("/data/uids/uids.txt")
    for uid in f:
        if uid.strip():
            yield msg_send(msg_type1,uid.strip())
            yield gen.sleep(0.01)
    f.close()
   
if __name__ == "__main__":
    parse_command_line()
    ioloop.IOLoop.instance().run_sync(fetch_uids)  
