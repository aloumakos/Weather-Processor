FROM python:latest

ENV TZ="Europe/Athens"
RUN apt-get update && apt-get -y install cron

WORKDIR /home/weather

COPY ./ ./
RUN chmod +x ./cron_scripts/pull_data.sh ./cron_scripts/start.sh
RUN crontab ./cron_scripts/crontab
RUN pip install -r requirements.txt
EXPOSE 8050
ENTRYPOINT [ "./cron_scripts/start.sh" ]

