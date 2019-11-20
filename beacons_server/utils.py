from beacons_server import db

def get_db():
    return db.DB('beacons.sqlite')
