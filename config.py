__author__ = 'qweqwe'

import os

COOKIE_USER_AUTH_TOKEN = 'auth_token'
COOKIE_APP_TOKEN       = 'app_token'

MYSQL_DEBUG_URI = os.environ.get('COLTRANE_MYSQL_DEBUG_URI') or \
                  'mysql://root@127.0.0.1:3306/coltrane'
MYSQL_TEST_URI  = os.environ.get('COLTRANE_MYSQL_TEST_URI') or \
                  'mysql://root@127.0.0.1:3306/coltrane_test'

  