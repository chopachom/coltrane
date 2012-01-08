from sqlalchemy import *
from migrate import *

meta = MetaData()

users = Table('users', meta,
            Column('id', Integer, primary_key=True, nullable=False),
        )
#users2 = Table('users', meta,
#            Column('id', Integer(), primary_key=True, nullable=False),
#        )
facebook_users = Table('facebook_users', meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('facebook_id', BigInteger, nullable=False),
        Column('access_token', String(512), nullable=False)
        )

twitter_users = Table('twitter_users', meta,
        Column('id', Integer, primary_key=True, nullable=False),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('twitter_name',  String(512), nullable=False),
        Column('access_token', String(512), nullable=False),
        Column('access_token_secret', String(512), nullable=False),
        )

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind = migrate_engine

    facebook_users.create()
    twitter_users.create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    meta.drop_all(tables=[facebook_users])
    meta.drop_all(tables=[twitter_users])
