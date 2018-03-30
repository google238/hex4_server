#!/bin/bash
#!/bin/bash
src=/home/sumikko/admin/sync/activity_notice.json
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
printf '活动通知配置推送到服务器成功'
exit 0
