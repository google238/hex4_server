#!/bin/bash
src=/home/sumikko/admin/sync/activity.json
dst=/home/sumikko/pitayaserver/config/
home=/home/sumikko/admin/sync
hosts=`cat $home/host.list`
olddir=`pwd`
cd $home
for host in $hosts
do
    echo "#####################sync maintian to $host ########################"
    scp -i /root/sumikko.pem $src $host:$dst
done
cd $olddir
