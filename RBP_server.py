#!/usr/bin/python3

##############################################################################
# RBP_server.py
#
# this module will pull data from the various input probes and record data
# to the log files
#
# Written by ReefSpy for the ReefBerry Pi, (c) 2019
# www.youtube.com/reefspy
##############################################################################

from datetime import datetime, timedelta, time
from colorama import Fore, Back, Style
import time
import queue
import threading
import pika
import json
import logging
import logging.handlers
import os.path
import configparser
import defs_common
import dht11
import ds18b20
import mcp3008
import GPIO_config
import RPi.GPIO as GPIO


class RBP_server:
    
    def __init__(self):

        self.threads=[]
        self.queue = queue.Queue()        

        LOG_FILEDIR = "logs"
        LOG_FILENAME = "RBP_server.log"
        LOGLEVEL_CONSOLE = logging.INFO # DEBUG, INFO, ERROR
        LOGLEVEL_LOGFILE = logging.INFO
          
        self.initialize_logger(LOG_FILEDIR, LOG_FILENAME, LOGLEVEL_CONSOLE, LOGLEVEL_LOGFILE)

        defs_common.logtoconsole("Starting up", fg="WHITE", style="BRIGHT")
        self.logger.info("Server startup...")

        # initialize the messanging queues
        self.connection1 = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', socket_timeout=15))
        self.channel1 = self.connection1.channel()

        self.connection2 = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel2 = self.connection2.channel()
        self.channel2.exchange_declare(exchange='rbp_currentstatus',
                                 exchange_type='fanout')



        # dictionaries to hold all the temperature probes and outlets
        self.tempProbeDict = {}
        self.outletDict = {}

        #read prefs
        self.read_preferences()
        

        # set up the GPIO
        GPIO_config.initGPIO()

        # dht11 temperature and humidity sensor
        self.dht_sensor = dht11.DHT11(pin=GPIO_config.dht11)

        # list to hold the raw ph data
        self.ph_dvlist = []             
##
##        # give these an initial value in case we fail to get a valid reading it will just report -1
##        #temp_f, temp_c = -1, -1
##
##        # some variables to hold the latest probe data
##        ds18b20_1 = None
##        dht11_t = None
##        dht_11_h = None
##        mcp3008_0 = None
##
        # need the initial probe time seed to compare our sampling intervals against
        self.ph_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
        self.ph_LastLogTime = int(round(time.time()*1000)) #convert time to milliseconds
        
        self.DHT_Sensor["dht11_lastlogtime"] = int(round(time.time()*1000)) #convert time to milliseconds
        self.DHT_Sensor["dht11_samplingtimeseed"] = int(round(time.time()*1000)) #convert time to milliseconds

        self.ds18b20_LastLogTime = int(round(time.time()*1000)) #convert time to milliseconds
        self.ds18b20_LastLogTimeDict = int(round(time.time()*1000)) #convert time to milliseconds
        self.ds18b20_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
        self.outlet_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds

        # need initial feed timer seed to compare our times against
        self.feed_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
        self.feed_CurrentMode = "CANCEL" #initialize with feed mode cancel to it is off
        self.feed_PreviousMode = "CANCEL"
        self.feed_ExtraTimeSeed = int(round(time.time()*1000))  #extra time after feed is over
        self.feed_ExtraTimeAdded = 0 # initialze to 0 extra time added
        
        self.threadManager()

    def read_preferences(self):
        # read in the preferences

        self.DHT_Sensor = {
            "enabled": defs_common.readINIfile('dht11/22', 'enabled', "False", logger=self.logger),
            "temperature_name": str(defs_common.readINIfile('dht11/22', 'temperature_name', "Ambient Temperature", logger=self.logger)), 
            "humidity_name": str(defs_common.readINIfile('dht11/22', 'humidity_name', "Humidity", logger=self.logger)), 
            "dht11_samplinginterval": int(defs_common.readINIfile('dht11/22', 'dht11_samplinginterval', "5000", logger=self.logger)), # milliseconds
            "dht11_loginterval": int(defs_common.readINIfile('dht11/22', 'dht11_loginterval', "300000", logger=self.logger)), # milliseconds
            }

        self.temperaturescale =  int(defs_common.readINIfile('global', 'tempscale', "0", logger=self.logger)) 
        self.ph_numsamples = int(defs_common.readINIfile('ph', 'ph_numsamples', "10", logger=self.logger)) # how many samples to collect before averaging
        self.ph_SamplingInterval = int(defs_common.readINIfile('ph', 'ph_samplinginterval', "1000", logger=self.logger)) # milliseconds
        self.ph_Sigma = int(defs_common.readINIfile('ph', 'ph_sigma', "1", logger=self.logger)) # how many standard deviations to clean up outliers
        self.ph_LogInterval = int(defs_common.readINIfile('ph', 'ph_loginterval', "300000", logger=self.logger)) # milliseconds
        self.ds18b20_SamplingInterval = int(defs_common.readINIfile('probes_ds18b20', 'ds18b20_samplinginterval', "5000", logger=self.logger)) # milliseconds
        self.ds18b20_LogInterval = int(defs_common.readINIfile('probes_ds18b20', 'ds18b20_loginterval', "300000", logger=self.logger)) # milliseconds
        self.outlet_SamplingInterval = int(defs_common.readINIfile('outlets', 'outlet_samplinginterval', "5000", logger=self.logger)) # milliseconds

        self.int_outlet_buttonstates = {
            "int_outlet1_buttonstate":defs_common.readINIfile("int_outlet_1", "button_state", "OFF", logger=self.logger),
            "int_outlet2_buttonstate":defs_common.readINIfile("int_outlet_2", "button_state", "OFF", logger=self.logger),
            "int_outlet3_buttonstate":defs_common.readINIfile("int_outlet_3", "button_state", "OFF", logger=self.logger),
            "int_outlet4_buttonstate":defs_common.readINIfile("int_outlet_4", "button_state", "OFF", logger=self.logger),
            "int_outlet5_buttonstate":defs_common.readINIfile("int_outlet_5", "button_state", "OFF", logger=self.logger),
            "int_outlet6_buttonstate":defs_common.readINIfile("int_outlet_6", "button_state", "OFF", logger=self.logger),
            "int_outlet7_buttonstate":defs_common.readINIfile("int_outlet_7", "button_state", "OFF", logger=self.logger),
            "int_outlet8_buttonstate":defs_common.readINIfile("int_outlet_8", "button_state", "OFF", logger=self.logger)
            }

        # read the temperature probes
        self.readTempProbes(self.tempProbeDict)

        # read the outlet prefs
        self.readOutletPrefs(self.outletDict)
        for outlet in self.outletDict:
            #outletDict[outlet]["outletname"]
            defs_common.logtoconsole("outlet prefs loaded for: " + str(self.outletDict[outlet].outletname), fg="BLUE", Style="BRIGHT")

        
    
    def initialize_logger(self, output_dir, output_file, loglevel_console, loglevel_logfile):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
         
        # create console handler and set level to info
        self.handler = logging.StreamHandler()
        self.handler.setLevel(loglevel_console)
        self.formatter = logging.Formatter('%(asctime)s %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
     
        # create log file handler and set level to info
        self.handler = logging.handlers.RotatingFileHandler(os.path.join(output_dir, output_file), maxBytes=2000000, backupCount=5)
        self.handler.setLevel(loglevel_logfile)
        self.formatter = logging.Formatter('%(asctime)s <%(levelname)s> [%(threadName)s:%(module)s] %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

        # reduce log level of pika, otherwise it's debug messages flood my logs
        logging.getLogger("pika").setLevel(logging.WARNING)
     
        # create debug file handler and set level to debug
        #handler = logging.FileHandler(os.path.join(output_dir, "all.log"),handler.setLevel(logging.DEBUG)
        #formatter = logging.Formatter('%(asctime)s <%(levelname)s> [%(threadName)s:%(module)s] %(message)s')
        #handler.setFormatter(formatter)
        #logger.addHandler(handler)


    def outlet_control(self, bus, outletnum): # bus = "int" or "ext"

        outlet = str(bus + "_outlet_" + outletnum)
        controltype = defs_common.readINIfile(outlet, "control_type", "Always")
        pin = GPIO_config.int_outletpins.get(outlet)
        

        if outlet == "int_outlet_1":
            button_state = self.int_outlet_buttonstates.get("int_outlet1_buttonstate")
        elif outlet == "int_outlet_2":
            button_state = self.int_outlet_buttonstates.get("int_outlet2_buttonstate")
        elif outlet == "int_outlet_3":
            button_state = self.int_outlet_buttonstates.get("int_outlet3_buttonstate")
        elif outlet == "int_outlet_4":
            button_state = self.int_outlet_buttonstates.get("int_outlet4_buttonstate")
        elif outlet == "int_outlet_5":
            button_state = self.int_outlet_buttonstates.get("int_outlet5_buttonstate")
        elif outlet == "int_outlet_6":
            button_state = self.int_outlet_buttonstates.get("int_outlet6_buttonstate")
        elif outlet == "int_outlet_7":
            button_state = self.int_outlet_buttonstates.get("int_outlet7_buttonstate")
        elif outlet == "int_outlet_8":
            button_state = self.int_outlet_buttonstates.get("int_outlet8_buttonstate")
        else:
            button_state = "OFF"
##########################
# is this the problem???
##########################

        #defs_common.writeINIfile(bus + "_outlet_" + outletnum, "button_state", button_state)
        curstate = defs_common.readINIfile(outlet, "button_state", "OFF", logger=self.logger)
        if curstate != button_state:
            changerequest = {}
            changerequest["outletid"] = outlet
            changerequest["button_state"] = button_state
            #self.queue.put("i want to change " + outlet + " to " + button_state + " curstate = " + curstate)
            #print("i want to change " + outlet + " to " + button_state + " curstate = " + curstate)
            self.logger.debug("outlet_control: change " + outlet + " button_state to " + button_state + " (from " + curstate + ")")
            self.queue.put(changerequest)

        
        # control type ALWAYS
        if controltype == "Always":
            return self.handle_outlet_always(outlet, button_state, pin)   
        # control type HEATER    
        elif controltype == "Heater":
            return self.handle_outlet_heater(outlet, button_state, pin)
        # control type RETURN PUMP
        elif controltype == "Return Pump":
            return self.handle_outlet_returnpump(outlet, button_state, pin)
        elif controltype == "Skimmer":
            return self.handle_outlet_skimmer(outlet, button_state, pin)
        elif controltype == "Light":
            return self.handle_outlet_light(outlet, button_state, pin)

    def handle_outlet_always(self, outlet, button_state, pin):
        if button_state == "OFF":
            GPIO.output(pin, True)
            return "OFF"
        elif button_state == "ON":
            GPIO.output(pin, False)
            return "ON"
        elif button_state == "AUTO":
            state = defs_common.readINIfile(outlet, "always_state", "OFF", logger=self.logger)
            if state == "OFF":
                GPIO.output(pin, True)
                return "OFF"
            elif state == "ON":
                GPIO.output(pin, False)
                return "ON"
        else:
            GPIO.output(pin, True)
            return "OFF"

    def handle_outlet_heater(self, outlet, button_state, pin):
        #global tempProbeDict
        if button_state == "OFF":
            GPIO.output(pin, True)
            return "OFF"
        elif button_state == "ON":
            GPIO.output(pin, False)
            return "ON"
        elif button_state == "AUTO":
            probe = defs_common.readINIfile(outlet, "heater_probe", "28-000000000000", logger=self.logger)
            on_temp = defs_common.readINIfile(outlet, "heater_on", "25.0", logger=self.logger)
            off_temp = defs_common.readINIfile(outlet, "heater_off", "25.5", logger=self.logger)


            for p in self.tempProbeDict:
                if self.tempProbeDict[p].probeid == probe:
                    #print("last temp " + str(self.tempProbeDict[p].lastTemperature))
                    if float(self.tempProbeDict[p].lastTemperature) <= float(on_temp):
                        #print(str(tempProbeDict[p].lastTemperature) + " " + str(on_temp))
                        GPIO.output(pin, False)
                        tempScale = defs_common.readINIfile("global", "tempscale", "0", logger=self.logger)
                        if  tempScale == str(defs_common.SCALE_F):
                            on_temp = defs_common.convertCtoF(float(on_temp))
                            off_temp = defs_common.convertCtoF(float(off_temp))                   
                        return "ON (" + str("%.1f" % float(on_temp)) + " - " + str("%.1f" % float(off_temp)) + ")"  
                    if float(self.tempProbeDict[p].lastTemperature) >= float(off_temp):
                        GPIO.output(pin, True)
                        tempScale = defs_common.readINIfile("global", "tempscale", "0", logger=self.logger)
                        if tempScale == str(defs_common.SCALE_F):
                            on_temp = defs_common.convertCtoF(on_temp)
                            off_temp = defs_common.convertCtoF(off_temp)
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

    def handle_outlet_light(self, outlet, button_state, pin):
        if button_state == "OFF":
            GPIO.output(pin, True)
            return "OFF"
        elif button_state == "ON":
            GPIO.output(pin, False)
            return "ON"
        elif button_state == "AUTO":
            on_time = defs_common.readINIfile(outlet, "light_on", "08:00", logger=self.logger)
            off_time = defs_common.readINIfile(outlet, "light_off", "17:00", logger=self.logger)
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

    def handle_outlet_returnpump (self, outlet, button_state, pin):  
        #global feed_PreviousMode
        if self.feed_PreviousMode == "A":
            self.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "return_feed_delay_a", "0") 
        elif self.feed_PreviousMode == "B":
            self.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "return_feed_delay_b", "0")
        elif self.feed_PreviousMode == "C":
            self.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "return_feed_delay_c", "0")
        elif self.feed_PreviousMode == "D":
            self.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "return_feed_delay_d", "0")
        else:
            self.feed_ExtraTimeAdded = 0
            
        if button_state == "OFF":
            GPIO.output(pin, True)
            return "OFF"
        elif button_state == "ON":
            GPIO.output(pin, False)
            return "ON"
        elif button_state == "AUTO":
            if self.feed_CurrentMode == "A":
                return_enable_feed_a = defs_common.readINIfile(outlet, "return_enable_feed_a", "False")
                self.feed_PreviousMode = "A"
                if return_enable_feed_a == "True":
                    GPIO.output(pin, True)
                    return "OFF (feed)"
                elif return_enable_feed_a == "False":
                    GPIO.output(pin, False)
                    return "ON"
            elif self.feed_CurrentMode == "B":
                return_enable_feed_b = defs_common.readINIfile(outlet, "return_enable_feed_b", "False")
                self.feed_PreviousMode = "B"
                if return_enable_feed_b == "True":
                    GPIO.output(pin, True)
                    return "OFF (feed)"
                elif return_enable_feed_b == "False":
                    GPIO.output(pin, False)
                    return "ON"
            elif self.feed_CurrentMode == "C":
                return_enable_feed_c = defs_common.readINIfile(outlet, "return_enable_feed_c", "False")
                self.feed_PreviousMode = "C"
                if return_enable_feed_c == "True":
                    GPIO.output(pin, True)
                    return "OFF (feed)"
                elif return_enable_feed_c == "False":
                    GPIO.output(pin, False)
                    return "ON"
            elif self.feed_CurrentMode == "D":
                return_enable_feed_d = defs_common.readINIfile(outlet, "return_enable_feed_d", "False")
                self.feed_PreviousMode = "D"
                if return_enable_feed_d == "True":
                    GPIO.output(pin, True)
                    return "OFF (feed)"
                elif return_enable_feed_d == "False":
                    GPIO.output(pin, False)
                    return "ON"
            else:
                difference = round(((int(self.feed_ExtraTimeSeed) + (int(self.feed_ExtraTimeAdded)*1000)) - int(round(time.time())*1000))/1000)
                
                if int(round(time.time())*1000) <= int(self.feed_ExtraTimeSeed) + (int(self.feed_ExtraTimeAdded)*1000):
                    #print("Extra feed time remaining: " + str(difference) + "s")
                    print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                       " Delay Mode: " + outlet + " (" + str(self.feed_ExtraTimeAdded) + "s) " + " Delay Time Remaining: " + str(round(difference)) + "s"
                       + Style.RESET_ALL)
                    GPIO.output(pin, True)
                    return "OFF (delay)"
                else:
                    GPIO.output(pin, False)
                    return "ON"
        else:
            GPIO.output(pin, True)
            return "OFF"

    def handle_outlet_skimmer (self, outlet, button_state, pin):  
        if self.feed_PreviousMode == "A":
            self.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "skimmer_feed_delay_a", "0") 
        elif self.feed_PreviousMode == "B":
            self.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "skimmer_feed_delay_b", "0")
        elif self.feed_PreviousMode == "C":
            self.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "skimmer_feed_delay_c", "0")
        elif self.feed_PreviousMode == "D":
            self.feed_ExtraTimeAdded = defs_common.readINIfile(outlet, "skimmer_feed_delay_d", "0")
        else:
            self.feed_ExtraTimeAdded = 0

        if button_state == "OFF":
            GPIO.output(pin, True)
            return "OFF"
        elif button_state == "ON":
            GPIO.output(pin, False)
            return "ON"
        elif button_state == "AUTO":
            if self.feed_CurrentMode == "A":
                skimmer_enable_feed_a = defs_common.readINIfile(outlet, "skimmer_enable_feed_a", "False")
                self.feed_PreviousMode = "A"
                if skimmer_enable_feed_a == "True":
                    GPIO.output(pin, True)
                    return "OFF (feed)"
                elif skimmer_enable_feed_a == "False":
                    GPIO.output(pin, False)
                    return "ON"
            elif self.feed_CurrentMode == "B":
                skimmer_enable_feed_b = defs_common.readINIfile(outlet, "skimmer_enable_feed_b", "False")
                self.feed_PreviousMode = "B"
                if skimmer_enable_feed_b == "True":
                    GPIO.output(pin, True)
                    return "OFF (feed)"
                elif skimmer_enable_feed_b == "False":
                    GPIO.output(pin, False)
                    return "ON"
            elif self.feed_CurrentMode == "C":
                skimmer_enable_feed_c = defs_common.readINIfile(outlet, "skimmer_enable_feed_c", "False")
                self.feed_PreviousMode = "C"
                if skimmer_enable_feed_c == "True":
                    GPIO.output(pin, True)
                    return "OFF (feed)"
                elif skimmer_enable_feed_c == "False":
                    GPIO.output(pin, False)
                    return "ON"
            elif self.feed_CurrentMode == "D":
                skimmer_enable_feed_d = defs_common.readINIfile(outlet, "skimmer_enable_feed_d", "False")
                self.feed_PreviousMode = "D"
                if skimmer_enable_feed_d == "True":
                    GPIO.output(pin, True)
                    return "OFF (feed)"
                elif skimmer_enable_feed_d == "False":
                    GPIO.output(pin, False)
                    return "ON"
            else:
                difference = round(((int(self.feed_ExtraTimeSeed) + (int(self.feed_ExtraTimeAdded)*1000)) - int(round(time.time())*1000))/1000)
                if int(round(time.time())*1000) <= int(self.feed_ExtraTimeSeed) + (int(self.feed_ExtraTimeAdded)*1000):
                    #print("Extra feed time remaining: " + str(difference) + "s")
                    print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                       " Delay Mode: " + outlet + " (" + str(self.feed_ExtraTimeAdded) + "s) " + " Delay Time Remaining: " + str(round(difference)) + "s"
                       + Style.RESET_ALL)
                    GPIO.output(pin, True)
                    return "OFF (delay)"
                else:
                    GPIO.output(pin, False)
                    return "ON"
        else:
            GPIO.output(pin, True)
            return "OFF"


    def threadManager(self):
        connection1= pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel1 = connection1.channel()
        connection2= pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel2 = connection2.channel()
        t1 = threading.Thread(target=self.handle_rpc, args=(channel1,))
        t1.daemon = True
        self.threads.append(t1)
        t1.start()
        
        t2 = threading.Thread(target=self.apploop, args=(channel2,))
        t2.daemon = True
        self.threads.append(t2)
        t2.start()

        for t in self.threads:
          t.join()

    def handle_rpc(self,channel):    
        channel.queue_declare(queue='rpc_queue')
        self.logger.info("Waiting for rpc messages...")

        def callback(ch, method, props, body):
            
            body = body.decode()
            body = json.loads(body)
            response = ""

            self.logger.debug("[handle_rpc:callback] ch=" + str(ch) + " method=" + str(method) + " props=" + str(props) + " body-" + str(body))
            defs_common.logtoconsole(str(body["rpc_req"]), fg="MAGENTA", style="BRIGHT")

            # handle the RPC calls
            if str(body["rpc_req"]) == "get_probedata24h":
                defs_common.logtoconsole("RPC: " + str(body["rpc_req"]) + " [" + str(body["probetype"]) + ", " + str(body["probeid"]) + "]", fg="GREEN", style="BRIGHT")
                self.logger.info("RPC: " + str(body["rpc_req"]) + " [" + str(body["probetype"]) + ", " + str(body["probeid"]) + "]")
                #probelogdata = self.get_probedata24h(str(body["probetype"]), str(body["probeid"]))
                probelogdata = self.get_probedatadays(str(body["probetype"]), str(body["probeid"]), 2) # 2 days to ensure you get yesterdays data too

                try:
                    response = {
                               "datetime": probelogdata[0],
                               "probevalue": probelogdata[1],
                            }
                    response = json.dumps(response)
                    self.logger.debug(str(response))
                except:
                   pass

            elif str(body["rpc_req"]) == "get_probedatadays":
                defs_common.logtoconsole("RPC: " + str(body["rpc_req"]) + " [" + str(body["probetype"])
                                         + ", " + str(body["probeid"]) + ", " + str(body["numdays"])
                                         + "]", fg="GREEN", style="BRIGHT")
                self.logger.info("RPC: " + str(body["rpc_req"]) + " [" + str(body["probetype"]) + ", " + str(body["probeid"]) + ", " + str(body["numdays"]) + "]")
                #probelogdata = self.get_probedata24h(str(body["probetype"]), str(body["probeid"]))
                probelogdata = self.get_probedatadays(str(body["probetype"]), str(body["probeid"]), int(body["numdays"])) # 2 days to ensure you get yesterdays data too

                try:
                    response = {
                               "datetime": probelogdata[0],
                               "probevalue": probelogdata[1],
                            }
                    response = json.dumps(response)
                    self.logger.debug(str(response))
                except:
                   pass
                
            elif str(body["rpc_req"]) == "get_probelist":
                defs_common.logtoconsole("RPC: " + str(body["rpc_req"]), fg="GREEN", style="BRIGHT")
                self.logger.info("RPC: " + str(body["rpc_req"]))
                probelist = self.get_probelist()
                response = {
                            "probelist":probelist
                            }
                response = json.dumps(response)
                self.logger.debug(str(response))
                
            elif str(body["rpc_req"]) == "get_outletlist":
                defs_common.logtoconsole("RPC: " + str(body["rpc_req"]), fg="GREEN", style="BRIGHT")
                self.logger.info("RPC: " + str(body["rpc_req"]))
                outletlist = self.get_outletlist()
                #print(outletlist)
                #print (Fore.GREEN + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
                #        + " RPC: " + str(body["rpc_req"]) + Style.RESET_ALL)
                response = {
                            "outletlist":outletlist
                            }

                response = json.dumps(response)
                self.logger.debug(str(response))

            elif str(body["rpc_req"]) == "set_outletoperationmode":
                defs_common.logtoconsole("set_outletoperationmode " + str(body), fg="GREEN", style="BRIGHT")
                self.logger.info("set_outletoperationmode " + str(body))
                outlet = str(str(body["bus"]) + "_outlet" + str(body["outletnum"]))
                mode = str(body["opmode"]).upper()

                # bad things happened when I tried to control outlets from this thread
                # allow control to happen in the other thread by just changing the dictionary value
                self.int_outlet_buttonstates[str(outlet) + "_buttonstate"] = mode

            elif str(body["rpc_req"]) == "set_feedmode":
                defs_common.logtoconsole("set_feedmode " + str(body), fg="GREEN", style="BRIGHT")
                self.logger.info("set_feedmode " + str(body))
                self.feed_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
                defs_common.logtoconsole("Mode is " + str(body["feedmode"]), fg="BLUE", style="BRIGHT")
                self.feed_CurrentMode = str(body["feedmode"])
                self.feed_PreviousMode = "CANCEL"
                

                # if feed mode was cancelled, broadcast it out 
                if self.feed_CurrentMode == "CANCEL":
                    self.broadcastFeedStatus(self.feed_CurrentMode, "0")

            else:
                response = {
                               "rpc_ack": "Error"
                            }
                respose = json.dumps(response)
                
                self.logger.debug(str(response))



            ch.basic_publish(exchange='',
                      routing_key=props.reply_to,
                      properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                      body=str(response))
            ch.basic_ack(delivery_tag = method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback, queue='rpc_queue')
        channel.start_consuming()


    def broadcastProbeStatus(self, probetype, probeid, probeval):   
        message = {
            "status_currentprobeval":
                      {
                        "probetype": str(probetype),
                        "probeid": str(probeid),
                        "probeval": str(probeval)
                      }
                  }
        
        message = json.dumps(message)
            
        self.channel2.basic_publish(exchange='rbp_currentstatus',
            routing_key='',
            body=message)

    def broadcastFeedStatus(self, feedmode, timeremaining):   
        message = {
            "status_feedmode":
                      {
                        "feedmode": str(feedmode),
                        "timeremaining": str(timeremaining),
                      }
                  }
        
        message = json.dumps(message)
            
        self.channel2.basic_publish(exchange='rbp_currentstatus',
            routing_key='',
            body=message)


    def broadcastOutletStatus(self, outletid, outletname, outletbus, control_type, button_state, outletstate, statusmsg):   
        message = {
            "status_currentoutletstate" :
                      {
                        "outletid": str(outletid),
                        "outletname": str(outletname),
                        "outletbus": str(outletbus),
                        "control_type": str(control_type),
                        "button_state": str(button_state),
                        "outletstate": str(outletstate),
                        "statusmsg": str(statusmsg)
                      }
                  }
     
        message = json.dumps(message)
            
        self.channel2.basic_publish(exchange='rbp_currentstatus',
            routing_key='',
            body=message)

    def readTempProbes(self, tempProbeDict):
        self.tempProbeDict.clear()
        config = configparser.ConfigParser()
        config.read(defs_common.CONFIGFILENAME)
        # loop through each section and see if it is a ds18b20 temp probe
        for section in config:
            if section.split("_")[0] == "ds18b20":
                probe = tempProbeClass()
                probe.probeid = section.split("_")[1]
                probe.name = config[section]["name"]
                tempProbeDict [section.split("_")[1]] = probe

                self.logger.info("read temperature probe from config: probeid = " + probe.probeid + ", probename = " + probe.name)

    def readOutletPrefs(self, outletDict):
        outletDict.clear()
        config = configparser.ConfigParser()
        config.read(defs_common.CONFIGFILENAME)
        # loop through each section and see if it is a ds18b20 temp probe
        for section in config:
            #if section.split("_")[1] == "":
            if "int_outlet" in section:
                outlet = outletPrefs()
                outlet.ischanged            = "False"
                outlet.outletid             = section
                outlet.outletname           = defs_common.readINIfile(section, "name", "Unnamed", logger=self.logger)
                outlet.control_type         = defs_common.readINIfile(section, "control_type", "Always", logger=self.logger)
                outlet.always_state         = defs_common.readINIfile(section, "always_state", "OFF", logger=self.logger)
                outlet.enable_log           = defs_common.readINIfile(section, "enable_log", "False", logger=self.logger)
                outlet.heater_probe         = defs_common.readINIfile(section, "heater_probe", "", logger=self.logger)
                outlet.heater_on            = defs_common.readINIfile(section, "heater_on", "25.0", logger=self.logger)
                outlet.heater_off           = defs_common.readINIfile(section, "heater_off", "25.5", logger=self.logger)
                outlet.button_state         = defs_common.readINIfile(section, "button_state", "OFF", logger=self.logger)
                outlet.light_on             = defs_common.readINIfile(section, "light_on", "08:00", logger=self.logger)
                outlet.light_off            = defs_common.readINIfile(section, "light_off", "17:00", logger=self.logger)
                outlet.return_enable_feed_a = defs_common.readINIfile(section, "return_enable_feed_a", "False", logger=self.logger)
                outlet.return_feed_delay_a  = defs_common.readINIfile(section, "return_feed_delay_a", "0", logger=self.logger)
                outlet.return_enable_feed_b = defs_common.readINIfile(section, "return_enable_feed_b", "False", logger=self.logger)
                outlet.return_feed_delay_b  = defs_common.readINIfile(section, "return_feed_delay_b", "0", logger=self.logger)
                outlet.return_enable_feed_c = defs_common.readINIfile(section, "return_enable_feed_c", "False", logger=self.logger)
                outlet.return_feed_delay_c  = defs_common.readINIfile(section, "return_feed_delay_c", "0", logger=self.logger)
                outlet.return_enable_feed_d = defs_common.readINIfile(section, "return_enable_feed_d", "False", logger=self.logger)
                outlet.return_feed_delay_d  = defs_common.readINIfile(section, "return_feed_delay_d", "0", logger=self.logger)

                outletDict[section] = outlet

                self.logger.info("read outlet prefs from config: probeid = " + outlet.outletid + ", outletname = " + outlet.outletname)
               

    def get_probelist(self):
        probedict = {}
        config = configparser.ConfigParser()
        config.read(defs_common.CONFIGFILENAME)
        # loop through each section and see if it is a ds18b20 temp probe
        for section in config:
            #print(section)
            if section.split("_")[0] == "ds18b20":
                probetype = section.split("_")[0]
                probeid = section
                probename = config[section]["name"]
                sensortype = "temperature"
                probedict[probeid]={"probetype": probetype, "probeid": probeid, "probename": probename, "sensortype": sensortype}
                
            if section == "dht11/22":
                    if config[section]["enabled"]:
                        probetype = "dht"
                        probeid = "dht_t"
                        probename = config[section]["temperature_name"]
                        sensortype = "temperature"
                        probedict[probeid]={"probetype": probetype, "probeid": probeid, "probename": probename, "sensortype": sensortype}

                        probetype = "dht"
                        probeid = "dht_h"
                        probename = config[section]["humidity_name"]
                        sensortype = "humidity"
                        probedict[probeid]={"probetype": probetype, "probeid": probeid, "probename": probename, "sensortype": sensortype}

            if section == "mcp3008":
                #print(config[section]["ch0_enabled"])
                if config[section]["ch0_enabled"] == "True": 
                    probetype = "mcp3008"
                    probeid = "mcp3008_ch0"
                    probename = config[section]["ch0_name"]
                    sensortype = config[section]["ch0_type"]
                    probedict[probeid]={"probetype": probetype, "probeid": probeid, "probename": probename, "sensortype": sensortype}
          
                if  config[section]["ch1_enabled"] == "True": 
                    probetype = "mcp3008"
                    probeid = "mcp3008_ch1"
                    probename = config[section]["ch1_name"]
                    sensortype = config[section]["ch1_type"]
                    probedict[probeid]={"probetype": probetype, "probeid": probeid, "probename": probename, "sensortype": sensortype}
    
        return probedict


    def get_outletlist(self):
        outletdict = {}
        config = configparser.ConfigParser()
        config.read(defs_common.CONFIGFILENAME)
        # loop through each section and see if it is an outlet on internl bus
        
        for section in config:
            #print(section)
            #if section.find("int_outlet") > -1 or section.find("ext_outlet") > -1:
            if section.find("int_outlet") > -1:
                outletid = section
                outletname = config[section]["name"]
                outletbus = section.split("_")[0]
                control_type = config[section]["control_type"]
                #print (outletname)
                outletdict[outletid]={"outletid": outletid, "outletname": outletname, "outletbus": outletbus, "control_type": control_type}
    
        return outletdict    



    #def get_probedata24h(self, probetype, probeid):
    def get_probedatadays(self, probetype, probeid, numdays):
        if probetype == "":
           return
          
        #days_to_plot = 2
        days_to_plot = numdays
        
        xList = [] # datetime
        yList = [] # temp in C or other probe data
        zList = [] # temp in F
        for d in reversed(range(0,days_to_plot)):
            
            DateSeed = datetime.now() - timedelta(days=d)
            TimeSeed = datetime.now()
            LogFileName = probeid + "_" + DateSeed.strftime("%Y-%m-%d") + ".txt"
            #print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Reading data points from: %s" % LogFileName)
            self.logger.info("Reading data points from: %s" % LogFileName)
            
            try:
                pullData = open("logs/" + LogFileName,"r").read()    
                dataList = pullData.split('\n')
                
                for index, eachLine in enumerate(dataList):
                    if len(eachLine) > 1:
                        if probetype == "ds18b20" or probeid == "dht_t":
                            x, y, z = eachLine.split(',')
                        else:
                            x, y = eachLine.split(',')
                        x = datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
                        if d==1: # in yesterdays log file (0 is today, 1 is yesterday etc...)
                            if x.strftime("%H:%M:%S") >= TimeSeed.strftime("%H:%M:%S"): # we only want data for last 24 hours, so ignore values created before that
                                #print("D=0" + " x= " + str(x.strftime("%H:%M:%S")) + " TimeSeed = " + str(TimeSeed.strftime("%H:%M:%S")))
                                xList.append(x.strftime("%Y-%m-%d %H:%M:%S"))
                                yList.append(y)
                                if probetype == "ds18b20" or probeid == "dht_t":
                                    zList.append(z)
                        else:
                            xList.append(x.strftime("%Y-%m-%d %H:%M:%S"))
                            yList.append(y)
                            if probetype == "ds18b20" or probeid == "dht_t":
                                zList.append(z)
                
            except:
            #    print("Error parsing: %s" % LogFileName)
                self.logger.error("Error parsing: %s" % LogFileName)
        if probetype == "ds18b20" or probeid == "dht_t":
            if  str(defs_common.readINIfile("global", "tempscale", str(defs_common.SCALE_C))) == str(defs_common.SCALE_F):
                return xList, zList
            else:
                return xList, yList
        else:
            return xList, yList

    
############################################################################################################################
#
#  Main application loop
#
############################################################################################################################
    def apploop(self, channel):
        while True:
##            ##########################################################################################
##            # read ph probe
##            #
##            # this probe is suseptable to noise and interference, we will take a suffiently large data
##            # set and filter out the bad data, or outliers so we can get a better data point
##            ##########################################################################################
##            # only read the ph data at every ph_SamplingInterval (ie: 500ms or 1000ms)
##            if (int(round(time.time()*1000)) - self.ph_SamplingTimeSeed) > self.ph_SamplingInterval:
##                # read the analog pin
##                ph_dv = mcp3008.readadc(GPIO_config.ph_adc, GPIO_config.SPICLK, GPIO_config.SPIMOSI,
##                                         GPIO_config.SPIMISO, GPIO_config.SPICS)
##                ph_dvlist.append(ph_dv)
##                #print (len(ph_ListCounts),":", ph_dv)
##
##                # once we hit our desired sample size of ph_numsamples (ie: 120)
##                # then calculate the average value
##                if len(ph_dvlist) >= ph_numsamples:
##                    # The ph probe may pick up noise and read very high or
##                    # very low values that we know are not good values. We are going to use numpy
##                    # to calculate the standard deviation and remove the outlying data that is
##                    # ph_Sigma standard deviations away from the mean.  This way these outliers
##                    # do not affect our ph results
##                    ph_FilteredCounts = numpy.array(ph_dvlist)
##                    ph_FilteredMean = numpy.mean(ph_FilteredCounts, axis=0)
##                    ph_FlteredSD = numpy.std(ph_FilteredCounts, axis=0)
##                    ph_dvlistfiltered = [x for x in ph_FilteredCounts if
##                                            (x > ph_FilteredMean - ph_Sigma * ph_FlteredSD)]
##                    ph_dvlistfiltered = [x for x in ph_dvlistfiltered if
##                                            (x < ph_FilteredMean + ph_Sigma * ph_FlteredSD)]
##                    
##                    # calculate the average of our filtered list
##                    try:
##                        ph_AvgCountsFiltered = int(sum(ph_dvlistfiltered)/len(ph_dvlistfiltered))
##                    except:
##                        ph_AvgCountsFiltered = 1  # need to revisit this error handling. Exception thrown when all
##                                                  # values were 1023
##                        print("Error collecting data")  
##                    #convert digital value to ph
##                    ph_AvgFiltered = ph.dv2ph(ph_AvgCountsFiltered)
##
##                    # if enough time has passed (ph_LogInterval) then log the data to file
##                    # otherwise just print it to console
##                    timestamp = datetime.now()
##                    if (int(round(time.time()*1000)) - ph_LastLogTime) > ph_LogInterval:
##                        # sometimes a high value, like 22.4 gets recorded, i need to fix this, but for now don't log that
##                        if ph_AvgFiltered < 14.0:  
##                            RBP_commons.logprobedata(config['logs']['ph_log_prefix'], "{:.2f}".format(ph_AvgFiltered))
##                            RBP_commons.logprobedata("mcp3008_ch0_", "{:.2f}".format(ph_AvgFiltered))
##                            print(timestamp.strftime(Fore.CYAN + Style.BRIGHT + "%Y-%m-%d %H:%M:%S") + " ***Logged*** pH = "
##                                  + "{:.2f}".format(ph_AvgFiltered) + Style.RESET_ALL)
##                            ph_LastLogTime = int(round(time.time()*1000))
##                    else:
##                        print(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " pH = "
##                              + "{:.2f}".format(ph_AvgFiltered))
##                        #writeCurrentState('probes','ph', str("{:.2f}".format(ph_AvgFiltered)))
##                        channel.basic_publish(exchange='',
##                            routing_key='current_state',
##                            properties=pika.BasicProperties(expiration='10000'),
##                            body=str("mcp3008_0" + "," + timestamp.strftime("%Y-%m-%d %H:%M:%S") + "," + "{:.2f}".format(ph_AvgFiltered)))
##                        broadcastProbeStatus("mcp3008", "mcp3008_ch0", str("{:.2f}".format(ph_AvgFiltered))) 
##                    # clear the list so we can populate it with new data for the next data set
##                    ph_dvlist.clear()
##                    # record the new sampling time
##                    ph_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds





            ################################################################################################################
            # read dht11 temperature and humidity sensor
            #
            # these sensors are slow to refresh and should not be read more
            # than once every second or two (ie: dht_SamplingInterval = 3000ms or 5000ms for 3s or 5s) would be safe
            ################################################################################################################
            if (int(round(time.time()*1000)) - self.DHT_Sensor.get("dht11_samplingtimeseed")) > int(self.DHT_Sensor.get("dht11_samplinginterval")):    
                # let's read the dht11 temp and humidity data
                result = self.dht_sensor.read()
                if result.is_valid():
                    temp_c = result.temperature
                    temp_f = defs_common.convertCtoF(float(temp_c))
                    temp_f = float(temp_f)
                    hum = result.humidity
                    timestamp = datetime.now()

                    if str(self.temperaturescale) == str(defs_common.SCALE_F):
                        broadcasttemp = str("%.1f" % temp_f)
                    else:
                        broadcasttemp = str("%.1f" % temp_c)
                    
                    if (int(round(time.time()*1000)) - self.DHT_Sensor.get("dht11_lastlogtime")) > int(self.DHT_Sensor.get("dht11_loginterval")):
                        tempData = str("{:.1f}".format(temp_c)) + "," + str(temp_f)

                        # log and broadcast temperature value
                        defs_common.logprobedata("dht_t_", tempData)
                        defs_common.logtoconsole("***Logged*** [dht_t] " +  self.DHT_Sensor.get("temperature_name") + " = %.1f C" % temp_c + " | %.1f F" % temp_f, fg="CYAN", style="BRIGHT")
                        self.logger.info(str("***Logged*** [dht_t] " +  self.DHT_Sensor.get("temperature_name") + " = %.1f C" % temp_c + " | %.1f F" % temp_f))
                        self.broadcastProbeStatus("dht", "dht_t", str(broadcasttemp))

                        # log and broadcast humidity value
                        defs_common.logprobedata("dht_h_", "{:.0f}".format(hum))
                        defs_common.logtoconsole("***Logged*** [dht_h] " +  self.DHT_Sensor.get("humidity_name") + " = %d %%" % hum, fg="CYAN", style="BRIGHT")
                        self.logger.info(str("***Logged*** [dht_h] " +  self.DHT_Sensor.get("humidity_name") + " = %d %%" % hum))
                        self.broadcastProbeStatus("dht", "dht_h", str(hum)) 
                        
                        self.DHT_Sensor["dht11_lastlogtime"] = int(round(time.time()*1000))
                    else:
                        self.logger.info(str("[dht_t] " +  self.DHT_Sensor.get("temperature_name") + " = %.1f C" % temp_c + " | %.1f F" % temp_f))
                        self.logger.info(str("[dht_h] " +  self.DHT_Sensor.get("humidity_name") + " = %d %%" % hum))

                        # broadcast humidity value
                        self.broadcastProbeStatus("dht", "dht_h", str(hum))    
                        # broadcast temperature value
                        self.broadcastProbeStatus("dht", "dht_t", str(broadcasttemp))
                        
                    # record the new sampling time
                    self.DHT_Sensor["dht11_samplingtimeseed"] = int(round(time.time()*1000)) #convert time to milliseconds

            ##########################################################################################
            # read ds18b20 temperature sensor
            #
            # we support multiple probes, so work from the probe dictionary and get data
            # for each
            ##########################################################################################
            # read data from the temperature probes
            if (int(round(time.time()*1000)) - self.ds18b20_SamplingTimeSeed) > self.ds18b20_SamplingInterval:
                for p in self.tempProbeDict:
                    try:
                        timestamp = datetime.now()
                        dstempC =  float(ds18b20.read_temp("C"))
                        dstempF = defs_common.convertCtoF(float(dstempC))
                        dstempF = float(dstempF)
                        tempData = str(dstempC) + "," + str(dstempF)
                        
                        if str(self.temperaturescale) == str(defs_common.SCALE_F):
                            broadcasttemp = str("%.1f" % dstempF)
                        else:
                            broadcasttemp = str("%.1f" % dstempC)
                        
                        self.tempProbeDict[p].lastLogTime = self.ds18b20_LastLogTimeDict

                        if (int(round(time.time()*1000)) - int(self.tempProbeDict[p].lastLogTime)) > self.ds18b20_LogInterval:
                            # log and broadcast temperature value
                            defs_common.logprobedata("ds18b20_" + self.tempProbeDict[p].probeid + "_", tempData)
                            defs_common.logtoconsole("***Logged*** [ds18b20_" + self.tempProbeDict[p].probeid + "] " +
                                                     self.tempProbeDict[p].name + str(" = {:.1f}".format(dstempC)) + " C | " + str("{:.1f}".format(dstempF)) +
                                                     " F", fg="CYAN", style="BRIGHT")
                            self.logger.info(str("***Logged*** [ds18b20_" + self.tempProbeDict[p].probeid + "] " +
                                                     self.tempProbeDict[p].name + str(" = {:.1f}".format(dstempC)) + " C | " + str("{:.1f}".format(dstempF))) +
                                                     " F")
                            self.broadcastProbeStatus("ds18b20", "ds18b20_" + self.tempProbeDict[p].probeid, str(broadcasttemp))

                            self.ds18b20_LastLogTimeDict = int(round(time.time()*1000))             
                            self.tempProbeDict[p].lastTemperature = dstempC
                        else:
                            self.logger.info(str("[ds18b20_" + self.tempProbeDict[p].probeid + "] " +
                                                     self.tempProbeDict[p].name + str(" = {:.1f}".format(dstempC)) + " C | " + str("{:.1f}".format(dstempF))) +
                                                     " F")
                            
                            # broadcast temperature value
                            self.broadcastProbeStatus("ds18b20", "ds18b20_" + str(self.tempProbeDict[p].probeid), str(broadcasttemp))   
                            self.tempProbeDict[p].lastTemperature = broadcasttemp
                    except:
                        print(Back.RED + Fore.WHITE + timestamp.strftime("%Y-%m-%d %H:%M:%S") +
                              " <<<Error>>> Can not read ds18b20_" + self.tempProbeDict[p].probeid + " temperature data!" + Style.RESET_ALL)
        
                # record the new sampling time
                self.ds18b20_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds


            ##########################################################################################
            # check if Feed mode is enabled
            #
            ##########################################################################################
            
            if self.feed_CurrentMode == "A":
                #defs_common.logtoconsole("++++++++++++++ FEED A +++++++++++++++", fg="MAGENTA", style="BRIGHT")
                self.feed_ModeTotaltime = defs_common.readINIfile("feed_timers", "feed_a", "60")
            elif self.feed_CurrentMode == "B":
                self.feed_ModeTotaltime = defs_common.readINIfile("feed_timers", "feed_b", "60")
            elif self.feed_CurrentMode == "C":
                self.feed_ModeTotaltime = defs_common.readINIfile("feed_timers", "feed_c", "60")
            elif self.feed_CurrentMode == "D":
                self.feed_ModeTotaltime = defs_common.readINIfile("feed_timers", "feed_d", "60")
            else:
                self.feed_ModeTotaltime = "0"

            if self.feed_CurrentMode != "CANCEL":
                self.feedTimeLeft = (int(self.feed_ModeTotaltime)*1000) - (int(round(time.time()*1000)) - self.feed_SamplingTimeSeed)
                if self.feedTimeLeft <=0:
                    print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                           " Feed Mode: " + self.feed_CurrentMode + " COMPLETE" + Style.RESET_ALL)
                    self.feed_CurrentMode = "CANCEL"
                    timestamp = datetime.now()
##                    channel.basic_publish(exchange='',
##                            routing_key='current_state',
##                            properties=pika.BasicProperties(expiration='10000'),
##                            body=str("feed_timer" + "," + timestamp.strftime("%Y-%m-%d %H:%M:%S") + "," + str(self.feed_CurrentMode) + "," + str(0)))

                    self.broadcastFeedStatus(self.feed_CurrentMode, self.feedTimeLeft)
                         
                    self.feed_ExtraTimeSeed = int(round(time.time()*1000))
                    print ("Extra time starts at: " + str(self.feed_ExtraTimeSeed) + " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:    
                    print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                           " Feed Mode: " + self.feed_CurrentMode + " (" + self.feed_ModeTotaltime + "s) " + "Time Remaining: " + str(round(self.feedTimeLeft/1000)) + "s"
                           + Style.RESET_ALL)
                    timestamp = datetime.now()
##                    channel.basic_publish(exchange='',
##                            routing_key='current_state',
##                            properties=pika.BasicProperties(expiration='10000'),
##                            body=str("feed_timer" + "," + timestamp.strftime("%Y-%m-%d %H:%M:%S") + "," + str(self.feed_CurrentMode) + "," + str(round(self.feedTimeLeft/1000))))
                    self.broadcastFeedStatus(self.feed_CurrentMode, round(self.feedTimeLeft/1000))
        






            ##########################################################################################
            # handle outlet states (turn outlets on or off)
            #
            ##########################################################################################
            #outlet1_control()
            # do each of the outlets on the internal bus (outlets 1-8)
            for x in range (1,9):
                status = self.outlet_control("int", str(x))
                
                self.broadcastOutletStatus("int_outlet_" + str(x),
                      defs_common.readINIfile("int_outlet_" + str(x), "name", "Unnamed", logger=self.logger),
                      "int",
                      defs_common.readINIfile("int_outlet_" + str(x), "control_type", "Always", logger=self.logger),
                      self.int_outlet_buttonstates.get("int_outlet" + str(x) + "_buttonstate"),
                      "STATEUNKNOWN",
                      status)

                self.logger.debug("int_outlet_" + str(x) +
                    " [label: " + defs_common.readINIfile("int_outlet_" + str(x), "name", "Unnamed", logger=self.logger) +
                    "] [type: " + defs_common.readINIfile("int_outlet_" + str(x), "control_type", "Always", logger=self.logger) +
                    "] [button: " + defs_common.readINIfile("int_outlet_" + str(x), "button_state", "OFF", logger=self.logger) +  
                    "] [status: " + str(status) + "]" +
                    " [pin: " + str(GPIO_config.int_outletpins.get("int_outlet_" + str(x))) + "]")
                    
##            ##########################################################################################
##            # broadcast current state of outlets
##            #
##            ##########################################################################################
##            if (int(round(time.time()*1000)) - self.outlet_SamplingTimeSeed) > self.outlet_SamplingInterval:
##
##
##                # do each of the outlets on the internal bus (outlets 1-8)
##                for x in range (1,9):
##                    status = self.outlet_control("int", str(x))
####                    channel.basic_publish(exchange='',
####                                    routing_key='current_state',
####                                    properties=pika.BasicProperties(expiration='10000'),
####                                    body=str("int_outlet_" + str(x) + "," + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + 
####                                         "," + int_outlet_buttonstates.get("int_outlet" + str(x) + "_buttonstate") + "," + str(status) +
####                                             "," + cfg_common.readINIfile("int_outlet_" + str(x), "name", "Unnamed")))
####                    
##
##                    self.broadcastOutletStatus("int_outlet_" + str(x),
##                                          defs_common.readINIfile("int_outlet_" + str(x), "name", "Unnamed", logger=self.logger),
##                                          "int",
##                                          defs_common.readINIfile("int_outlet_" + str(x), "control_type", "Always", logger=self.logger),
##                                          self.int_outlet_buttonstates.get("int_outlet" + str(x) + "_buttonstate"),
##                                          "STATEUNKNOWN",
##                                          status)
##
####                    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") +    
####                        " int_outlet_" + str(x) +
####                        " [label: " + defs_common.readINIfile("int_outlet_" + str(x), "name", "Unnamed", logger=self.logger) +
####                        "] [type: " + defs_common.readINIfile("int_outlet_" + str(x), "control_type", "Always", logger=self.logger) +
####                        "] [button: " + defs_common.readINIfile("int_outlet_" + str(x), "button_state", "OFF", logger=self.logger) +  
####                        "] [status: " + str(status) + "]" +
####                        " [pin: " + str(GPIO_config.int_outletpins.get("int_outlet_" + str(x))) + "]")
##                   
##                    self.logger.info("int_outlet_" + str(x) +
##                        " [label: " + defs_common.readINIfile("int_outlet_" + str(x), "name", "Unnamed", logger=self.logger) +
##                        "] [type: " + defs_common.readINIfile("int_outlet_" + str(x), "control_type", "Always", logger=self.logger) +
##                        "] [button: " + defs_common.readINIfile("int_outlet_" + str(x), "button_state", "OFF", logger=self.logger) +  
##                        "] [status: " + str(status) + "]" +
##                        " [pin: " + str(GPIO_config.int_outletpins.get("int_outlet_" + str(x))) + "]")
##                    
##                self.outlet_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
            ##########################################################################################
            # update configuration file with any change requests sitting in the queue
            ##########################################################################################
            if self.queue.qsize(  ) > 0:
                for i in range(0,self.queue.qsize()):
                    msg = self.queue.get(0)
                    self.logger.info("Configuration update: " + msg["outletid"] + " button_state to " + msg["button_state"])
                    defs_common.writeINIfile(msg["outletid"], "button_state", msg["button_state"], logger=self.logger)
                    print (msg)
                    print (self.queue.qsize(  ))
            ########################################################################################## 
            # pause to slow down the loop, otherwise CPU usage spikes as program is busy waiting
            ##########################################################################################            
            time.sleep(1)

class tempProbeClass():
    name = ""
    probeid = ""
    lastTemperature = "0"
    lastLogTime = ""

class outletPrefs():
    ischanged            = ""
    outletid             = ""
    outletname           = ""
    control_type         = ""
    always_state         = ""
    enable_log           = ""
    heater_probe         = ""
    heater_on            = ""
    heater_off           = ""
    button_state         = ""
    light_on             = ""
    light_off            = ""
    return_enable_feed_a = ""
    return_feed_delay_a  = ""
    return_enable_feed_b = ""
    return_feed_delay_b  = ""
    return_enable_feed_c = ""
    return_feed_delay_c  = ""
    return_enable_feed_d = ""
    return_feed_delay_d  = ""
  

    
root = RBP_server()

