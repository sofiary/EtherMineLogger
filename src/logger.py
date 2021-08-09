#!/usr/bin/env python3

import json
import os
import psycopg2
from threading import Thread, Event
import urllib.request

# Constant definitions

API_ENDPOINT = r"https://api.ethermine.org"
API_DATA = ['time', 'reportedHashrate', 'currentHashrate', 'validShares',
            'invalidShares', 'staleShares', 'averageHashrate']
MINER = os.environ.get('EML_MINER')
WORKERS = list(os.environ.get('EML_WORKERS').split(','))
# Database defaults. User can change as required.
PG_DB = 'emldb'
PG_USER = os.environ.get('PG_USER')
PG_PW = os.environ.get('PG_PW')
PG_HOST = 'localhost'
PG_PORT = 5433
  
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

    def __repr__(self) -> str:
        pass
    
    def run(self, *, timeout=15, **kw):
        '''Overrides the parent Class method to periodically poll the
        EtherMine API and store new data into the persistent db.'''
        self.create_workers_tables()
        while not self.stopped.wait(self.delay):
            self._get_workers_data(timeout=timeout)
            self._store_workers_data()

    def connect_pg(self, *, dbname: str, user: str, password: str, host: str, 
                   port: int, **kw) -> None:
        '''Connects to selected PostgreSQL db and sets the internal db 
        connection and cursor objects.
        '''
        self.conn = psycopg2.connect(f"dbname={dbname} user={user} "
                                     f"password={password} host={host} "
                                     f"port={port}")
        self.cur = self.conn.cursor()

    def create_workers_tables(self, *args, **kw) -> None:
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
            api_url = f"{self.api}/miner/:{self.miner}/worker/{worker}/history"
            request = urllib.request.Request(url=api_url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                self.workers_data[worker] = json.loads(response.read())

    def _store_workers_data(self, *args, **kw) -> None:
        '''Adds worker data to the PostgreSQL database.'''
        for worker in self.workers_data.keys():
            worker_stats = self._disassemble_json(worker=worker)
            if worker_stats is not None:
                for entry in worker_stats:
                    sql_statement = (f"INSERT INTO {worker} ("
                                    f"epoch,{self.api_data[0]},"
                                    f"{','.join(self.api_data[1:])}) VALUES ("
                                    f"{entry[self.api_data[0]]},"
                                    f"TO_TIMESTAMP({str(entry[self.api_data[0]])}),"
                                    f"{','.join([str(x) for x in entry.values()][1:])}"
                                    f") ON CONFLICT DO NOTHING; COMMIT")
                    self.cur.execute(sql_statement)

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
    eml = EtherMineLogger(event=halter, api=API_ENDPOINT, api_data=API_DATA,
                          miner=MINER, workers=WORKERS, delay=600)
    eml.connect_pg(dbname=PG_DB, user=PG_USER, password=PG_PW,
                   host=PG_HOST, port=PG_PORT)
    eml.start()