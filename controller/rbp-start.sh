#!/bin/sh
cd /usr/local/bin/reefberrypi &&
flask --app RBP_controller.py run --host=0.0.0.0 --port=5000