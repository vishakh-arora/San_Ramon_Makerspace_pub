import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, DateTime
)
from sqlalchemy_json import mutable_json_type
from sqlalchemy.dialects.postgresql import JSONB

__all__ = ['student', 'admin', 'school', 'partner', 'locker', 'organization']

meta = MetaData()

# question = Table(
#     'question', meta,
#
#     Column('id', Integer, primary_key=True),
#     Column('question_text', String(200), nullable=False),
#     Column('pub_date', Date, nullable=False)
# )
#
# choice = Table(
#     'choice', meta,
#
#     Column('id', Integer, primary_key=True),
#     Column('choice_text', String(200), nullable=False),
#     Column('votes', Integer, server_default="0", nullable=False),
#
#     Column('question_id',
#            Integer,
#            ForeignKey('question.id', ondelete='CASCADE'))
# )

student = Table(
    'student', meta,

    Column('id', Integer, primary_key=True),
    Column('email', String(100), nullable=False),
    Column('first_name', String(100), nullable=False),
    Column('last_name', String(100), nullable=False),
    Column('school_id', Integer, ForeignKey('school.id', ondelete='CASCADE'), nullable=False),
    Column('grade', Integer, nullable=False),
    Column('submit_time', DateTime(timezone='UTC')),
    #Column('assignment', mutable_json_type(dbtype=JSONB, nested=True))
)

admin = Table(
    'admin', meta,

    Column('id', Integer, primary_key=True),
    Column('email', String(100), nullable=False),
    Column('prefix', String(7), nullable=False),
    Column('last_name', String(100), nullable=False),
    Column('school_id', Integer, ForeignKey('school.id', ondelete='CASCADE'), nullable=False),
    #Column('responses', mutable_json_type(dbtype=JSONB, nested=True))
)

school = Table(
    'school', meta,

    Column('id', Integer, primary_key=True),
    Column('name', String(100), nullable=False),
)

partner = Table(
    'partner', meta,
    Column('student_id', Integer, ForeignKey('student.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('partner_id', Integer, ForeignKey('student.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('preference', Integer, nullable=False),
)
# Vishakh | Shubham 0
# Vishakh | Chaitu 1
# Vishakh | Shlok 2

locker = Table(
    'locker', meta,

    Column('id', Integer, primary_key=True),
    Column('number', String(32), nullable=False), #1234
    Column('school_id', Integer, ForeignKey('school.id', ondelete='CASCADE'), nullable=False), #DVHS
    Column('combination', String(10)),
    Column('organization', Integer, ForeignKey('organization.id', ondelete='CASCADE'), nullable=False), #id
    #1000 | 2 | 2 | 1
)
#
organization = Table(
    'organization', meta,

    Column('id', Integer, primary_key=True),
    Column('school_id', Integer, ForeignKey('school.id', ondelete='CASCADE'), nullable=False),
    Column('hierarchy_1', String(32)), #1000, 2000, 3000, 4000
    Column('hierarchy_2', String(32)), # Floor
    Column('hierarchy_3', String(32)), # Level
    Column('hierarchy_4', String(32)),
    Column('hierarchy_5', String(32)),
    Column('hierarchy_6', String(32)),
    Column('hierarchy_7', String(32)),
    Column('hierarchy_8', String(32)),
    Column('hierarchy_9', String(32)),
    Column('hierarchy_10', String(32))
)
# locker # | combination (optional) | hierarchy (largest --> smallest level)
# 1 | 23 | building | floor | bay | level | row
# building | level | row
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
