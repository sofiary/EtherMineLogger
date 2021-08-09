# EtherMineLogger
A simple Python helper to store EtherMine miner data into a persistent PostgreSQL database.<br>
This preparatory README has been developed for an Ubuntu 20.04LTS installation.

# General Preparation
Ensure:
<ul>
    <li>the installation instructions on the <a href="https://www.postgresql.org/">PostgreSQL<a> website have been followed, and the server/client are ready for your machine</li>
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
<username> and <password> need to be stored in environment variables EML_USER and EML_PW respectively.

This can be done by updating your ~/.bashrc file with a terminal editor such as vim/nano, and reloading the environment with:<br>
    $ source ~/.bashrc
    
If it is not already running, the Postgres server can be initialised with:<br>
    $ sudo service postgresql start

PSQL can be logged into with:<br>
    $ sudo -u postgres psql

Establish a new database in PSQL with:<br>
    CREATE DATABASE emldb;
    
# Execution
Navigate to the working directory of the cloned EtherMineLogger repository and execute the script with:<br>
    $ source .config.sh

This will initiate the necessary virtual environment and execute the python script (assuming python3 is the python PATH variable).
