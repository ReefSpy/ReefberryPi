#!/usr/bin/python3

##############################################################################
# RBP_server.py
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
import cfg_common
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', socket_timeout=15))
channel = connection.channel()

# queue for posting state update
channel.queue_declare(queue='current_state' )
# queue for reading outlet state change requests
channel.queue_declare(queue='outlet_change' )


# initialize config file
config = configparser.ConfigParser()
config.read('ReefberryPi.ini')
currentStateFile = 'RBP_currentstate.ini'
curstate = configparser.ConfigParser()
curstate.read(currentStateFile)

# read in the preferences
#ph_numsamples = int(config['ph']['ph_numsamples']) # how many samples to collect before averaging
#ph_SamplingInterval = int(config['ph']['ph_SamplingInterval']) # milliseconds
#ph_Sigma = int(config['ph']['ph_Sigma']) # how many standard deviations to clean up outliers
#ph_LogInterval = int(config['ph']['ph_LogInterval']) # milliseconds
#dht11_SamplingInterval = int(config['dht11']['dht11_SamplingInterval']) # milliseconds
#dht11_LogInterval = int(config['dht11']['dht11_LogInterval']) # milliseconds
#ds18b20_SamplingInterval = int(config['ds18b20']['ds18b20_SamplingInterval']) # milliseconds
#ds18b20_LogInterval = int(config['ds18b20']['ds18b20_LogInterval']) # milliseconds
#outlet_SamplingInterval = int(config['outlets']['outlet_SamplingInterval']) # milliseconds
#outlet_1_buttonstate = config['outlet_1']['button_state']

# read in the preferences
ph_numsamples = int(cfg_common.readINIfile('ph', 'ph_numsamples', "10")) # how many samples to collect before averaging
ph_SamplingInterval = int(cfg_common.readINIfile('ph', 'ph_samplinginterval', "1000")) # milliseconds
ph_Sigma = int(cfg_common.readINIfile('ph', 'ph_sigma', "1")) # how many standard deviations to clean up outliers
ph_LogInterval = int(cfg_common.readINIfile('ph', 'ph_loginterval', "300000")) # milliseconds
dht11_SamplingInterval = int(cfg_common.readINIfile('dht11/22', 'dht11_samplinginterval', "5000")) # milliseconds
dht11_LogInterval = int(cfg_common.readINIfile('dht11/22', 'dht11_loginterval', "300000")) # milliseconds
ds18b20_SamplingInterval = int(cfg_common.readINIfile('probes_ds18b20', 'ds18b20_samplinginterval', "5000")) # milliseconds
ds18b20_LogInterval = int(cfg_common.readINIfile('probes_ds18b20', 'ds18b20_loginterval', "300000")) # milliseconds
outlet_SamplingInterval = int(cfg_common.readINIfile('outlets', 'outlet_samplinginterval', "5000")) # milliseconds
#int_outlet2_buttonstate = cfg_common.readINIfile("int_outlet_2", "button_state", "OFF")
#int_outlet3_buttonstate = cfg_common.readINIfile("int_outlet_3", "button_state", "OFF")
#int_outlet4_buttonstate = cfg_common.readINIfile("int_outlet_4", "button_state", "OFF")

int_outlet_buttonstates = {
    "int_outlet1_buttonstate":cfg_common.readINIfile("int_outlet_1", "button_state", "OFF"),
    "int_outlet2_buttonstate":cfg_common.readINIfile("int_outlet_2", "button_state", "OFF"),
    "int_outlet3_buttonstate":cfg_common.readINIfile("int_outlet_3", "button_state", "OFF"),
    "int_outlet4_buttonstate":cfg_common.readINIfile("int_outlet_4", "button_state", "OFF"),
    }

# dictionary to hold all the temperature probes
tempProbeDict = {}

class tempProbeClass():
    name = ""
    probeid = ""
    lastTemperature = ""
    lastLogTime = ""
    
# set up the GPIO
GPIO_config.initGPIO()

# dht11 temperature and humidity sensor
dht_sensor = dht11.DHT11(pin=GPIO_config.dht11)

# list to hold the raw ph data
ph_dvlist = []             

# give these an initial value in case we fail to get a valid reading it will just report -1
temp_f, temp_c = -1, -1

# some variables to hold the latest probe data
ds18b20_1 = None
dht11_t = None
dht_11_h = None
mcp3008_0 = None

# need the initial probe time seed to compare our sampling intervals against
ph_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
ph_LastLogTime = int(round(time.time()*1000)) #convert time to milliseconds
dht11_LastLogTime = int(round(time.time()*1000)) #convert time to milliseconds
dht11_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
ds18b20_LastLogTime = int(round(time.time()*1000)) #convert time to milliseconds
ds18b20_LastLogTimeDict = int(round(time.time()*1000)) #convert time to milliseconds
ds18b20_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
outlet_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds

# need initial feed timer seed to compare our times against
feed_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
feed_CurrentMode = "CANCEL" #initialize with feed mode cancel to it is off
feed_PreviousMode = "CANCEL"
feed_ExtraTimeSeed = int(round(time.time()*1000))  #extra time after feed is over
feed_ExtraTimeAdded = 0 # initialze to 0 extra time added

def writeCurrentState(section, key, value):
    curstate[section][key] = str(value)
    with open(currentStateFile,'w') as configfile:
        curstate.write(configfile)

def writeConfig(section, key, value):
    config.read('ReefberryPi.ini')
    config[section][key] = str(value)
    with open('ReefberryPi.ini','w') as configfile:
        config.write(configfile)

#Outlet Control
##def outlet1_control():
##    #print("outlet control 1 " + outlet_1_buttonstate + " " + str(GPIO_config.relay_1))
##    if int(outlet_1_buttonstate) == 1:
##        GPIO.output(GPIO_config.relay_1, True)
##        return "OFF"
##    elif int(outlet_1_buttonstate) == 2:
##        try:
##            if float(ds18b20_1) <= 77:
##                GPIO.output(GPIO_config.relay_1, False)
##                #lbl_heater_status.config(text="ON (77-78)", foreground="GREEN")
##                return "ON (77-78)"
##            elif float(ds18b20_1) >= 78:
##                GPIO.output(GPIO_config.relay_1, True)
##                #lbl_heater_status.config(text="OFF (77-78)", foreground="RED")
##                return "OFF (77-78)"
##            #else:
##            #    lbl_heater_status.config(text="ON (77-78)", foreground="GREEN")
##
##        except:
##            return    
##    elif int(outlet_1_buttonstate) == 3:
##        GPIO.output(GPIO_config.relay_1, False)
##        return "ON"
    
def outlet_control(bus, outletnum): # bus = "int" or "ext"

    outlet = str(bus + "_outlet_" + outletnum)
    controltype = cfg_common.readINIfile(outlet, "control_type", "Always")
    pin = GPIO_config.int_outletpins.get(outlet)
    

    if outlet == "int_outlet_1":
        button_state = int_outlet_buttonstates.get("int_outlet1_buttonstate")
    elif outlet == "int_outlet_2":
        button_state = int_outlet_buttonstates.get("int_outlet2_buttonstate")
    elif outlet == "int_outlet_3":
        button_state = int_outlet_buttonstates.get("int_outlet3_buttonstate")
    elif outlet == "int_outlet_4":
        button_state = int_outlet_buttonstates.get("int_outlet4_buttonstate")
    else:
        button_state = "OFF"

    # control type ALWAYS
    if controltype == "Always":
        return handle_outlet_always(outlet, button_state, pin)   
    # control type HEATER    
    elif controltype == "Heater":
        return handle_outlet_heater(outlet, button_state, pin)
    # control type RETURN PUMP
    elif controltype == "Return Pump":
        return handle_outlet_returnpump(outlet, button_state, pin)
    elif controltype == "Skimmer":
        return handle_outlet_skimmer(outlet, button_state, pin)
    elif controltype == "Light":
        return handle_outlet_light(outlet, button_state, pin)


def handle_outlet_always(outlet, button_state, pin):
    if button_state == "OFF":
        GPIO.output(pin, True)
        return "OFF"
    elif button_state == "ON":
        GPIO.output(pin, False)
        return "ON"
    elif button_state == "AUTO":
        state = cfg_common.readINIfile(outlet, "always_state", "OFF")
        if state == "OFF":
            GPIO.output(pin, True)
            return "OFF"
        elif state == "ON":
            GPIO.output(pin, False)
            return "ON"
    else:
        GPIO.output(pin, True)
        return "OFF"

def handle_outlet_heater(outlet, button_state, pin):
    global tempProbeDict
    if button_state == "OFF":
        GPIO.output(pin, True)
        return "OFF"
    elif button_state == "ON":
        GPIO.output(pin, False)
        return "ON"
    elif button_state == "AUTO":
        probe = cfg_common.readINIfile(outlet, "heater_probe", "28-000000000000")
        on_temp = cfg_common.readINIfile(outlet, "heater_on", "25.0")
        off_temp = cfg_common.readINIfile(outlet, "heater_off", "25.5")


        for p in tempProbeDict:
            if tempProbeDict[p].probeid == probe:
                if tempProbeDict[p].lastTemperature <= float(on_temp):
                    #print(str(tempProbeDict[p].lastTemperature) + " " + str(on_temp))
                    GPIO.output(pin, False)
                    tempScale = cfg_common.readINIfile("global", "tempscale", "0")
                    if  tempScale == str(cfg_common.SCALE_F):
                        on_temp = cfg_common.convertCtoF(on_temp)
                        off_temp = cfg_common.convertCtoF(off_temp)                   
                    return "ON (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ")"  
                if tempProbeDict[p].lastTemperature >= float(off_temp):
                    GPIO.output(pin, True)
                    tempScale = cfg_common.readINIfile("global", "tempscale", "0")
                    if tempScale == str(cfg_common.SCALE_F):
                        on_temp = cfg_common.convertCtoF(on_temp)
                        off_temp = cfg_common.convertCtoF(off_temp)
                    return "OFF (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ")"
                break
##        if state == "OFF":
##            GPIO.output(pin, True)
##            return "OFF"
##        elif state == "ON":
##            GPIO.output(pin, False)
##            return "ON"
    else:
        GPIO.output(pin, True)
        return "OFF"

def handle_outlet_light(outlet, button_state, pin):
    if button_state == "OFF":
        GPIO.output(pin, True)
        return "OFF"
    elif button_state == "ON":
        GPIO.output(pin, False)
        return "ON"
    elif button_state == "AUTO":
        on_time = cfg_common.readINIfile(outlet, "light_on", "08:00")
        off_time = cfg_common.readINIfile(outlet, "light_off", "17:00")
        now = datetime.now()
        now_time = now.time()
        on_time = datetime.strptime(on_time, '%H:%M')
        off_time = datetime.strptime(off_time, '%H:%M')
        # on time before off time
        if datetime.time(on_time) < datetime.time(off_time):
            if now_time >= datetime.time(on_time) and now_time <= datetime.time(off_time):
                GPIO.output(pin, False) #turn on light
                status = "ON" + " (" + str(datetime.strftime(on_time, '%H:%M')) + " - " + str(datetime.strftime(off_time, '%H:%M')) +")"
                return status
            else:
                GPIO.output(pin, True) #turn on light
                status = "OFF" + " (" + str(datetime.strftime(on_time, '%H:%M')) + " - " + str(datetime.strftime(off_time, '%H:%M')) +")"
                return status
        else: # on time after off time
            if now_time <= datetime.time(on_time) and now_time >= datetime.time(off_time):
                GPIO.output(pin, True) #turn off light
                status = "OFF" + " (" + str(datetime.strftime(on_time, '%H:%M')) + " - " + str(datetime.strftime(off_time, '%H:%M')) +")"
                return status
            else:
                GPIO.output(pin, False) #turn on light
                status = "ON" + " (" + str(datetime.strftime(on_time, '%H:%M')) + " - " + str(datetime.strftime(off_time, '%H:%M')) +")"
                return status
    else:
        GPIO.output(pin, True)
        return "OFF"

def handle_outlet_returnpump (outlet, button_state, pin):  
    global feed_PreviousMode
    if feed_PreviousMode == "A":
        feed_ExtraTimeAdded = cfg_common.readINIfile(outlet, "return_feed_delay_a", "0") 
    elif feed_PreviousMode == "B":
        feed_ExtraTimeAdded = cfg_common.readINIfile(outlet, "return_feed_delay_b", "0")
    elif feed_PreviousMode == "C":
        feed_ExtraTimeAdded = cfg_common.readINIfile(outlet, "return_feed_delay_c", "0")
    elif feed_PreviousMode == "D":
        feed_ExtraTimeAdded = cfg_common.readINIfile(outlet, "return_feed_delay_d", "0")
    else:
        feed_ExtraTimeAdded = 0
        
    if button_state == "OFF":
        GPIO.output(pin, True)
        return "OFF"
    elif button_state == "ON":
        GPIO.output(pin, False)
        return "ON"
    elif button_state == "AUTO":
        if feed_CurrentMode == "A":
            return_enable_feed_a = cfg_common.readINIfile(outlet, "return_enable_feed_a", "False")
            feed_PreviousMode = "A"
            if return_enable_feed_a == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif return_enable_feed_a == "False":
                GPIO.output(pin, False)
                return "ON"
        elif feed_CurrentMode == "B":
            return_enable_feed_b = cfg_common.readINIfile(outlet, "return_enable_feed_b", "False")
            feed_PreviousMode = "B"
            if return_enable_feed_b == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif return_enable_feed_b == "False":
                GPIO.output(pin, False)
                return "ON"
        elif feed_CurrentMode == "C":
            return_enable_feed_c = cfg_common.readINIfile(outlet, "return_enable_feed_c", "False")
            feed_PreviousMode = "C"
            if return_enable_feed_c == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif return_enable_feed_c == "False":
                GPIO.output(pin, False)
                return "ON"
        elif feed_CurrentMode == "D":
            return_enable_feed_d = cfg_common.readINIfile(outlet, "return_enable_feed_d", "False")
            feed_PreviousMode = "D"
            if return_enable_feed_d == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif return_enable_feed_d == "False":
                GPIO.output(pin, False)
                return "ON"
        else:
            difference = round(((int(feed_ExtraTimeSeed) + (int(feed_ExtraTimeAdded)*1000)) - int(round(time.time())*1000))/1000)
            
            if int(round(time.time())*1000) <= int(feed_ExtraTimeSeed) + (int(feed_ExtraTimeAdded)*1000):
                #print("Extra feed time remaining: " + str(difference) + "s")
                print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                   " Delay Mode: " + outlet + " (" + str(feed_ExtraTimeAdded) + "s) " + " Delay Time Remaining: " + str(round(difference)) + "s"
                   + Style.RESET_ALL)
                GPIO.output(pin, True)
                return "OFF (delay)"
            else:
                GPIO.output(pin, False)
                return "ON"
    else:
        GPIO.output(pin, True)
        return "OFF"

def handle_outlet_skimmer (outlet, button_state, pin):  
    global feed_PreviousMode
    if feed_PreviousMode == "A":
        feed_ExtraTimeAdded = cfg_common.readINIfile(outlet, "skimmer_feed_delay_a", "0") 
    elif feed_PreviousMode == "B":
        feed_ExtraTimeAdded = cfg_common.readINIfile(outlet, "skimmer_feed_delay_b", "0")
    elif feed_PreviousMode == "C":
        feed_ExtraTimeAdded = cfg_common.readINIfile(outlet, "skimmer_feed_delay_c", "0")
    elif feed_PreviousMode == "D":
        feed_ExtraTimeAdded = cfg_common.readINIfile(outlet, "skimmer_feed_delay_d", "0")
    else:
        feed_ExtraTimeAdded = 0

    if button_state == "OFF":
        GPIO.output(pin, True)
        return "OFF"
    elif button_state == "ON":
        GPIO.output(pin, False)
        return "ON"
    elif button_state == "AUTO":
        if feed_CurrentMode == "A":
            skimmer_enable_feed_a = cfg_common.readINIfile(outlet, "skimmer_enable_feed_a", "False")
            feed_PreviousMode = "A"
            if skimmer_enable_feed_a == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif skimmer_enable_feed_a == "False":
                GPIO.output(pin, False)
                return "ON"
        elif feed_CurrentMode == "B":
            skimmer_enable_feed_b = cfg_common.readINIfile(outlet, "skimmer_enable_feed_b", "False")
            feed_PreviousMode = "B"
            if skimmer_enable_feed_b == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif skimmer_enable_feed_b == "False":
                GPIO.output(pin, False)
                return "ON"
        elif feed_CurrentMode == "C":
            skimmer_enable_feed_c = cfg_common.readINIfile(outlet, "skimmer_enable_feed_c", "False")
            feed_PreviousMode = "C"
            if skimmer_enable_feed_c == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif skimmer_enable_feed_c == "False":
                GPIO.output(pin, False)
                return "ON"
        elif feed_CurrentMode == "D":
            skimmer_enable_feed_d = cfg_common.readINIfile(outlet, "skimmer_enable_feed_d", "False")
            feed_PreviousMode = "D"
            if skimmer_enable_feed_d == "True":
                GPIO.output(pin, True)
                return "OFF (feed)"
            elif skimmer_enable_feed_d == "False":
                GPIO.output(pin, False)
                return "ON"
        else:
            difference = round(((int(feed_ExtraTimeSeed) + (int(feed_ExtraTimeAdded)*1000)) - int(round(time.time())*1000))/1000)
            if int(round(time.time())*1000) <= int(feed_ExtraTimeSeed) + (int(feed_ExtraTimeAdded)*1000):
                #print("Extra feed time remaining: " + str(difference) + "s")
                print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                   " Delay Mode: " + outlet + " (" + str(feed_ExtraTimeAdded) + "s) " + " Delay Time Remaining: " + str(round(difference)) + "s"
                   + Style.RESET_ALL)
                GPIO.output(pin, True)
                return "OFF (delay)"
            else:
                GPIO.output(pin, False)
                return "ON"
    else:
        GPIO.output(pin, True)
        return "OFF"

def readTempProbes(tempProbeDict):
    tempProbeDict.clear()
    config = configparser.ConfigParser()
    config.read(cfg_common.CONFIGFILENAME)
    # loop through each section and see if it is a ds18b20 temp probe
    for section in config:
        if section.split("_")[0] == "ds18b20":
            #print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " +
            #      "Temperature probe: " + section.split("_")[1])
            #print (section.split("_")[1])
            probe = tempProbeClass()
            probe.probeid = section.split("_")[1]
            probe.name = config[section]["name"]
            tempProbeDict [section.split("_")[1]] = probe

            #print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " +
            #      "ds18b20 [id: " + probe.probeid + "] [label: " + probe.name + "]")
            #print("probe class id: " + probe.probeid)
            #print("probe class name: " + probe.name)
    
    
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
                # sometimes a high value, like 22.4 gets recorded, i need to fix this, but for now don't log that
                if ph_AvgFiltered < 14.0:  
                    RBP_commons.logprobedata(config['logs']['ph_log_prefix'], "{:.2f}".format(ph_AvgFiltered))
                    print(timestamp.strftime(Fore.CYAN + Style.BRIGHT + "%Y-%m-%d %H:%M:%S") + " ***Logged*** pH = "
                          + "{:.2f}".format(ph_AvgFiltered) + Style.RESET_ALL)
                    ph_LastLogTime = int(round(time.time()*1000))
            else:
                print(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " pH = "
                      + "{:.2f}".format(ph_AvgFiltered))
                writeCurrentState('probes','ph', str("{:.2f}".format(ph_AvgFiltered)))
                channel.basic_publish(exchange='',
                    routing_key='current_state',
                    properties=pika.BasicProperties(expiration='10000'),
                    body=str("mcp3008_0" + "," + timestamp.strftime("%Y-%m-%d %H:%M:%S") + "," + "{:.2f}".format(ph_AvgFiltered)))

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
            #print("Last valid input: " + str(datetime.datetime.now()))
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
                channel.basic_publish(exchange='',
                    routing_key='current_state',
                    properties=pika.BasicProperties(expiration='10000'),
                    body=str("dht11_t" + "," + timestamp.strftime("%Y-%m-%d %H:%M:%S") + "," + "%.1f" % temp_f))
                channel.basic_publish(exchange='',
                    routing_key='current_state',
                    properties=pika.BasicProperties(expiration='10000'),
                    body=str("dht11_h" + "," + timestamp.strftime("%Y-%m-%d %H:%M:%S") + "," + str(hum)))
                                  
            # record the new sampling time
            dht11_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
    ##########################################################################################
    # read ds18b20 temperature sensor
    #
    # it is possible to support multiple probes but we will use just one for now
    ##########################################################################################
    if (int(round(time.time()*1000)) - ds18b20_SamplingTimeSeed) > ds18b20_SamplingInterval:
        readTempProbes(tempProbeDict)
        for p in tempProbeDict:
            tempProbeDict[p].lastLogTime = ds18b20_LastLogTimeDict
        # let's read the ds18b20 temperature
        try:
            timestamp = datetime.now()
            dstemp = float(ds18b20.read_temp("F"))      
            if (int(round(time.time()*1000)) - ds18b20_LastLogTime) > ds18b20_LogInterval:
                RBP_commons.logprobedata(config['logs']['temp1_log_prefix'], "{:.1f}".format(dstemp))
                print(timestamp.strftime(Fore.CYAN + Style.BRIGHT + "%Y-%m-%d %H:%M:%S") + " ***Logged*** Temperature: %.1f F" % dstemp + Style.RESET_ALL)
                ds18b20_LastLogTime = int(round(time.time()*1000))
                ds18b20_1 = dstemp # set variable so we can use it later in something like outlets
            else:
                print(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " Temperature: %.1f F" % dstemp)
                #writeCurrentState('probes','temp1', str(dstemp))
                # publish the temperature via rabbitmq
                channel.basic_publish(exchange='',
                    routing_key='current_state',
                    properties=pika.BasicProperties(expiration='10000'),
                    body=str("ds18b20_1" + "," + timestamp.strftime("%Y-%m-%d %H:%M:%S") + "," + "%.1f" % dstemp))
                ds18b20_1 = dstemp # set variable so we can use it later in something like outlets
        except:
            print(Back.RED + Fore.WHITE + timestamp.strftime("%Y-%m-%d %H:%M:%S") +
                  " <<<Error>>> Can not read ds18b20 temperature data!" + Style.RESET_ALL)
            
#######################
        # read data from the temperature probes
        for p in tempProbeDict:
            try:
                timestamp = datetime.now()
                dstemp =  float(ds18b20.read_temp("C"))
                
                if (int(round(time.time()*1000)) - tempProbeDict[p].lastLogTime) > ds18b20_LogInterval:
                    tempData = str("{:.1f}".format(dstemp)) + "," + str(RBP_commons.convertCtoF(dstemp))
                    RBP_commons.logprobedata("ds18b20_" + tempProbeDict[p].probeid + "_", tempData)
                    print(timestamp.strftime(Fore.CYAN + Style.BRIGHT + "%Y-%m-%d %H:%M:%S") + " ***Logged*** Temperature: %.1f" % dstemp + " C, "
                          + RBP_commons.convertCtoF(dstemp) + " F" + " [" + tempProbeDict[p].name + "] [" + tempProbeDict[p].probeid + "]" + Style.RESET_ALL)
                    #ds18b20_LastLogTime = int(round(time.time()*1000))
                    ds18b20_LastLogTimeDict = int(round(time.time()*1000))
                    #ds18b20_1 = dstemp # set variable so we can use it later in something like outlets
                    tempProbeDict[p].lastTemperature = dstemp
                else:
                    #print(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " Temperature: %.1f" % dstemp)
                    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " +
                        "ds18b20 [label: " + tempProbeDict[p].name + "] [id: " + tempProbeDict[p].probeid + "]" + " [value: " + str(dstemp) + " C, " + str(RBP_commons.convertCtoF(dstemp)) + " F]")
                    #writeCurrentState('probes','temp1', str(dstemp))
                    # publish the temperature via rabbitmq
                    channel.basic_publish(exchange='',
                        routing_key='current_state',
                        properties=pika.BasicProperties(expiration='10000'),
                        body=str("ds18b20_" + tempProbeDict[p].probeid + "," + timestamp.strftime("%Y-%m-%d %H:%M:%S") + "," + "%.1f" % dstemp + "," + RBP_commons.convertCtoF(dstemp)))
                    #ds18b20_1 = dstemp # set variable so we can use it later in something like outlets
                    tempProbeDict[p].lastTemperature = dstemp
            except:
                print(Back.RED + Fore.WHITE + timestamp.strftime("%Y-%m-%d %H:%M:%S") +
                      " <<<Error>>> Can not read ds18b20_" + tempProbeDict[p].probeid + " temperature data!" + Style.RESET_ALL)
#######################

        # record the new sampling time
        ds18b20_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds

    ##########################################################################################
    # check if Feed mode is enabled
    #
    ##########################################################################################
    
    if feed_CurrentMode == "A":
        feed_ModeTotaltime = cfg_common.readINIfile("feed_timers", "feed_a", "60")
    elif feed_CurrentMode == "B":
        feed_ModeTotaltime = cfg_common.readINIfile("feed_timers", "feed_b", "60")
    elif feed_CurrentMode == "C":
        feed_ModeTotaltime = cfg_common.readINIfile("feed_timers", "feed_c", "60")
    elif feed_CurrentMode == "D":
        feed_ModeTotaltime = cfg_common.readINIfile("feed_timers", "feed_d", "60")
    else:
        feed_ModeTotaltime = "0"

    if feed_CurrentMode != "CANCEL":
        feedTimeLeft = (int(feed_ModeTotaltime)*1000) - (int(round(time.time()*1000)) - feed_SamplingTimeSeed)
        if feedTimeLeft <=0:
            print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                   " Feed Mode: " + feed_CurrentMode + " COMPLETE" + Style.RESET_ALL)
            feed_CurrentMode = "CANCEL"
            timestamp = datetime.now()
            channel.basic_publish(exchange='',
                    routing_key='current_state',
                    properties=pika.BasicProperties(expiration='10000'),
                    body=str("feed_timer" + "," + timestamp.strftime("%Y-%m-%d %H:%M:%S") + "," + str(feed_CurrentMode) + "," + str(0)))

            feed_ExtraTimeSeed = int(round(time.time()*1000))
            print ("Extra time starts at: " + str(feed_ExtraTimeSeed) + " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:    
            print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                   " Feed Mode: " + feed_CurrentMode + " (" + feed_ModeTotaltime + "s) " + "Time Remaining: " + str(round(feedTimeLeft/1000)) + "s"
                   + Style.RESET_ALL)
            timestamp = datetime.now()
            channel.basic_publish(exchange='',
                    routing_key='current_state',
                    properties=pika.BasicProperties(expiration='10000'),
                    body=str("feed_timer" + "," + timestamp.strftime("%Y-%m-%d %H:%M:%S") + "," + str(feed_CurrentMode) + "," + str(round(feedTimeLeft/1000))))
    
           
        

    ##########################################################################################
    # handle any state changes requested for the outlets
    #
    ##########################################################################################
    
    method_frame, header_frame, body = channel.basic_get(queue='outlet_change',
                              no_ack=True)
    if body != None:
        body = body.decode()
        outlet = body.split(",")[0]
        value = body.split(",")[1]
        print(Fore.YELLOW + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
              " outlet state change: " + outlet + " to " + value + Style.RESET_ALL)
        if outlet == "int_outlet_1":
            #writeConfig(outlet, "button_state", value)
            cfg_common.writeINIfile(outlet, "button_state", value)
            #print("Write configfile " + outlet + " " + value)
            #outlet_1_buttonstate = value
            int_outlet_buttonstates["int_outlet1_buttonstate"] = value
        elif outlet =="int_outlet_2":
            cfg_common.writeINIfile(outlet, "button_state", value)
            #int_outlet2_buttonstate = value
            int_outlet_buttonstates["int_outlet2_buttonstate"] = value
        elif outlet =="int_outlet_3":
            cfg_common.writeINIfile(outlet, "button_state", value)
            #int_outlet3_buttonstate = value
            int_outlet_buttonstates["int_outlet3_buttonstate"] = value
        elif outlet =="int_outlet_4":
            cfg_common.writeINIfile(outlet, "button_state", value)
            #int_outlet4_buttonstate = value
            int_outlet_buttonstates["int_outlet4_buttonstate"] = value

        if outlet =="feed_mode":
            feed_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
            feed_CurrentMode = value
            print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                   " Feed Mode: " + feed_CurrentMode + " Start" + Style.RESET_ALL)
            feed_PreviousMode = "CANCEL"
            #print ("feed mode: " + value)
            if feed_CurrentMode == "CANCEL":
                timestamp=datetime.now()
                channel.basic_publish(exchange='',
                    routing_key='current_state',
                    properties=pika.BasicProperties(expiration='10000'),
                    body=str("feed_timer" + "," + timestamp.strftime("%Y-%m-%d %H:%M:%S") + "," + str(feed_CurrentMode) + "," + str(0)))
            

            
            
    ##########################################################################################
    # handle outlet states (turn outlets on or off)
    #
    ##########################################################################################
    #outlet1_control()
    # do each of the outlets on the internal bus (outlets 1-4)
    for x in range (1,5):
        status = outlet_control("int", str(x))
    #    #print (str(x) + " " + str(status))
    ##########################################################################################
    # broadcast current state of outlets
    #
    ##########################################################################################
    if (int(round(time.time()*1000)) - outlet_SamplingTimeSeed) > outlet_SamplingInterval:
##        # internal outlet 1
##        status = outlet1_control()
##        channel.basic_publish(exchange='',
##                        routing_key='current_state',
##                        properties=pika.BasicProperties(expiration='10000'),
##                        body=str("outlet_1" + "," + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + 
##                                 "," + outlet_1_buttonstate + "," + str(status) + "," + "Out1Heater"))
##        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
##              " Outlet_1 button state: " + outlet_1_buttonstate + " " + str(status))

        # do each of the outlets on the internal bus (outlets 1-4)
        for x in range (1,5):
            status = outlet_control("int", str(x))
            channel.basic_publish(exchange='',
                            routing_key='current_state',
                            properties=pika.BasicProperties(expiration='10000'),
                            body=str("int_outlet_" + str(x) + "," + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + 
                                 "," + int_outlet_buttonstates.get("int_outlet" + str(x) + "_buttonstate") + "," + str(status) +
                                     "," + cfg_common.readINIfile("int_outlet_" + str(x), "name", "Unnamed")))
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") +    
                " int_outlet_" + str(x) +
                " [label: " + cfg_common.readINIfile("int_outlet_" + str(x), "name", "Unnamed") +
                "] [type: " + cfg_common.readINIfile("int_outlet_" + str(x), "control_type", "Always") +
                "] [button: " + cfg_common.readINIfile("int_outlet_" + str(x), "button_state", "OFF") +  
                "] [status: " + str(status) + "]" +
                " [pin: " + str(GPIO_config.int_outletpins.get("int_outlet_" + str(x))) + "]")


        outlet_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds

    ##########################################################################################
    # pause to slow down the loop, otherwise CPU usage spikes as program is busy waiting
    ##########################################################################################
    time.sleep(1)
