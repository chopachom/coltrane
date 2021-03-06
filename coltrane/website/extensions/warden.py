# -*- coding: utf-8 -*-
from urlparse import urlparse
from flask import request, g, session
from flaskext.bcrypt import check_password_hash
from coltrane.db.models import User
from coltrane.website.lib.hooks import after_this_request
from coltrane.config import COOKIE_USER_AUTH_TOKEN
from hashlib import sha256
from functools import wraps
from datetime import datetime, timedelta


class Warden(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)


    def init_app(self, app):
        self.app = app
        app.before_request(self.cookie_login)
        # This inject current_user variable to all jinja2 templates
        app.context_processor(lambda: dict(current_user=self.current_user()))

    def current_user(self):
        if getattr(g, 'current_user', None):
            return g.current_user
        else:
            return None

    def cookie_login(self):
        if request.cookies.get(COOKIE_USER_AUTH_TOKEN):
            #print request.cookies.get('auth_tkn')
            self.login_by_token(request.cookies.get(COOKIE_USER_AUTH_TOKEN))

    def login_by_token(self, token):
        user = User.query.filter(User.auth_hash == sha256(token).hexdigest()).first()
        if user:
            g.current_user = user
            return True
        else:
            return False

    def login_required(self, fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not self.current_user():
                #return redirect(url_for('index'))
                return "Protected area"
            return fn(*args, **kwargs)
        return decorated_view


    # store session.user_id and adds auth_token to cookies
    def login(self, user, password=None):

        success = False

        # assuming that if password isn't given then we have a user object
        if password is None:
            session['user_id'] = user.id
            success = True
        # otherwise we have a username
        else:
            user = User.query.filter(User.nickname == user).first()
            if not user:
                return False
            if check_password_hash(user.pwdhash, password):
                session['user_id'] = user.id
                success = True

        if success:
            user.regenerate_auth_tokens()
            after_this_request(
                lambda resp: resp.set_cookie(
                    COOKIE_USER_AUTH_TOKEN,
                    user.auth_token,
                    expires=datetime.utcnow() + timedelta(days=14),
                    domain = urlparse(request.url_root).netloc.split(':')[0],
                    httponly=True) or resp # using 'or' because set_cookie returns NoneType without it
            )
            g.current_user = user

        return success


    def logout(self):
        try:
            del session['user_id']
        except KeyError:
            pass

        after_this_request(
            lambda resp: resp.set_cookie(
                COOKIE_USER_AUTH_TOKEN,
                '',
                expires=datetime(1971,01,01),
                httponly=True) or resp # using 'or' because set_cookie returns NoneType
            )


    def protect(self, blueprint):
        """ Makes routes of blueprint private, i.e. only logged in users have
            access to its routes.
        """
        @blueprint.before_request
        def protector():
            if not self.current_user():
                #TODO: shall return 401
                return "Protected area"

warden = Warden()
