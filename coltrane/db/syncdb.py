# -*- coding: utf-8 -*-
"""
    :Authors: - qweqwe
"""

from migrate.versioning import api as versioning_api
from migrate import exceptions as versioning_exceptions
import os

from coltrane.config import MYSQL_URI

def db_sync(version=None):
    db_version()
    repo_path = _find_migrate_repo()
    return versioning_api.upgrade(MYSQL_URI, repo_path, version)

def db_version():
    repo_path = _find_migrate_repo()
    try:
        return versioning_api.db_version(MYSQL_URI, repo_path)
    except versioning_exceptions.DatabaseNotControlledError:
        return db_version_control(0)

def db_version_control(version=None):
    repo_path = _find_migrate_repo()
    versioning_api.version_control(MYSQL_URI, repo_path, version)
    return version

def _find_migrate_repo():
    """Get the path for the migrate repository."""
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        'migrate_repo')
    assert os.path.exists(path)
    return path

db_sync()