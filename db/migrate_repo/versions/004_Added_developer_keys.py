from sqlalchemy import *
from migrate import *

meta = MetaData()

users = Table('users', meta, Column('id', Integer(), primary_key=True))

dev_keys = Table('dev_keys', meta,
                  Column('id', Integer(), primary_key=True),
                  Column('user_id', Integer, ForeignKey("users.id")),
                  Column('key', Text(8128), nullable=True),
                  Column('hash', String(512), nullable=True))

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    dev_keys.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    dev_keys.drop()
