# -*- coding: utf-8 -*-
import logging
from api import api
from flask import Flask
from config import DefaultConfig
from extensions import crud
from logging.handlers import RotatingFileHandler


DEFAULT_APP_NAME = "coltrane"

DEFAULT_MODULES = (
    (api, ""),
)


def create_app(config=None, modules=None, dict_config=None):
    app = Flask(__name__)

    if not modules: modules = DEFAULT_MODULES

    configure_app(app, config, dict_config)
    configure_extensions(app)
    #configure_modules(app, modules)
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


def configure_extensions(app):
    crud.init_app(app)


def configure_logging(app):
    if app.debug or app.testing:
        return

    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')

    debug_log = app.config['DEBUG_LOG']
    debug_file_handler = RotatingFileHandler(
        debug_log, maxBytes=100000, backupCount=10)
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(formatter)
    app.logger.addHandler(debug_file_handler)


    error_log = app.config['ERROR_LOG']
    error_file_handler =  RotatingFileHandler(
        error_log, maxBytes=100000, backupCount=10)
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    app.logger.addHandler(error_file_handler)