# specify the node base image with your desired version node:<version>
FROM node:12-buster
# application's default port
EXPOSE 8001
# copy files
ADD mqttproxy.js mqttproxy/

RUN npm install