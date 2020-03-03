docker run -it --rm \
--name rbp_simulator \
--network="host" \
-v ~/RBPstack/simulator:/usr/src/reefberrypi \
-w /usr/src/reefberrypi \
python:3 \
