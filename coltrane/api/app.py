# -*- coding: utf-8 -*-
__author__ = 'apetrovich'

import logging
import sys
from logging.handlers import RotatingFileHandler
from flask import Flask
from coltrane.api.config import DefaultConfig
from coltrane.api.lib.guard_manager import GuardManager
from coltrane.api.extensions import mongodb
from coltrane.api.extensions import guard
from coltrane.db.extension import db
from coltrane.api.rest import api_v1, converters


guard.manager = GuardManager

DEFAULT_APP_NAME = "coltrane"

DEFAULT_MODULES = (
    (api_v1, '/v1'),
)

DEFAULT_EXTENSIONS = (guard, mongodb, db)


def create_app(exts = None, modules=None, config=None, dict_config=None):
    app = Flask(__name__)
    
    # init url converters
    for key in converters.keys():
        app.url_map.converters[key] = converters[key]
        
    if not exts:
        exts = DEFAULT_EXTENSIONS
        
    if not modules:
        modules = DEFAULT_MODULES

    configure_app(app, config, dict_config)
    configure_extensions(app, exts)
    configure_modules(app, modules)
    configure_logging(app)

    return app


def configure_app(app, config, dict_config=None):
    app.config.from_object(DefaultConfig)

    if config is not None:
        app.config.from_object(config)

    if dict_config is not None:
        app.config.update(**dict_config)


def configure_modules(app, modules):
    for module, url_prefix in modules:
        app.register_blueprint(module, url_prefix=url_prefix)


def configure_extensions(app, exts):
    for ext in exts:
        ext.init_app(app)


def configure_logging(app):
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s '
                                  '[in %(pathname)s:%(lineno)d]')

    if app.debug or app.testing:
        stdout_handler = logging.StreamHandler(sys.__stdout__)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(formatter)
        app.logger.addHandler(stdout_handler)
        logging.getLogger('coltrane').addHandler(stdout_handler)
        return

    debug_log = app.config['DEBUG_LOG_FILE']
    debug_file_handler = RotatingFileHandler(debug_log, maxBytes=100000,
                                             backupCount=10)
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(formatter)
    app.logger.addHandler(debug_file_handler)

    error_log = app.config['ERROR_LOG_FILE']
    error_file_handler =  RotatingFileHandler(error_log, maxBytes=100000,
                                              backupCount=10)
    error_file_handler.setLevel(logging.WARNING)
    error_file_handler.setFormatter(formatter)
    app.logger.addHandler(error_file_handler)