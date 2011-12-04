# -*- coding: utf-8 -*-
__author__ = 'qweqwe'

from coltrane.apphosting.app import app
from coltrane.config import TestConfig

if __name__ == '__main__':
    app.config.from_object(TestConfig)
    app.run()