# -*- coding: utf-8 -*-

class DefaultConfig(object):
    SECRET_KEY        = 'A0Zr98˙™£ª¶3yX R~XHH!jmMPC.s39 LWfk wN]LWX/,?RT'
    BCRYPT_LOG_ROUNDS = 8
    BITCOIN_USER      = 'qweqwe'
    BITCOIN_PASSWORD  = 'qweqwe'
    BITCOIN_PORT      = 19332
#    DEBUG_LOG         = '/web/logs/bitstant/debug.log'
#    ERROR_LOG         = '/web/logs/bitstant/error.log'


class TestConfig(object):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:qweqwe@127.0.0.1:3306/bitstant'
