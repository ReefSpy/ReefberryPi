# specify the node base image with your desired version node:<version>
FROM node:12-buster
# application's default port
EXPOSE 8001
# copy files
COPY package.json /mqttproxy/
COPY package-lock.json /mqttproxy/
COPY mqttproxy.js /mqttproxy/

WORKDIR /mqttproxy

RUN npm install
