#!/usr/bin/env python3

from datetime import datetime
from getpass import getpass
import json
import os
import psycopg2
import sys
from threading import Thread, Event
import urllib.request

# Database defaults. User can change as required.
PG_PARAMS = {
    'dbname': 'emldb',
    'user': 'emluser',
    'host': 'localhost',
    'port': 5432,
    'timeout': 2 # seconds
}
# Logger defaults. User can change as required.
API_DATA = ['time', 'reportedHashrate', 'currentHashrate', 'validShares',
            'invalidShares', 'staleShares', 'averageHashrate']
EML_PARAMS = {
    'api': r"https://api.ethermine.org",
    'api_data': API_DATA,
    'miner': os.environ.get('EML_MINER'),
    'workers': os.environ.get('EML_WORKERS').split(','),
    'delay': 600 # seconds
}
  
class EtherMineLogger(Thread):
    
    def __init__(self, *, event: Event, api: str, api_data: list, miner: str, 
                 workers: list, delay: int, **kw) -> None:
        super().__init__()
        self.stopped = event
        self.api = api
        self.api_data = api_data
        self.miner = miner
        self.workers = workers
        self.workers_data: dict = {}
        self.delay = delay # Delay between API calls
        self.conn = None
        self.cur = None
        self.db = None
    
    def run(self, *, timeout=15, **kw):
        '''Overrides the parent Class method to periodically poll the
        EtherMine API and store new data into the persistent db.'''
        self._create_workers_tables()
        while not self.stopped.wait(self.delay):
            self._get_workers_data(timeout=timeout)
            self._store_workers_data()

    def connect_pg(self, *, dbname: str, user: str, password: str, host: str, 
                   port: int, timeout: int, **kw) -> None:
        '''Connects to selected PostgreSQL db and sets the internal db 
        connection and cursor objects.
        '''
        try:
            self.conn = psycopg2.connect(f"dbname={dbname} user={user} "
                                         f"password={password} host={host} "
                                         f"port={port} connect_timeout={timeout}")
        except psycopg2.OperationalError as e:
            # The error periodically repeats itself twice, this trims the error message
            print(str(e).split('\n')[0])
            sys.exit()
        else:
            self.cur = self.conn.cursor()

    def _create_workers_tables(self, *args, **kw) -> None:
        '''Establishes necessary PostgreSQL db tables for each worker,
        only if they don't exist already.
        '''
        for worker in self.workers:
            self.cur.execute(f"CREATE TABLE IF NOT EXISTS {worker} ("
                            f"epoch BIGINT NOT NULL PRIMARY KEY,"
                            f"{self.api_data[0]} TIMESTAMP NOT NULL,"
                            f"{self.api_data[1]} NUMERIC NOT NULL,"
                            f"{self.api_data[2]} NUMERIC NOT NULL,"
                            f"{self.api_data[3]} INT NOT NULL,"
                            f"{self.api_data[4]} INT NOT NULL,"
                            f"{self.api_data[5]} INT NOT NULL,"
                            f"{self.api_data[6]} NUMERIC NOT NULL); COMMIT") 

    def _get_workers_data(self, *, timeout: int, **kw) -> None:
        '''Returns raw JSON information on workers' statistics'''
        # Use Mozilla header to prevent the 403 Forbidden error blocking urllib
        headers = {'User-Agent': 'Mozilla/5.0'}
        self.workers_data = {}
        for worker in self.workers:
            # Perform an EtherMine API call to retrieve each worker's stats
            # and amalgamate the raw JSON information into a dictionary
            api_url = f"{self.api}/miner/:{self.miner}/worker/{worker}/history"
            request = urllib.request.Request(url=api_url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                self.workers_data[worker] = json.loads(response.read())

    def _store_workers_data(self, *args, **kw) -> None:
        '''Adds worker data to the PostgreSQL database.'''

        # Since EtherMine data only goes back 24h in 10m segments,
        # return only (24h*60m/10m) = 144 entries
        data_limit = 144

        def tuple_splitter(tuplelist: list) -> list:
            return [x[0] for x in tuplelist]

        for worker in self.workers_data.keys():
            # Decode workers' JSON information and update each worker's respective
            # table with the most recent mining stats.
            worker_stats = self._disassemble_json(worker=worker)
            
            if worker_stats is not None:
                # Retrieve existing db data
                self.cur.execute(f"SELECT DISTINCT epoch FROM {worker} "
                                 f"ORDER BY epoch DESC LIMIT {data_limit};")
                retmsg = self.cur.statusmessage
                statusfirst, *_, statuslast = retmsg.split(" ")
                try:
                    # Check if all the necessary data was retrieved
                    if statusfirst == "SELECT" and (rowsize := int(statuslast)) < data_limit:
                        # Define the number of scroll operations required
                        numscrolls = data_limit // rowsize
                        existing_db_data = tuple_splitter(self.cur.fetchall())
                        for i in range(numscrolls):
                            try:
                                self.cur.scroll(-1*rowsize)
                                existing_db_data += tuple_splitter(self.cur.fetchall())
                            except psycopg2.ProgrammingError as e:
                                # No more data left to scroll through
                                break
                    else:
                        existing_db_data = tuple_splitter(self.cur.fetchall())
                except ValueError as e:
                    print(f"Unexpected value returned from database call.")
                    print(f"Expected: 'SELECT <num>'")
                    print(f"Received: '{retmsg}'")

                for entry in worker_stats:
                    col_time, *col_remaining = self.api_data

                    if (epoch := entry[col_time]) in existing_db_data:
                        continue
                    else:
                        entry_time = datetime.fromtimestamp(epoch).strftime("%d-%m-%Y %H-%M-%S")
                        print(f"Adding epoch {epoch} at date/time "
                              f"{entry_time} to database.")

                    sql_statement = (f"INSERT INTO {worker} ("
                                    f"epoch,{col_time},"
                                    f"{','.join(col_remaining)}) VALUES ("
                                    f"{entry[col_time]},"
                                    f"TO_TIMESTAMP({str(entry[col_time])}),"
                                    f"{','.join([str(entry[item]) for item in col_remaining])}"
                                    f") ON CONFLICT DO NOTHING; COMMIT")
                    self.cur.execute(sql_statement)
            else:
                time_now = datetime.now().strftime("%d-%M-%Y %H:%M%:S")
                print(f"Failed to retrieve worker '{worker}' stats at {time_now}.")

    def _disassemble_json(self, *, worker: str, **kw):
        '''Disassembles the EtherMine API JSON schema to retrieve worker
        information for easy import into the relevant db table.'''
        if self.workers_data[worker]['status'] == 'OK':
            _worker_stats = []
            for entry in self.workers_data[worker]['data']:
                _worker_stats.append({key: entry[key] for key in self.api_data})
            return _worker_stats
        else:
            return None

if __name__=="__main__":
    halter = Event()
    eml = EtherMineLogger(**EML_PARAMS, event=halter)
    eml.connect_pg(**PG_PARAMS, password=getpass())
    eml.start()