docker run -d --rm \
--name rbp_simulator \
--network="host" \
-v ~/RBPstack/simulator:/usr/src/reefberrypi \
-w /usr/src/reefberrypi \
reefspy/reefberrypi \
python3 RBP_Simulator.py
