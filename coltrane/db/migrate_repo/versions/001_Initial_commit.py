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
    email     = Column(String(255), unique=True)
    pwd_hash  = Column(String(255))
    #: used to identify user in applications
    token     = Column(String(255), default=uuid4, unique=True)
    #: used in cookies to identify user
    auth_hash = Column(String(255))
    created   = Column(DateTime, default=datetime.utcnow)


class Developer(Base):
    __tablename__ = 'developers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created = Column(DateTime, default=datetime.utcnow)

    
class DeveloperKeys(Base):
    __tablename__ = 'dev_keys'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key  = Column(Text(8128), nullable=True)
    hash = Column(String(512), nullable=True)
    created   = Column(DateTime, default=datetime.utcnow)


class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255))
    description = Column(Text(2048))
    domain = Column(String(255))
    created = Column(DateTime, default=datetime.utcnow)


class AppToken(Base):
    __tablename__ = 'apptokens'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    app_id  = Column(Integer, ForeignKey("applications.id"))
    token   = Column(String(255),default=uuid4,  unique=True)
    created = Column(DateTime, default=datetime.utcnow)
    

class ApplicationAsset(Base):
    """
        Applications assets holds addition info for application description,
        like images, screenshots and videos
    """

    __tablename__ = 'app_assets'

    id = Column(Integer, primary_key=True)
    app_id  = Column(Integer, ForeignKey("applications.id"))
    url     = Column(String(4096))
    type    = Column(Enum('image', 'video'))
    created = Column(DateTime, default=datetime.utcnow)


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    app_id    = Column(Integer, ForeignKey("applications.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    description = Column(Text(8128))
    rate      = Column(Integer(128))
    created   = Column(DateTime, default=datetime.utcnow)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    User.__table__.create(migrate_engine)
    Developer.__table__.create(migrate_engine)
    DeveloperKeys.__table__.create(migrate_engine)
    Application.__table__.create(migrate_engine)
    AppToken.__table__.create(migrate_engine)
    ApplicationAsset.__table__.create(migrate_engine)
    Comment.__table__.create(migrate_engine)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    Developer.__table__.drop(migrate_engine)
    DeveloperKeys.__table__.drop(migrate_engine)
    AppToken.__table__.drop(migrate_engine)
    ApplicationAsset.__table__.drop(migrate_engine)
    Comment.__table__.drop(migrate_engine)
    Application.__table__.drop(migrate_engine)
    User.__table__.drop(migrate_engine)


