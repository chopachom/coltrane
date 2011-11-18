# -*- coding: utf-8 -*-
import os

MYSQL_DEBUG_URI = os.environ['COLTRANE_MYSQL_DEBUG_URI'] or \
                  'mysql://root:ololo@127.0.0.1:3306/coltrane'


class DefaultConfig(object):
    SECRET_KEY        = 'A0Zr98˙™£ª¶3yX R~XHH!jmMPC.s39 LWfk wN]LWX/,?RT'
    BCRYPT_LOG_ROUNDS = 8
#    DEBUG_LOG         = '/web/logs/coltrane/debug.log'
#    ERROR_LOG         = '/web/logs/coltrane/error.log'


class TestConfig(object):
    SQLALCHEMY_DATABASE_URI = MYSQL_DEBUG_URI


class DebugConfig(object):
    DEBUG = True
    SECRET_KEY = 'topsy kretts'
    SQLALCHEMY_DATABASE_URI = MYSQL_DEBUG_URI
    SQLALCHEMY_ECHO = True
