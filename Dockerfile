FROM python:latest

ENV TZ="Europe/Athens"
RUN apt-get update && apt-get -y install cron

WORKDIR /home/weather

COPY ./ ./
RUN chmod +x script start
RUN crontab ./cron_scripts/crontab
RUN pip install -r requirements.txt
EXPOSE 8050
ENTRYPOINT [ "./start" ]

