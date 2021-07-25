import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Boolean, DateTime
)
from sqlalchemy_json import mutable_json_type
from sqlalchemy.dialects.postgresql import JSONB

__all__ = ['student', 'admin', 'school', 'preference', 'locker', 'organization', 'assignment', 'org_name']

meta = MetaData()

student = Table(
    'student', meta,

    Column('id', Integer, primary_key=True),
    Column('email', String(100), nullable=False),
    Column('first_name', String(100), nullable=False),
    Column('last_name', String(100), nullable=False),
    Column('school_id', Integer, ForeignKey('school.id', ondelete='CASCADE'), nullable=False),
    Column('grade', Integer, nullable=False),

    #Column('assignment', mutable_json_type(dbtype=JSONB, nested=True))
)

# Store every school administrator using this website
# Should be manually pre-populated
admin = Table(
    'admin', meta,

    Column('id', Integer, primary_key=True),
    Column('email', String(100), nullable=False),
    Column('prefix', String(7), nullable=False),
    Column('last_name', String(100), nullable=False),
    Column('school_id', Integer, ForeignKey('school.id', ondelete='CASCADE'), nullable=False)
)

# Store every school using this website
# Should be manually pre-populated
school = Table(
    'school', meta,

    Column('id', Integer, primary_key=True),
    Column('name', String(100), nullable=False),
    Column('students_spreadsheet_uploaded', Boolean),
    Column('lockers_spreadsheet_uploaded', Boolean),
    Column('preassignments_spreadsheet_uploaded', Boolean),
    Column('students_spreadsheet_filename', String(100)),
    Column('lockers_spreadsheet_filename', String(100)),
    Column('preassignments_spreadsheet_filename', String(100))
)
    # Column('org_id', Integer, ForeignKey('org_name.school_id', ondelete='CASCADE'), nullable=False), (3rd column)

# Store student preferences for their partner/locker
# Should be populated upon a student's submission of the form
preference = Table(
    'preference', meta,
    Column('submit_time', DateTime(timezone='UTC'), nullable=False), # Store a timezone aware datetime object storing the current time
    Column('student_id', Integer, ForeignKey('student.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('partner_id', Integer, ForeignKey('student.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('partner_rank', Integer, nullable=False), # 1, 2, or 3 depending on how the student ranked this partner
    Column('locker_pref', Integer, ForeignKey('organization.id', ondelete='CASCADE'), nullable=False) # Points to one of the 20-30 possible
                                                                                                      #  organizations stored in the organizations table
)

# Store every locker in every school
# Should be populated from lockers spreadsheet
locker = Table(
    'locker', meta,

    Column('id', Integer, primary_key=True),
    Column('number', String(32), nullable=False),
    Column('school_id', Integer, ForeignKey('school.id', ondelete='CASCADE'), nullable=False),
    Column('combination', String(10)),
    Column('organization', Integer, ForeignKey('organization.id', ondelete='CASCADE'), nullable=False)
)


# Store every possible organization as values
# Should be populated from lockers spreadsheet
organization = Table(
    'organization', meta,

    Column('id', Integer, primary_key=True),
    Column('school_id', Integer, ForeignKey('school.id', ondelete='CASCADE'), nullable=False),
    Column('hierarchy_1', String(32)), # 1000, 2000, 3000, 4000 (building)
    Column('hierarchy_2', String(32)), # 1, 2 (Floor)
    Column('hierarchy_3', String(32)), # T, B (Level)
    Column('hierarchy_4', String(32)),
    Column('hierarchy_5', String(32))
)
# Example of organization table:
# 1 | 23 | 1000 | 2 | T
# 2 | 23 | 1000 | 2 | B
# 3 | 23 | 1000 | 1 | T
# 4 | 23 | 1000 | 1 | B
# 5 | 23 | 2000 | 2 | T
# ...
# There will only be 20-30 rows like this (ex. 4 buildings * 2 floors * 3 levels = 24),
# there will be many lockers belonging to each row though.
# This makes it easy to look up all lockers belonging to a specific org - simply look up all lockers that have
# a specific org id.

# Store every possible organization as names
# Should be populated from lockers spreadsheet
org_name = Table(
    'org_name', meta,

    # Column('id', Integer, primary_key=True),
    Column('school_id', Integer, ForeignKey('school.id', ondelete='CASCADE'), nullable=False, primary_key=True),
    Column('hierarchy_1', String(32)), # 'Building'
    Column('hierarchy_2', String(32)), # 'Floor'
    Column('hierarchy_3', String(32)), # 'Level'
    Column('hierarchy_4', String(32)),
    Column('hierarchy_5', String(32))
)
# Example of org_name table:
# 1 | 23 | Building | Floor | Level
# 2 | 12 | Building | Floor | Bay | Level
# ...

# Store final outcomes of partner/locker assignment
# Should be populated from preassignments spreadsheet
assignment = Table(
    'assignment', meta,
    Column('student_id', Integer, ForeignKey('student.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('partner_id', Integer, ForeignKey('student.id', ondelete='CASCADE')),
    Column('status', String(6), nullable=False), # either 'ASSIGN' or 'MATCH' depending on if the student got any of their preferences or not
    Column('locker_id', Integer, ForeignKey('locker.id', ondelete='CASCADE'), nullable=False)
)

async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    app['db'] = engine

async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()
