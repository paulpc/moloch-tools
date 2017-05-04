#!/bin/bash
# assuming centos 6 / rhel 6

echo "[+] shutting down viewers"
for vihost in `cat viewers.txt`; do
  ssh $vihost "sudo /sbin/initctl stop viewer"
done

echo "[+] shutting down captures"
for cahost in `cat capture.txt`; do
  for caproc in `ssh $cahost "ls /etc/init/capture*"`; do
    ssh $cahost "sudp /sbin/initctl stop $caproc"
done

echo "[+] shutting down elasticsearch"

for eshost in `cat eshosts.txt`; do
  echo $eshost
  for esprocess in `ssh $eshost "ls /etc/init.d/elasticsearch-es*"`
    do
    echo $esprocess
    ssh $eshost "sudo $esprocess stop"
  done
done

for eshost in `cat eshosts.txt`; do
  echo $eshost
  for esprocess in `ssh $eshost "ls /etc/init.d/elasticsearch-es*"`
    do
    echo $esprocess
    ssh $eshost "sudo $esprocess status"
  done
done
