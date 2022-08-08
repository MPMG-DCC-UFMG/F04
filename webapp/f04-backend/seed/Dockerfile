FROM mongo:latest
COPY tweets.json /tweets.json
#CMD mongoimport --host ${DB_HOST} --db ${DB_NAME} --username ${DB_USERNAME}  --password ${DB_PASSWORD} --authenticationDatabase admin --collection tweets --drop --file /tweets.json --jsonArray