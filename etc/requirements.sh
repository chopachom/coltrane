#!/usr/bin/env sh

#install mysql
sudo apt-get -y install mysql-server mysql-client nginx uwsgi uwsgi-plugin-python supervisor python-pip

#install mongodb
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10
echo "deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen"| sudo tee -a /etc/apt/sources.list
sudo apt-get update
sudo apt-get -y install mongodb-10gen

sudo pip install virtualenvwrapper
echo -e "\nsource /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
