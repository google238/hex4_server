#/bin/bash
date=`date +%Y%m%d -d "1 days ago"`
date_del=`date +%Y%m%d -d "7 days ago"`
/usr/local/bin/python /data/fetchlog.py $date|/usr/local/bin/python /data/mapper.py|/usr/local/bin/python /data/reducer.py | /usr/local/bin/python /data/handle_result.py $date


