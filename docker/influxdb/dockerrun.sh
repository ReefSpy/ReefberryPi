docker run -d \
-p 8086:8086 \
--restart always \
--name rbp_influxdb \
-v ~/RBPstack/influxdb:/var/lib/influxdb \
influxdb