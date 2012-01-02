# -*- coding: utf-8 -*-
"""
    :Authors: - qweqwe
"""

from fabric.api import *
from fabric.contrib.files import exists

repo_host     = '192.168.42.101'
remote_repo   = '~/repos/coltrane.git'
remote_webdir = '~/web/app'
uwsgi_cfgs    = {
    'rest.xml'   :'/web/rest/config.xml',
    'hosting.xml':'/web/hosting/config.xml',
    'website.xml':'/web/website/config.xml'
}


env.hosts     = ['192.168.42.101']
env.key_filename = '/Users/qweqwe/.ssh/git_rsa'

def push(force):
    local("git push {}:{} master {}".format(repo_host, remote_repo, force))

def deploy(force=False):
    f = "-f" if force else ""
    push(f)
    if not exists(remote_webdir+'/.git'):
        run('mkdir -p {0}'.format(remote_webdir))
        with cd(remote_webdir):
            run('git init')
            run('git remote add origin {}'.format(remote_repo))
    with cd(remote_webdir):
        if force:
            run('git fetch --all')
            run("git reset --hard origin/master")
        else:
            run('git pull origin master')
    with cd(remote_repo):
        run('pwd')
        #using xargs to prevent grep for returning 1 error code when nothing have been found
        revno = run("git tag|grep -E '^r[0-9]+'|sort|tail -1|grep -oE '[0-9]+'|xargs -i echo {}")
        new_revno = int(revno) + 1 if revno else 0
        run('git tag r{}'.format(new_revno))
    for config in uwsgi_cfgs:
        run('mkdir -p {}'.format(uwsgi_cfgs[config][:-11]))
        #remote_webdir[2:] = '~/web/app' -> 'web/app'
        cmd = 'ln -sf /home/`whoami`/{}/etc/uwsgi/{} {}'.format(
            remote_webdir[2:], config, uwsgi_cfgs[config]
        )
        run(cmd)
