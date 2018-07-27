#!/bin/bash

# Build up the bbr user so that it can run the site.  This user cannot sudo.

chmod 600 .pgpass

echo '' >> ~/.bashrc
echo 'export WORKON_HOME=$HOME/.venv' >> ~/.bashrc
echo 'export PROJECT_HOME=$HOME' >> ~/.bashrc
echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc
source .bashrc

git clone https://github.com/BrassBandResults/bbr4.git

# create virtualenv
mkvirtualenv bbr4
cd ~/bbr4/web/site
pip install -r requirements.txt
