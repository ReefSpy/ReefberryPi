import configparser
import time
import defs_common
import random 
import string 


    
class analogChannelClass():
    # class for probes connected to mcp3008 a-d chip
    ch_num = ""
    ch_name = ""
    ch_enabled = ""
    ch_type = ""
    ch_ph_low = ""
    ch_ph_med = ""
    ch_ph_high = ""
    # list to hold the raw digital values
    ch_dvlist = []
    ch_numsamples = ""
    ch_sigma = ""
    LastLogTime = ""
    lastValue = ""

class tempProbeClass():
    name = ""
    probeid = ""
    lastTemperature = "0"
    lastLogTime = ""

class outletPrefs():
    ischanged             = ""
    outletid              = ""
    outletname            = ""
    control_type          = ""
    always_state          = ""
    enable_log            = ""
    heater_probe          = ""
    heater_on             = ""
    heater_off            = ""
    button_state          = ""
    light_on              = ""
    light_off             = ""
    return_enable_feed_a  = ""
    return_feed_delay_a   = ""
    return_enable_feed_b  = ""
    return_feed_delay_b   = ""
    return_enable_feed_c  = ""
    return_feed_delay_c   = ""
    return_enable_feed_d  = ""
    return_feed_delay_d   = ""
    skimmer_enable_feed_a = ""
    skimmer_feed_delay_a  = ""
    skimmer_enable_feed_b = ""
    skimmer_feed_delay_b  = ""
    skimmer_enable_feed_c = ""
    skimmer_feed_delay_c  = ""
    skimmer_enable_feed_d = ""
    skimmer_feed_delay_d  = ""
    ph_probe              = ""
    ph_high               = ""
    ph_low                = ""
    ph_onwhen             = ""

class AppPrefs():

    def __init__(self, controller):
        self.readAllPrefs(controller)

    def readAllPrefs(self, controller):
        
        self.outletDict = {}
        self.mcp3008Dict = {}
        self.tempProbeDict = {}

        self.readGlobalPrefs(controller)
        self.readTempProbes(controller)
        self.readOutletPrefs(controller)
        self.readmcp3008Prefs(controller)

        self.DHT_Sensor = {
            "enabled": defs_common.readINIfile('dht11/22', 'enabled', "False", lock=controller.threadlock, logger=controller.logger),
            "temperature_name": str(defs_common.readINIfile('dht11/22', 'temperature_name', "Ambient Temperature", lock=controller.threadlock, logger=controller.logger)), 
            "humidity_name": str(defs_common.readINIfile('dht11/22', 'humidity_name', "Humidity", lock=controller.threadlock, logger=controller.logger)), 
            "dht11_samplinginterval": int(defs_common.readINIfile('dht11/22', 'dht11_samplinginterval', "5000", lock=controller.threadlock, logger=controller.logger)), # milliseconds
            "dht11_loginterval": int(defs_common.readINIfile('dht11/22', 'dht11_loginterval', "300000", lock=controller.threadlock, logger=controller.logger)), # milliseconds
            }


        self.ds18b20_SamplingInterval = int(defs_common.readINIfile('probes_ds18b20', 'ds18b20_samplinginterval', "5000", lock=controller.threadlock, logger=controller.logger)) # milliseconds
        self.ds18b20_LogInterval = int(defs_common.readINIfile('probes_ds18b20', 'ds18b20_loginterval', "300000", lock=controller.threadlock, logger=controller.logger)) # milliseconds
        self.outlet_SamplingInterval = int(defs_common.readINIfile('outlets', 'outlet_samplinginterval', "5000", lock=controller.threadlock, logger=controller.logger)) # milliseconds

        self.int_outlet_buttonstates = {
            "int_outlet1_buttonstate":defs_common.readINIfile("int_outlet_1", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
            "int_outlet2_buttonstate":defs_common.readINIfile("int_outlet_2", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
            "int_outlet3_buttonstate":defs_common.readINIfile("int_outlet_3", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
            "int_outlet4_buttonstate":defs_common.readINIfile("int_outlet_4", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
            "int_outlet5_buttonstate":defs_common.readINIfile("int_outlet_5", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
            "int_outlet6_buttonstate":defs_common.readINIfile("int_outlet_6", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
            "int_outlet7_buttonstate":defs_common.readINIfile("int_outlet_7", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
            "int_outlet8_buttonstate":defs_common.readINIfile("int_outlet_8", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger)
            }

        # need the initial probe time seed to compare our sampling intervals against
        self.dv_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
        self.dv_SamplingInterval = int(defs_common.readINIfile('mcp3008', 'dv_samplinginterval', "1000", lock=controller.threadlock, logger=controller.logger)) # milliseconds
        self.dv_LogInterval = int(defs_common.readINIfile('mcp3008', 'dv_loginterval', "300000", lock=controller.threadlock, logger=controller.logger)) # milliseconds

        
        self.DHT_Sensor["dht11_lastlogtime"] = int(round(time.time()*1000)) #convert time to milliseconds
        self.DHT_Sensor["dht11_samplingtimeseed"] = int(round(time.time()*1000)) #convert time to milliseconds

        self.ds18b20_LastLogTime = int(round(time.time()*1000)) #convert time to milliseconds
        self.ds18b20_LastLogTimeDict = int(round(time.time()*1000)) #convert time to milliseconds
        self.ds18b20_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
        self.outlet_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds

        self.readFeedPrefs(controller)

    def readGlobalPrefs(self, controller):
        controller.logger.info("read global prefs")
        self.temperaturescale =  int(defs_common.readINIfile('global',
                                                             'tempscale',
                                                             "0",
                                                             lock=controller.threadlock,
                                                             logger=controller.logger)) 

  
        # Generate a random UID string with 8 random characters.
        # we will use this UID if no UID is already present in the prefs file
        uid = ''.join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890") for n in range(8)]) 

        self.appuid =  defs_common.readINIfile('global',
                                               'appuid',
                                                str(uid),
                                                lock=controller.threadlock,
                                                logger=controller.logger)
  
        controller.logger.info("App UID: " + str(self.appuid))

        # Influx DB and MQTT server settings
        self.influxdb_host =  defs_common.readINIfile('global',
                                                          'influxdb_host',
                                                          "127.0.0.1",
                                                          lock=controller.threadlock,
                                                          logger=controller.logger) 

        self.influxdb_port =  defs_common.readINIfile('global',
                                                          'influxdb_port',
                                                          "8086",
                                                          lock=controller.threadlock,
                                                          logger=controller.logger) 
                                                 
        self.mqtt_broker_host =  defs_common.readINIfile('global',
                                                          'mqtt_broker_host',
                                                          "127.0.0.1",
                                                          lock=controller.threadlock,
                                                          logger=controller.logger) 

        
    def readFeedPrefs(self, controller):
        # need initial feed timer seed to compare our times against
        self.feed_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
        self.feed_CurrentMode = "CANCEL" #initialize with feed mode cancel to it is off
        self.feed_PreviousMode = "CANCEL"
        self.feed_ExtraTimeSeed = int(round(time.time()*1000))  #extra time after feed is over
        self.feed_ExtraTimeAdded = 0 # initialze to 0 extra time added

        self.feed_a_time = defs_common.readINIfile("feed_timers", "feed_a", "60", lock=controller.threadlock, logger=controller.logger)
        self.feed_b_time = defs_common.readINIfile("feed_timers", "feed_b", "60", lock=controller.threadlock, logger=controller.logger)
        self.feed_c_time = defs_common.readINIfile("feed_timers", "feed_c", "60", lock=controller.threadlock, logger=controller.logger)
        self.feed_d_time = defs_common.readINIfile("feed_timers", "feed_d", "60", lock=controller.threadlock, logger=controller.logger)

        controller.logger.info("read feed timer prefs")
        

    def reloadDHTPrefs(self, controller):        
        self.DHT_Sensor = {
            "enabled": defs_common.readINIfile('dht11/22', 'enabled', "False", lock=controller.threadlock, logger=controller.logger),
            "temperature_name": str(defs_common.readINIfile('dht11/22', 'temperature_name', "Ambient Temperature", lock=controller.threadlock, logger=controller.logger)), 
            "humidity_name": str(defs_common.readINIfile('dht11/22', 'humidity_name', "Humidity", lock=controller.threadlock, logger=controller.logger)), 
            "dht11_samplinginterval": int(defs_common.readINIfile('dht11/22', 'dht11_samplinginterval', "5000", lock=controller.threadlock, logger=controller.logger)), # milliseconds
            "dht11_loginterval": int(defs_common.readINIfile('dht11/22', 'dht11_loginterval', "300000", lock=controller.threadlock, logger=controller.logger)), # milliseconds
            }
        self.DHT_Sensor["dht11_lastlogtime"] = int(round(time.time()*1000)) #convert time to milliseconds
        self.DHT_Sensor["dht11_samplingtimeseed"] = int(round(time.time()*1000)) #convert time to milliseconds
        
    def readTempProbes(self, controller):
        controller.threadlock.acquire()
        self.tempProbeDict.clear()
        config = configparser.ConfigParser()
        config.read(defs_common.CONFIGFILENAME)
        # loop through each section and see if it is a ds18b20 temp probe
        for section in config:
            if section.split("_")[0] == "ds18b20":
                probe = tempProbeClass()
                probe.probeid = section.split("_")[1]
                probe.name = config[section]["name"]
                probe.lastLogTime = int(round(time.time()*1000)) #convert time to milliseconds
                self.tempProbeDict [section.split("_")[1]] = probe

                controller.logger.info("read temperature probe from config: probeid = " + probe.probeid + ", probename = " + probe.name)
        controller.threadlock.release()

    def readOutletPrefs(self, controller):
        #controller.threadlock.acquire()
        self.outletDict.clear()
        config = configparser.ConfigParser()
        config.read(defs_common.CONFIGFILENAME)
        # loop through each section and see if it is an internal bus outlet
        for section in config:
            if "int_outlet" in section:
                outlet = outletPrefs()
                outlet.ischanged            = "False"
                outlet.outletid             = section
                outlet.outletname           = defs_common.readINIfile(section, "name", "Unnamed", lock=controller.threadlock, logger=controller.logger)
                outlet.control_type         = defs_common.readINIfile(section, "control_type", "Always", lock=controller.threadlock, logger=controller.logger)
                outlet.always_state         = defs_common.readINIfile(section, "always_state", "OFF", lock=controller.threadlock, logger=controller.logger)
                outlet.enable_log           = defs_common.readINIfile(section, "enable_log", "False", lock=controller.threadlock, logger=controller.logger)
                outlet.heater_probe         = defs_common.readINIfile(section, "heater_probe", "", lock=controller.threadlock, logger=controller.logger)
                outlet.heater_on            = defs_common.readINIfile(section, "heater_on", "25.0", lock=controller.threadlock, logger=controller.logger)
                outlet.heater_off           = defs_common.readINIfile(section, "heater_off", "25.5", lock=controller.threadlock, logger=controller.logger)
                outlet.button_state         = defs_common.readINIfile(section, "button_state", "OFF", lock=controller.threadlock, logger=controller.logger)
                outlet.light_on             = defs_common.readINIfile(section, "light_on", "08:00", lock=controller.threadlock, logger=controller.logger)
                outlet.light_off            = defs_common.readINIfile(section, "light_off", "17:00", logger=controller.logger)
                outlet.return_enable_feed_a = defs_common.readINIfile(section, "return_enable_feed_a", "False", lock=controller.threadlock, logger=controller.logger)
                outlet.return_feed_delay_a  = defs_common.readINIfile(section, "return_feed_delay_a", "0", lock=controller.threadlock, logger=controller.logger)
                outlet.return_enable_feed_b = defs_common.readINIfile(section, "return_enable_feed_b", "False", lock=controller.threadlock, logger=controller.logger)
                outlet.return_feed_delay_b  = defs_common.readINIfile(section, "return_feed_delay_b", "0", lock=controller.threadlock, logger=controller.logger)
                outlet.return_enable_feed_c = defs_common.readINIfile(section, "return_enable_feed_c", "False", lock=controller.threadlock, logger=controller.logger)
                outlet.return_feed_delay_c  = defs_common.readINIfile(section, "return_feed_delay_c", "0", lock=controller.threadlock, logger=controller.logger)
                outlet.return_enable_feed_d = defs_common.readINIfile(section, "return_enable_feed_d", "False", lock=controller.threadlock, logger=controller.logger)
                outlet.return_feed_delay_d  = defs_common.readINIfile(section, "return_feed_delay_d", "0", lock=controller.threadlock, logger=controller.logger)
                outlet.skimmer_enable_feed_a = defs_common.readINIfile(section, "skimmer_enable_feed_a", "False", lock=controller.threadlock, logger=controller.logger)
                outlet.skimmer_feed_delay_a  = defs_common.readINIfile(section, "skimmer_feed_delay_a", "0", lock=controller.threadlock, logger=controller.logger)
                outlet.skimmer_enable_feed_b = defs_common.readINIfile(section, "skimmer_enable_feed_b", "False", lock=controller.threadlock, logger=controller.logger)
                outlet.skimmer_feed_delay_b  = defs_common.readINIfile(section, "skimmer_feed_delay_b", "0", lock=controller.threadlock, logger=controller.logger)
                outlet.skimmer_enable_feed_c = defs_common.readINIfile(section, "skimmer_enable_feed_c", "False", lock=controller.threadlock, logger=controller.logger)
                outlet.skimmer_feed_delay_c  = defs_common.readINIfile(section, "skimmer_feed_delay_c", "0", lock=controller.threadlock, logger=controller.logger)
                outlet.skimmer_enable_feed_d = defs_common.readINIfile(section, "skimmer_enable_feed_d", "False", lock=controller.threadlock, logger=controller.logger)
                outlet.skimmer_feed_delay_d  = defs_common.readINIfile(section, "skimmer_feed_delay_d", "0", lock=controller.threadlock, logger=controller.logger)
                outlet.ph_probe              = defs_common.readINIfile(section, "ph_probe", "mcp3008_ch1", lock=controller.threadlock, logger=controller.logger)
                outlet.ph_high               = defs_common.readINIfile(section, "ph_high", "8.0", lock=controller.threadlock, logger=controller.logger)
                outlet.ph_low                = defs_common.readINIfile(section, "ph_low", "7.9", lock=controller.threadlock, logger=controller.logger)
                outlet.ph_onwhen             = defs_common.readINIfile(section, "ph_onwhen", "HIGH", lock=controller.threadlock, logger=controller.logger)
                
                self.outletDict[section] = outlet

                controller.logger.info("read outlet prefs from config: outletid = " + outlet.outletid + ", outletname = " + outlet.outletname)

        #controller.threadlock.release()

    def readmcp3008Prefs(self, controller):
        self.mcp3008Dict.clear()

        # there are 8 channels on this chip
        for x in range(8):
            channel = analogChannelClass()
            channel.ch_num = x
            prefix = "ch" + str(x)
            channel.ch_name = defs_common.readINIfile("mcp3008", prefix + "_name", "Unnamed", lock=controller.threadlock, logger=controller.logger)
            channel.ch_enabled = defs_common.readINIfile("mcp3008", prefix + "_enabled", "False", lock=controller.threadlock, logger=controller.logger)
            channel.ch_type = defs_common.readINIfile("mcp3008", prefix + "_type", "raw", lock=controller.threadlock, logger=controller.logger)
            channel.ch_ph_low = defs_common.readINIfile("mcp3008", prefix + "_ph_low", "900", lock=controller.threadlock, logger=controller.logger)
            channel.ch_ph_med = defs_common.readINIfile("mcp3008", prefix + "_ph_med", "800", lock=controller.threadlock, logger=controller.logger)
            channel.ch_ph_high = defs_common.readINIfile("mcp3008", prefix + "_ph_high", "700", lock=controller.threadlock, logger=controller.logger)
            channel.ch_dvlist = []
            channel.ch_numsamples = defs_common.readINIfile("mcp3008", prefix + "_numsamples", "10", lock=controller.threadlock, logger=controller.logger) # how many samples to collect before averaging
            channel.ch_sigma = defs_common.readINIfile("mcp3008", prefix + "_sigma", "1", lock=controller.threadlock, logger=controller.logger) # how many standard deviations to clean up outliers
            channel.LastLogTime = int(round(time.time()*1000)) #convert time to milliseconds
            self.mcp3008Dict [x] = channel

    def reloadPrefSection(self, controller, section):
        if "int_outlet" in section:
            outlet = outletPrefs()
            outlet.ischanged            = "False"
            outlet.outletid             = section
            outlet.outletname           = defs_common.readINIfile(section, "name", "Unnamed", lock=controller.threadlock, logger=controller.logger)
            outlet.control_type         = defs_common.readINIfile(section, "control_type", "Always", lock=controller.threadlock, logger=controller.logger)
            outlet.always_state         = defs_common.readINIfile(section, "always_state", "OFF", lock=controller.threadlock, logger=controller.logger)
            outlet.enable_log           = defs_common.readINIfile(section, "enable_log", "False", lock=controller.threadlock, logger=controller.logger)
            outlet.heater_probe         = defs_common.readINIfile(section, "heater_probe", "", lock=controller.threadlock, logger=controller.logger)
            outlet.heater_on            = defs_common.readINIfile(section, "heater_on", "25.0", lock=controller.threadlock, logger=controller.logger)
            outlet.heater_off           = defs_common.readINIfile(section, "heater_off", "25.5", lock=controller.threadlock, logger=controller.logger)
            outlet.button_state         = defs_common.readINIfile(section, "button_state", "OFF", lock=controller.threadlock, logger=controller.logger)
            outlet.light_on             = defs_common.readINIfile(section, "light_on", "08:00", lock=controller.threadlock, logger=controller.logger)
            outlet.light_off            = defs_common.readINIfile(section, "light_off", "17:00", logger=controller.logger)
            outlet.return_enable_feed_a = defs_common.readINIfile(section, "return_enable_feed_a", "False", lock=controller.threadlock, logger=controller.logger)
            outlet.return_feed_delay_a  = defs_common.readINIfile(section, "return_feed_delay_a", "0", lock=controller.threadlock, logger=controller.logger)
            outlet.return_enable_feed_b = defs_common.readINIfile(section, "return_enable_feed_b", "False", lock=controller.threadlock, logger=controller.logger)
            outlet.return_feed_delay_b  = defs_common.readINIfile(section, "return_feed_delay_b", "0", lock=controller.threadlock, logger=controller.logger)
            outlet.return_enable_feed_c = defs_common.readINIfile(section, "return_enable_feed_c", "False", lock=controller.threadlock, logger=controller.logger)
            outlet.return_feed_delay_c  = defs_common.readINIfile(section, "return_feed_delay_c", "0", lock=controller.threadlock, logger=controller.logger)
            outlet.return_enable_feed_d = defs_common.readINIfile(section, "return_enable_feed_d", "False", lock=controller.threadlock, logger=controller.logger)
            outlet.return_feed_delay_d  = defs_common.readINIfile(section, "return_feed_delay_d", "0", lock=controller.threadlock, logger=controller.logger)
            outlet.skimmer_enable_feed_a = defs_common.readINIfile(section, "skimmer_enable_feed_a", "False", lock=controller.threadlock, logger=controller.logger)
            outlet.skimmer_feed_delay_a  = defs_common.readINIfile(section, "skimmer_feed_delay_a", "0", lock=controller.threadlock, logger=controller.logger)
            outlet.skimmer_enable_feed_b = defs_common.readINIfile(section, "skimmer_enable_feed_b", "False", lock=controller.threadlock, logger=controller.logger)
            outlet.skimmer_feed_delay_b  = defs_common.readINIfile(section, "skimmer_feed_delay_b", "0", lock=controller.threadlock, logger=controller.logger)
            outlet.skimmer_enable_feed_c = defs_common.readINIfile(section, "skimmer_enable_feed_c", "False", lock=controller.threadlock, logger=controller.logger)
            outlet.skimmer_feed_delay_c  = defs_common.readINIfile(section, "skimmer_feed_delay_c", "0", lock=controller.threadlock, logger=controller.logger)
            outlet.skimmer_enable_feed_d = defs_common.readINIfile(section, "skimmer_enable_feed_d", "False", lock=controller.threadlock, logger=controller.logger)
            outlet.skimmer_feed_delay_d  = defs_common.readINIfile(section, "skimmer_feed_delay_d", "0", lock=controller.threadlock, logger=controller.logger)
            outlet.ph_probe              = defs_common.readINIfile(section, "ph_probe", "mcp3008_ch1", lock=controller.threadlock, logger=controller.logger)
            outlet.ph_high               = defs_common.readINIfile(section, "ph_high", "8.0", lock=controller.threadlock, logger=controller.logger)
            outlet.ph_low                = defs_common.readINIfile(section, "ph_low", "7.9", lock=controller.threadlock, logger=controller.logger)
            outlet.ph_onwhen             = defs_common.readINIfile(section, "ph_onwhen", "HIGH", lock=controller.threadlock, logger=controller.logger)

            self.outletDict[section] = outlet

            controller.logger.info("read outlet prefs from config: outletid = " + outlet.outletid + ", outletname = " + outlet.outletname)

        if "feed_timers" in section:
            self.readFeedPrefs(controller)

        if "global" in section:
            self.readGlobalPrefs(controller)

        if "mcp3008" in section:
            self.readmcp3008Prefs(controller)

        if "dht11/22" in section:
            self.reloadDHTPrefs(controller)
            
        
