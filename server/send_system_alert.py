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

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import datetime

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
    to_addr = ["5695953@qq.com", "331620337@qq.com","331700165@qq.com", "454235581@qq.com", "6468158@qq.com","z@pitayagames.com"]
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = _format_addr(u'Sumikko后台 <%s>' % from_addr)
    msg['To'] = ", ".join(to_addr)
    msg['Subject'] = Header(u'【SUMIKKO 重要提醒】%s' % (subject), 'utf-8').encode()   
    server = smtplib.SMTP_SSL("smtp.exmail.qq.com",port=465)
    server.login(from_addr, "Pitaya.1058")
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.close()

@gen.coroutine
def main():
    BaseModel.install()
    try:
        f = open("/home/sumikko/pitayaserver/config/activity.json")
        f.seek(0)
        data = f.read(1024*64)
        f.close()
        configs = tornado.escape.json_decode(data)
        today = datetime.date.today() 
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        content = ""
        for config in configs:
            start_date = datetime.datetime.strptime(config["start_time"],"%Y/%m/%d %H:%M").date()
            over_date = datetime.datetime.strptime(config["over_time"],"%Y/%m/%d %H:%M").date()
            event = config.get("activity_id")
            if tomorrow == start_date:
                content += ("活动配置[%(activity_id)s - "+ events.get(event, event) +"]将在明天[%(start_time)s]自动启用,请注意检查配置\r\n") % config
            if today == start_date:
                content += ("活动配置[%(activity_id)s - "+ events.get(event, event) +"]将在今天[%(start_time)s]自动启用,请注意检查配置\r\n") % config
        content += "\r\n" 
        for config in configs:
            start_date = datetime.datetime.strptime(config["start_time"],"%Y/%m/%d %H:%M").date()
            over_date = datetime.datetime.strptime(config["over_time"],"%Y/%m/%d %H:%M").date()
            event = config.get("activity_id")
            if tomorrow == over_date:
                content += ("活动配置[%(activity_id)s - "+ events.get(event, event) +"]将在明天[%(over_time)s]自动停用,请注意检查配置\r\n") % config
            if today == over_date:
                content += ("活动配置[%(activity_id)s - "+ events.get(event, event) +"]将在今天[%(over_time)s]自动停用,请注意检查配置\r\n") % config
        if content and content != "\r\n":
            send_mail(content.split("\r\n")[0], content)

    except Exception , e:
        logging.info(str(e))

 
if __name__ == "__main__":
    parse_command_line()
    ioloop.IOLoop.instance().run_sync(main)  
