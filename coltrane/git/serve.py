__author__ = 'qweqwe'

import re
import sys
import os
import logging
import base64
import subprocess

import access
from errors import *
from utils import die_gracefuly


LOGR = logging.getLogger('gitward')

COMMANDS_READONLY = [
    'git-upload-pack',
    'git upload-pack',
]

COMMANDS_WRITE = [
    'git-receive-pack',
    'git receive-pack',
]


def parse_command(command):
    """ Parses received command and returns git verb and path
    """

    ARGUMENTS_RE = re.compile("^'/*(?P<path>[a-zA-Z0-9][a-zA-Z0-9@._-]*(/[a-zA-Z0-9][a-zA-Z0-9@._-]*)*)'$")

    is_valid = False
    for allowed_cmd in COMMANDS_READONLY + COMMANDS_WRITE:
        if command.startswith(allowed_cmd):
            is_valid = True

    if not is_valid:
        raise NotaGitCommandError(command)

    try:
        #split only first argument - the command itself
        verb, args = command.split(None, 1)
    except ValueError:
        # all known "git-foo" commands take one argument; improve
        # if/when needed
        raise UnknownCommandError(command)

    if verb == 'git':
        try:
            subverb, args = args.split(None, 1)
        except ValueError:
            # all known "git foo" commands take one argument; improve
            # if/when needed
            raise UnknownCommandError(command)
        verb = '{0} {0}'.format(verb, subverb)

    if verb not in COMMANDS_READONLY + COMMANDS_WRITE:
        raise NotaGitCommandError(command)

    match = ARGUMENTS_RE.match(args)
    if match is None:
        raise UnsafeArgumentsError(command, args)

    path = match.group('path')

    return verb, path


def get_ssh_command():
    orig_command = os.getenv('SSH_ORIGINAL_COMMAND')
    LOGR.debug('SSH_ORIGINAL_COMMAND: {0}'.format(orig_command))

    # if user tries to use this ssh to get shell access
    if not orig_command:
        # random error code:
        code = os.urandom(12)
        #TODO: raise error
        LOGR.error('NO COMMAND SPECIFIED BY USER {0}'.format(get_user_id()))
        die_gracefuly('Sorry, but there\'s no shell access available.\n')

    return orig_command


def get_user_id():
    #: user id that was passed as command line argument in authorized_keys
    user_id = None

    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        LOGR.debug('USER_ID: {0}'.format(user_id))

    if not user_id:
        # TODO: raise error
        # we can use generated code to search in the logs later
        code = base64.urlsafe_b64encode(os.urandom(9))
        print >> sys.stderr, ('Internal error occurred, please, '
                              'contact us and specify this code: {0}')\
                             .format(code)
        LOGR.critical('INTERNAL ERROR - NO USER_ID; CODE: {0} SSH_CLIENT: {1}'.format(
            code, os.getenv('SSH_CLIENT')
        ))
        sys.exit(1)

    return user_id


def serve():
    """ Handles each
    """
    #: The original ssh command
    orig_command = get_ssh_command()
    #: user id that was passed as command line argument in authorized_keys
    user_id = get_user_id()
    verb, virt_path = parse_command(orig_command)
    real_path = access.get_real_path(user_id, virt_path)

    LOGR.debug('GOT VERB: {0}'.format(verb))
    LOGR.debug('GOT PATH: {0}'.format(real_path))

    subprocess.Popen([verb, real_path])
