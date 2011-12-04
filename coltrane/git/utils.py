__author__ = 'qweqwe'

import sys


def die_gracefuly(message):
    """ Exit and print a message to a user """
    print >> sys.stderr, message
    sys.exit(1)

def print_err(message):
    """ Print a message to a user """
    print >> sys.stderr, message