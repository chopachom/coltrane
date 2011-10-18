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
    def current_user_token(self):
        return g.app_token

    @property
    def current_app(self):
        return g.current_ap

    def _before_request(self):
        auth_tkn = request.cookies.get('auth_tkn', None)
        app_tkn = request.cookies.get('app_token', None)

        if auth_tkn:
            self.app.logger.debug("Got cookie %s: %s", 'auth_token', auth_tkn)
            g.user_token = auth_tkn
        if app_tkn:
            self.app.logger.debug("Got cookie %s: %s", 'app_token', app_tkn)
            g.app_token = app_tkn

        if not getattr(g, 'user_token', False) or getattr(g, 'app_token', False):
            return abort(401)

guard = Guard()