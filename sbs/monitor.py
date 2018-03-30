#coding:utf-8
import os
import re
import datetime
import requests

hd_usage_rate_threshold = 80
webhook = "https://oapi.dingtalk.com/robot/send?access_token=f8b0cb496bc5d99cb3abaadd3ac80ffb31452f19e93f0a7a9190907eac94f164"
def send_mail(sub,content):
    r = requests.post(webhook, json={"msgtype":"text", "text":{"content":"%s\n%s"% (sub,content)}})
    print(r)
    return True

def get_wan_ip():
    cmd_get_ip = "/sbin/ifconfig |grep 'inet addr'|awk -F\: '{print $2}'|awk '{print $1}' | grep -v '^127' | grep -v '192'"
    get_ip_info = os.popen(cmd_get_ip).readline().strip()
    return get_ip_info

def check_hd_use():
    cmd_get_hd_use = '/bin/df'
    try:
        fp = os.popen(cmd_get_hd_use)
    except:
        ErrorInfo = r'get_hd_use_error'
        print ErrorInfo
        return ErrorInfo
    re_obj = re.compile(r'^/dev/.+\s+(?P<used>\d+)%\s+(?P<mount>.+)')
    hd_use = {}
    for line in fp:
        match = re_obj.search(line)
        if match is not None:
            hd_use[match.groupdict()['mount']] = match.groupdict()['used']
    fp.close()
    return  hd_use

def hd_use_alarm():
    for key, v in check_hd_use().iteritems():
        if int(v) > hd_usage_rate_threshold:
            if send_mail('磁盘警报','IP地址:%s\n挂载点: %s 使用情况: %s%%' % (get_wan_ip(),key , v)):
                print  "sendmail success!!!!!"
        else:
            print "disk not mail"

if __name__ == '__main__':
    hd_use_alarm()
