#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(url='mysql://root@127.0.0.1:3306/coltrane_test', debug='False', repository='migrate_repo')
