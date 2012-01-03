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
nginx_cfgs    = {
    'website.cfg' : 'website',
    'rest.cfg'    : 'rest',
    'hosting.cfg' : 'hosting'
}

supervisor_cfgs = [
    'hosting.conf',
    'rest.conf',
    'website.conf'
]

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
        #TODO: add new revision only if source code have been changed
        #using xargs to prevent grep for returning 1 error code when nothing have been found
        revno = run("git tag|grep -E '^r[0-9]+'|grep -oE '[0-9]+'|sort -n|tail -1|xargs -i echo {}")
        new_revno = int(revno) + 1 if revno else 0
        run('git tag r{}'.format(new_revno))

    with prefix('workon coltrane'):
        run('pip install -r '+remote_webdir+'/etc/requirements.txt')

    for config in uwsgi_cfgs:
        if not exists(uwsgi_cfgs[config]):
            #uwsgi_cfgs[config][:-11] = /web/hosting/config.xml -> /web/hosting
            run('mkdir -p {}'.format(uwsgi_cfgs[config][:-11]))
            cmd = 'ln -sf /home/`whoami`/{}/etc/uwsgi/{} {}'.format(
                #remote_webdir[2:] = '~/web/app' -> 'web/app'
                remote_webdir[2:], config, uwsgi_cfgs[config]
            )
            run(cmd)
        run('touch {}/reloader'.format(uwsgi_cfgs[config][:-11]))

    for config in nginx_cfgs:
        if not exists('/etc/nginx/sites-available/' + nginx_cfgs[config]):
            user = run('whoami')
            sudo('ln -sf /home/{}/{}/etc/nginx/{} /etc/nginx/sites-available/{}'.format(
                #remote_webdir[2:] = '~/web/app' -> 'web/app'
                user, remote_webdir[2:], config, nginx_cfgs[config]
            ))
            sudo('ln -sf /etc/nginx/sites-available/{} /etc/nginx/sites-enabled/'.format(
                nginx_cfgs[config]
            ))

    for config in supervisor_cfgs:
        user = run('whoami')
        sudo('ln -sf /home/{}/{}/etc/supervisor/{} /etc/supervisor/conf.d/'.format(
            user, remote_webdir[2:], config
        ))

    #TODO: gracefuly reload nginx and supervisor configuration
    sudo('service supervisor restart')
    sudo('service nginx reload')

