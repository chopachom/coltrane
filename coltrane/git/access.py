__author__ = 'qweqwe'

import os, errno, subprocess
from fnmatch import fnmatch
import logging

from errors import *
import user


BASE_DIR  = os.path.expanduser('~')
REPOS_DIR = os.path.join(BASE_DIR, 'repositories')
LOGR      = logging.getLogger('gitward')


def get_real_path(user_id, path):
    """ Given virtual path (e.g. user/repo.git), returns internal absolute
        path for the repo (e.g. /home/git/repos/user/repo.git
    """
    return path_accessible(user_id, path)


def path_accessible(user_id, path):
    """ Return True if the given user_id has access to the given path.
        Raises RepoAccessDeniedError if path doesn't exists and user have not access
    """
    real_path =  os.path.join(REPOS_DIR, path)
    if user.has_repo(user_id, path):
        if not repo_exists(real_path):
            # Lazy repo initialization
            init_repo(real_path)
    else:
        raise RepoAccessDeniedError(real_path)
    return real_path


def repo_exists(real_path):
   return os.path.exists(os.path.join(real_path, '.git'))


def init_repo(real_path):
    _mkdir_p(real_path)
    git_init = subprocess.Popen(['git', 'init', '--bare', real_path],
                                 stderr=subprocess.STDOUT,
                                 stdout = subprocess.PIPE)
    # wait for repo to create
    out, err = git_init.communicate()
    LOGR.info('CREATED REPO, PATH: {0}'.format(real_path))
    LOGR.debug('STDOUT:\n{0}'.format(out))
    LOGR.debug('STDERR:\n{0}'.format(err))


def _mkdir_p(path):
    """ Same as mkdir -p """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise

