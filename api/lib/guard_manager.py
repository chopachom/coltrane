__author__ = 'qweqwe'

from website.models import User, Application, AppToken

#TODO: (Someday) use HandlerSocket
class GuardManager(object):
    
    def __init__(self, app=None):
        pass

    def authenticate_user(self, token):
        return User.query.filter(User.token==token).first()

    def authenticate_app(self, token):
        return AppToken.query.filter(AppToken.token == token).first().application