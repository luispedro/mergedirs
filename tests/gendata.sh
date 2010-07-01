#!/usr/bash
mkdir data
cd data
mkdir A
cd A
for i in `seq 20`; do
    echo $i > $i
done
cd ..
rsync --archive A/ B
sleep 2
touch B/3
cd ..

