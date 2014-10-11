#!/bin/bash
#this is script which will prepare your RPi to work with module via I2C bus and also it will set up other things like web server, cron table, etc.



echo '# blacklist spi and i2c by default (many users dont need them)' > /etc/modprobe.d/raspi-blacklist.conf
echo 'blacklist spi-bcm2708' >> /etc/modprobe.d/raspi-blacklist.conf
echo 'i2c-dev' >> /etc/modules

sudo apt-get update
sudo apt-get install i2c-tool

(sudo crontab -l; echo "@reboot sleep 10 &&/home/pi/.run &" ) | sudo crontab

cp ./run ~/.run

reboot
