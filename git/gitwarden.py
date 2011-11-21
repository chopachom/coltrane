#!/usr/bin/env python
__author__ = 'qweqwe'

import os
from serve import serve
import logging
from logging.handlers import RotatingFileHandler

from errors import *
from utils import die_gracefuly


LOGR = logging.getLogger('gitward')
LOGPATH = os.path.join(os.path.expanduser('~'), 'log_event.log')
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
handler = RotatingFileHandler(LOGPATH)
handler.setFormatter(formatter)
LOGR.addHandler(handler)
LOGR.setLevel(logging.DEBUG)
LOGR.debug('------------------------------------------')


if __name__ == '__main__':
# if user send not a git command
    try:
        serve()
    except InvalidCommandError as e:
        LOGR.error('DISCARDING COMMAND: {0}'.format(e.command))
        LOGR.error('EXCEPTION MESSAGE: {0}'.format(e.formatted_message))
        die_gracefuly('Only git-upload-pack and git-receive-pack are allowed')
    except InvalidCommandArgumentError as e:
        LOGR.error('DISCARDING COMMAND: {0}'.format(e.command))
        LOGR.error('EXCEPTION MESSAGE: {0}'.format(e.formatted_message))
        die_gracefuly('Invalid command arguments')
    except RepoAccessDeniedError as e:
        LOGR.error("PATH DOESN'T EXIST: {0}".format(e.path))
        die_gracefuly("You dont have access to this repository")

