#!/usr/bin/sh

# Helper script

source ./venv/bin/activate
sudo service postgresql start
python3 src/logger.py