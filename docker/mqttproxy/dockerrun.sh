docker run -it \
--name rbp_mqttproxy \
--restart always \
-p 8001:8001 \
-v ~/RBPstack/mqttproxy:/usr/src/reefberrypi \
-w /usr/src/reefberrypi \
node:12-buster \
node mqttproxy.js




