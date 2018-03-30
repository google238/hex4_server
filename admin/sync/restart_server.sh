#!/bin/bash
home=/home/sumikko/admin/sync
olddir=`pwd`
cd $home
hosts=`cat $home/host.list`
for host in $hosts
do
   echo "restart server $host:5555"
   /usr/local/bin/circusctl --endpoint=tcp://$host:5555 restart 
done
cd $olddir
