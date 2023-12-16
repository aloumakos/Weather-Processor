#!/bin/bash
cron
cd /home/weather
python bootstrap.py
gunicorn -w 2 -b 0.0.0.0:8050 -t 60 --log-level DEBUG front:server