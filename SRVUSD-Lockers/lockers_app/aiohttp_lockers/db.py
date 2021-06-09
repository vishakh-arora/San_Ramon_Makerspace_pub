import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, DateTime
)
from sqlalchemy_json import mutable_json_type
from sqlalchemy.dialects.postgresql import JSONB

__all__ = ['students', 'admin']

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

students = Table(
    'students', meta,

    Column('email', String(100), primary_key=True),
    Column('first_name', String(100), nullable=False),
    Column('last_name', String(100), nullable=False),
    Column('school', String(100), nullable=False),
    Column('grade', String(2), nullable=False),
    Column('submit_time', DateTime(timezone='UTC')),
    Column('responses', mutable_json_type(dbtype=JSONB, nested=True)),
    Column('assignment', mutable_json_type(dbtype=JSONB, nested=True))
)
#students.c.submit_time.alter(nullable=True)
admin = Table(
    'admin', meta,

    Column('email', String(100), primary_key=True),
    Column('prefix', String(7), nullable=False),
    Column('last_name', String(100), nullable=False),
    Column('school', String(100), nullable=False),
    Column('responses', mutable_json_type(dbtype=JSONB, nested=True))
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
