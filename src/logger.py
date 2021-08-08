import os
import psycopg2

API_ENDPOINT: str = r"https://api.ethermine.org/"
MINER: str = os.environ.get('EML_MINER')
WORKERS: list = os.environ.get('EML_WORKERS').split(',')

if __name__=="__main__":
    pass

