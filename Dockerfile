FROM python:latest
ENV TZ="Europe/Athens"

RUN apt-get update && apt-get -y install cron lsb-release curl gpg
RUN curl -fsSL https://packages.redis.io/gpg | gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/redis.list
RUN apt-get -y install redis

WORKDIR /home/weather
COPY ./ ./
RUN chmod +x ./cron_scripts/pull_data.sh ./cron_scripts/start.sh
RUN crontab ./cron_scripts/crontab
RUN pip install -r requirements.txt

EXPOSE 8050
CMD [ "./cron_scripts/start.sh" ]

