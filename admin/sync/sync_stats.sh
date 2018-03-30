#!/bin/bash
src=/home/sumikko/stats_codes/
dst=/home/sumikko/stats/
home=/home/sumikko/admin/sync
hosts=`cat $home/host.list`
olddir=`pwd`
cd $home
svn up $src
for host in $hosts
do
    echo "#####################sync all code to $host ########################"
    rsync  -rvztopglHpogDtS --progress --exclude-from=$home/exclude.list -e "ssh -i /root/sumikko.pem" $src $host:$dst 
done
cd $olddir
