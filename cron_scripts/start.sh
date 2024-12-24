#!/bin/bash
redis-server --daemonize yes
sleep 5
cd /home/weather
crontab ./cron_scripts/crontab
cron
touch log
tail -F log &
python bootstrap.py
gunicorn --worker-class gevent -b 0.0.0.0:8050 -t 60 front:server