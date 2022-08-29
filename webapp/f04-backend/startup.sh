#docker-compose -f docker-compose.yml down --volumes 
#docker image prune -f
#docker rmi -f $(docker images -f "dangling=true" -q)
docker-compose -f docker-compose.yml up -d --build --remove-orphans --force-recreate
#docker-compose logs -f
#docker ps -a | grep "15 months ago" | awk '{print $1}' | xargs docker rm -f
#docker ps -a | grep "15 months ago" | awk '{print $2}' | xargs docker rmi -f
#docker exec f04-classifier tail -f /var/log/cron.log
#docker run -it -p 8280:8280 -p 8243:8243 -p 9443:9443 -v ./deployment.toml:/home/wso2carbon/wso2am-4.1.0/repository/conf/deployment.toml --name ws02 wso2/wso2am:4.1.0