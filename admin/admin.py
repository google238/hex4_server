# -*- coding: utf-8 -*-
import tornado
import shlex, subprocess
import time
import datetime
import tornado.ioloop
import tornado.web
import os, uuid
import logging
import hashlib
import signal
from collections import OrderedDict
from StringIO import StringIO
from tornado import gen
import tornado.httpserver
from tornado.options import define, options, parse_command_line
from mysql import Connection
from tornado.escape import json_encode, json_decode
from level import level_std

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import json
from db import BaseModel
from client import Sbs

define("port", default=8080, help="run on the given port", type=int)
define("mysql_host", default="172.31.15.206:3306", help="admin database host")
define("mysql_database", default="admin", help="admin database name")
define("mysql_user", default="pitayagames", help="admin database user")
define("mysql_password", default="cUycN6&$", help="admin database password")

define("sbs_url", default="https://sbs.playfun.me", help="sbs url")
define("sbs_key", default="9wf8wrx3bqjbb47sictyzgf3", help="sbs admin id")
define("sbs_pass", default="gzrf1vq440k2qq3jrek9z8yaxq6d75l0n1iadoc1lhn1dwl", help="sbs password")

modules = ['playerids','playerdatas','playercommands','ad','gacha','avatar','event','apl','level','pic','activity','battleserv','logicserv', 'dataserv' , 'cacheserv', 'guestmsg' ,'pushmsg', 'mainten', 'notice', 'gift', 'player', 'payment', 'finance', 'shopcnf', 'levelcnf' ,'mapcnf' , 'copycnf', 'taskcnf', 'users']

events = {1: "钻石促销",
          2: "体力促销",
          3: "金币促销",
          4: "gacha打折",
          5: "复活打折",
          6: "关卡前道具打折",
          7: "关卡内道具打折",
          8: "gacha重复点数翻倍",
          9: "签到",
          10: "体力回复速度翻倍",
          11: "道具得分速度翻倍",
          12: "关卡得分翻倍",
          13: "钻石解锁MINI",
          14: "首次通关金币奖励翻倍",
          15: "关卡前道具免费",
          16: "首次lucky bonus免费",
          20: "登录送钻石",
          101: "白熊gachaUP",
          102: "蜥蜴gachaUP",
          103: "企鹅gachaUP",
          104: "猪排gachaUP",
          105: "猫gachaUP",
          201: "主题1gachaUP",
          202: "主题2gachaUP",
          203: "主题3gachaUP",
          204: "主题4gachaUP",
          205: "主题5gachaUP"
          }

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

def send_mail(subject,content):
    from_addr = "mon@pitayagames.com"
    to_addr = ["5695953@qq.com","331620337@qq.com","331700165@qq.com", "454235581@qq.com", "6468158@qq.com","z@pitayagames.com"]
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = _format_addr(u'Sumikko后台 <%s>' % from_addr)
    msg['To'] = ", ".join(to_addr)
    msg['Subject'] = Header(u'【SUMIKKO 重要提醒】%s' % (subject), 'utf-8').encode()
    server = smtplib.SMTP_SSL("smtp.exmail.qq.com",port=465)
    server.login(from_addr, "Pitaya.1058")
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.close()

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        user_id = self.get_secure_cookie("pitaya_user")
        if not user_id: return None
        return self.db.get("SELECT * FROM adm_users WHERE locked <> 1 and user_id = %s", user_id)

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.do_request()

    @tornado.web.authenticated
    def post(self):
        self.do_request()

    def do_request(self):
        user = self.get_current_user()
        usermodules  =user.get('module_ids','')
        if user.get('user_id','') == 'admin':
            usermodules = ['users']
        elif usermodules:
            usermodules = usermodules.split(",")
        else:
            usermodules = []
        datas = {}
        for v in modules:
            if v in usermodules:
                 datas[v] = True
            else:
                 datas[v] = False
        self.render("index.html", **datas)

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    @gen.coroutine
    def post(self):
        author = self.db.get("SELECT * FROM adm_users WHERE locked <> 1 and user_id = %s limit 1",
                             self.get_argument("user"))
        if not author:
            self.render("login.html", error="user not found")
            return
        elif self.get_argument("user") != u"admin" and author['password'] != hashlib.md5(tornado.escape.utf8(self.get_argument("pass",u""))).hexdigest():
            self.render("login.html", error="password error")
            return
        logging.info("%s login" % (self.get_argument("user")))
        self.set_secure_cookie("pitaya_user", tornado.escape.utf8(self.get_argument("user",u"")))
        self.redirect(self.get_argument("next", "/"))

class LogoutHandler(BaseHandler):
    def post(self):
        self.do_request()

    def get(self):
        self.do_request()

    def do_request(self):
        self.clear_cookie("pitaya_user")
        self.redirect("/login")

class MaintenHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self, method):
        self.do_request(method)

    def do_request(self,method):
        if method == "list":
            fo = open("/home/sumikko/admin/sync/mainten.txt", "r+")
            lines = [line.rstrip('\n') for line in fo]
            maint = False
            if len(lines) > 0 and lines[0] == "1":
                maint = True
            self.render("mainten.html", maint=maint)
            fo.close()
            return

        if method == "restart":
            cmd = '/bin/sh /home/sumikko/admin/sync/restart_server.sh'
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            logging.info(output)
            self.write(output)

        if method == "updateres":
            cmd = '/bin/sh /home/sumikko/admin/sync/sync_resource.sh'
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            logging.info(output)
            self.write(output)

        if method == "updatecode":
            cmd = '/bin/sh /home/sumikko/admin/sync/sync_code.sh'
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            logging.info(output)
            self.write(output)

        if method == "maint":
            fo = open("/home/sumikko/admin/sync/mainten.txt", "r+")
            lines = [line.rstrip('\n') for line in fo]
            maint = False
            if len(lines) > 0 and lines[0] == "1":
                maint = True
            fo.close()
            if maint:
                cmd = 'echo "0" > /home/sumikko/admin/sync/mainten.txt'
            else:
                cmd = 'echo "1" > /home/sumikko/admin/sync/mainten.txt'
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            logging.info(output)
            output = subprocess.check_output("/bin/sh /home/sumikko/admin/sync/sync_mainten.sh", stderr=subprocess.STDOUT, shell=True)
            logging.info(output)
            self.write(output)
            send_mail(cmd, cmd)

class ActivityHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self,method):
        self.do_request(method)

    def do_request(self, method):
        if method == "list":
            activities = self.db.query("SELECT * FROM adm_activity order by activity_id"),
            self.render("activity.html", adm_activity = activities[0])
        if method == "addcommit":
            addnew = int(self.get_argument("addnew","-1"))
            activity_id = int(self.get_argument("activity_id","-1"))
            minver = self.get_argument("minver")
            channels = self.get_argument("channels")
            data = self.get_argument("data", "")
            start_time = self.get_argument("start_time","")
            over_time = self.get_argument("over_time","")
            try:
                values = "minver='%s', channels='%s', data='%s' ,start_time='%s', over_time='%s'" % (minver, channels , data, start_time , over_time)
                if addnew >= 0 :
                    sql = "UPDATE adm_activity SET %s where activity_id=%d"%(values, activity_id)
                    cmd = "活动配置ID %s-%s 被修改了,请到后台管理确认 %s" % (activity_id, events.get(activity_id,activity_id), values)
                else:
                    sql = "INSERT INTO adm_activity SET activity_id=%s, %s "%(activity_id, values)
                    cmd = "活动配置ID %s-%s 添加了,请到后台管理确认 %s" % (activity_id, events.get(activity_id,activity_id),values)
                self.db.execute(sql)
                if addnew >= 0 :
                    activities = self.db.query("SELECT * FROM adm_activity order by activity_id"),
                    fo = open("/home/sumikko/admin/sync/activity.json", "w")
                    fo.write(json_encode(activities[0]))
                    fo.close()
                    output = subprocess.check_output("/bin/sh /home/sumikko/admin/sync/sync_activity.sh", stderr=subprocess.STDOUT, shell=True)
                send_mail(cmd, cmd)
            except Exception, e:
                logging.error(str(e))
                self.write('')

        if method == "del":
            activity_id = int(self.get_argument("id"))
            self.db.execute("delete from adm_activity  where activity_id=%d" % (activity_id))
            cmd = "活动配置ID %s-%s 删除了,请到后台管理确认 " % (activity_id, events.get(activity_id,activity_id))
            send_mail(cmd, cmd)

        if method == "start":
            activity_id = int(self.get_argument("id"))
            self.db.execute("update adm_activity set usable=MOD(usable + 1,2)  where activity_id=%d" % (activity_id))
            activities = self.db.query("SELECT * FROM adm_activity order by activity_id"),
            fo = open("/home/sumikko/admin/sync/activity.json", "w")
            fo.write(json_encode(activities[0]))
            fo.close()
            output = subprocess.check_output("/bin/sh /home/sumikko/admin/sync/sync_activity.sh", stderr=subprocess.STDOUT, shell=True)
            cmd = "活动配置ID %s-%s 处于生效状态了,请到后台管理确认 " % (activity_id, events.get(activity_id,activity_id))
            send_mail(cmd, cmd)

class ActivityNoticeHandler(BaseHandler):
    '''活动通知'''
    def post(self, method):
        self.do_request(method)

    def get(self, method):
        self.do_request(method)

    def do_request(self, method):
        dir_name = os.path.join(os.path.dirname(__file__), "sync")
        t_noticefile, t_noticedata = os.path.join(dir_name, "activity_notice.json"), ""
        if method == "list":
            if os.path.exists(t_noticefile):
                with open(t_noticefile, "rb") as pf:
                    t_noticedata = pf.read()
            self.render("activity_notice.html", noticedata=t_noticedata)
        elif method == "save":
            t_noticedata = self.get_argument("data") 
            try:
                t_check = json.loads(t_noticedata)
                with open(t_noticefile, "wb") as pf:
                    pf.write(t_noticedata)
                output = subprocess.check_output("/bin/sh %s/sync_activity_notice.sh" % (dir_name), stderr=subprocess.STDOUT, shell=True)
                self.write(output)
            except Exception, e:
               logging.error(str(e))
               self.write(str(e))

class AplHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self,method):
        self.do_request(method)

    def do_request(self, method):
        if method == "list":
            apls = self.db.query("SELECT * FROM adm_apl order by  apl_id"),
            self.render("apl.html", adm_apl = apls[0])
        if method == "save":
            apl_id = int(self.get_argument("apl_id",""))
            version = self.get_argument("version","")
            opened = int(self.get_argument("opened", 0))
            try:
                values = "version='%s', opened=%d " % (version, opened)
                sql = "UPDATE adm_apl SET %s where apl_id=%d" %(values, apl_id)
                self.db.execute(sql)
                activities = self.db.query("SELECT * FROM adm_apl order by apl_id"),
                fo = open("/home/sumikko/admin/sync/apl.json", "w")
                fo.write(json_encode(activities[0]))
                fo.close()
                output = subprocess.check_output("/bin/sh /home/sumikko/admin/sync/sync_apl.sh", stderr=subprocess.STDOUT, shell=True)
            except Exception, e:
                logging.error(str(e))
                self.write('')

class GuestmsgHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self,method):
        self.do_request(method)

    def do_request(self, method):
        if method == "list":
            msgs = self.db.query("SELECT * FROM adm_message order by msgid desc"),
            self.render("message.html", adm_message = msgs[0])
        if method == "addcommit":
            msgid = int(self.get_argument("msgid","-1"))
            msgtype = self.get_argument("msgtype")
            target = self.get_argument("target")
            send_all = self.get_argument("send_all","0")
            self_invoke = self.get_argument("self_invoke","0")
            if send_all == "0":
                send_all = 0
            else:
                send_all = 1

            if self_invoke == "0":
                self_invoke = 0
            else:
                self_invoke = 1

            try:
                values = "msgtype='%s',target='%s', send_all=%d, self_invoke=%d" % (msgtype, target, send_all, self_invoke)
                if msgid >= 0 :
                    sql = "UPDATE adm_message SET %s where msgid=%d"%(values, msgid)
                else:
                    sql = "INSERT INTO adm_message SET %s "%(values)
                self.db.execute(sql)
            except Exception, e:
                logging.error(str(e))
                self.write('')

        if method == "del":
            msgid = int(self.get_argument("id"))
            self.db.execute("delete from adm_message  where msgid ='%d'" % (msgid))

        if method == "start":
            msgid = int(self.get_argument("id"))
            self.db.execute("update adm_message set status=1  where msgid ='%d'" % (msgid))

class FinanceHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self,method):
        self.do_request(method)

    def do_request(self, method):
        if method == "list":
            nowstr = (datetime.datetime.today() - datetime.timedelta(days=1) ).strftime("%Y-%m-%d")
            datestr = self.get_argument("date", nowstr)
            dateendstr = self.get_argument("date_end", nowstr)
            versionstr = self.get_argument("version", '')

            fields = self.db.query("select * from Level limit 1");
            extras = ""
            extraFields = []
            for f in fields[0]:
                if "prestartItems" in f or "stageItems" in f:
                    extras += ",sum(%s) as %s" % (f,f)
                    extraFields.append(f)
            logging.info(extras)
            if not datestr:
                datestr = nowstr
            if not dateendstr:
                dateendstr = nowstr
            wherestr = " datestr >= '%s' and datestr <= '%s' " % (datestr.replace("-","").replace("/",""), dateendstr.replace("-","").replace("/",""))
            if versionstr:
                wherestr += " and version = '%s' " % (versionstr)
            datas = self.db.query("SELECT level, sum(wins) as win_times , sum(loses) as lose_times,%s, %s,%s,%s,%s,%s,%s,%s,%s,%s %s FROM Level where %s  group by level order by level limit 2000 " % (
                                 "sum(wins+loses+quits) as end_times",
                                 "sum(quits) as stop_times",
                                 "sum(wins) / sum(wins+loses+quits)*100.0  as avg_comp",
                                 "sum(wins_n) / sum(wins_n+loses_n+quits_n)*100.0  as avg_comp_n",
                                 "sum(winstars) / sum(wins)  as avg_stars",
                                 "sum(winsteps) / sum(wins)  as avg_steps",
                                 "sum(winskills) / sum(wins) as avg_skills",
                                 "sum(losetargetrate) / sum(loses+quits) as avg_targets",
                                 "sum(buyClimber) as buyClimber",
                                 "sum(extraMove) as extraMove",
                                 extras,
                                 wherestr))
            for d in datas:
                d['comp'] = level_std.get(d['level'],0)

            self.render("finance.html", extraFields = extraFields, datestr=datestr, dateendstr=dateendstr, versionstr = versionstr,datas=datas)

class GachaHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self,method):
        self.do_request(method)

    def do_request(self, method):
        if method == "list":
            nowstr = (datetime.datetime.today() - datetime.timedelta(days=1) ).strftime("%Y-%m-%d")
            datestr = self.get_argument("date", nowstr)
            if not datestr:
                datestr = nowstr
            wherestr = " datestr = '%s' " % (datestr.replace("-","").replace("/","") )
            datas = self.db.query("select * from Gacha where %s " % (wherestr))
            self.render("gacha.html", datestr=datestr , datas=datas)

class AvatarHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self,method):
        self.do_request(method)

    def do_request(self, method):
        if method == "list":
            nowstr = (datetime.datetime.today() - datetime.timedelta(days=1) ).strftime("%Y-%m-%d")
            datestr = self.get_argument("date", nowstr)
            level = self.get_argument("level", "").strip()
            if not datestr:
                datestr = nowstr
            wherestr = " datestr = '%s' " % (datestr.replace("-","").replace("/","") )
            if level:
                wherestr += " and level=%d" % (int(level))

            datas = self.db.query("select avatar, sum(count) as count from FightAvatar  where %s  group by avatar " % (wherestr))
            self.render("avatar.html", level=level , datestr=datestr , datas=datas)

class AdHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self,method):
        self.do_request(method)

    def do_request(self, method):
        if method == "list":
            nowstr = (datetime.datetime.today() - datetime.timedelta(days=1) ).strftime("%Y-%m-%d")
            datestr = self.get_argument("date", nowstr)
            ui = self.get_argument("ui", "").strip()
            if not datestr:
                datestr = nowstr
            wherestr = " datestr = '%s' " % (datestr.replace("-","").replace("/","") )
            if ui:
                wherestr += " and ad_ui='%s'" % (ui)
                datas = self.db.query("select ad_id, ad_ui, sum(count) as count from Ad  where %s  group by ad_id , ad_ui" % (wherestr))
            else:
                datas = self.db.query("select ad_id, '-' as ad_ui,  sum(count) as count from Ad  where %s  group by ad_id " % (wherestr))
            self.render("ad.html", ui=ui , datestr=datestr , datas=datas)

class PicHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self,method):
        self.do_request(method)

    def do_request(self, method):
        if method == "list":
            datas = self.db.query("SELECT pic_id, sum(count) as count FROM Pic group by pic_id")
            self.render("pic.html", datas = datas)

class EventHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self,method):
        self.do_request(method)

    def do_request(self, method):
        if method == "list":
            datas = self.db.query("SELECT event_id, sum(count) as count from ShopEvent  group by event_id")
            self.render("event.html", datas = datas)

class LevelHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self,method):
        self.do_request(method)

    def do_request(self, method):
        if method == "list":
            datas = self.db.query("SELECT level, count FROM Level_Dis order by level")
            self.render("level.html", datas = datas)

class UserHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self,method):
        self.do_request(method)

    def do_request(self, method):
        if method == "list":
            users = self.db.query("SELECT * FROM adm_users"),
            self.render("users.html", adm_users = users[0])
        if method == "addcommit":
            user = self.get_argument("user")
            passwd = self.get_argument("pass")
            pssswdformer = self.get_argument("passformer")
            if passwd == pssswdformer:
                pass
            else:
                passwd =hashlib.md5(tornado.escape.utf8(self.get_argument("pass"))).hexdigest()
            username = self.get_argument("username")
            email = self.get_argument("email")
            mstr = []
            for m in modules:
                checked = self.get_argument(m,'')
                if checked:
                    mstr.append(m)
            ms = ','.join(mstr)
            try:
                values = "user_id='%s',user_name='%s',password='%s',module_ids='%s',email='%s',locked=0 " % (user,username,passwd,ms,email)
                sql = "INSERT INTO adm_users  SET %s ON DUPLICATE KEY UPDATE %s" % (values, values)
                self.db.execute(sql)
            except Exception, e:
                logging.error(str(e))
                self.write('')
        if method == "lock":
            user = self.get_argument("user")
            self.db.execute("update adm_users set locked=1 where user_id='%s'" % (user))
        if method == "unlock":
            user = self.get_argument("user")
            self.db.execute("update adm_users set locked=0 where user_id='%s'" % (user))
        if method == "del":
            user = self.get_argument("id")
            self.db.execute("delete from  adm_users where user_id='%s'" % (user))

class LevelHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self,method):
        self.do_request(method)

    def do_request(self, method):
        if method == "list":
            datas = self.db.query("SELECT level, count FROM Level_Dis order by level")
            self.render("level.html", datas = datas)

class LevelHandler(BaseHandler):
    def post(self,method):
        self.do_request(method)

    def get(self,method):
        self.do_request(method)

    def do_request(self, method):
        if method == "list":
            datas = self.db.query("SELECT level, count FROM Level_Dis order by level")
            self.render("level.html", datas = datas)

class PlayerIDsHandler(BaseHandler):
    @gen.coroutine
    def post(self,method):
        yield self.do_request(method)

    @gen.coroutine
    def get(self,method):
        yield self.do_request(method)

    @gen.coroutine
    def do_request(self, method):
        if method == "list":
            playerid = self.get_argument("playerid", "")
            regcode = self.get_argument("playerinvitecode", "")
            playername = ""
            friends = ""
            rubys = []
            payments = []
            if regcode:
                from api.data.regcode import RegCode
                r = RegCode.get(regcode)
                if r:
                    playerid = r.uid

            if playerid:
                from api.data.player import Player
                p = Player.get(playerid)
                if p:
                    playername = p.name
                from api.data.friends import Friends
                f = Friends.get(playerid)
                if f:
                    regcode = f.code
                    friends = ",".join(f.friends)
                from api.data.player import Ruby
                r = Ruby.get(playerid)
                if r:
                    rubys = r.list
                sbs_id = options.sbs_key
                password = options.sbs_pass
                device_id = "adminplatform"
                client = Sbs(sbs_id, playerid, device_id, password, url = options.sbs_url)
                try:
                    payments = yield client.getPayments(playerid)
                except Exception as e:
                    logging.exception(str(e))
            self.render("playerids.html", datas = {}, payments = payments , playerid=playerid, invitecode=regcode, playername = playername, friends = friends, rubys=[r for r in rubys if len(r) >=6 ])

class PlayerDatasHandler(BaseHandler):
    @gen.coroutine
    def post(self,method):
        yield self.do_request(method)

    @gen.coroutine
    def get(self,method):
        yield self.do_request(method)

    @gen.coroutine
    def do_request(self, method):
        if method == "list":
            playerid = self.get_argument("playerid", "")
            bucket = self.get_argument("bucket", "userData")
            datas = {}
            if playerid:
                sbs_id = options.sbs_key
                password = options.sbs_pass
                device_id = "adminplatform"
                client = Sbs(sbs_id, playerid, device_id, password, url = options.sbs_url)
                try:
                    datas = yield client.getBucketData(bucket,playerid)
                except:
                    datas = {"data" : {}, "format_version": 4}
            datas = json.dumps(datas, sort_keys=True,indent=4).replace("</", "<\\/")
            self.render("playerdatas.html", datas = datas, playerid = playerid, bucket=bucket)

        if method == "upload":
            fileinfo = self.request.files['file'][0]
            data = json_decode(fileinfo['body'])
            self.write(json.dumps(data, sort_keys=True,indent=4).replace("</", "<\\/"))
            self.set_header('Content-Type', 'application/json; charset=utf-8')
        if method == "save":
            playerid = self.get_argument("playerid", "")
            bucket = self.get_argument("bucket", "")
            player_data  = self.get_argument("id", "")
            datas = json_encode(json_decode(player_data))
            if playerid:
                sbs_id = options.sbs_key
                password = options.sbs_pass
                device_id = "adminplatform"
                client = Sbs(sbs_id, playerid, device_id, password, url = options.sbs_url)
                datas = yield client.setBucketData(bucket,playerid, datas)
                self.write("{}")
            self.set_header('Content-Type', 'application/json; charset=utf-8')

class PlayerCommandsHandler(BaseHandler):
    @gen.coroutine
    def post(self,method):
        yield self.do_request(method)

    @gen.coroutine
    def get(self,method):
        yield self.do_request(method)

    @gen.coroutine
    def do_request(self, method):
        if method == "list":
            playerid = self.get_argument("playerid", "")
            datas = {}
            commands  = {}
            if playerid:
                sbs_id = options.sbs_key
                password = options.sbs_pass
                device_id = "adminplatform"
                client = Sbs(sbs_id, playerid, device_id, password, url = options.sbs_url)
                try:
                    datas = yield client.getBucketData("userData",playerid)
                except:
                    datas = {"data" : {}, "format_version": 4}
                try:
                    commands = yield client.getBucketData("Command",playerid)
                except:
                    commands = {"data" : [], "format_version": 1 }
            logging.info(commands)
            if not commands.get("data"):
                commands["data"] = []
            self.render("playercommands.html", datas=datas,  commands=commands, playerid=playerid)

        if method == "create":
            command = self.get_argument("command", "")
            value   = self.get_argument("value", "")
            if value.isdigit():
                value = int(value)
            jsonobj = {}
            jsonobj["id"] = str(uuid.uuid4())
            jsonobj["name"] = command
            jsonobj["args"] = [value]
            jsonobj["created_at"] = int(time.time())
            jsonobj["success"] = False
            jsonobj["completed_at"] = 0
            self.write(json_encode(jsonobj))
            self.set_header('Content-Type', 'application/json; charset=utf-8')

        if method == "save":
            playerid = self.get_argument("playerid", "")
            player_data  = self.get_argument("id", "")
            datas = json_encode({"data": json_decode(player_data).get("data",[]), "format_version":1})
            if playerid:
                sbs_id = options.sbs_key
                password = options.sbs_pass
                device_id = "adminplatform"
                client = Sbs(sbs_id, playerid, device_id, password, url = options.sbs_url)
                datas = yield client.setBucketData("Command",playerid, datas)
                self.write("{}")
            self.set_header('Content-Type', 'application/json; charset=utf-8')

def shutdown():
    """ Stop server and add a callback to stop I/O loop"""
    try:
        io_loop = tornado.ioloop.IOLoop.current()
        logging.info('Will shutdown in 1 seconds ...')
        io_loop.add_timeout(time.time() + 1, io_loop.stop)
    except Exception,e:
        logging.exception(str(e))

def sig_handler(sig,frame):
    """ Catch signals and callback"""
    tornado.ioloop.IOLoop.current().add_callback(shutdown)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
                    (r'/', MainHandler),
                    (r'/users/([^/]*)', UserHandler),
                    (r'/gacha/([^/]*)', GachaHandler),
                    (r'/avatar/([^/]*)', AvatarHandler),
                    (r'/ad/([^/]*)', AdHandler),
                    (r'/finance/([^/]*)', FinanceHandler),
                    (r'/guestmsg/([^/]*)', GuestmsgHandler),
                    (r'/activity/([^/]*)', ActivityHandler),
                    (r'/apl/([^/]*)', AplHandler),
                    (r'/activity_notice/([^/]*)', ActivityNoticeHandler),
                    (r'/pic/([^/]*)', PicHandler),
                    (r'/event/([^/]*)', EventHandler),
                    (r'/level/([^/]*)', LevelHandler),
                    (r'/mainten/([^/]*)', MaintenHandler),
                    (r'/playerids/([^/]*)', PlayerIDsHandler),
                    (r'/playerdatas/([^/]*)', PlayerDatasHandler),
                    (r'/playercommands/([^/]*)', PlayerCommandsHandler),
                    (r'/logout', LogoutHandler),
                    (r'/login', LoginHandler)
                    ]
        settings = dict(
                    template_path=os.path.join(os.path.dirname(__file__), "templates"),
                    static_path=os.path.join(os.path.dirname(__file__), "static"),
                    xsrf_cookies=False,
                    cookie_secret="dsfc333cdddW!0de",
                    login_url="/login"
                )
        super(Application, self).__init__(handlers, **settings)
        # Have one global connection to the blog DB across all handlers
        self.db = Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)

        self.maybe_create_tables()

    def maybe_create_tables(self):
        try:
            sql = "SELECT * FROM adm_users LIMIT 1"
            conn.get(sql)
        except Exception , e:
            subprocess.check_call(['mysql',
                                   '--host=' + options.mysql_host.split(":")[0],
                                   '--port=' + options.mysql_host.split(":")[1],
                                   '--database=' + options.mysql_database,
                                   '--user=' + options.mysql_user,
                                   '--password=' + options.mysql_password],
                                  stdin=open('schema.sql'))

if __name__ == "__main__":
    parse_command_line()

    BaseModel.install()
    signal.signal(signal.SIGTERM , sig_handler)
    signal.signal(signal.SIGINT , sig_handler)
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
