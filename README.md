# Reefberry Pi

Reefberry Pi is an aquarium controller built with a Raspberry Pi 
single board computer

# Prerequisites
RaspberryPi OS (64-bit) \
Influx Database 2.0 \
MySql or MariaDB \
Python 3 \
Apache Web Server 

# Configuration
If installing on Raspberry Pi 3B you should increase the amount of swap space since RPi 3B only has 1GB of memory.  Raspberry Pi 4 and later should have enough RAM to run everything smoothly so this step is unecessary.

## Increasing Swap Space (for Raspberry Pi 3B)
(refer to https://pimylifeup.com/raspberry-pi-swap-file/)

```
sudo dphys-swapfile swapoff 
sudo nano /etc/dphys-swapfile 
```
Find:  
```
CONF_SWAPSIZE=100 
```
Change value to this and save:
```
CONF_SWAPSIZE=1024 
```

Activate the new swap space by executing following commands:
```
sudo dphys-swapfile setup 
sudo dphys-swapfile swapon 
sudo reboot 
```

Verify with: 
```
free -m 
```

## Installation of MariaDB
(refer to https://pimylifeup.com/raspberry-pi-mysql/ )

```
sudo apt install mariadb-server
sudo mysql_secure_installation
Set password to ‘raspberry’
sudo mysql -u root -p
```

To allow remote access: \
(refer to
https://webdock.io/en/docs/how-guides/database-guides/how-enable-remote-access-your-mariadbmysql-database )
```
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```
Set to (default was 127.0.0.1): 
```
bind-address = 0.0.0.0 
```
restart database service:
```
sudo systemctl restart mariadb
```
To grant access to all db for root user from all remote IP’s: \
(run this command on MariaDB command line)
```
GRANT ALL ON *.* to 'root'@'%' IDENTIFIED BY ‘raspberry’ WITH GRANT OPTION;
```

## Installation of Influx Database
(refer to https://pimylifeup.com/raspberry-pi-influxdb/)

Add InfluxDB repository:
```
curl https://repos.influxdata.com/influxdata-archive.key | gpg --dearmor | sudo tee /usr/share/keyrings/influxdb-archive-keyring.gpg > /dev/null
```
```
echo "deb [signed-by=/usr/share/keyrings/influxdb-archive-keyring.gpg] https://repos.influxdata.com/debian stable main" | sudo tee /etc/apt/sources.list.d/influxdb.list
```
```
sudo apt update
sudo apt install influxdb2
```
Make it start on boot: 
```
sudo systemctl unmask influxdb
sudo systemctl enable influxdb
sudo systemctl start influxdb
```
Test by going to:
```
http://<serverip>:8086
```

## Install Apache Webserver
(refer to https://pimylifeup.com/raspberry-pi-apache/)
```
sudo apt install apache2 -y
```
Give privileges to user pi:
```
sudo usermod -a -G www-data pi
sudo chown -R -f www-data:www-data /var/www/html
```
```
sudo reboot 
```
Test apache is running by going to:
```
http://<servername>
```