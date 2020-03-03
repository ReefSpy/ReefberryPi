docker run -d \
-p 15671:15671 \
-p 15672:15672 \
-p 15675:15675 \
-p 1883:1883 \
--restart always \
-v ~/RBPstack/rabbitmq:/var/lib/rabbitmq \
-e RABBITMQ_DEFAULT_USER=pi \
-e RABBITMQ_DEFAULT_PASS=reefberry \
--name rbp_rabbitmq reefspy/rabbitmq

