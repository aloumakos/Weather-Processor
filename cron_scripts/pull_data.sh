#!/bin/bash
cd /home/weather
sed -i -e "s/^RAND=[0-9]*/RAND=$RANDOM/g" .env
/usr/local/bin/python main.py -c $1

