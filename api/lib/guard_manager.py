__author__ = 'qweqwe'

from api.extensions import mongodb

class GuardManager(object):
    
    def __init__(self, app):
        c = app.config
        self.users = mongodb.connection[c.get('MONGODB_DATABASE')][c.get('USERS_COLLECTION')]
        self.apps = mongodb.connection[c.get('MONGODB_DATABASE')][c.get('APPS_COLLECTION')]

    def authenticate_user(self, token):
        self.users.find_one({'token': token})

    def authenticate_app(self, token):
        self.apps.find_one({'token': token})