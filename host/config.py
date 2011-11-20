# -*- coding: utf-8 -*-
__author__ = 'apetrovich'

class DefaultConfig(object):
    SECRET_KEY             = 'A0Zr98˙™£ª¶3yX R~XHH!jmMPC.s39 LWfk wN]LWX/,?RT'
    DEBUG_LOG_FILE         = '/web/logs/shareall/debug.log'
    ERROR_LOG_FILE         = '/web/logs/shareall/error.log'


class TestConfig(object):
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = 27017
    MONGODB_DATABASE   ='test_db'
    MONGODB_SLAVE_OKAY = False
    MONGODB_USERNAME   = None
    MONGODB_PASSWORD   = None
    APPDATA_COLLECTION = 'appdata'
    USERS_COLLECTION   = 'users'
    APPS_COLLECTION    = 'apps'



