# -*- coding: utf-8 -*-
"""
    :Authors: - qweqwe
"""

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
    email     = db.Column(db.String(255), unique=True)
    pwd_hash  = db.Column(db.String(255))
    #: used to identify user in applications
    token     = db.Column(db.String(255), default=uuid4, unique=True)
    #: used in cookies to identify user
    auth_hash = db.Column(db.String(255))
    created   = db.Column(db.DateTime, default=datetime.utcnow)


    def __init__(self, nickname, email, password):
        self.nickname  = nickname
        self.email     = email
        if password:
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

    @property
    def screen_name(self):
        """
            Used to display username on the site.
            If user doesn't have nor nickname nor email nor last or first names
            he probably had registered using twitter, so we return his twitter
            name.
            If user have last or first names, we return them
            If user have no last of first names he probably have nickname or
            at least an email
        """
        if not self.nickname and not self.email and \
           not self.firstname and not self.lastname:
            if self.twitter_user:
                return "@{0}".format(self.twitter_user.twitter_name)
            else:
                #TODO: CRITICAL ERROR
                return
        if self.firstname or self.lastname:
            #TODO: remove space if user doesn't have a first name
            return '{0} {1}'.format(self.firstname, self.lastname)
        else:
            return self.nickname or self.email





    @classmethod
    def create(cls, nickname=None, email=None, password=None,
               first_name=None, last_name=None):
        user = cls(nickname, email, password)
        user.firstname = first_name
        user.lastname  = last_name
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get(cls, nickname):
        #TODO: get_or_404
        return cls.query.filter(User.nickname == nickname).first()


class FacebookUser(db.Model):
    __tablename__ = 'facebook_users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    facebook_id = db.Column(db.BigInteger, nullable=False, unique=True)
    access_token = db.Column(db.String(512), nullable=False)

    #primaryjoin=(user_id==User.id),
    user = db.relationship(User, uselist=False, backref=db.backref('facebook_user'))

    def __init__(self, user, id, access_token):
        self.user = user
        self.facebook_id = id
        self.access_token = access_token

    def update_token(self, access_token):
        self.access_token = access_token
        db.session.commit()

    @classmethod
    def create(cls, user, id, access_token):
        facebook_user = cls(user, id, access_token)
        db.session.add(facebook_user)
        db.session.commit()
        return facebook_user

    @classmethod
    def get(cls, id):
        return cls.query.filter(FacebookUser.facebook_id == id).first()



class TwitterUser(db.Model):
    __tablename__ = 'twitter_users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    twitter_name = db.Column(db.String(512), nullable=False, unique=True)
    twitter_id   = db.Column(db.BigInteger, nullable=False, unique=True)
    access_token = db.Column(db.String(512), nullable=False)
    access_token_secret = db.Column(db.String(512), nullable=False)

    user = db.relationship(User, uselist=False, backref=db.backref('twitter_user'))

    def __init__(self, user, name, twitter_id, access_token, access_token_secret):
        self.user = user
        self.twitter_name = name
        self.twitter_id = twitter_id
        self.access_token = access_token
        self.access_token_secret = access_token_secret

    def update_tokens(self, access_token, access_toke_secret):
        self.access_token = access_token
        self.access_token_secret = access_toke_secret
        db.session.commit()

    @classmethod
    def create(cls, user, name, twitter_id, access_token, access_token_secret):
        twitter_user = cls(user, name, twitter_id, access_token, access_token_secret)
        db.session.add(twitter_user)
        db.session.commit()
        return twitter_user

    @classmethod
    def get(cls, name):
        return cls.query.filter(TwitterUser.twitter_name == name).first()



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
    token   = db.Column(db.String(255), default=uuid4,  unique=True)
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