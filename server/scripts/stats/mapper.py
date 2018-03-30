#!/usr/bin/env python

import sys
import urlparse
import json

for l in sys.stdin:
    try:
        data = urlparse.parse_qs(l.strip().split(" ")[-1])
        log_type = data["type"][0]
        if log_type == "ad":
            ad_type = data.get("ad_type",[None])[0]
            ad_ui = data.get("ad_ui",[None])[0]
            print "%s\t%s\tad\t1" %(ad_type, ad_ui)
            continue

        if log_type == "gacha":
            item_id = data["item_id"][0]
            print "%s\t%s\tgacha\t1" %(item_id, 1)
            continue

        if log_type == "puzzle_mission_done":
            pic_id = data["pic_id"][0]
            print "%s\t%s\tpic_id\t1" %(pic_id, 1)
            continue
 
        if log_type == "event_shop_reward":
            uid = data["sbsuid"][0]
            eventid= data["event_id"][0]
            reward_id= data["reward_id"][0]
            print "%s\t%s\tevent_shop_event\t1" %( eventid, reward_id)
            continue

        level = data["level"][0]
        version = data.get("version",["-"])[0]    
        if log_type == "start_of_round":
            print "%s\t%s\tstart\t1" %(version,level) 
        elif 'win=Quit' in l:
            avatar = data.get("fight_avatar",[None])[0]
            required = data["objectiveRequired"][0]
            collected = data["objectiveCollect"][0]
            buyAnyBuff = data.get("buyAnyBuff",["False"])[0]
            buyClimber = data.get("buyClimber",["0"])[0]
            extraMove = data.get("extraMove",["0"])[0]
            prestartItems = data.get("prestartItems",["{}"])[0]
            stageItems = data.get("stageItems",["{}"])[0]
            prestarts = json.loads(prestartItems)
            stages = json.loads(stageItems)

            for item in prestarts:
                print "%s\t%s\tprestartItems_%s\t%s" %(version, level, item, prestarts[item]) 
            for item in stages:
                print "%s\t%s\tstageItems_%s\t%s" %(version, level, item, stages[item]) 
                 
            print "%s\t%s\tquit\t1" %(version,level) 
            print "%s\t%s\tbuyClimber\t%s" %(version, level, buyClimber) 
            print "%s\t%s\textraMove\t%s" %(version, level, extraMove) 
            if avatar is not None:
                print "%s\t%s\tfight_avatar\t%s" %(level, avatar, 1) 
            if buyAnyBuff == "False":
                print "%s\t%s\tquit_n\t1" %(version,level) 

            print "%s\t%s\ttargetrate\t% 12.2f" %(version,level, float(collected) / float(required) *100 ) 
        elif 'win=Lost' in l:
            avatar = data.get("fight_avatar",[None])[0]
            required = data["objectiveRequired"][0]
            collected = data["objectiveCollect"][0]
            buyAnyBuff = data.get("buyAnyBuff",["False"])[0]
            buyClimber = data.get("buyClimber",["0"])[0]
            extraMove = data.get("extraMove",["0"])[0]
            prestartItems = data.get("prestartItems",["{}"])[0]
            stageItems = data.get("stageItems",["{}"])[0]
            prestarts = json.loads(prestartItems)
            stages = json.loads(stageItems)

            for item in prestarts:
                print "%s\t%s\tprestartItems_%s\t%s" %(version, level, item, prestarts[item]) 
            for item in stages:
                print "%s\t%s\tstageItems_%s\t%s" %(version, level, item, stages[item]) 

            print "%s\t%s\tlost\t1" %(version,level) 
            print "%s\t%s\tbuyClimber\t%s" %(version, level, buyClimber) 
            print "%s\t%s\textraMove\t%s" %(version, level, extraMove) 
            if avatar is not None:
                print "%s\t%s\tfight_avatar\t%s" %(level, avatar, 1) 
            if buyAnyBuff == "False":
                print "%s\t%s\tlost_n\t1" %(version,level) 

            print "%s\t%s\ttargetrate\t% 12.2f" %(version,level, float(collected) / float(required) *100 ) 

        elif 'win=Won' in l:
            avatar = data.get("fight_avatar",[None])[0]
            stars = data["stars"][0]
            moves = data["useMoves"][0]
            skills = data["comSkillNum"][0]
            buyAnyBuff = data.get("buyAnyBuff",["False"])[0]
            buyClimber = data.get("buyClimber",["0"])[0]
            extraMove = data.get("extraMove",["0"])[0]
            prestartItems = data.get("prestartItems",["{}"])[0]
            stageItems = data.get("stageItems",["{}"])[0]
            prestarts = json.loads(prestartItems)
            stages = json.loads(stageItems)

            for item in prestarts:
                print "%s\t%s\tprestartItems_%s\t%s" %(version, level, item, prestarts[item]) 
            for item in stages:
                print "%s\t%s\tstageItems_%s\t%s" %(version, level, item, stages[item]) 

            print "%s\t%s\twin\t1" %(version,level) 
            print "%s\t%s\tbuyClimber\t%s" %(version, level, buyClimber) 
            print "%s\t%s\textraMove\t%s" %(version, level, extraMove) 
            if avatar is not None:
                print "%s\t%s\tfight_avatar\t%s" %(level, avatar, 1) 
            if buyAnyBuff == "False":
                print "%s\t%s\twin_n\t1" %(version,level) 
            print "%s\t%s\tstars\t%s" %(version,level, stars) 
            print "%s\t%s\tmoves\t%s" %(version,level, moves) 
            print "%s\t%s\tskills\t%s" %(version,level, skills) 
    except:
        pass
