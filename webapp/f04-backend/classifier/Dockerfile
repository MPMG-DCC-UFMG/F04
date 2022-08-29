FROM python:3.8
WORKDIR /code
COPY ./classifier /code
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN [ "python", "-c", "import nltk; nltk.download('stopwords')" ]
RUN apt-get update && apt-get -y install cron
COPY ./classifier/cronjobs /etc/cron.d/cronjobs
RUN chmod 0644 /etc/cron.d/cronjobs
RUN touch /var/log/cron.log
RUN crontab /etc/cron.d/cronjobs
COPY ./.env  /code
CMD ["cron", "-f"]