#!/bin/bash

# Build the initial machine setup using the admin user.
# This user can sudo, others cannot.

# Bring machine up to date
sudo apt-get update
sudo apt-get upgrade -y

# install required software as root
sudo apt-get install git python3-pip nginx postgresql-client -y
export VIRTUALENVWRAPPER_PYTHON=`which python3`
sudo pip3 install -U pip
sudo pip3 install -U virtualenv virtualenvwrapper

# install geodjango libraries
sudo apt-get install binutils libproj-dev gdal-bin -y

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

# create log file folders
sudo mkdir /var/log/bbr
sudo chmod a+rwx /var/log/bbr

# run bbr gunicorn server
sudo cp ~/init-gu-bbr /etc/init.d/gu-bbr
sudo chmod a+x /etc/init.d/gu-bbr
sudo chown root:root /etc/init.d/gu-bbr
#sudo /etc/init.d/gu-bbr start
#sudo systemctl enable gu-bbr

# configure nginx
sudo mkdir /var/log/bbr
sudo cp ~/nginx-bbr4 /etc/nginx/sites-available/bbr4
sudo ln -s /etc/nginx/sites-available/bbr4 /etc/nginx/sites-enabled/bbr4
sudo /etc/init.d/nginx restart
