# EtherMineLogger
A simple Python helper to store EtherMine miner data into a persistent PostgreSQL database.

# General Preparation
This repo is only being developed for Ubuntu 20.04 LTS.<br>
However, it should be relatively adaptable for use in other Linux distributions, Windows or MAC O/S.<br>

Ensure:
<ul>
    <li>the installation instructions on the <a href="https://www.postgresql.org/download/linux/ubuntu/">PostgreSQL<a> website have been followed, and the server/client are ready for your machine</li>
    <li>the virtual environment requirements in requirements.txt have been installed</li>
    <li>your environment variable EML_MINER is set to your miner wallet (excluding the 0x prefix)</li>
    <li>your environment variable EML_WORKERS is set to a comma delimited list of your miner's worker names</li>
    <li>psycopg2 <a href="https://www.psycopg.org/install/">pre-requisites</a> have been installed</li>
</ul>
      
