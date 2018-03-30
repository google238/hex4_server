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
import copy
import shortuuid
import datetime
import time
from distutils.version import LooseVersion
from tornado import gen
from api.data.player import Checkin , Player, FBIdBind , Finance, Ruby, CheckinEvent
from api.data.level import Level
from api.data.friends import Friends
from api.data.mail import Mail

class Service(object):
    @gen.coroutine 
    def do_request(self):
        method = self.request.get_argument("method",u"")
        if not self.uid:
            raise gen.Return({"status":404, "content":[]})
        self.player = Player.get(self.uid)
        result = {"status":200, "content":[]}
        if not self.player:
            self.player = Player()
            self.player.pkey = self.uid
            self.player.put()
 
        if method == "save":
            self.player.pkey = self.uid
            self.player.name = self.request.get_argument("name",u"nobody")
            self.player.fbname = self.request.get_argument("fbname",u"")
            self.player.avatar = self.request.get_argument("avatar",u"")
            self.player.banner = self.request.get_argument("banner",u"")
            self.player.stars = int(self.request.get_argument("stars",u"0"))
            self.player.fb_id = self.request.get_argument("fb_id",u"") 
            self.player.level = int(self.request.get_argument("level",u"0"))
            self.player.recieve_heart = int(self.request.get_argument("recieve_heart",u"1"))

            maillist = self.system_mails
            m = Mail.get(self.uid)
            if not m:
                m = Mail()
                m.pkey = self.uid
            newmail = False
            for mail in self.system_mails:
                if mail.get("mid") and mail.get("mid") not in self.player.system_mail:
                    mail_send = copy.deepcopy(mail)
                    mail_send["mid"] = shortuuid.uuid()[:8] 
                    self.player.system_mail.append(mail.get("mid"))
                    m.append(mail_send)
                    newmail = True
            if newmail:
                m.put()

            self.player.put()

            if self.sbs_uid and self.player.fb_id:
                sbs_bind = FBIdBind.get(self.player.fb_id)
                if not sbs_bind:
                    sbs_bind = FBIdBind()
                    sbs_bind.pkey = self.player.fb_id
                    sbs_bind.sbs_user_id = self.sbs_uid
                    sbs_bind.put()
                    
            level = self.request.get_argument("cur_level",u"0")
            level_star = int(self.request.get_argument("level_star",u"0"))
            level_score = int(self.request.get_argument("level_score",u"0"))

            level_key = "%s_%s" % ( self.uid, level)

            l = Level.get(level_key)
            if not l:
                l = Level()
                l.pkey = level_key
                l.stars = level_star
                l.score = level_score
            elif level_star > l.stars: 
                l.stars = level_star
            elif level_score > l.score: 
                l.score = level_score
            l.put()
           
        elif method == "del":
            self.player.delete()
        elif method == "finance":
            f = Finance.get(self.uid) 
            if not f:
                f = Finance()
                f.pkey = self.uid
            f.source = self.request.get_argument("source",u"")
            f.total_gold = int(self.request.get_argument("total_gold",u"0"))
            f.total_free_gold = int(self.request.get_argument("total_free_gold",u"0"))
            f.total_pay_gold = int(self.request.get_argument("total_pay_gold",u"0"))
            f.total_ruby = int(self.request.get_argument("total_ruby",u"0"))
            f.total_free_ruby = int(self.request.get_argument("total_free_ruby",u"0"))
            f.total_pay_ruby = int(self.request.get_argument("total_pay_ruby",u"0"))
            f.gold = int(self.request.get_argument("gold",u"0"))
            f.free_gold = int(self.request.get_argument("free_gold",u"0"))
            f.pay_gold = int(self.request.get_argument("pay_gold",u"0"))
            old_ruby = f.ruby
            ruby_changed = False
            f.ruby = int(self.request.get_argument("ruby",u"0"))
            if old_ruby != f.ruby:
                ruby_changed = True

            f.free_ruby = int(self.request.get_argument("free_ruby",u"0"))
            f.pay_ruby = int(self.request.get_argument("pay_ruby",u"0"))

            delta_ruby = int(self.request.get_argument("delta_ruby",u"0"))
            delta_free_ruby = int(self.request.get_argument("delta_free_ruby",u"0"))

            f.put()

            if ruby_changed:
                r = Ruby.get(self.uid)
                if not r:
                    r = Ruby()
                    r.pkey = self.uid
                if len(r.list) > 500:
                    r.list.pop() 
                if ruby_changed:
                    r.list.insert(0,[f.source, f.ruby, f.pay_ruby, delta_ruby , delta_free_ruby, time.time()])
                r.put()

        elif method == "getbind":
            pid = self.request.get_argument("pid",u"")
            player = Player.get(pid)
            if player and player.fb_id:
                result["content"].append(player.fb_id) 
        elif method == "getfbbind":
            pid = self.request.get_argument("pid",u"")
            sbs_bind = FBIdBind.get(pid)
            if sbs_bind and sbs_bind.sbs_user_id:
                result["content"].append(sbs_bind.sbs_user_id) 
            result = {"status":404, "content":[]}
        elif method == "checkin":
            starttime = self.request.get_argument("start", "0000")
            endtime = self.request.get_argument("end", "9999")
            c = Checkin.get(self.uid) 
            if not c:
                c = Checkin()
                c.pkey = self.uid
            
            now = (datetime.datetime.now() - datetime.timedelta(hours=3)).strftime("%Y%m%d")
            if c.data.get(now) == 1:
                result["status"] = 201 
            else:
                c.data[now] = 1
                for key in c.data.keys():
                    if key < starttime or key > endtime:
                        del c.data[key]
                c.put()

                l = len(c.data)
                if l in (1,2,3,4,5,6,7,8):
                    msgobj = Mail.get(self.uid)
                    if not msgobj:
                        msgobj = Mail()
                        msgobj.pkey = self.uid
                     
                    msg = {"mid":shortuuid.uuid()[:8],
                           "local_mid": "checkInActivity_%d" % (l),
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
                    msgobj.put()

            result["content"] = c.data.keys() 

        # 签到事件2
        elif method == "checkin_event":
            logging.info("checkin_event:%s" % self.uid)
            c = CheckinEvent.get(self.uid)
            if not c:
                c = CheckinEvent()
                c.pkey = self.uid

            now = (datetime.datetime.now() - datetime.timedelta(hours=3)).strftime("%Y%m%d")
            if c.data.get(now) == 1:
                result["status"] = 201 
            else:
                c.data[now] = 1
                for key in c.data.keys():
                    if not key.startswith(now[:6]):
                        del c.data[key]
                c.put()

            result["content"] = c.data.keys()

        elif method == "getservertime":
            result["content"] = int(time.time())

        elif method == "checkinlist":
            starttime = self.request.get_argument("start", "0000")
            endtime = self.request.get_argument("end","9999")
            c = Checkin.get(self.uid) 
            if not c:
                c = Checkin()
                c.pkey = self.uid
            now = (datetime.datetime.now() - datetime.timedelta(hours=3)).strftime("%Y%m")
            for key in c.data.keys():
                if key < starttime or key > endtime:
                    del c.data[key]
            c.put()
            result["content"] = c.data.keys() 
        raise gen.Return( result )
