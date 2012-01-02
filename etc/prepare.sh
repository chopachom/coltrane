#!/usr/bin/env sh

MYSQL_PASSWORD=$1
COLTRANE_PASSWORD=${2:-"C*#VS@fakFHvT&qfnsр]8"}  
COLTRANEDIR=~/repos/coltrane

mysql -uroot -p$MYSQL_PASSWORD -e "CREATE USER 'coltrane'@'localhost' IDENTIFIED BY '$COLTRANE_PASSWORD';"
mysql -uroot -p$MYSQL_PASSWORD -e "CREATE DATABASE coltrane;"
mysql -uroot -p$MYSQL_PASSWORD -e "GRANT SELECT,INSERT,UPDATE ON coltrane.* TO 'coltrane'@'localhost';"


. ~/.bashrc
mkvirtualenv coltrane
sudo ln -s /home/`whoami`/.virtualenvs /var/lib/venv

mkdir ~/web
sudo ln -s /home/`whoami`/web /web

mkdir /web/rest/
mkdir /web/hosting/
mkdir /web/website/