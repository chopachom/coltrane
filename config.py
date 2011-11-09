# -*- coding: utf-8 -*-
__author__ = 'apetrovich'

class DefaultConfig(object):
    pass

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


class DebugConfig(object):
    DEBUG=True
    LOGGER_NAME='coltrane.api'
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = 27017
    MONGODB_DATABASE   ='test_db'
    MONGODB_SLAVE_OKAY = False
    MONGODB_USERNAME   = None
    MONGODB_PASSWORD   = None
    APP_DATABASE       = 'coltrane_test'
    USERS_COLLECTION   = 'users'
    APPS_COLLECTION    = 'apps'




