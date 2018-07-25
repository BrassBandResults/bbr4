#!/bin/bash
sudo apt-get update
sudo apt-get upgrade

sudo apt-get install git -y

sudo addgroup ${username}
sudo adduser ${username} --ingroup ${username} --disabled-password --gecos ""
#sudo bash -c echo ${username}:${password} | chpasswd
sudo mkdir /home/${username}/.ssh
sudo cp ~/.ssh/authorized_keys /home/${username}/.ssh
sudo chown -R ${username}:${username} /home/${username}/.ssh

cd /home/${username}
sudo chown -R ${username}:${username} /home/${username}