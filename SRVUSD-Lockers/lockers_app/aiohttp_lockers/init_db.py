from sqlalchemy import create_engine, MetaData
from settings import config
from db import *
import datetime, pytz

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[student, admin, school, preference, locker, organization, assignment])

def connect(engine):
    conn = engine.connect()
    return conn

def access(conn, table, function, rows):
    # use .insert() when adding rows for the first time, use .update() when changing existing rows
    conn.execute(globals()[table].globals()[function](), rows)

def disconnect(conn):
    conn.close()

def initialize_db():
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)
    create_tables(engine)
    conn = connect(engine)

    return conn

# if __name__ == '__main__':
#     db_url = DSN.format(**config['postgres'])
#     engine = create_engine(db_url)
#
#     create_tables(engine)
    #connect(engine)
