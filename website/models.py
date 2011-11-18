# -*- coding: utf-8 -*-
from extensions import db
from sqlalchemy.dialects.mysql import BIGINT
from datetime import datetime
from flaskext.bcrypt import generate_password_hash, check_password_hash
from hashlib import sha256, sha224
from os import urandom


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nickname  = db.Column(db.String(80), unique=True)
    firstname = db.Column(db.String(255), unique=True)
    lastname  = db.Column(db.String(255), unique=True)
    email   = db.Column(db.String(120))
    pwdhash = db.Column(db.String(255))
    token   = db.Column(db.String(255))
    created = db.Column(db.DateTime, default=datetime.utcnow)


    def __init__(self, username, email, password):
        self.username = username
        self.email    = email
        self.pwdhash  = generate_password_hash(password)
        self.token    = sha256(
            str(datetime.utcnow()) +
            str(self.pwdhash) +
            str(username) +
            str(urandom(12))
        ).hexdigest()


    def __repr__(self):
        return "<User {0} name: {1} email: {2} pwd hash: {3} token hash: {4} at {5:x}>".format(
            self.id, self.username, self.email, self.pwdhash, self.token, id(self))


    def _generate_tokens(self):
        self.token = sha256(
            str(datetime.utcnow()) +
            str(self.pwdhash) +
            str(self.username) +
            str(urandom(12))
        ).hexdigest()
        db.session.commit()
        return self.token



class Developer(db.Model):

    __tablename__ = 'developers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))



class Application(db.Model):

    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    developer_id = db.Column(db.Integer, db.ForeignKey("developers.id"))
    name = db.Column(db.String(255))