# -*- coding: utf-8 -*-
__author__ = 'qweqwe'

from coltrane.db.extension import db
from datetime import datetime
from flaskext.bcrypt import generate_password_hash, check_password_hash
from hashlib import sha256, sha224
from os import urandom
from uuid import  uuid4

from sqlalchemy.orm import joinedload


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nickname  = db.Column(db.String(80), unique=True)
    firstname = db.Column(db.String(255), unique=True)
    lastname  = db.Column(db.String(255), unique=True)
    email     = db.Column(db.String(255))
    pwd_hash  = db.Column(db.String(255))
    #: used to identify user in applications
    token     = db.Column(db.String(255), default=uuid4)
    #: used in cookies to identify user
    auth_hash = db.Column(db.String(255))
    created   = db.Column(db.DateTime, default=datetime.utcnow)


    def __init__(self, nickname, email, password):
        self.nickname  = nickname
        self.email     = email
        self.pwd_hash  = generate_password_hash(password)
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
        db.session.commit()
        return self.auth_token


    @classmethod
    def get(cls, nickname):
        #TODO: get_or_404
        return cls.query.filter(User.nickname == nickname).first()


class FacebookUser(db.Model):
    __tablename__ = 'facebook_users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    facebook_id = db.Column(db.BigInteger, nullable=False)
    access_token = db.Column(db.String(512), nullable=False)



class Developer(db.Model):

    __tablename__ = 'developers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created   = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship(User, uselist=False)

    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return "<Developer {0} user_id: {1} at {2:x}>".format(
                self.id, self.user_id, id(self))


class DeveloperKeys(db.Model):

    __tablename__ = 'dev_keys'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    key  = db.Column(db.Text(8128), nullable=True)
    hash = db.Column(db.String(512), nullable=True)
    created   = db.Column(db.DateTime, default=datetime.utcnow)



class Application(db.Model):

    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    name   = db.Column(db.String(255))
    description = db.Column(db.Text(2048))
    domain = db.Column(db.String(255))
    created   = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship(User, uselist=False,)


    def __init__(self, name, domain, description, user):
        self.name = name
        self.domain = domain
        self.description = description
        self.author = user


    def __repr__(self):
        return "<Application {0} name: {1} domain: {2} author_id: {3} at {4:x}>".format(
                self.id, self.name, self.domain, self.author_id, id(self))

    @classmethod
    def create(cls, name, domain, description, user):
        app = cls(name, domain, description, user)
        db.session.add(app)
        db.session.commit()
        return app

    #TODO: get or 404
    @classmethod
    def get(cls, domain, author):
        if isinstance(author, basestring):
            author = User.get(author)
        return cls.query.filter(
            (cls.domain == domain) & (cls.author == author)
        ).first()

    @classmethod
    def find(cls, author):
        if isinstance(author, basestring):
            author = User.get(author)
        return cls.query.filter(cls.author == author)

    @classmethod
    def all(cls):
        #TODO: joined load
        return cls.query.options(joinedload('author')).all()


class ApplicationAsset(db.Model):
    """
        Applications assets holds addition info for application description,
        like images, screenshots and videos
    """

    __tablename__ = 'app_assets'

    id = db.Column(db.Integer, primary_key=True)
    app_id  = db.Column(db.Integer, db.ForeignKey("applications.id"))
    url     = db.Column(db.String(4096))
    type    = db.Column(db.Enum('image', 'video'))
    created = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    app_id    = db.Column(db.Integer, db.ForeignKey("applications.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    description = db.Column(db.Text(8128))
    rate      = db.Column(db.Integer(128))
    created   = db.Column(db.DateTime, default=datetime.utcnow)




class AppToken(db.Model):
    """
        Tokens used to authenticate app and user. When an user uses app for the
        first time a new token generated for the user. This token then always
        passed by the browser with each request.
    """

    __tablename__ = 'apptokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    app_id  = db.Column(db.Integer, db.ForeignKey("applications.id"))
    token   = db.Column(db.String(255))
    created   = db.Column(db.DateTime, default=datetime.utcnow)


    user = db.relationship(User, uselist=False)
    application = db.relationship(Application, uselist=False)


    def __init__(self, user, application):
        self.user = user
        self.application = application
        self.token = self.generate()


    def generate(self):
        return sha256(
            str(datetime.utcnow()) +
            str(self.user_id) +
            str(self.app_id)  +
            str(urandom(12))
        ).hexdigest()