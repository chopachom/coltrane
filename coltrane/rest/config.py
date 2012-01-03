# -*- coding: utf-8 -*-
"""
    :Authors: - qweqwe
"""

from coltrane import config

class DefaultConfig(object):
    DEFAULT_QUERY_LIMIT = 1000
    LOGGER_NAME        ='coltrane.rest'
    SQLALCHEMY_DATABASE_URI = config.MYSQL_URI
    MONGODB_HOST       ='127.0.0.1'
    MONGODB_PORT       = 27017
    MONGODB_DATABASE   ='coltrane_test'
    MONGODB_SLAVE_OKAY = False
    MONGODB_USERNAME   = None
    MONGODB_PASSWORD   = None
    APPDATA_COLLECTION ='appdata'
    DEBUG_LOG              = '/web/rest/debug.log'
    ERROR_LOG              = '/web/rest/error.log'

class TestConfig(object):
    TESTING            = True
    SQLALCHEMY_DATABASE_URI = config.MYSQL_TEST_URI


class DebugConfig(object):
    DEBUG              = True
    SQLALCHEMY_DATABASE_URI = config.MYSQL_DEBUG_URI


