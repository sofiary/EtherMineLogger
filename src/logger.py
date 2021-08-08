#!/usr/bin/env python3

import json
import os
import psycopg2
from typing import Union
import urllib

# Constant definitions

API_ENDPOINT = r"https://api.ethermine.org/"
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

def get_worker_data(*, api: str, miner: str, workers: list) -> list:
    '''Returns raw JSON information on workers' statistics'''
    # Use Mozilla header to prevent the 403 Forbidden error blocking urllib
    headers = {'User-Agent': 'Mozilla/5.0'}
    worker_data = {}
    for worker in workers:
        request = urllib.request.Request(f"{api}/miner/{miner}/worker/{worker}"
                                         f"/history", headers=headers)
        with urllib.request.urlopen(request, timeout=15) as response:
            worker_data[worker] = json.loads(response.read())
    
    return worker_data
    
if __name__=="__main__":
    conn, cur = connect_pg(dbname=PG_DB, user=PG_USER, password=PG_PW,
                           host=PG_HOST, port=PG_PORT)
    cur.execute("CREATE TABLE IF NOT EXISTS test (); COMMIT")