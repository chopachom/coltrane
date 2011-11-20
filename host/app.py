# -*- coding: utf-8 -*-
__author__ = 'qweqwe'

from flask import Flask, request, make_response, abort
from pprint import PrettyPrinter
from urlparse import urlparse
from hashlib import sha256
from os import urandom
from datetime import datetime
from janelle.models import mongokit
from janelle.config import TestConfig

pp = PrettyPrinter(indent=4)

app = Flask(__name__)
mongokit.init_app(app)


@app.before_request
def before_request():
    response = make_response("ololo")
    base_path = get_base_path()
    app_name = get_subdomain()
    full_domain = get_topdomain()

    print 'domain:', full_domain
    print base_path, app_name
    print 'cookies: '
    pp.pprint(request.cookies)

    #TODO: add anonymous users
    user_token = request.cookies.get('user_token')
    app_token = request.cookies.get('app_token')
    
    if user_token and not app_token:
        # generate token
        user = mongokit.User.find_one({'token': user_token})
        app  = mongokit.Application.find_one({'id': app_name})
        if not app:
            print 'not an app'
            return abort(404)
        new_token = generate_token(user._id, app._id)
        token = mongokit.AppToken()
        token.update(dict(user=user, app=app, token=new_token))
        token.save()
        print 'setting cookies'
        response.set_cookie('app_token', value=new_token, domain=full_domain)

    #TODO: anonymous users
    if not user_token:
        response.set_cookie('user_token', value='TheUserToken', domain=full_domain)

    response.headers['X-Accel-Redirect'] = "/files/"+base_path
    return response


def generate_token(user_id, app_id):
    return sha256(
        str(datetime.utcnow()) +
        str(user_id) +
        str(app_id)  +
        str(urandom(12))
    ).hexdigest()


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



if __name__ == '__main__':
    app.config.from_object(TestConfig)
    app.run(debug=True, port=5001)

