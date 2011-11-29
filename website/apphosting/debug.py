# -*- coding: utf-8 -*-
__author__ = 'qweqwe'

from host.app import create_app
from host.config import TestConfig

if __name__ == '__main__':
    app = create_app(dict_config=dict(
        DEBUG=True
    ), config=TestConfig)
    app.run()