docker run -it \
--name rbp_mqttproxy \
--restart always \
-p 8001:8001 \
-v ~/RBPstack/mqttproxy/config:/mqttproxy/config \
-w /mqttproxy \
reefspy/mqttproxy node mqttproxy.js




