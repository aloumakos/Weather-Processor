#!/bin/bash
redis-server --daemonize yes
sleep 5
ttyf=$(tty)
echo $ttyf
cd /home/weather
sed -i "s|$| >> $ttyf 2>\&1|" ./cron_scripts/crontab
crontab ./cron_scripts/crontab
cron
python bootstrap.py
gunicorn --worker-class gevent -b 0.0.0.0:8050 -t 60 front:server