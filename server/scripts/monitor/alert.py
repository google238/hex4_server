#coding:utf-8
import sys
import os
import re
import datetime
import requests
import xmlrpclib
import json
import logging
import socket

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

class TimeoutTransport (xmlrpclib.Transport):
    def __init__(self, timeout=10 , use_datetime=0):
        xmlrpclib.Transport.__init__(self, use_datetime)
        self._timeout = timeout

    def make_connection(self, host):
        conn = xmlrpclib.Transport.make_connection(self, host)
        conn.timeout = self._timeout
        return conn

webhook = "https://oapi.dingtalk.com/robot/send?access_token=f8b0cb496bc5d99cb3abaadd3ac80ffb31452f19e93f0a7a9190907eac94f164"
servers = {
           "172.31.18.30":  [7776,6666,6667,6668,6669,80,1998,2998,3998,4998,8080],
           "172.31.31.51": [7776,6666,6667,6668,6669,80,1998,2998,3998,4998],
           "172.31.22.27": [7776,6666,6667,6668,6669,80,1998,2998,3998,4998],
           "172.31.22.226": [7776,6666,6667,6668,6669,80,1998,2998,3998,4998],
           "172.31.27.222": [7776,6666,6667,6668,6669,80,1998,2998,3998,4998],
           "172.31.15.206": [3306],
           "172.31.25.121": [3306],
           "172.31.19.56":  [3306],
           "172.31.19.57":  [3306],
           #"172.31.20.119": [3306],
           "172.31.29.152": [3306],
           "172.31.25.3":   [3306],
           "172.31.25.4":   [3306],
           "172.31.25.2":   [3306],
           "172.31.25.7":   [11211,11311],
           "172.31.25.8":   [11211,11311],
           "172.31.25.6":   [11211,11311],
           "172.31.28.255": [],
           "172.31.22.126": []
          }
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

def send_mail1(subject,content):
    from_addr = "mon@pitayagames.com"
    to_addr = ["sumikko_puzzle_dev@imagineer.co.jp"]
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = _format_addr(u'Sumikko Puzzle Server <%s>' % from_addr)
    msg['To'] = ", ".join(to_addr)
    msg['Subject'] = Header(u'【SUMIKKO Puzzle】%s' % (subject), 'utf-8').encode()
    server = smtplib.SMTP_SSL("smtp.exmail.qq.com",port=465)
    server.login(from_addr, "Pitaya.1058")
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.close()

def send_mail(sub,content):
    print(sub)
    print(content)
    r = requests.post(webhook, json={"msgtype":"text", "text":{"content":"%s\n%s"% (sub,content)}})
    print(r)
    send_mail1(sub, content)
    return True

def get_wan_ip():
    cmd_get_ip = "/sbin/ifconfig |grep 'inet addr'|awk -F\: '{print $2}'|awk '{print $1}' | grep -v '^127' | grep -v '192'"
    get_ip_info = os.popen(cmd_get_ip).readline().strip()
    return get_ip_info

def check_server(address, port):
    # Create a TCP socket
    s = socket.socket()
    s.settimeout(10)
    print "Attempting to connect to %s on port %s" % (address, port)
    try:
        s.connect((address, port))
        s.close()
        print "Connected to %s on port %s" % (address, port)
        return True
    except socket.error, e:
        print "Connection to %s on port %s failed: %s" % (address, port, e)
        return False

def hd_use_alarm():
    message  = ""
    for ip, ports in servers.iteritems():
        try:
            t = TimeoutTransport(timeout=10)
            s = xmlrpclib.ServerProxy('http://%s:61209' % (ip), transport=t) 
            logging.info(ip)
            data = s.getAll()
            all = json.loads(data)
            print all
            for alert in ["load", "fs", "mem", "memswap", "processlist"]:
                warn = 0
                critical = 0
                result = all.get(alert)
                if alert == "load":
                    wm = 1 *  result.get("cpucore",1)
                    cm = 5 *  result.get("cpucore",1)
                    if result.get("min1") > wm or result.get("min5") > wm or result.get("min15") > wm:
                        warn = 1

                    if result.get("min1") > cm  or result.get("min5") > cm or result.get("min15") > cm:
                        critical = 1
                    
                if alert == "fs":
                    for r in result:
                        if r.get("percent") > 70:
                            warn = 1
                        if r.get("percent") > 90:
                            critical = 1
                if alert == "mem":
                    if result.get("percent") > 	70:
                       warn = 1
                    if result.get("percent") > 90:
                       critical = 1

                if alert == "memswap":
                    if result.get("percent") > 70:
                        warn = 1
                    if result.get("percent") > 90:
                       critical = 1

                if alert == "processlist":
                    deleted = []
                    for r in result:
                        if r.get("memory_percent") > 70 or r.get("cpu_percent") > 70 or r.get("status") == "Z":
                            warn = 1
                            if r.get("memory_percent") > 90 or r.get("cpu_percent") > 90:
                                critical = 1
                        else:
                            deleted.append(r)
                    for r in deleted:
                        result.remove(r)  
                if warn:
                    data = json.dumps(result, sort_keys=True, indent=4).replace("</", "<\\/")
                    message += '\nThere have been [%s %s] on %s\n%s\n' % (alert,"CRITCAL" if critical  else "WARN" , ip, data)
        except Exception, e:
            logging.exception(str(e))
            message += '\nserver %s status check failed\n' % (ip)

        for port in ports:
            if not check_server(ip,port):
                message += '\n[CRITCAL] The Server port %s has died on %s' % (port, ip) 

    if message:
        send_mail('server warnning',message)
if __name__ == '__main__':
    hd_use_alarm()
