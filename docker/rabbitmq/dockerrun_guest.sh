docker run -d \
-p 15671:15671 \
-p 15672:15672 \
-p 15675:15675 \
-p 1883:1883 \
-v /home/pi/RBPstack/rabbitmq:/var/lib/rabbitmq \
--name rbp_rabbitmq reefspy/rabbitmq

