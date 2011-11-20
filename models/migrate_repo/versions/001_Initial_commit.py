from sqlalchemy import *
from migrate import *
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    nickname  = Column(String(80), unique=True)
    firstname = Column(String(255), unique=True)
    lastname  = Column(String(255), unique=True)
    email     = Column(String(255))
    pwd_hash  = Column(String(255))
    #: used to identify user in applications
    token     = Column(String(255), default=uuid4)
    #: used in cookies to identify user
    auth_hash = Column(String(255))
    created   = Column(DateTime, default=datetime.utcnow)


class Developer(Base):
    __tablename__ = 'developers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))


class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    developer_id = Column(Integer, ForeignKey("developers.id"))
    name = Column(String(255))


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    User.__table__.create(migrate_engine)
    Developer.__table__.create(migrate_engine)
    Application.__table__.create(migrate_engine)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    Application.__table__.drop(migrate_engine)
    Developer.__table__.drop(migrate_engine)
    User.__table__.drop(migrate_engine)

