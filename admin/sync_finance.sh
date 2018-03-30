echo "delete from admin.Finance" | mysql -h172.31.15.206 -upitayagames -p"cUycN6&$"
ii="0 1 2 3 4 5 6 7 8 9 a b c d e f"
for i in $ii 
do
  for j in $ii
  do
     echo "insert into admin.Finance(pkey, flag, data) select pkey, flag, data from kvs$i.Finance_$j " | mysql -h172.31.15.206 -upitayagames -p"cUycN6&$"
  done
done

