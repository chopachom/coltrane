from sqlalchemy import *
from migrate import *
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from uuid import uuid4
from datetime import datetime

Base = declarative_base()

class AppTokenMixin(object):

    __tablename__ = 'apptokens'

    id = Column(Integer, primary_key=True)
    token   = Column(String(255))

    @declared_attr
    def app_id(cls):
        Column(Integer, ForeignKey("applications.id"))

    @declared_attr
    def user_id(cls):
        Column(Integer, ForeignKey("users.id"))



def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta = MetaData(bind=migrate_engine)
    applications = Table('applications', meta, autoload=True,
                       autoload_with=migrate_engine)
    # http://groups.google.com/group/migrate-users/browse_thread/thread/b6e554987a269526
    class AppToken(AppTokenMixin, Base):
        pass
    AppToken.__table__.create(migrate_engine)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(bind=migrate_engine)
    applications = Table('applications', meta, autoload=True,
                       autoload_with=migrate_engine, )
    # http://groups.google.com/group/migrate-users/browse_thread/thread/b6e554987a269526
    class AppToken(AppTokenMixin, Base):
        __table_args__ = {'extend_existing': True}
    AppToken.__table__.drop(migrate_engine)
