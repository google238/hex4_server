#!/usr/bin/env python

import sys

values = {}

for l in sys.stdin:
    try:
        version, level , stats , count = l.strip().split('\t')
        if stats == "event_shop_event" or stats == "event_shop_reward" or stats == "ad":
            pass
        else:
            level = int(level)
        if stats == "targetrate":
            values[(version, level , stats)] = values.get((version, level , stats),0) + float(count)
        else: 
            values[(version, level , stats)] = values.get((version, level , stats),0) + int(count)
    except:
        pass

for key, value in sorted(values.items()):
    if key[2] == "targetrate": 
        print "%s\t%s\t%s\t% 12.2f" % (key[0],key[1],key[2],value)
    else:
        print "%s\t%s\t%s\t%d" % (key[0],key[1],key[2],value)
