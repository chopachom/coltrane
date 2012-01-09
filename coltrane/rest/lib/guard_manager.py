__author__ = 'qweqwe'

from coltrane.db.models import User, AppToken
from hashlib import sha256

#TODO: (Someday) use HandlerSocket
class GuardManager(object):
    
    def __init__(self):
        pass

    def authenticate_user(self, token):
        return User.query.filter(User.auth_hash == sha256(token).hexdigest()).first()

    def authenticate_app(self, token):
        token = AppToken.query.filter(AppToken.token == token).first()
        if token:
            return token.application