__author__ = 'qweqwe'

from pymongo import Connection
from pymongo.database import Database

class FlaskMongodb(object):


    _default_config = {
        'MONGODB_HOST': '127.0.0.1',
        'MONGODB_PORT': 27017,
        'MONGODB_DATABASE': 'test_db',
        'MONGODB_SLAVE_OKAY': False,
        'MONGODB_USERNAME': None,
        'MONGODB_PASSWORD': None
    }

    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(self.app)

    def init_app(self, app):
        #setting default configuration for this app
        for k,v in self._default_config.items():
            app.config.setdefault(k, v)

        app.teardown_request(self._teardown_request)

        # register extension with app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['flask_mongodb'] = self
        
        self.app = app

        self.app.mongodb_connection, \
        self.app.mongodb_database = self.init_connection()


    def _teardown_request(self, request):
        self.app.mongodb_connection.end_request()
        return request


    def init_connection(self):
        if hasattr(self, 'app'):
            config = self.app.config
        else:
            config = self._default_config

        connection = Connection(
            host=config.get('MONGODB_HOST'),
            port=config.get('MONGODB_PORT'),
            slave_okay=config.get('MONGODB_SLAVE_OKAY')
        )

        database = Database(connection, config.get('MONGODB_DATABASE'))

        if config.get('MONGODB_USERNAME') is not None:
            database.authenticate(
                config.get('MONGODB_USERNAME'),
                config.get('MONGODB_PASSWORD')
            )

        return connection, database


    @property
    def connection(self):
        if hasattr(self, 'app') and self.app.mongodb_connection is not None:
            return self.app.mongodb_connection
        else:
            connection, _ = self.init_connection()
            return connection
