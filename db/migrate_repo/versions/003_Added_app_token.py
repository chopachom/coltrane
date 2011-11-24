from sqlalchemy import *
from migrate import *
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from uuid import uuid4
from datetime import datetime

Base = declarative_base()

c_description = Column("description", Text(2048))

class AppTokenMixin(object):
    __tablename__ = 'apptokens'

    id = Column(Integer, primary_key=True)
    token = Column(String(255))

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
    developers = Table('developers', meta, autoload=True,
        autoload_with=migrate_engine)
    users = Table('users', meta, autoload=True,
        autoload_with=migrate_engine)
    applications = Table('applications', meta, autoload=True,
        autoload_with=migrate_engine)
    # rename index?
    ForeignKeyConstraint(columns=[applications.c.developer_id],
        refcolumns=[developers.c.id], name='applications_ibfk_1').drop()
    applications.columns.developer_id.drop()
    author_column = Column('author_id', Integer, ForeignKey("users.id"))
    author_column.create(applications)
    # http://groups.google.com/group/migrate-users/browse_thread/thread/b6e554987a269526

    class AppToken(AppTokenMixin, Base):
        pass

    AppToken.__table__.create(migrate_engine)
    applications.create_column(c_description)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta = MetaData(bind=migrate_engine)
    developers = Table('developers', meta, autoload=True,
        autoload_with=migrate_engine)
    users = Table('users', meta, autoload=True,
        autoload_with=migrate_engine)
    applications = Table('applications', meta, autoload=True,
        autoload_with=migrate_engine)
    ForeignKeyConstraint(columns=[applications.c.author_id],
        refcolumns=[users.c.id], name='applications_ibfk_1').drop()
    applications.columns.author_id.drop()
    developer_id = Column('developer_id', Integer, ForeignKey("developers.id"))
    developer_id.create(applications)
    # http://groups.google.com/group/migrate-users/browse_thread/thread/b6e554987a269526

    class AppToken(AppTokenMixin, Base):
        __table_args__ = {'extend_existing': True}

    AppToken.__table__.drop(migrate_engine)
    applications.drop_column(c_description)
