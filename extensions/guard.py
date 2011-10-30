__author__ = 'apetrovich'

from flask import request, g, abort


class Guard(object):
    
    def __init__(self, app=None, manager=None):
        if app is not None:
            self.init_app(app)
        if manager is not None:
            self.manager = manager


    def init_app(self, app):
        self.app = app
        if not hasattr(self, 'manager'):
            raise RuntimeError('Manager instance is not defined')
        self.init_manager()
        self.app.before_request(self._before_request)


    def init_manager(self):
        # Dirty, dirty, dirty,  dirty,  dirty,  dirty, sucka
        self.manager = self.manager(self.app)
        self._authenticate_user = self.manager.authenticate_user
        self._authenticate_app = self.manager.authenticate_app
        if hasattr(self.manager, 'get_auth_token'):
            self.get_auth_token = self.manager.get_auth_token
            self.get_app_token  = self.manager.get_app_token


    def get_auth_token(self):
        auth_tkn = request.cookies.get('auth_tkn', None)
        self.app.logger.debug("Got cookie %s: %s", 'get_auth_token', auth_tkn)
        return auth_tkn


    def get_app_token(self):
        app_tkn = request.cookies.get('get_app_token', None)
        self.app.logger.debug("Got cookie %s: %s", 'get_app_token', app_tkn)
        return app_tkn


    @property
    def current_user(self):
        return g.current_user


    @property
    def current_app(self):
        return g.current_app


    def _before_request(self):
        if not self.get_auth_token() or not self.get_app_token():
            return abort(401)

        user = self._authenticate_user(self.get_auth_token())
        app = self._authenticate_app(self.get_app_token())

        if not user or not app:
            return abort(401)

        g.current_user = user
        g.current_app = app



#    def authenticate_user(self, func):
#        """ Decorator that registers passed func as an user authenticator
#            function, this functions accepts user token as an argument and
#            returns a user object if authentication was successful
#        """
#        self._authenticate_user = func
#
#
#    def authenticate_app(self, func):
#        """ Decorator that registers passed func as an app authenticator
#            function, this function accepts app token as an argument and
#            return an app object if authentication was successful
#        """
#        self._authenticate_app = func
