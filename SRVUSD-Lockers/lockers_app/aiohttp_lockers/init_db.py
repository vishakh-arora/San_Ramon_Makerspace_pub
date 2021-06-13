from sqlalchemy import create_engine, MetaData
from settings import config
from db import *
import datetime, pytz

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[students, admin])

def connect(engine):
    conn = engine.connect()
    return conn

def access(conn, table, function, rows):
    # use students.insert() when adding new students for the first time, use .update() when changing submit_time, responses, and assignment
    conn.execute(globals()[table].globals()[function](), rows)

    # conn.execute(students.update(), [
    #     {'email': 'dh.varora@students.srvusd.net',
    #      'first_name': 'Vishakh',
    #      'last_name': 'Arora',
    #      'school': 'Dougherty Valley High School',
    #      'grade': '12',
    #      'submit_time': datetime.datetime.now().replace(tzinfo=pytz.UTC),
    #      'responses': {'floor': '1',
    #                    'level': 'Bottom',
    #                    'bay': 'A'},
    #      'assignment': {'locker': '1234',
    #                     'partner': 'Shubham Kumar'}
    #     }
    # ])
    # conn.execute(admin.update(), [
    #     {'email': 'bspain@srvusd.net',
    #      'prefix': 'Mr. ',
    #      'last_name': 'Spain',
    #      'school': 'Dougherty Valley High School'}
    # ])
def disconnect(conn):
    conn.close()


if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)

    create_tables(engine)
    #connect(engine)
