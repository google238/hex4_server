#!/usr/bin/env python

import sys
import datetime
from mysql import Connection
db = Connection(host="172.31.15.206:3306", database="admin",user="pitayagames", password="cUycN6&$")

values = {}
datestr = sys.argv[1]
sql = "delete from Level where datestr='%s'" % (datestr)
db.execute(sql)
for l in sys.stdin:
    try:
        version, level , stats , count = l.strip().split('\t')
        if stats == "ad":
            sql = "INSERT INTO Ad SET ad_id='%s',ad_ui='%s', datestr='%s',count=%s ON DUPLICATE KEY UPDATE count=%s" % (version, level , datestr , count, count)
            db.execute(sql) 
            continue

        if stats == "gacha":
            sql = "INSERT INTO Gacha SET item_id='%s', datestr='%s',count=%s ON DUPLICATE KEY UPDATE count=%s" % (version, datestr , count, count)
            db.execute(sql) 
            continue

        if stats == "fight_avatar":
            sql = "INSERT INTO FightAvatar SET level=%s, avatar='%s', datestr='%s',count=%s ON DUPLICATE KEY UPDATE count=%s" % (version, level ,datestr , count, count)
            db.execute(sql) 
            continue

        if stats == "pic_id":
            sql = "INSERT INTO Pic SET pic_id='%s', datestr='%s',count=%s ON DUPLICATE KEY UPDATE count=%s" % (version, datestr , count, count)
            db.execute(sql) 
            continue

        if stats == "event_shop_event":
            sql = "INSERT INTO ShopEvent SET event_id='%s_%s', datestr='%s',count=%s ON DUPLICATE KEY UPDATE count=%s" % (version,level, datestr , count, count)
            db.execute(sql) 
            continue

        setstr = " version='%s', datestr='%s', level=%s " % (version, datestr , level)
        statsstr = ""
        if stats == "lost":
            statsstr = "loses=%s"
        elif stats == "quit":
            statsstr = "quits=%s"
        elif stats == "win":
            statsstr = "wins=%s"
        elif stats == "lost_n":
            statsstr = "loses_n=%s"
        elif stats == "quit_n":
            statsstr = "quits_n=%s"
        elif stats == "win_n":
            statsstr = "wins_n=%s"
        elif stats == "targetrate":
            statsstr = "losetargetrate=%s"
        elif stats == "start":
            statsstr = "starts=%s"
        elif stats == "stars":
            statsstr = "winstars=%s"
        elif stats == "moves":
            statsstr = "winsteps=%s"
        elif stats == "skills":
            statsstr = "winskills=%s"
        elif stats == "buyClimber":
            statsstr = "buyClimber=%s"
        elif stats == "extraMove":
            statsstr = "extraMove=%s"
        else:
            statsstr = stats +"=%s"
            sql = "ALTER TABLE Level add %s int DEFAULT 0" % (stats)
            try:
                db.execute(sql) 
            except:
                pass
           
        if statsstr:
            statsstr = statsstr % (count)
            sql = "INSERT INTO Level SET %s,%s ON DUPLICATE KEY UPDATE %s" % (setstr,statsstr,statsstr)
            db.execute(sql) 

        sql = "delete from Level where datestr<'%s'" % ((datetime.datetime.now()- datetime.timedelta(days = 30)).strftime("%Y%m%d"))
        db.execute(sql) 
    except:
        pass
