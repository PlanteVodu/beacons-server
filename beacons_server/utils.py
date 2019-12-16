import os
from beacons_server import db

DB_PATH = 'beacons.sqlite'

def get_db():
    return db.DB(DB_PATH, silent=False)


def get_db_last_modification():
    return os.path.getmtime(DB_PATH)
