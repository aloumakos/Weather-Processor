FROM python:latest

ENV TZ="Europe/Athens"
RUN apt-get update && apt-get -y install cron

WORKDIR /home/weather

COPY ./ ./
RUN chmod +x test
RUN chmod +x script
RUN chmod +x start
RUN crontab crontab.txt

RUN pip install -r requirements.txt
EXPOSE 8050
ENTRYPOINT [ "./start" ]

