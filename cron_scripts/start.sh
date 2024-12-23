#!/bin/bash
cron -f
redis-server --daemonize yes
sleep 5
cd /home/weather
python bootstrap.py
gunicorn --worker-class gevent -b 0.0.0.0:8050 -t 60 front:server