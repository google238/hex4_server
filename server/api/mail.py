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
import time
import copy
import logging
import tornado
import hashlib
import shortuuid
import math
from tornado import gen
from api.data.mail import Mail, MAIL_LEN
from api.data.friends import Friends
from api.data.player import FBIdBind, Player 
from db import BaseModel

SENDHEART_INTERVAL = 1800

class Service(object):
    @gen.coroutine 
    def do_request(self):
        method = self.request.get_argument("method",u"")
        self.num  = int(self.request.get_argument("num",u"0"))
        self.type = self.request.get_argument("type",u"")
        self.fids  = self.request.get_argument("fid",u"")
        if not self.uid:
            raise gen.Return({"status":404, "content":[]})

        self.mail = Mail.get(self.uid)
        #if (not self.mail) and self.uid != self.sbs_uid:
        #    fbbind = FBIdBind.get(self.uid)
        #    if fbbind:
        #        self.mail = Mail.get(fbbind.sbs_user_id)
        #        if self.mail:
        #            self.mail.pkey = self.uid
        #            self.mail.put()

        if not self.mail:
            self.mail = Mail()
            self.mail.pkey = self.uid

        if method == "list":
            result = self.mail_list()
        elif method == "send":
            result = self.mail_send()
        elif method == "recieve":
            result = self.mail_recieve()
        elif method == "count":
            result = self.mail_count()
        else: 
            result = {"status":404, "content":[]}
        raise gen.Return( result )
    
    def mail_list(self):
        mail = self.mail
        result = {"status":404, "content":[]}
        if mail:
           result["status"] = 200
           result["content"] = mail.mail
        return result
  
    def mail_count(self):
        mail = self.mail
        result = {"status":404, "content":[]}
        if mail:
           result["status"] = 200
           result["content"] = filter(lambda m: not m.get("opened"), mail.mail)
           result["count"] = len(result["content"])

        return result

    def mail_send(self):
        player = Player.get(self.uid) 
        name = ''
        fbname = ''
        avatar = ''
        if player:
            name = player.name
            fbname = player.fbname
            avatar = player.avatar

        message = {"mid"   :shortuuid.uuid()[:8],
                   "local_mid":"",
                   "opened":False,
                   "time"  :int(time.time()),
                   "type"  :self.type,
                   "num"   :self.num,
                   "name"  :name,
                   "fbname"  :fbname,
                   "avatar":avatar,
                   "sender":self.uid
                  }

        if self.type == "heart":
            friends = Friends.get(self.uid)
            if not friends:
                friends = Friends()
                friends.pkey = self.uid

        for fid in self.fids.split(","):
            mail =  Mail.get(fid)
            if not mail:
                mail = Mail()
                mail.pkey = fid

            if self.type == "heart":
                # 送体力检测
                f_obj = Player.get(fid) 
                if not f_obj:
                    logging.info("[%s]赠送体力给好友[%s]时，好友不存在!" % (self.uid, fid))
                    continue #好友不存在

                # 判断好友是关闭了接收体力
                if int(f_obj.recieve_heart) == 0:
                    logging.info("[%s]赠送体力给好友[%s]时，好友关闭了体力接收!" % (self.uid, fid))
                    continue
            message["mid"] = shortuuid.uuid()[:8]
            mail.delete_old()
            mail.mail.insert(0,message)
            mail.put()

            if self.type == "heart":
                friends.hearts[fid] = int(time.time())

        #if self.type == "heart":
        #    for key,value in copy.copy(friends.hearts.items()):
        #        if (int(time.time()) - value) > SENDHEART_INTERVAL:
        #            del friends.hearts[key]
        #    friends.put()

        result = {"status":200, "content":[]}
        return result
 
    def mail_recieve(self):
        mid = self.request.get_argument("mid",u"")
        mail = self.mail

        if mail:
            #for m in mail.mail:
            #    if m["mid"] == mid:
            #        m["opened"] = True
            #mail.put()
            mails = copy.deepcopy(mail.mail)
            for msg_id  in mid.split(","):
                for m in mails:
                    if m["mid"] == msg_id:
                        mail.mail.remove(m)
            mail.put()
                
        result = {"status":200, "content":[]}
        return result
