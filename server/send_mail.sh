script_home=/home/sumikko/pitayaserver
/usr/local/bin/python $script_home/send_mail.py  --db_conf=$script_home/config/db_sumikko.conf --memcached="172.31.25.7:11211;172.31.25.8:11211;172.31.25.6:11211" --writecache="172.31.25.7:11311;172.31.25.8:11311;172.31.25.6:11311"  --log_file_prefix=/data/uids/send_mail.log
