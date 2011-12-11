__author__ = 'qweqwe'

import os

COOKIE_USER_AUTH_TOKEN = 'auth_token'
COOKIE_APP_TOKEN       = 'app_token'
COOKIE_ANONYMOUS_TOKEN = 'anonymous'

MYSQL_DEBUG_URI = os.environ.get('COLTRANE_MYSQL_DEBUG_URI') or \
                  'mysql://root@127.0.0.1:3306/coltrane'
MYSQL_TEST_URI  = os.environ.get('COLTRANE_MYSQL_TEST_URI') or \
                  'mysql://root@127.0.0.1:3306/coltrane_test'
    

class TestConfig(object):
    SQLALCHEMY_DATABASE_URI = MYSQL_TEST_URI


class DebugConfig(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = MYSQL_DEBUG_URI
    SQLALCHEMY_ECHO = True