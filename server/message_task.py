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
def msg_send(msg_type, target_id):
    if target_id and msg_type:
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
        msgobj = Mail.get(target_id)
        if not msgobj:
            msgobj = Mail()
            msgobj.pkey = target_id
        msgobj.delete_old()
        msgobj.mail.insert(0,msg)
        msgobj.put()   
        logging.info("target_id: %s %s" % (target_id, msg))

@gen.coroutine
def fetch_uids(msg_type):
    p = subprocess.Popen('/bin/sh /data/uids/stats_uids.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        uid = line.split("|")[-1]
        yield msg_send(msg_type ,uid)
        yield gen.sleep(0.01)
    retval = p.wait()
   
@gen.coroutine
def shell():
    BaseModel.install()
    db = Connection("172.31.15.206:3306", "admin" ,"pitayagames", "cUycN6&$")
    msgs = db.query("SELECT * FROM adm_message where status = 1 and intask = 0 limit 1")
    for msg in msgs:
        db.execute("update adm_message set intask = 1 where msgid = %d" % (msg.get("msgid")))
        if msg.get("send_all", 0 ) == 1:
            if msg.get("self_invoke", 0 ) == 1:
                yield msg_send(msg.get("msgtype","") , "ALL_INVOKE")
            else:
                yield fetch_uids(msg.get("msgtype",""))
        else:
            user_id = msg.get("target","");
            userids = user_id.split(",")
            for uid in userids:
                yield msg_send(msg.get("msgtype","") , uid)
        db.execute("update adm_message set status = 2 where msgid = %d" % (msg.get("msgid")))
    db.close()

if __name__ == "__main__":
    parse_command_line()
    ioloop.IOLoop.instance().run_sync(shell)  
