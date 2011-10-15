__author__ = 'PedoFinderGeneral'

from flask import request, current_app, g, abort

logger = current_app.logger


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
        if request.cookies.get('auth_tkn'):
            logger.debug("Got cookie %s: %s", 'auth_token', request.cookies['auth_tkn'])
            g.user_token = request.cookies['auth_tkn']
        if request.cookies.get('app_token'):
            logger.debug("Got cookie %s: %s", 'app_token', request.cookies['app_tkn'])
            g.app_token = request.cookies['app_tkn']

        if not g.user_token or g.app_token:
            return abort(401)

guard = Guard()