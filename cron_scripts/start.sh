#!/bin/bash
cron
cd /home/weather
python bootstrap.py
gunicorn --worker-class gevent -b 0.0.0.0:8050 -t 60 --log-level DEBUG front:server