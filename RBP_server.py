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
import numpy
import ph_sensor
import cls_Preferences
import defs_outletcontrol


class RBP_server:
    
    def __init__(self):

        self.threads=[]
        self.queue = queue.Queue()

        self.threadlock = threading.Lock()

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
        self.mcp3008Dict = {}

        #read prefs
        cls_Preferences.read_preferences(self)

        # set up the GPIO
        GPIO_config.initGPIO()

        # dht11 temperature and humidity sensor
        self.dht_sensor = dht11.DHT11(pin=GPIO_config.dht11)

        # list to hold the raw ph data
        #self.ph_dvlist = []             

        # need the initial probe time seed to compare our sampling intervals against
        self.dv_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
        
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
        controltype = defs_common.readINIfile(outlet, "control_type", "Always", lock=self.threadlock, logger=self.logger)
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
        # <<<<<< don't write to ini file from this thread!
        #defs_common.writeINIfile(bus + "_outlet_" + outletnum, "button_state", button_state)
        curstate = defs_common.readINIfile(outlet, "button_state", "OFF", lock=self.threadlock, logger=self.logger)
        if curstate != button_state:
            changerequest = {}
            changerequest["section"] = outlet
            changerequest["key"] = "button_state"
            changerequest["value"] = button_state
            self.logger.debug("outlet_control: change " + outlet + " button_state to " + button_state + " (from " + curstate + ")")
            self.queue.put(changerequest)        
        
        # control type ALWAYS
        if controltype == "Always":
            return defs_outletcontrol.handle_outlet_always(self, outlet, button_state, pin)   
        # control type HEATER    
        elif controltype == "Heater":
            return defs_outletcontrol.handle_outlet_heater(self, outlet, button_state, pin)
        # control type RETURN PUMP
        elif controltype == "Return Pump":
            return defs_outletcontrol.handle_outlet_returnpump(self, outlet, button_state, pin)
        elif controltype == "Skimmer":
            return defs_outletcontrol.handle_outlet_skimmer(self, outlet, button_state, pin)
        elif controltype == "Light":
            return defs_outletcontrol.handle_outlet_light(self, outlet, button_state, pin)


    def threadManager(self):
        connection1= pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel1 = connection1.channel()
        connection2= pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel2 = connection2.channel()
        connection3= pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel3 = connection3.channel()
        
        t1 = threading.Thread(target=self.handle_rpc, args=(channel1,))
        t1.daemon = True
        self.threads.append(t1)
        t1.start()
        
        t2 = threading.Thread(target=self.apploop, args=(channel2,))
        t2.daemon = True
        self.threads.append(t2)
        t2.start()

        t3 = threading.Thread(target=self.handle_nodered, args=(channel3,))
        t3.daemon = True
        self.threads.append(t3)
        t3.start()

        for t in self.threads:
          t.join()

    def handle_nodered(self, channel):
        channel.queue_declare(queue='rbp_nodered')
        self.logger.info("Waiting for node-red messages...")

        def callback(ch, method, props, body):
            
            body = body.decode()
            body = json.loads(body)
            response = ""

            self.logger.debug("[handle_nodered:callback] ch=" + str(ch) + " method=" + str(method) + " props=" + str(props) + " body-" + str(body))
            defs_common.logtoconsole(str(body["rpc_req"]), fg="MAGENTA", style="BRIGHT")

            if str(body["rpc_req"]) == "set_outletopmodenodered":
                defs_common.logtoconsole("set_outletopmodenodered " + str(body), fg="GREEN", style="BRIGHT")
                self.logger.info("set_outletopmodenodered " + str(body))
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

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback, no_ack = True, queue='rbp_nodered')
        channel.start_consuming()


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

            elif str(body["rpc_req"]) == "set_keepalive":
                # periodically, a call is sent out on the channel to ensure
                # Rabbit MQ knows it is alive and keeps connection open
                # just log it, don't do anything else
                defs_common.logtoconsole("set_keepalive " + str(body), fg="GREEN", style="BRIGHT")
                self.logger.debug("set_keepalive " + str(body))

            elif str(body["rpc_req"]) == "set_writeinifile":
                # write values to the configuration file
                defs_common.logtoconsole("set_writeinifile " + str(body), fg="GREEN", style="BRIGHT")
                self.logger.debug("set_writeinifile " + str(body))

                changerequest = {}
                changerequest["section"] = str(body["section"])
                changerequest["key"] = str(body["key"])
                changerequest["value"] = str(body["value"])
                self.queue.put(changerequest)

            elif str(body["rpc_req"]) == "get_readinifile":
                # read values from the configuration file
                defs_common.logtoconsole("get_readinifile " + str(body), fg="GREEN", style="BRIGHT")
                self.logger.debug("get_readinifile " + str(body))

                # do the read here
                returnval = defs_common.readINIfile(str(body["section"]), str(body["key"]), str(body["defaultval"]), lock=self.threadlock, logger=self.logger)
                
                # respond with result here...
                response = {
                            "readinifile":returnval
                            }

                response = json.dumps(response)
                self.logger.debug(str(response))

            
            else:
                response = {
                               "rpc_ack": "Error"
                            }
                respose = json.dumps(response)
                
                self.logger.debug(str(response))



            try:
                ch.basic_publish(exchange='',
                          routing_key=props.reply_to,
                          properties=pika.BasicProperties(correlation_id = \
                                                             props.correlation_id),
                          body=str(response))
                
                ch.basic_ack(delivery_tag = method.delivery_tag)
            except:
                print("error with RPC publish")

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
                for x in range (0,8):
                    if config[section]["ch" + str(x) + "_enabled"] == "True":
                        probetype = "mcp3008"
                        probeid = "mcp3008_ch" + str(x)
                        probename = config[section]["ch" + str(x) + "_name"]
                        sensortype = config[section]["ch" + str(x) + "_type"]
                        probedict[probeid]={"probetype": probetype, "probeid": probeid, "probename": probename, "sensortype": sensortype}
                        
    
        return probedict


    def get_outletlist(self):
        outletdict = {}
        config = configparser.ConfigParser()
        config.read(defs_common.CONFIGFILENAME)
        # loop through each section and see if it is an outlet on internl bus
        
        for section in config:
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
            if  str(defs_common.readINIfile("global", "tempscale", str(defs_common.SCALE_C), lock=self.threadlock, logger=self.logger)) == str(defs_common.SCALE_F):
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


            
            ##########################################################################################
            # read each of the 8 channels on the mcp3008
            # channels (0-7)
            ##########################################################################################
            # only read the data at every ph_SamplingInterval (ie: 500ms or 1000ms)
            if (int(round(time.time()*1000)) - self.dv_SamplingTimeSeed) > self.dv_SamplingInterval:
                #for x in range (0,8):
                for ch in self.mcp3008Dict:
                    if self.mcp3008Dict[ch].ch_enabled == "True":
                        #defs_common.logtoconsole(str(self.mcp3008Dict[ch].ch_num) + " " + str(self.mcp3008Dict[ch].ch_name) + " " + str(self.mcp3008Dict[ch].ch_enabled) + " " + str(len(self.mcp3008Dict[ch].ch_dvlist)))
                        dv = mcp3008.readadc(int(self.mcp3008Dict[ch].ch_num), GPIO_config.SPICLK, GPIO_config.SPIMOSI,
                                                GPIO_config.SPIMISO, GPIO_config.SPICS)

                        self.mcp3008Dict[ch].ch_dvlist.append(dv)
                        #self.logger.info(str(self.mcp3008Dict[ch].ch_num) + " " + str(self.mcp3008Dict[ch].ch_name) + " " + str(self.mcp3008Dict[ch].ch_dvlist))
                    # once we hit our desired sample size of ph_numsamples (ie: 120)
                    # then calculate the average value
                    if len(self.mcp3008Dict[ch].ch_dvlist) >= int(self.mcp3008Dict[ch].ch_numsamples):
                        # The probes may pick up noise and read very high or
                        # very low values that we know are not good values. We are going to use numpy
                        # to calculate the standard deviation and remove the outlying data that is
                        # Sigma standard deviations away from the mean.  This way these outliers
                        # do not affect our results
                        self.logger.info("mcp3008 ch" + str(self.mcp3008Dict[ch].ch_num) + " raw data " + str(self.mcp3008Dict[ch].ch_name) + " " + str(self.mcp3008Dict[ch].ch_dvlist))
                        dv_FilteredCounts = numpy.array(self.mcp3008Dict[ch].ch_dvlist)
                        dv_FilteredMean = numpy.mean(dv_FilteredCounts, axis=0)
                        dv_FlteredSD = numpy.std(dv_FilteredCounts, axis=0)
                        dv_dvlistfiltered = [x for x in dv_FilteredCounts if
                                            (x > dv_FilteredMean - float(self.mcp3008Dict[ch].ch_sigma) * dv_FlteredSD)]
                        dv_dvlistfiltered = [x for x in dv_dvlistfiltered if
                                            (x < dv_FilteredMean + float(self.mcp3008Dict[ch].ch_sigma) * dv_FlteredSD)]

                        self.logger.info("mcp3008 ch" + str(self.mcp3008Dict[ch].ch_num) + " filtered " + str(self.mcp3008Dict[ch].ch_name) + " " + str(dv_dvlistfiltered))
                    
                        # calculate the average of our filtered list
                        try:
                            dv_AvgCountsFiltered = int(sum(dv_dvlistfiltered)/len(dv_dvlistfiltered))
                            print( "{:.2f}".format(dv_AvgCountsFiltered)) ## delete this line
                        except:
                            dv_AvgCountsFiltered = 1  # need to revisit this error handling. Exception thrown when all
                                                      # values were 1023
                            print("Error collecting data")  

                        #self.mcp3008Dict[ch].ch_dvlist.clear()  ## delete  this line

                        if self.mcp3008Dict[ch].ch_type == "pH":
                            # bug, somtimes value is coming back high, like really high, like 22.0.  this is an impossible
                            # value since max ph is 14.  need to figure this out later, but for now, lets log this val to aid in
                            # debugging
                            orgval = dv_AvgCountsFiltered
                            
                            #convert digital value to ph
                            dv_AvgCountsFiltered = ph_sensor.dv2ph(dv_AvgCountsFiltered)
                            dv_AvgCountsFiltered = float("{:.2f}".format(dv_AvgCountsFiltered))

                            if dv_AvgCountsFiltered > 14:
                                self.logger.error("Invalid PH value: " + str(dv_AvgCountsFiltered) + " " + str(orgval) + " " + str(dv_dvlistfiltered))
                                defs_common.logtoconsole("Invalid PH value: " + str(dv_AvgCountsFiltered) + " " + str(orgval) + " " + str(dv_dvlistfiltered), fg="RED", style = "BRIGHT")

                        # if enough time has passed (ph_LogInterval) then log the data to file
                        # otherwise just print it to console
                        timestamp = datetime.now()
                        if (int(round(time.time()*1000)) - self.mcp3008Dict[ch].LastLogTime) > self.dv_LogInterval:
                            # sometimes a high value, like 22.4 gets recorded, i need to fix this, but for now don't log that
##                            if ph_AvgFiltered < 14.0:  
                            #RBP_commons.logprobedata(config['logs']['ph_log_prefix'], "{:.2f}".format(ph_AvgFiltered))
                            defs_common.logprobedata("mcp3008_ch" + str(self.mcp3008Dict[ch].ch_num) + "_", "{:.2f}".format(dv_AvgCountsFiltered))
                            print(timestamp.strftime(Fore.CYAN + Style.BRIGHT + "%Y-%m-%d %H:%M:%S") + " ***Logged*** dv = "
                                  + "{:.2f}".format(dv_AvgCountsFiltered) + Style.RESET_ALL)
                            self.mcp3008Dict[ch].LastLogTime = int(round(time.time()*1000))
                        else:
                            print(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " dv = "
                                  + "{:.2f}".format(dv_AvgCountsFiltered))

                        self.broadcastProbeStatus("mcp3008", "mcp3008_ch" + str(self.mcp3008Dict[ch].ch_num), (dv_AvgCountsFiltered)) 
                        # clear the list so we can populate it with new data for the next data set
                        self.mcp3008Dict[ch].ch_dvlist.clear()
                        # record the new sampling time
                        self.dv_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
                        
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
                        dstempC =  float(ds18b20.read_temp(self.tempProbeDict[p].probeid, "C"))
                        dstempF = defs_common.convertCtoF(float(dstempC))
                        dstempF = float(dstempF)
                        tempData = str(dstempC) + "," + str(dstempF)
                        
                        if str(self.temperaturescale) == str(defs_common.SCALE_F):
                            broadcasttemp = str("%.1f" % dstempF)
                        else:
                            broadcasttemp = str("%.1f" % dstempC)
                        
                        #self.tempProbeDict[p].lastLogTime = self.ds18b20_LastLogTimeDict

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

                            #self.ds18b20_LastLogTimeDict = int(round(time.time()*1000))
                            self.tempProbeDict[p].lastLogTime = int(round(time.time()*1000))
                            
                            self.tempProbeDict[p].lastTemperature = dstempC
                        else:
                            self.logger.info(str("[ds18b20_" + self.tempProbeDict[p].probeid + "] " +
                                                     self.tempProbeDict[p].name + str(" = {:.1f}".format(dstempC)) + " C | " + str("{:.1f}".format(dstempF))) +
                                                     " F")
                            
                            # broadcast temperature value
                            self.broadcastProbeStatus("ds18b20", "ds18b20_" + str(self.tempProbeDict[p].probeid), str(broadcasttemp))   
                            self.tempProbeDict[p].lastTemperature = broadcasttemp
                    except Exception as e:
                        defs_common.logtoconsole(Back.RED + Fore.WHITE + timestamp.strftime("<<<Error>>> Can not read ds18b20_" + self.tempProbeDict[p].probeid + " temperature data!", fg="WHITE", bg="RED", style="BRIGHT"))
                        self.logger.error ("<<<Error>>> Can not read ds18b20_" + self.tempProbeDict[p].probeid + " temperature data!")
                        self.logger.error (e)
                # record the new sampling time
                self.ds18b20_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds


            ##########################################################################################
            # check if Feed mode is enabled
            #
            ##########################################################################################
            
            if self.feed_CurrentMode == "A":
                self.feed_ModeTotaltime = defs_common.readINIfile("feed_timers", "feed_a", "60", lock=self.threadlock, logger=self.logger)
            elif self.feed_CurrentMode == "B":
                self.feed_ModeTotaltime = defs_common.readINIfile("feed_timers", "feed_b", "60", lock=self.threadlock, logger=self.logger)
            elif self.feed_CurrentMode == "C":
                self.feed_ModeTotaltime = defs_common.readINIfile("feed_timers", "feed_c", "60", lock=self.threadlock, logger=self.logger)
            elif self.feed_CurrentMode == "D":
                self.feed_ModeTotaltime = defs_common.readINIfile("feed_timers", "feed_d", "60", lock=self.threadlock, logger=self.logger)
            else:
                self.feed_ModeTotaltime = "0"

            if self.feed_CurrentMode != "CANCEL":
                self.feedTimeLeft = (int(self.feed_ModeTotaltime)*1000) - (int(round(time.time()*1000)) - self.feed_SamplingTimeSeed)
                if self.feedTimeLeft <=0:
                    print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                           " Feed Mode: " + self.feed_CurrentMode + " COMPLETE" + Style.RESET_ALL)
                    self.feed_CurrentMode = "CANCEL"
                    timestamp = datetime.now()

                    self.broadcastFeedStatus(self.feed_CurrentMode, self.feedTimeLeft)
                         
                    self.feed_ExtraTimeSeed = int(round(time.time()*1000))
                    print ("Extra time starts at: " + str(self.feed_ExtraTimeSeed) + " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:    
                    print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                           " Feed Mode: " + self.feed_CurrentMode + " (" + self.feed_ModeTotaltime + "s) " + "Time Remaining: " + str(round(self.feedTimeLeft/1000)) + "s"
                           + Style.RESET_ALL)
                    timestamp = datetime.now()

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
                      defs_common.readINIfile("int_outlet_" + str(x), "name", "Unnamed", lock=self.threadlock, logger=self.logger),
                      "int",
                      defs_common.readINIfile("int_outlet_" + str(x), "control_type", "Always", lock=self.threadlock, logger=self.logger),
                      self.int_outlet_buttonstates.get("int_outlet" + str(x) + "_buttonstate"),
                      "STATEUNKNOWN",
                      status)

                self.logger.debug("int_outlet_" + str(x) +
                    " [label: " + defs_common.readINIfile("int_outlet_" + str(x), "name", "Unnamed", lock=self.threadlock, logger=self.logger) +
                    "] [type: " + defs_common.readINIfile("int_outlet_" + str(x), "control_type", "Always", lock=self.threadlock, logger=self.logger) +
                    "] [button: " + defs_common.readINIfile("int_outlet_" + str(x), "button_state", "OFF", lock=self.threadlock, logger=self.logger) +  
                    "] [status: " + str(status) + "]" +
                    " [pin: " + str(GPIO_config.int_outletpins.get("int_outlet_" + str(x))) + "]")
                    

            ##########################################################################################
            # update configuration file with any change requests sitting in the queue
            ##########################################################################################
            if self.queue.qsize(  ) > 0:
                for i in range(0,self.queue.qsize()):
##                    msg = self.queue.get(0)
##                    self.logger.info("Configuration update: " + msg["outletid"] + " button_state to " + msg["button_state"])
##                    defs_common.writeINIfile(msg["outletid"], "button_state", msg["button_state"], logger=self.logger)
##                    print (msg)
##                    print (self.queue.qsize(  ))

                    msg = self.queue.get(0)
                    self.logger.info("Configuration update: [" + msg["section"] + "] [ " + msg["key"] + "] = " + msg["value"])
                    defs_common.writeINIfile(msg["section"], msg["key"], msg["value"], lock=self.threadlock, logger=self.logger)
                    print (msg)
                    print (self.queue.qsize())                    
            ########################################################################################## 
            # pause to slow down the loop, otherwise CPU usage spikes as program is busy waiting
            ##########################################################################################            
            time.sleep(1)


    
root = RBP_server()

