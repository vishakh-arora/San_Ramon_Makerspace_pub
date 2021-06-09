from sqlalchemy import create_engine, MetaData
from aiohttp_lockers.settings import config
from aiohttp_lockers.db import students, admin
import datetime, pytz

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[students, admin])

def sample_data(engine):
    conn = engine.connect()
    # use students.insert() when adding new students for the first time, use .update() when changing submit_time, responses, and assignment
    conn.execute(students.update(), [
        {'email': 'dh.varora@students.srvusd.net',
         'first_name': 'Vishakh',
         'last_name': 'Arora',
         'school': 'Dougherty Valley High School',
         'grade': '12',
         'submit_time': datetime.datetime.now().replace(tzinfo=pytz.UTC),
         'responses': {'floor': '1',
                       'level': 'Bottom',
                       'bay': 'A'},
         'assignment': {'locker': '1234',
                        'partner': 'Shubham Kumar'}
        }
    ])
    conn.execute(admin.update(), [
        {'email': 'bspain@srvusd.net',
         'prefix': 'Mr. ',
         'last_name': 'Spain',
         'school': 'Dougherty Valley High School'}
    ])
    conn.close()


if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)

    create_tables(engine)
    sample_data(engine)
