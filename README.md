# Reefberry Pi

Reefberry Pi is an aquarium controller built with a Raspberry Pi 
microcontroller

# Prerequisites
sudo apt install python3-pip  
pip3 install colorama  
pip3 install pika  
pip3 install numpy --no-binary :all:  
<br />
# Config
cd ./ReefberryPi  
mkdir logs  
<br />
nano RBP_server.py  
ctrl+shift+_ 58  
add  
	credentials = pika.PlainCredentials('user','pass')  
then add the credentials variable to the self.connection1 and self.conenction2 lines  
format is host,port,vhost,credentials  
vhost is '/' usually  
<br />
credentials also need added to line 200 and connection1 2 and 3 need rabbit host set to actual hostname if not local
