#!/bin/sh
cd /usr/local/bin/reefberrypi &&
source venv/bin/activate &&
flask --app RBP_controller.py run --host=0.0.0.0 --port=5000