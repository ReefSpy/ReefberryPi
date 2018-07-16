##############################################################################
# RBP_probes.py
#
# this module will pull data from the various input probes and record data
# to the log files
#
# Written by ReefSpy for the ReefBerry Pi, (c) 2018
# www.youtube.com/reefspy
##############################################################################

from datetime import datetime
from colorama import Fore, Back, Style
import time
import RPi.GPIO as GPIO
import numpy
import ds18b20
import dht11
import mcp3008
import GPIO_config
import ph_sensor as ph
import configparser
import RBP_commons

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()


channel.queue_declare(queue='hello' )

channel.basic_publish(exchange='',
                      routing_key='hello',
                      properties=pika.BasicProperties(
                      expiration='10000'),
                      body='Hello World again!')

#connection.close()


# initialize config file
config = configparser.ConfigParser()
config.read('ReefberryPi.ini')
currentStateFile = 'RBP_currentstate.ini'
curstate = configparser.ConfigParser()
curstate.read(currentStateFile)

# read in the preferences
ph_numsamples = int(config['ph']['ph_numsamples']) # how many samples to collect before averaging
ph_SamplingInterval = int(config['ph']['ph_SamplingInterval']) # milliseconds
ph_Sigma = int(config['ph']['ph_Sigma']) # how many standard deviations to clean up outliers
ph_LogInterval = int(config['ph']['ph_LogInterval']) # milliseconds
dht11_SamplingInterval = int(config['dht11']['dht11_SamplingInterval']) # milliseconds
dht11_LogInterval = int(config['dht11']['dht11_LogInterval']) # milliseconds
ds18b20_SamplingInterval = int(config['ds18b20']['ds18b20_SamplingInterval']) # milliseconds
ds18b20_LogInterval = int(config['ds18b20']['ds18b20_LogInterval']) # milliseconds


# set up the GPIO
GPIO_config.initGPIO()

# dht11 temperature and humidity sensor
dht_sensor = dht11.DHT11(pin=GPIO_config.dht11)

# list to hold the raw ph data
ph_dvlist = []             

# give these an initial value in case we fail to get a valid reading it will just report 0
temp_f, temp_c = -1, -1

# need the initial probe time seed to compare our sampling intervals against
ph_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
ph_LastLogTime = int(round(time.time()*1000)) #convert time to milliseconds
dht11_LastLogTime = int(round(time.time()*1000)) #convert time to milliseconds
dht11_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
ds18b20_LastLogTime = int(round(time.time()*1000)) #convert time to milliseconds
ds18b20_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds

def writeCurrentState(section, key, value):
    curstate[section][key] = str(value)
    with open(currentStateFile,'w') as configfile:
        curstate.write(configfile)


while True:
    ##########################################################################################
    # read ph probe
    #
    # this probe is suseptable to noise and interference, we will take a suffiently large data
    # set and filter out the bad data, or outliers so we can get a better data point
    ##########################################################################################
    # only read the ph data at every ph_SamplingInterval (ie: 500ms or 1000ms)
    if (int(round(time.time()*1000)) - ph_SamplingTimeSeed) > ph_SamplingInterval:
        # read the analog pin
        ph_dv = mcp3008.readadc(GPIO_config.ph_adc, GPIO_config.SPICLK, GPIO_config.SPIMOSI,
                                 GPIO_config.SPIMISO, GPIO_config.SPICS)
        ph_dvlist.append(ph_dv)
        #print (len(ph_ListCounts),":", ph_dv)

        # once we hit our desired sample size of ph_numsamples (ie: 120)
        # then calculate the average value
        if len(ph_dvlist) >= ph_numsamples:
            # The ph probe may pick up noise and read very high or
            # very low values that we know are not good values. We are going to use numpy
            # to calculate the standard deviation and remove the outlying data that is
            # ph_Sigma standard deviations away from the mean.  This way these outliers
            # do not affect our ph results
            ph_FilteredCounts = numpy.array(ph_dvlist)
            ph_FilteredMean = numpy.mean(ph_FilteredCounts, axis=0)
            ph_FlteredSD = numpy.std(ph_FilteredCounts, axis=0)
            ph_dvlistfiltered = [x for x in ph_FilteredCounts if
                                    (x > ph_FilteredMean - ph_Sigma * ph_FlteredSD)]
            ph_dvlistfiltered = [x for x in ph_dvlistfiltered if
                                    (x < ph_FilteredMean + ph_Sigma * ph_FlteredSD)]
            
            # calculate the average of our filtered list
            try:
                ph_AvgCountsFiltered = int(sum(ph_dvlistfiltered)/len(ph_dvlistfiltered))
            except:
                ph_AvgCountsFiltered = 1  # need to revisit this error handling. Exception thrown when all
                                          # values were 1023
                print("Error collecting data")
                      
            #convert digital value to ph
            ph_AvgFiltered = ph.dv2ph(ph_AvgCountsFiltered)

            # if enough time has passed (ph_LogInterval) then log the data to file
            # otherwise just print it to console
            timestamp = datetime.now()
            if (int(round(time.time()*1000)) - ph_LastLogTime) > ph_LogInterval:
                RBP_commons.logprobedata(config['logs']['ph_log_prefix'], "{:.2f}".format(ph_AvgFiltered))
                print(timestamp.strftime(Fore.CYAN + Style.BRIGHT + "%Y-%m-%d %H:%M:%S") + " ***Logged*** pH = "
                      + "{:.2f}".format(ph_AvgFiltered) + Style.RESET_ALL)
                ph_LastLogTime = int(round(time.time()*1000))
            else:
                print(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " pH = "
                      + "{:.2f}".format(ph_AvgFiltered))
                writeCurrentState('probes','ph', str("{:.2f}".format(ph_AvgFiltered)))

            # clear the list so we can populate it with new data for the next data set
            ph_dvlist.clear()
            # record the new sampling time
            ph_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds

    ##########################################################################################
    # read dht11 temperature and humidity sensor
    #
    # these sensors are slow to refresh and should not be read more
    # than once every second or two (ie: dht_SamplingInterval = 3000ms or 5000ms)
    ##########################################################################################
    if (int(round(time.time()*1000)) - dht11_SamplingTimeSeed) > dht11_SamplingInterval:
        # let's read the dht11 temp and humidity data
        result = dht_sensor.read()
        if result.is_valid():
            #print("Last valid input: " + str(datetiml;./e.datetime.now()))
            #print("Temperature: %.1f C" % result.temperature)
            temp_f = result.temperature * 9.0 / 5.0 + 32.0
            hum = result.humidity
            timestamp = datetime.now()
            if (int(round(time.time()*1000)) - dht11_LastLogTime) > dht11_LogInterval:
                RBP_commons.logprobedata(config['logs']['extemp1_log_prefix'], "{:.1f}".format(temp_f))
                RBP_commons.logprobedata(config['logs']['humidity_log_prefix'], "{:.0f}".format(hum))
                print(timestamp.strftime(Fore.CYAN + Style.BRIGHT + "%Y-%m-%d %H:%M:%S") + " ***Logged*** External Temperature: %.1f F" % temp_f + Style.RESET_ALL)
                print(timestamp.strftime(Fore.CYAN + Style.BRIGHT + "%Y-%m-%d %H:%M:%S") + " ***Logged*** Humidity: %d %%" % hum + Style.RESET_ALL)
                dht11_LastLogTime = int(round(time.time()*1000))
            else:
                print(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " External Temperature: %.1f F" % temp_f)
                print(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " Humidity: %d %%" % hum)
                writeCurrentState('probes','ext_temp', str(temp_f))
                writeCurrentState('probes','humidity', str(hum))
                                  
            # record the new sampling time
            dht11_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
    ##########################################################################################
    # read ds18b20 temperature sensor
    #
    # it is possible to support multiple probes but we will use just one for now
    ##########################################################################################
    if (int(round(time.time()*1000)) - ds18b20_SamplingTimeSeed) > ds18b20_SamplingInterval:
        # let's read the ds18b20 temperature
        try:
            timestamp = datetime.now()
            dstemp = float(ds18b20.read_temp("F"))      
            if (int(round(time.time()*1000)) - ds18b20_LastLogTime) > ds18b20_LogInterval:
                RBP_commons.logprobedata(config['logs']['temp1_log_prefix'], "{:.1f}".format(dstemp))
                print(timestamp.strftime(Fore.CYAN + Style.BRIGHT + "%Y-%m-%d %H:%M:%S") + " ***Logged*** Temperature: %.1f F" % dstemp + Style.RESET_ALL)
                ds18b20_LastLogTime = int(round(time.time()*1000))
            else:
                print(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " Temperature: %.1f F" % dstemp)
                writeCurrentState('probes','temp1', str(dstemp))
                # publish the temperature via rabbitmq
                channel.basic_publish(exchange='',
                    routing_key='hello',
                    properties=pika.BasicProperties(expiration='10000'),
                    body=str(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " Temperature: %.1f F" % dstemp))
        except:
            print(Back.RED + Fore.WHITE + timestamp.strftime("%Y-%m-%d %H:%M:%S") +
                  " <<<Error>>> Can not read ds18b20 temperature data!" + Style.RESET_ALL)
            
        # record the new sampling time
        ds18b20_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
        
    # pause to slow down the loop, otherwise CPU usage spikes as program is busy waiting
    time.sleep(1)
