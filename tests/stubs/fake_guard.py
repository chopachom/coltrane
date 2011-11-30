__author__ = 'qweqwe'


from api.extensions.guard import Guard
from utils import Enum


AUTH_TOKEN = 'ThIsIsUsErAuThToKeN'
APP_TOKEN  = 'tHiSiSaPpLiCaTiOnToKeN'


class user(Enum):
    id = 101
    name = 'Fake and Gay'
    token = AUTH_TOKEN


class app(Enum):
    id = 100500
    title = 'Anal Prestige'
    token = APP_TOKEN


class FakeGuardManager(object):

    def __init__(self):
        pass

    def authenticate_user(self, token):
        if token in user.values():
            return user

    def authenticate_app(self, token):
        if token in app.values():
            return app

    def get_auth_token(self):
        return AUTH_TOKEN

    def get_app_token(self):
        return APP_TOKEN

guard = Guard()
guard.manager = FakeGuardManager