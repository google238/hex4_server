#!/bin/bash
home=/home/sumikko/admin/sync
olddir=`pwd`
cd $home
hosts=`cat $home/host.list`
for host in $hosts
do
   echo "restart server $host:4444"
   /usr/local/bin/circusctl --endpoint=tcp://$host:4444 restart 
done
cd $olddir
