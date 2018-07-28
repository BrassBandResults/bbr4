#!/bin/bash

# Build the initial machine setup using the admin user.
# This user can sudo, others cannot.

# Bring machine up to date
sudo apt-get update
sudo apt-get upgrade -y

# install required software as root
sudo apt-get install git python3-pip nginx -y
export VIRTUALENVWRAPPER_PYTHON=`which python3`
sudo pip3 install -U pip
sudo pip3 install -U virtualenv virtualenvwrapper


# sort out virtualenv settings
echo '' >> ~/.profile
echo 'export WORKON_HOME=$HOME/.venv' >> ~/.profile
echo 'export PROJECT_HOME=$HOME' >> ~/.profile
echo 'export VIRTUALENVWRAPPER_PYTHON=`which python3`' >> ~/.profile
echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.profile

# Create bbr user and group, and copy in certificate and .pgpass
sudo addgroup ${username}
sudo adduser ${username} --ingroup ${username} --disabled-password --gecos ""
#sudo bash -c echo ${username}:${password} | chpasswd
sudo mkdir /home/${username}/.ssh
sudo cp ~/.ssh/authorized_keys /home/${username}/.ssh
sudo chown -R ${username}:${username} /home/${username}/.ssh

# Make sure copied in files on bbr user are owned by bbr:bbr
cd /home/${username}
sudo chown -R ${username}:${username} /home/${username}