# -*- coding: utf-8 -*-
#TODO: USE HANDLER SOCKET OR SOME FORM OF CACHING

__author__ = 'qweqwe'

from flask import Flask, request, make_response, abort
from pprint import PrettyPrinter
from urlparse import urlparse
from hashlib import sha256
from os import urandom
from datetime import datetime
from coltrane.db.models import User, Application, AppToken
from coltrane.db.extension import db
from coltrane import config

pp = PrettyPrinter(indent=4)

app = Flask(__name__)
db.init_app(app)

@app.before_request
def before_request():
    response = make_response()
    base_path = get_base_path()
    app_domain = get_subdomain()
    full_domain = get_topdomain()

    if app.debug:
        print 'domain:', full_domain
        print base_path, app_domain
        print 'cookies: '
        pp.pprint(request.cookies)

    #TODO: add anonymous users
    auth_token = request.cookies.get(config.COOKIE_USER_AUTH_TOKEN)
    app_token = request.cookies.get(config.COOKIE_APP_TOKEN)
    anonymous = request.cookies.get(config.COOKIE_ANONYMOUS_TOKEN)

    # if user opens this app for the first time
    if auth_token and not app_token:
        # generate token
        user = User.query.filter(User.auth_token == auth_token).first()
        app  = Application.query.filter(Application.domain == app_domain).first()
        if not app:
            print 'app with domin %s was not found' % app_domain
            return abort(404)
        token = AppToken(user, app)
        db.session.add(token)
        db.session.commit()
        print 'setting cookies'
        response.set_cookie(config.COOKIE_APP_TOKEN, value=token.token,
                            domain=full_domain, httponly=True)

    # if user was anonymous but have authenticated
    if auth_token and anonymous:
        response.set_cookie(config.COOKIE_ANONYMOUS_TOKEN, '',
                            expires=datetime(1971,01,01))

    #TODO: anonymous users
    if not auth_token and not anonymous:
        response.set_cookie(config.COOKIE_ANONYMOUS_TOKEN, value='true',
                            domain=full_domain)

    response.headers['X-Accel-Redirect'] = "/files/"+base_path
    return response


#def generate_token(user_id, app_id):
#    return sha256(
#        str(datetime.utcnow()) +
#        str(user_id) +
#        str(app_id)  +
#        str(urandom(12))
#    ).hexdigest()


def get_subdomain():
    host = urlparse(request.url_root).netloc.split(':')[0]
    #olololo, super magic,
    #subdomain = host[:-len('.'.join(host.split('.')[1:]))].rstrip('.')
    subdomain = host.split('.')[0]
    topdomain = '.'.join(host.split('.')[-2:])
    return subdomain

def get_topdomain():
    return urlparse(request.url_root).netloc.split(':')[0]


def get_base_path():
    url = request.url[::-1]
    url_root = request.url_root[:-1][::-1]
    index = url.find(url_root)
    return request.url[-index:]