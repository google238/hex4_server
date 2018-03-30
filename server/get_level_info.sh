#!/bin/bash
date=`date +%y%m%d -d "1 days ago"`
fpath=/home/sumikko/pitayaserver/static/images
cat /home/sumikko/pitayaserver/logs/server_* |grep $date| grep log:28 | sort |grep "end_of_round"  | awk 'BEGIN { ORS = ""; print "["}{s=""; for (i=5; i<=NF; i++) s=s""$i; if(NR == 1) print s;else print "\n,"s}END{print "]"}' > $fpath/level_end_$date.json
cat /home/sumikko/pitayaserver/logs/server_* |grep $date| grep log:28 | sort |grep "start_of_round"  | awk 'BEGIN { ORS = ""; print "["}{s=""; for (i=5; i<=NF; i++) s=s""$i; if(NR == 1) print s;else print "\n,"s}END{print "]"}' > $fpath/level_start_$date.json

/usr/local/bin/python /home/sumikko/pitayaserver/json2cvs.py -i $fpath/level_start_$date.json -o $fpath/level_start_$date.cvs -t 0
/usr/local/bin/python /home/sumikko/pitayaserver/json2cvs.py -i $fpath/level_end_$date.json -o $fpath/level_end_$date.cvs -t 1

rm -rf $fpath/level_start_$date.json
rm -rf $fpath/level_end_$date.json
