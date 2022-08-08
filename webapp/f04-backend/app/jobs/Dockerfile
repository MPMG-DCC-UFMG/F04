# syntax=docker/dockerfile:1
FROM mongo
WORKDIR /code
RUN apt-get update && apt-get -y install cron
COPY ./app/jobs/cronjobs /etc/cron.d/cronjobs
RUN chmod 0644 /etc/cron.d/cronjobs
RUN crontab /etc/cron.d/cronjobs
RUN touch /var/log/cron.log
COPY ./app/jobs /code/jobs
COPY ./.env  /code/jobs
RUN chmod a+x /code/jobs/*.sh
CMD ["cron", "-f"]

