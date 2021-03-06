#!/bin/bash
cd ~
# Fresh installations of Ubuntu do not have a locale yet, and this will cause
# the Open edX installer scripts to fail, so we'll  set it now.
# For any input prompts that follow, you can select the default value.
# locale-gen sets the character set for terminal output.
sudo locale-gen en_GB en_GB.UTF-8
# With the locale set, we'll reconfigure the Ubuntu packages
# to use whatever character set you selected.
# dpkg-reconfigure locales
sudo dpkg --configure -a
# Update Ubuntu 20.04
sudo apt-get update
sudo apt-get upgrade -y

# Install open edX
wget https://raw.githubusercontent.com/BbrSofiane/edx.scripts/master/edx.platform-install.sh 
chmod +x edx.platform-install.sh
sudo nohup ./edx.platform-install.sh &