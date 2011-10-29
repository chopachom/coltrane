__author__ = 'apetrovich'

from flask import request, g, abort


class Guard(object):
    
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)


    def init_app(self, app):
        self.app = app
        self.app.before_request(self._before_request)


    @property
    def current_user(self):
        return g.current_user


    @property
    def current_app(self):
        return g.current_app


    def authenticate_user(self, func):
        """ Decorator that registers passed func as an user authenticator
            function, this functions accepts user token as an argument and
            returns a user object if authentication was successful
        """
        self._authenticate_user = func


    def authenticate_app(self, func):
        """ Decorator that registers passed func as an app authenticator
            function, this function accepts app token as an argument and
            return an app object if authentication was successful
        """
        self._authenticate_app = func


    def _before_request(self):
        auth_tkn = request.cookies.get('auth_tkn', None)
        app_tkn = request.cookies.get('app_token', None)

        if not auth_tkn or not app_tkn or not len(auth_tkn) or not len(app_tkn):
            return abort(401)

        self.app.logger.debug("Got cookie %s: %s", 'auth_token', auth_tkn)
        user = self._authenticate_user(auth_tkn)

        self.app.logger.debug("Got cookie %s: %s", 'app_token', app_tkn)
        app = self._authenticate_app(app_tkn)

        if not user or not app:
            return abort(401)

        g.current_user = user
        g.current_app = app
