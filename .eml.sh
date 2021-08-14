#!/usr/bin/sh

# Execution script

source ./venv/bin/activate
sudo service postgresql start
# The next command exposes which port PostgreSQL is running on
pgport=sudo sed -n 4p /var/lib/postgresql/12/main/postmaster.pid
echo PostgreSQL server running on port $pgport
python3 ./src/logger.py