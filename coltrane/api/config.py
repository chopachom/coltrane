# -*- coding: utf-8 -*-
__author__ = 'apetrovich'

from coltrane import config

class DefaultConfig(object):
    DEFAULT_QUERY_LIMIT = 1000


class TestConfig(object):
    TESTING            = True
    LOGGER_NAME        ='coltrane.api'
    SQLALCHEMY_DATABASE_URI = config.MYSQL_TEST_URI
    MONGODB_HOST       ='127.0.0.1'
    MONGODB_PORT       = 27017
    MONGODB_DATABASE   ='coltrane_test'
    MONGODB_SLAVE_OKAY = False
    MONGODB_USERNAME   = None
    MONGODB_PASSWORD   = None
    APPDATA_COLLECTION ='appdata'
    USERS_COLLECTION   ='users'
    APPS_COLLECTION    ='apps'


class DebugConfig(object):
    DEBUG              = True
    LOGGER_NAME        ='coltrane.api'
    SQLALCHEMY_DATABASE_URI = config.MYSQL_DEBUG_URI
    MONGODB_HOST       ='127.0.0.1'
    MONGODB_PORT       = 27017
    MONGODB_DATABASE   ='coltrane_debug'
    MONGODB_SLAVE_OKAY = False
    MONGODB_USERNAME   = None
    MONGODB_PASSWORD   = None
    APPDATA_COLLECTION ='appdata'




