#!/usr/bin/env bash
mkdir data
cd data
mkdir A
cd A
for i in `seq 20`; do
    echo $i > $i
done
cd ..

cp -pir A/ B
sleep 2
touch B/3
cd ..

