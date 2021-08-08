# EtherMineLogger
A simple Python helper to store EtherMine miner data into a persistent PostgreSQL database.

# General Preparation
Ensure:
<ul>
    <li>the installation instructions on the <a href="https://www.postgresql.org/">PostgreSQL<a> website have been followed, and the server/client are ready for your machine</li>
    <li>an appropriate virtual environment has been established</li>
    <li>the virtual environment requirements in requirements.txt have been installed</li>
    <li>your environment variable EML_MINER is set to your miner wallet (excluding the 0x prefix)</li>
    <li>your environment variable EML_WORKERS is set to a comma delimited list of your miner's worker names</li>
    <li>psycopg2 <a href="https://www.psycopg.org/install/">pre-requisites</a> have been installed</li>
</ul>
      
# PostgreSQL
A purpose-created user should have been created using the statement (change username and password respectively with your own selection):<br>
        CREATE USER username WITH ENCRYPTED PASSWORD 'password';<br>
<username> and <password> are stored in environment variables EML_USER and EML_PW respectively.
    
    
The server can be initialised with:
   $ sudo service postgresql start
