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
import shortuuid
import math
import time
from tornado import gen
from tornado.options import define, options
from api.data.friends import Friends,FacebookFriends
from api.data.player import Player, FBIdBind
from api.data.regcode import RegCode
from api.data.level import Level
from api.data.mail import Mail, MAIL_LEN

from db import BaseModel
uuid_engine = shortuuid.ShortUUID(alphabet="1234567890abcdefghigklmnopqrstuvwxyz")
SENDHEART_INTERVAL = 1800
FRIEND_LIMIT = 100
class Service(object):
    @gen.coroutine
    def do_request(self):
        method = self.request.get_argument("method",u"")
        if not self.uid:
            raise gen.Return({"status":404, "content":[]})
        self.friends = Friends.get(self.uid)

        """if (not self.friends) and self.uid != self.sbs_uid:
            fbbind = FBIdBind.get(self.uid)
            if fbbind:
                self.friends = Friends.get(fbbind.sbs_user_id)
                if self.friends:
                    self.friends.pkey = self.uid
                    self.friends.put()
                    for fid in self.friends.friends:
                        f = Friends.get(fid)
                        if f:
                            for i, n in enumerate(f.friends):
                                if n == self.sbs_uid:
                                    f.friends[i] = self.uid
                                    f.put()
        """
        if not self.friends:
            self.friends = Friends()
            self.friends.pkey = self.uid
            self.friends.put()

        self.fbfriends = FacebookFriends.get(self.uid)
        if not self.fbfriends:
            self.fbfriends = FacebookFriends()
            self.fbfriends.pkey = self.uid
            self.fbfriends.put()

        if method == "list":
            result = self.friend_list()
        elif method == "rank":
            result = self.friend_rank()
        elif method == "level":
            result = self.friend_level_rank()
        elif method == "add":
            result = self.friend_add()
        elif method == "syncfb":
            result = self.friend_sync_fb()
        elif method == "del":
            result = self.friend_del()
        elif method == "code":
            result = self.friend_code()
        elif method == "search":
            result = self.friend_search()
        elif method == "request":
            result = self.friend_request()
        elif method == "accept":
            result = self.friend_accept()
        elif method == "invite_count":
            result = self.invite_count()
        else:
            result = {"status":404, "content":[]}
        raise gen.Return( result )

    def user_list(self, uids):
        result = []
        for uid in uids:
            player = Player.get(uid)
            if player:
                result.append({"uid":    str(uid),
                               "name":   player.name,
                               "fbname": player.fbname,
                               "avatar": player.avatar if player.avatar else "0",
                               "banner": player.banner if player.banner else "0",
                               "fb_id":  player.fb_id,
                               "stars":  int(player.stars),
                               "is_local":uid == self.uid ,
                               "level":  int(player.level)
                              })
            else:
                result.append({"uid":    str(uid),
                               "name":   "",
                               "fbname":   "",
                               "avatar":   "0",
                               "fb_id":  "",
                               "stars":  0,
                               "is_local":uid == self.uid ,
                               "level":  0
                              })
        return result

    def friend_list(self):
        result = {"status":200, "content":[]}
        type = int(self.request.get_argument("type",u"0"))
        fids = self.friends.friends
        if type == 0:
            fb_fids = self.fbfriends.friends
            fids.extend(fb_fids)
        elif type == 1:
            fids = self.friends.invited
        elif type == 2:
            fids = self.fbfriends.friends
        if self.uid in fids:
           fids.remove(self.uid)
        fids = {}.fromkeys(fids).keys()
        if not fids:
            return result
        fids.sort()

        #cache_key = "%s|%s|%s" % ("TMP",type, hashlib.md5(str(fids)).hexdigest())
        #result["content"] = BaseModel.mc.get(cache_key,[])
        if not result["content"]:
            result["content"] = self.user_list(fids)
            #BaseModel.mc.set(cache_key,result["content"],timeout=1800)
        #logging.info(result)
        return result

    def friend_level_rank(self):
        count = int(self.request.get_argument("count",u"3"))
        level = int(self.request.get_argument("level",u"1"))
        result = self.friend_list()
        for user in result["content"]:
            level_key = "%s_%s" % (user["uid"], level)
            l = Level.get(level_key)
            if l:
                user["score"] = l.score
            else:
                user["score"] = 0
            user["level"] = level
        ranking = sorted(result["content"], key = lambda x : x.get("score",0), reverse = True)
        result["content"] = ranking[:count]
        return result

    def friend_rank(self):
        current_stars = self.request.get_argument("stars",u"0")
        current_name = self.request.get_argument("name",u"")
        current_fbname = self.request.get_argument("fbname",u"")
        current_avatar = self.request.get_argument("avatar",u"")
        current_banner = self.request.get_argument("banner",u"")
        current_fbid = self.request.get_argument("fb_id",u"")
        current_level = self.request.get_argument("level",u"0")
        page = int(self.request.get_argument("page",u"0"))
        result = self.friend_list()
        player = self.user_list([self.uid])
        if player:
            result["content"].append(player[0])
            result["content"][-1]["stars"] = int(current_stars)
            if current_fbid:
                result["content"][-1]["fb_id"] = current_fbid
            result["content"][-1]["name"] = current_name
            result["content"][-1]["fbname"] = current_fbname
            result["content"][-1]["avatar"] = current_avatar
            result["content"][-1]["banner"] = current_avatar
            result["content"][-1]["level"] = int(current_level)

        ranking = sorted(result["content"], key = lambda x : x.get("stars",0), reverse = True)
        totals = len(ranking)
        rank = 1
        for user_rank in ranking:
            user_rank["rank"] = rank
            lasttime = self.friends.hearts.get(user_rank["uid"],0)
            can_send = False

            if user_rank["uid"] != self.uid and (int(time.time()) - lasttime) > SENDHEART_INTERVAL:
                can_send = True
            user_rank["can_send_heart"] = can_send

            rank += 1
        pageNum = 100
        pageCount = int(math.ceil(totals /pageNum))
        if page > 0 and page <= pageCount:
            pass
        else:
            index = 0
            page = 1
            for f in ranking:
                page = int(index / pageNum) + 1
                if f.get("uid") == self.uid:
                    break
                index += 1
        result["totals"] = totals
        result["pages"] = pageCount
        result["pageSize"] = pageNum
        result["page"] = page
        result["content"] = ranking[(page-1)* pageNum: (page-1) * pageNum + pageNum]
        return result

    def friend_sync_fb(self):
        fids  = self.request.get_argument("fids","")
        fbid  = self.request.get_argument("fbid","")
        self.fbfriends.friends = []
        for fid in fids.split(","):
            if fbid == fid:
                continue

            sbs_bind = FBIdBind.get(fid)
            if sbs_bind:
                sbs_uid = sbs_bind.sbs_user_id
                if sbs_uid == self.uid:
                    continue
                if len(self.fbfriends.friends) < FRIEND_LIMIT and sbs_uid not in self.fbfriends.friends and sbs_uid not in self.friends.friends:
                    self.fbfriends.friends.append(sbs_uid) 
               
        self.fbfriends.put()
        return {"status":200, "content":[]}

    def friend_request(self):
        player = Player.get(self.uid)
        name = ''
        fbname = ''
        avatar = ''
        if player:
            name = player.name
            fbname = player.fbname
            avatar = player.avatar
        fid  = self.request.get_argument("fid","")
        if not fid:
            return {"status":404, "content":[]}

        friend = Friends.get(fid)
        if not friend:
            friend = Friends()
            friend.pkey = fid

        if fid in self.friends.friends:
            return {"status":405, "content":[]}

        if len(friend.friends) >= FRIEND_LIMIT:
            return {"status":406, "content":[]}

        if len(self.friends.friends) >= FRIEND_LIMIT:
            return {"status":407, "content":[]}

        message = {"mid":shortuuid.uuid()[:8],
                   "local_mid":"",
                   "opened"   :False,
                   "time"     :int(time.time()),
                   "type"     :'friend_request',
                   "num"      :1,
                   "name"     :name,
                   "fbname"   :fbname,
                   "avatar"   :avatar,
                   "sender":  self.uid
                  }

        mail =  Mail.get(fid)
        if not mail:
            mail = Mail()
            mail.pkey = fid
        mail.delete_old()

        for message in mail.mail:
            if message.get("type") == "friend_request" and message.get("sender") == self.uid:
                return {"status":408, "content":[]}

        mail.mail.insert(0,message)
        mail.put()
        return {"status":200, "content":[]}

    def friend_accept(self):
        player = Player.get(self.uid)
        name = ''
        fbname = ''
        avatar = ''
        if player:
            name = player.name
            fbname = player.fbname
            avatar = player.avatar
        fid  = self.request.get_argument("fid","")
        if not fid:
            return {"status":404, "content":[]}

        friend = Friends.get(fid)
        if not friend:
            friend = Friends()
            friend.pkey = fid

        if fid in self.friends.friends:
            return {"status":405, "content":[]}

        if len(friend.friends) >= FRIEND_LIMIT:
            return {"status":406, "content":[]}

        if len(self.friends.friends) >= FRIEND_LIMIT:
            return {"status":407, "content":[]}

        if fid not in self.friends.friends:
            self.friends.friends.append(fid)
            self.friends.put()

        if self.uid not in friend.friends:
            friend.friends.append(self.uid)
            friend.put()

        return {"status":200, "content":self.friends.friends}

    def friend_add(self):
        player = Player.get(self.uid)
        name = ''
        fbname = ''
        avatar = ''
        if player:
            name = player.name
            fbname = player.fbname
            avatar = player.avatar

        fid  = self.request.get_argument("fid","")
        code = self.request.get_argument("code","")
        invite = False
        if code:
            invite = True
            regcode = RegCode.get(code)
            if regcode:
                fid = regcode.uid
            else:
                return {"status":404, "first_invite":False ,"content":[]}

        if not fid:
            return {"status":404, "first_invite":False ,"content":[]}

        if fid == self.uid:
            return {"status":408, "first_invite":False ,"content":[]}

        friend = Friends.get(fid)
        if not friend:
            friend = Friends()
            friend.pkey = fid

        invite_ok = False 
        if invite and (not self.friends.inviter) and self.device_id not in friend.invited:
            invited_count = len(friend.invited)
            if invited_count < FRIEND_LIMIT:
                friend.invited.append(self.device_id)
                invited_count += 1

                mail =  Mail.get(fid)
                if not mail:
                    mail = Mail()
                    mail.pkey = fid
                count_set = (1,3,10,20)
                if invited_count in count_set:
                    msg = {"mid":shortuuid.uuid()[:8],
                           "local_mid": "invite_success_%d"%(count_set.index(invited_count)+1),
                           "opened":False,
                           "time"  :int(time.time()),
                           "type"  :"reward",
                           "num"   :1,
                           "name"  :"",
                           "fbname"  :"",
                           "avatar":"",
                           "sender":"gmuser"
                          }
                    mail.delete_old()
                    mail.mail.insert(0 , msg)

                msg = {"mid":shortuuid.uuid()[:8],
                           "local_mid": "invite_everytime_1",
                           "opened":False,
                           "time"  :int(time.time()),
                           "type"  :"reward",
                           "num"   :1,
                           "name"  :"",
                           "fbname"  :"",
                           "avatar":"",
                           "sender":"gmuser"
                       }
                mail.delete_old()
                mail.mail.insert(0 , msg)

                msg = {"mid":shortuuid.uuid()[:8],
                           "local_mid": "invite_everytime_2",
                           "opened":False,
                           "time"  :int(time.time()),
                           "type"  :"reward",
                           "num"   :1,
                           "name"  :"",
                           "fbname"  :"",
                           "avatar":"",
                           "sender":"gmuser"
                       }
                mail.delete_old()
                mail.mail.insert(0 , msg)

                mail.put()
                invite_ok = True
                friend.put()
            else:
                return {"status":409, "first_invite":False ,"content":[]}
 
        if len(friend.friends) >= FRIEND_LIMIT:
            return {"status":205 if invite_ok else 407, "first_invite":False, "content":[]}

        if len(self.friends.friends) >= FRIEND_LIMIT:
            return {"status":205 if invite_ok else 406, "first_invite":False, "content":[]}

        if self.uid not in friend.friends:
            friend.friends.append(self.uid)
            friend.put()

            message = {"mid"   :  shortuuid.uuid()[:8],
                       "local_mid":"",
                       "opened":   False,
                       "time"  :   int(time.time()),
                       "type"  :   'friend',
                       "num"   :   1,
                       "name"  :   name ,
                       "fbname"  :  fbname ,
                       "avatar":   avatar,
                       "sender":   self.uid,
                       "gift"  :   {"type":4 , "amount":1} 
                      }

            mail =  Mail.get(fid)
            if not mail:
                mail = Mail()
                mail.pkey = fid
            mail.delete_old()
            mail.mail.insert(0,message)
            mail.put()

        first_invite = False
        if fid not in self.friends.friends:
            self.friends.friends.append(fid)
            if invite and not self.friends.inviter:
                self.friends.inviter = fid
                first_invite = True
            self.friends.put()
        else:
            return {"status":205 if invite_ok else  405, "first_invite":False , "content":[]}
        return {"status":200 if invite_ok else 206, "first_invite":first_invite ,"content":self.friends.friends}

    def invite_count(self):
        invited = list(set(self.friends.invited))
        return {"status":200, "count": len(invited) , "content":[]}
 
    def friend_del(self):
        fids = self.request.get_argument("fid")
        for fid in fids.split(","):
            if fid in self.friends.friends:
                self.friends.friends.remove(fid)

            friend = Friends.get(fid)
            if friend and self.uid in friend.friends:
                friend.friends.remove(self.uid)
                friend.put()
        self.friends.put()
        return {"status":200, "content":self.friends.friends}

    def friend_search(self):
        code = self.request.get_argument("code","")
        fid = None
        if code:
            regcode = RegCode.get(code)
            if regcode:
                fid = regcode.uid
            else:
                return {"status":404, "content":[]}

        if not fid or fid == self.uid:
            return {"status":404, "content":[]}

        result = {"status":200, "content":[]}
        result["content"] = self.user_list([fid])
        return result

    def friend_code(self):
        sharetype  = int(self.request.get_argument("type","2"))
        if not self.friends.code:
            hit = False
            for i in xrange(6,25):
                for j in xrange(10):
                    pid = uuid_engine.uuid()[:i]
                    p = RegCode.get(pid)
                    if not p:
                        p = RegCode()
                        p.pkey = pid
                        p.uid = self.uid
                        p.put()
                        self.friends.code = pid
                        self.friends.put()
                        hit = True
                        break
                if hit:
                    break
        
        content = """『すみっコぐらし〜パズルをするんです〜』好評配信中♪
ID【%s】を入力して私と友だちになりましょう！"""% (self.friends.code)

        if self.language_code == "zh-hant" or self.language_code == "zh_hant":
            content = """超萌人氣手游《Sumikko gurashi-Puzzling Ways》好評上線♪
輸入ID【%s】和我成為好友，爭排名，送飯糰，驚喜不斷！"""% (self.friends.code)
        elif self.language_code == "en":
            content = """Kawaii crazy《Sumikko gurashi-Puzzling Ways》in service♪
Input ID【%s】to become friends，compete with friends，send energies each other！""" % (self.friends.code)
            
        facebook = {
                    "link": "http://%s/api/share/%s/?lang=%s&icode=%s" % (options.base_host, self.friends.code, self.language_code, self.friends.code),
                    "picture": "http://%s/images/fb600x315.jpg" % (options.base_host),
                   }
        return {"status":200, "code":self.friends.code, "content":content,"type":sharetype,"facebook":facebook}
