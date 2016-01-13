#!/bin/bash

apt-get install build-essential -y
apt-get install libssl-dev -y

wget https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz
tar xvzf Python-2.7.10.tgz
cd Python-2.7.10
./configure
make && make install
cd ..
rm -rf Python-2.7.10 Python-2.7.10.tgz
tar xvzf lib/setuptools-18.5.tar.gz 
cd setuptools-18.5
python setup.py install
cd ..
rm -rf setuptools-18.5
tar xvzf lib/pip-7.1.2.tar.gz 
cd pip-7.1.2
python setup.py install
cd ..
rm -rf pip-7.1.2

apt-get install libfreetype* -y
apt-get install libpng* -y
apt-get install sysstat -y
apt-get install libmysqld-dev -y
apt-get install zip -y
pip2.7 install virtualenv
pip2.7 install -r requirements.txt
