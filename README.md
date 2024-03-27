# Reefberry Pi

![dashboard](./docs/assets/Dashboard-1.png)

Reefberry Pi is an aquarium controller built with a Raspberry Pi 
single board computer.  I started this project to learn new skills and see what I could accomplish with this device and off the shelf components.  It is a work in progress and I have lots of ideas for things I'd like to implement.  Fell free to follow along on this journey! 

# Features

* 4 ds18b20 submersible temperature probes 
* 1 DHT-22 temerature and humidity sensor
* 8 relays to control outlets
* 8 channel mcp3008 analog to digital converter (for things like PH probes)
* different outlet profiles (Always, Return Pump, Skimmer, Light, PH, Heater)
* configurable dashboard
* data logging and graphical displays
* ability to enable or disbale features as necessary
* login screen
* 4 configurable feed modes
* ability to switch between Celcius or Fahrenheit

# Prerequisites
Raspberry Pi (tested on 3B) \
RaspberryPi OS (64-bit) \
Influx Database 2.0 \
MariaDB \
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
# Update Raspberry Pi OS
It is good practice to update Raspberry Pi OS to ensure latest patches are installed

``` 
sudo apt update
sudo apt upgrade
```

## Installation of MariaDB
(refer to https://pimylifeup.com/raspberry-pi-mysql/ )

```
sudo apt install mariadb-server
sudo mysql_secure_installation
```
when prompted for password, just hit **ENTER** (we will add password later): 
```
Enter current password for root (enter for none): 
```
when prompted for unix_socket authentication, press "**n**"

```
Switch to unix_socket authentication [Y/n] n
```
When prompted to change root password, press "**y**"
```
Change the root password? [Y/n] y
```

Set password to ‘**reefberry**’
```
Change the root password? [Y/n] y
New password: 
Re-enter new password: 
Password updated successfully!
```
When prompted to remove anopnymous users, press "**y**"

```
Remove anonymous users? [Y/n] y
```

When prompted to disallow root login remotely, press "**y**" (we will add a remote user later)

```
Disallow root login remotely? [Y/n] y
```
When prompted to remove the test database, press "**y**"
```
Remove test database and access to it? [Y/n] y
```
When prompted to reload privlege tables, press "**y**"

```
Reload privilege tables now? [Y/n] y
```
Next we will allow **remote access** to  the database \
(this is helpful while configuring and debugging things remotely): \
(refer to
https://webdock.io/en/docs/how-guides/database-guides/how-enable-remote-access-your-mariadbmysql-database )
```
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```
Change the value of bind-address to **0.0.0.0** then save changes (default was 127.0.0.1): 
```
bind-address = 0.0.0.0 
```


Now login to the database command line as user "root" (use the password we set earlier)
```
sudo mysql -u root -p
```
We will create a new account fro the aquarium controller and grant full access to DB.  This account will be able to login remotely from all IPs: 

(run this command on MariaDB command line)
```
GRANT ALL ON *.* to 'pi'@'%' IDENTIFIED BY 'reefberry' WITH GRANT OPTION;
```

restart database service:
```
sudo systemctl restart mariadb
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