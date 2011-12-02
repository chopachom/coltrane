from sqlalchemy import *
from migrate import *
from datetime import datetime


meta = MetaData()

users = Table('users', meta, Column('id', Integer(), primary_key=True))

comments = Table('comments', meta,
                  Column('id', Integer(), primary_key=True),
                  Column('author_id', Integer, ForeignKey("users.id")),
                  Column('description', Text(8128)),
                  Column('rate', Integer(128)),
                  Column('created', DateTime, default=datetime.utcnow))

assets  = Table('app_assets', meta,
                 Column('id', Integer(), primary_key=True),
                 Column('app_id', Integer, ForeignKey("applications.id")),
                 Column('url', String(4096)),
                 Column('type', Enum('image', 'video')),
                 Column('created', DateTime, default=datetime.utcnow))





def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind = migrate_engine
    applications = Table('applications', meta, autoload=True,
                        autoload_with=migrate_engine)
    developers = Table('developers', meta, autoload=True,
                        autoload_with=migrate_engine)
    dev_keys = Table('dev_keys', meta, autoload=True,
                        autoload_with=migrate_engine)
    apptokens = Table('apptokens', meta, autoload=True,
                        autoload_with=migrate_engine)
    created = Column('created', DateTime, default=datetime.utcnow)
    created.create(developers)
    created = Column('created', DateTime, default=datetime.utcnow)
    created.create(dev_keys)
    created = Column('created', DateTime, default=datetime.utcnow)
    created.create(applications)
    created = Column('created', DateTime, default=datetime.utcnow)
    created.create(apptokens)
    assets.create()
    comments.create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    applications = Table('applications', meta, autoload=True,
                        autoload_with=migrate_engine)
    developers = Table('developers', meta, autoload=True,
                        autoload_with=migrate_engine)
    dev_keys = Table('dev_keys', meta, autoload=True,
                        autoload_with=migrate_engine)
    apptokens = Table('apptokens', meta, autoload=True,
                        autoload_with=migrate_engine)
    applications.columns.created.drop()
    developers.columns.created.drop()
    dev_keys.columns.created.drop()
    apptokens.columns.created.drop()
    assets.drop()
    comments.drop()
