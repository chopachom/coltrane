#!/usr/bin/env python
from migrate.versioning.shell import main
from coltrane import config

if __name__ == '__main__':
    main(url=config.MYSQL_TEST_URI, debug='True', repository='migrate_repo')
