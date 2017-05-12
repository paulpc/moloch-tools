#!/bin/bash
#assuming CentOS6 / RHEL 6

echo "[+] shutting down elasticsearch"
for eshost in `cat eshosts.txt`; do
  echo $eshost
  for esprocess in `ssh $eshost "ls /etc/init.d/elasticsearch-es*"`
    do
    echo $esprocess
    ssh $eshost "sudo $esprocess stop"
  done
done

echo "[+] starting up elasticsearch"
for eshost in `cat eshosts.txt`; do
  echo $eshost
  for esprocess in `ssh $eshost "ls /etc/init.d/elasticsearch-es*"`
    do
    echo $esprocess
    ssh $eshost "sudo $esprocess start"
  done
done

eshost=`head -n 1 eshosts.txt`
esstatus=`curl "http://$eshost:9200/_cat/health" | grep -v green`

while [ "$esstatus" != "" ]; do
echo "[-] something is broken, waiting for cluster to come alive"
sleep 15
esstatus=`curl "http://$eshost:9200/_cat/health" | grep -v green`
done
echo "[+] ES cluster is probably green, moving on"
