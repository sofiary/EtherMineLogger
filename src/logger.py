#!/usr/bin/env python3

import json
import os
import psycopg2
from threading import Thread, Event
from typing import Union
import urllib.request

# Constant definitions

API_ENDPOINT = r"https://api.ethermine.org"
MINER = os.environ.get('EML_MINER')
WORKERS = list(os.environ.get('EML_WORKERS').split(','))
# Database defaults. User can change as required.
PG_DB = "emldb"
PG_USER = os.environ.get('PG_USER')
PG_PW = os.environ.get('PG_PW')
PG_HOST = 'localhost'
PG_PORT = 5433

def connect_pg(*, dbname: str, user: str, password: str, host: str, port: int, 
               **kw) -> Union[psycopg2.extensions.connection,
                              psycopg2.extensions.cursor]:
    '''Connects to selected PostgreSQL db and returns
    the db connection and cursor objects.
    '''
    conn = psycopg2.connect(f"dbname={dbname} user={user} password={password} "
                            f"host={host} port={port}")
    cur = conn.cursor()

    return conn, cur

#class PeriodicChecker(Thread):
def get_workers_data(*, api: str, miner: str, workers: list, timeout: int) -> list:
    '''Returns raw JSON information on workers' statistics'''
    # Use Mozilla header to prevent the 403 Forbidden error blocking urllib
    headers = {'User-Agent': 'Mozilla/5.0'}
    worker_data = {}
    for worker in workers:
        api_url = f"{api}/miner/:{miner}/worker/{worker}/history"
        request = urllib.request.Request(url=api_url, headers=headers)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            worker_data[worker] = json.loads(response.read())

    return worker_data

def store_workers_data(*, workers: list, cur: psycopg2.extensions.cursor) -> None:
    '''Adds new worker data to the database.'''

if __name__=="__main__":
    # Initial setup of database tables
    conn, cur = connect_pg(dbname=PG_DB, user=PG_USER, password=PG_PW,
                           host=PG_HOST, port=PG_PORT)
    _ = [cur.execute(f"CREATE TABLE IF NOT EXISTS {worker} ("
                      "epoch BIGINT NOT NULL PRIMARY KEY,"
                      "time TIMESTAMP NOT NULL,"
                      "reportedHashrate NUMERIC(4) NOT NULL,"
                      "currentHashrate NUMERIC(4) NOT NULL,"
                      "validShares INT NOT NULL,"
                      "invalidShares INT NOT NULL,"
                      "staleShares INT NOT NULL,"
                      "averageHashrate NUMERIC(4) NOT NULL); COMMIT") 
         for worker in WORKERS]

    get_workers_data(api=API_ENDPOINT, miner=MINER, workers=WORKERS, timeout=15)
    # Creation of looping thread object

    # To do Postgres TO_TIMESTAMP(time) integration