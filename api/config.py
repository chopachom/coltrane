# -*- coding: utf-8 -*-
__author__ = 'apetrovich'

import os

MYSQL_DEBUG_URI = os.environ.get('COLTRANE_MYSQL_DEBUG_URI') or \
                  'mysql://root@127.0.0.1:3306/coltrane'

class DefaultConfig(object):
    COOKIE_USER_AUTH_TOKEN = 'auth_token'
    COOKIE_APP_TOKEN       = 'app_token'


class TestConfig(object):
    TESTING            = True
    LOGGER_NAME        = 'coltrane.api'
    SQLALCHEMY_DATABASE_URI = MYSQL_DEBUG_URI
    MONGODB_HOST       = '127.0.0.1'
    MONGODB_PORT       = 27017
    MONGODB_DATABASE   ='coltrane_test'
    MONGODB_SLAVE_OKAY = False
    MONGODB_USERNAME   = None
    MONGODB_PASSWORD   = None
    APPDATA_COLLECTION = 'appdata'
    USERS_COLLECTION   = 'users'
    APPS_COLLECTION    = 'apps'


class DebugConfig(object):
    DEBUG              = True
    LOGGER_NAME        = 'coltrane.api'
    SQLALCHEMY_DATABASE_URI = MYSQL_DEBUG_URI
    MONGODB_HOST       = '127.0.0.1'
    MONGODB_PORT       = 27017
    MONGODB_DATABASE   ='coltrane_debug'
    MONGODB_SLAVE_OKAY = False
    MONGODB_USERNAME   = None
    MONGODB_PASSWORD   = None
    APPDATA_COLLECTION = 'appdata'
    USERS_COLLECTION   = 'users'
    APPS_COLLECTION    = 'apps'




