from coltrane.rest import STATUS_CODE, http_status, app_status as app_status

__author__ = 'apetrovich'

from flask import request, g, jsonify
from coltrane import config
#from coltrane.rest.api import statuses


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
        if hasattr(self.manager, 'get_auth_token'):
            self.get_auth_token = self.manager.get_auth_token
            self.get_app_token  = self.manager.get_app_token


    def get_auth_token(self):
        auth_tkn = request.cookies.get(config.COOKIE_USER_AUTH_TOKEN, None)
        self.app.logger.debug("Got cookie %s: %s", config.COOKIE_USER_AUTH_TOKEN, auth_tkn)
        return auth_tkn


    def get_app_token(self):
        app_tkn = request.cookies.get(config.COOKIE_APP_TOKEN, None)
        self.app.logger.debug("Got cookie %s: %s", config.COOKIE_APP_TOKEN, app_tkn)
        return app_tkn


    @property
    def current_user(self):
        return g.current_user


    @property
    def current_app(self):
        return g.current_app


    def _before_request(self):
        if not self.get_auth_token():
            return jsonify({
                'message': 'User is not authorized',
                STATUS_CODE: app_status.USER_UNAUTHORIZED
            }), http_status.UNAUTHORIZED
        if not self.get_app_token():
            return jsonify({
                'message': 'App is not authorized',
                STATUS_CODE: app_status.APP_UNAUTHORIZED
            }), http_status.UNAUTHORIZED

        user = self.manager.authenticate_user(self.get_auth_token())
        app = self.manager.authenticate_app(self.get_app_token())

        if not user:
            return jsonify({
                'message': 'User is not authorized',
                STATUS_CODE: app_status.USER_UNAUTHORIZED
            }), http_status.UNAUTHORIZED
        if not app:
            return jsonify({
                'message': 'App is not authorized',
                STATUS_CODE: app_status.APP_UNAUTHORIZED
            }), http_status.UNAUTHORIZED

        g.current_user = user
        g.current_app = app
