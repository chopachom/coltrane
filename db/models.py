# -*- coding: utf-8 -*-
__author__ = 'qweqwe'

from datetime import datetime
from hashlib import sha256, sha224
from os import urandom
from uuid import  uuid4
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class UserMixin(object):

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


    def __init__(self, nickname, email, password):
        self.nickname  = nickname
        self.email     = email
        self.pwd_hash  = self.generate_password_hash(password)
        self.generate_auth_tokens()


    def __repr__(self):
        return "<User {0} name: {1} email: {2} pwd hash: {3} token hash: {4} at {5:x}>".format(
            self.id, self.nickname, self.email, self.pwd_hash, self.token, id(self))


    def generate_auth_tokens(self):
        """ Generates unique auth_token, sha256 hash of which is used to
            authenticate users by cookie
        """
        #: temporary auth token
        self.auth_token    = sha256(
            str(datetime.utcnow()) +
            str(self.pwd_hash) +
            str(self.nickname) +
            str(urandom(12))
        ).hexdigest()
        #; persistent auth hash
        self.auth_hash = sha256(self.auth_token).hexdigest()


    def regenerate_auth_tokens(self):
        """ Regenerate tokens and save them in db
        """
        self.generate_auth_tokens()
        self.session.commit()
        return self.auth_token


    def generate_password_hash(self, value):
        raise NotImplementedError()

    @property
    def session(self):
        raise NotImplementedError()




class DeveloperMixin(object):

    __tablename__ = 'developers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship(UserMixin, uselist=False)

    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return "<Developer {0} user_id: {1} at {2:x}>".format(
                self.id, self.user_id, id(self))



class ApplicationMixin(object):

    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    developer_id = Column(Integer, ForeignKey("developers.id"))
    name   = Column(String(255))
    domain = Column(String(255))


    def __repr__(self):
        return "<Application {0} name: {1} developer_id: {2} at {3:x}>".format(
                self.id, self.name, self.developer_id, id(self))


class AppTokenMixin(object):

    __tablename__ = 'apptokens'

    id = Column(Integer, primary_key=True)
    app_id  = Column(Integer, ForeignKey("applications.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    token   = Column(String(255))