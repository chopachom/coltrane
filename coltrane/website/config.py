# -*- coding: utf-8 -*-
"""
    :Authors: - qweqwe
"""

from coltrane.config import TestConfig, DebugConfig, DefaultConfig as dc

#TODO: replace all literal values with values from environment variables

class DefaultConfig(dc):
    SECRET_KEY             = 'A0Zr98˙™£ª¶3yX R~XHH!jmMPC.s39 LWfk wN]LWX/,?RT'
    BCRYPT_LOG_ROUNDS      = 8
    FACEBOOK_APP_ID        = '183128768399686'
    FACEBOOK_APP_SECRET    = 'c292a870251760f1bf0b7ea61d00f2a4'
    TWITTER_CONSUMER_KEY   = 'jdWkuTLvjvhFOyCkXr834w'
    TWITTER_CONSUMER_SECRET= 'tNDRnCVbfjNZeHI88iSXQa9NAEQ4vLH9VQCqq1rcp8'
    DEBUG_LOG              = '/web/website/debug.log'
    ERROR_LOG              = '/web/website/error.log'