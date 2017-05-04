#!/bin/bash
#assuming CentOS6 / RHEL 6

echo "[+] checking elasticsearch"
for eshost in `cat eshosts.txt`; do
  echo $eshost
  for esprocess in `ssh $eshost "ls /etc/init.d/elasticsearch-es*"`
    do
    echo $esprocess
    ssh $eshost "sudo $esprocess status"
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

echo "[+] checking viewers"
for vihost in `cat viewer.txt`; do
  echo $vihost
  ssh $vihost "sudo /sbin/initctl status viewer"
done

echo "[+] checking captures"
for cahost in `cat capture.txt`; do
  echo $cahost
  for caproc in `ssh $cahost "ls /etc/init/capture*" | cut -d "/" -f 4 | cut -d "." -f 1`; do
    echo $caproc
    ssh $cahost "sudo /sbin/initctl status $caproc"
  done
done
