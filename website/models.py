# -*- coding: utf-8 -*-
from extensions import db
from datetime import datetime
from flaskext.bcrypt import generate_password_hash, check_password_hash
from hashlib import sha256, sha224
from os import urandom


class User(db.Document):

    username = db.StringField(required=True)
    email = db.StringField(required=True)
    pwdhash = db.StringField(required=True)
    tknhash = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.utcnow)

    def __init__(self, *args, **kwargs):
        if 'password' in kwargs:
            kwargs['pwdhash'] = generate_password_hash(kwargs.pop('password'))
            self.auth_token = sha256( str(datetime.utcnow()) +  str(kwargs['pwdhash']) +
                str(kwargs['username']) +  str(urandom(12))).hexdigest()
            kwargs['tknhash'] = sha256(self.auth_token).hexdigest()
        super(User, self).__init__(*args, **kwargs)

    def _generate_tokens(self):
        self.auth_token = sha256(
            str(datetime.utcnow()) +
            str(self.pwdhash) +
            str(self.username) +
            str(urandom(12))
        ).hexdigest()
        self.tknhash = sha256(self.auth_token).hexdigest()
        self.save()
        return self.auth_token, self.tknhash



class Developer(db.Document):
    user = db.ReferenceField(User)

class Application(db.Document):
    name = db.StringField(required=True)
    developer = db.ReferenceField(Developer)
