from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData(bind=migrate_engine)
    applications = Table('applications', meta, autoload=True)
    domain_column = Column('domain', String(255))
    domain_column.create(applications)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(bind=migrate_engine)
    applications = Table('applications', meta, autoload=True)
    applications.c.domain.drop()
