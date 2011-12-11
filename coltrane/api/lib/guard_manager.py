__author__ = 'qweqwe'

from coltrane.db.models import User, AppToken

#TODO: (Someday) use HandlerSocket
class GuardManager(object):
    
    def __init__(self):
        pass

    def authenticate_user(self, token):
        return User.query.filter(User.token==token).first()

    def authenticate_app(self, token):
        token = AppToken.query.filter(AppToken.token == token).first()
        if token:
            return token.application