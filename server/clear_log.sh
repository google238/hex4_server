#!/bin/bash
nginxlog=/var/log/nginx/access_sumikko.log
cat /dev/null > $nginxlog
rm /home/sumikko/pitayaserver/logs/server_*.log.*
rm /home/sumikko/pitayaserver/logs/dbw*_*.log.*
rm /home/sumikko/sbs/logs/server_*.log.*
rm /usr/local/logs/*.log.*
rm /usr/local/logs/*.out.*
