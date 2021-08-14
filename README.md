# EtherMineLogger
A simple Python helper to store EtherMine miner data into a persistent PostgreSQL database.<br>
This preparatory README has been developed for an Ubuntu 20.04LTS installation.

# General Preparation
Ensure:
<ul>
    <li>your machine has PostgreSQL installed</li>
    <li>the installed Python version is >= 3.6</li>
    <li>a Python virtual environment has been established in the project folder as venv</li>
    <li>the virtual environment requirements in requirements.txt have been installed</li>
    <li>your environment variable EML_MINER is set to your miner wallet (excluding the 0x prefix)</li>
    <li>your environment variable EML_WORKERS is set to a comma delimited list of your miner's worker names</li>
    <li>psycopg2 <a href="https://www.psycopg.org/install/">pre-requisites</a> have been installed</li>
</ul>
      
# PostgreSQL
A purpose-created user should have been created using the statement (change username and password respectively with your own selection):<br>
    CREATE USER username WITH ENCRYPTED PASSWORD 'password' SUPERUSER;<br>
<username> is assumed by default to be emluser, but can be changed.
If it is changed, the entry for 'user' in the logger.py file's PG_PARAMS dictionary must be updated. 
    
If it is not already running, the Postgres server can be initialised with:<br>
    $ sudo service postgresql start

PSQL can be logged into with:<br>
    $ sudo -u postgres psql

Establish a new database in PSQL with:<br>
    CREATE DATABASE emldb;
If you choose a different database name, the entry for 'dbname' in the logger.py file's PG_PARAMS dictionary must be updated.
    
# Automatic Execution
From the EtherMineLogger repo cloned directory, execute the start-up script:<br>
    $ source .eml.sh

This will:
- initiate the necessary virtual environment;
- start the Postgres server; and
- execute the python script (assuming python3 is the python PATH variable).
