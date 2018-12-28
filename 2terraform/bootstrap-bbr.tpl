#!/bin/bash

# Build up the bbr user so that it can run the site.  This user cannot sudo.

chmod 600 .pgpass

git clone https://github.com/BrassBandResults/bbr4.git

# sort out virtualenv settings
export VIRTUALENVWRAPPER_PYTHON=`which python3`

echo '' >> ~/.profile
echo 'export WORKON_HOME=$HOME/.venv' >> ~/.profile
echo 'export PROJECT_HOME=$HOME' >> ~/.profile
echo 'export VIRTUALENVWRAPPER_PYTHON=`which python3`' >> ~/.profile
echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.profile

source ~/.profile

# create virtualenv
mkvirtualenv bbr4 --python=`which python3`
cd ~/bbr4/web/site
pip3 install -r requirements.txt
