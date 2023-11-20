#!/bin/bash
cron
cd /home/weather
gunicorn -w 2 -b 0.0.0.0:8050 front:server