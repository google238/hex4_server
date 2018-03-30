ii="0 1 2 3 4 5 6 7 8 9 a b c d e f"
c1="0 1 2 3"
c2="4 5 5 7"
c3="8 9 a b"
c4="c d e f"

for i in $c1
do
  for j in $ii
  do
     echo "select pkey from kvs$i.Player_$j " | mysql -h172.31.15.206 -upitayagames -p"cUycN6&$"
  done
done

for i in $c2 
do
  for j in $ii
  do
     echo "select pkey from kvs$i.Player_$j " | mysql -h172.31.25.121 -upitayagames -p"cUycN6&$"
  done
done

for i in $c3 
do
  for j in $ii
  do
     echo "select pkey from kvs$i.Player_$j " | mysql -h172.31.19.56 -upitayagames -p"cUycN6&$"
  done
done

for i in $c4 
do
  for j in $ii
  do
     echo "select pkey from kvs$i.Player_$j " | mysql -h172.31.19.57 -upitayagames -p"cUycN6&$"
  done
done
