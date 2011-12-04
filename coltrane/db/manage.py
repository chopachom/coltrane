#!/usr/bin/env python
from migrate.versioning.shell import main
from coltrane import config

if __name__ == '__main__':
    main(url=config.MYSQL_DEBUG_URI, debug='False', repository='migrate_repo')
