import configparser
import time
import defs_common

def read_preferences(controller):
    # read in the preferences

    controller.DHT_Sensor = {
        "enabled": defs_common.readINIfile('dht11/22', 'enabled', "False", lock=controller.threadlock, logger=controller.logger),
        "temperature_name": str(defs_common.readINIfile('dht11/22', 'temperature_name', "Ambient Temperature", lock=controller.threadlock, logger=controller.logger)), 
        "humidity_name": str(defs_common.readINIfile('dht11/22', 'humidity_name', "Humidity", lock=controller.threadlock, logger=controller.logger)), 
        "dht11_samplinginterval": int(defs_common.readINIfile('dht11/22', 'dht11_samplinginterval', "5000", lock=controller.threadlock, logger=controller.logger)), # milliseconds
        "dht11_loginterval": int(defs_common.readINIfile('dht11/22', 'dht11_loginterval', "300000", lock=controller.threadlock, logger=controller.logger)), # milliseconds
        }

    controller.temperaturescale =  int(defs_common.readINIfile('global', 'tempscale', "0", lock=controller.threadlock, logger=controller.logger)) 
    controller.ds18b20_SamplingInterval = int(defs_common.readINIfile('probes_ds18b20', 'ds18b20_samplinginterval', "5000", lock=controller.threadlock, logger=controller.logger)) # milliseconds
    controller.ds18b20_LogInterval = int(defs_common.readINIfile('probes_ds18b20', 'ds18b20_loginterval', "300000", lock=controller.threadlock, logger=controller.logger)) # milliseconds
    controller.outlet_SamplingInterval = int(defs_common.readINIfile('outlets', 'outlet_samplinginterval', "5000", lock=controller.threadlock, logger=controller.logger)) # milliseconds

    controller.int_outlet_buttonstates = {
        "int_outlet1_buttonstate":defs_common.readINIfile("int_outlet_1", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
        "int_outlet2_buttonstate":defs_common.readINIfile("int_outlet_2", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
        "int_outlet3_buttonstate":defs_common.readINIfile("int_outlet_3", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
        "int_outlet4_buttonstate":defs_common.readINIfile("int_outlet_4", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
        "int_outlet5_buttonstate":defs_common.readINIfile("int_outlet_5", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
        "int_outlet6_buttonstate":defs_common.readINIfile("int_outlet_6", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
        "int_outlet7_buttonstate":defs_common.readINIfile("int_outlet_7", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger),
        "int_outlet8_buttonstate":defs_common.readINIfile("int_outlet_8", "button_state", "OFF", lock=controller.threadlock, logger=controller.logger)
        }

    # read the temperature probes
    readTempProbes(controller)

    # read the outlet prefs
    readOutletPrefs(controller)
    for outlet in controller.outletDict:
        defs_common.logtoconsole("outlet prefs loaded for: " + str(controller.outletDict[outlet].outletname), fg="BLUE", Style="BRIGHT")

    # read the mcp3008 analog probe channels
    readmcp3008Prefs(controller)


def readmcp3008Prefs(controller):
    controller.mcp3008Dict.clear()
    controller.dv_SamplingInterval = int(defs_common.readINIfile('mcp3008', 'dv_samplinginterval', "1000", lock=controller.threadlock, logger=controller.logger)) # milliseconds
    controller.dv_LogInterval = int(defs_common.readINIfile('mcp3008', 'dv_loginterval', "300000", lock=controller.threadlock, logger=controller.logger)) # milliseconds

    # there are 8 channels on this chip
    for x in range(8):
        channel = analogChannelClass()
        channel.ch_num = x
        prefix = "ch" + str(x)
        channel.ch_name = defs_common.readINIfile("mcp3008", prefix + "_name", "Unnamed", lock=controller.threadlock, logger=controller.logger)
        channel.ch_enabled = defs_common.readINIfile("mcp3008", prefix + "_enabled", "False", lock=controller.threadlock, logger=controller.logger)
        channel.ch_type = defs_common.readINIfile("mcp3008", prefix + "_type", "raw", lock=controller.threadlock, logger=controller.logger)
        channel.ch_dvlist = []
        channel.ch_numsamples = defs_common.readINIfile("mcp3008", prefix + "_numsamples", "10", lock=controller.threadlock, logger=controller.logger) # how many samples to collect before averaging
        channel.ch_sigma = defs_common.readINIfile("mcp3008", prefix + "_sigma", "1", lock=controller.threadlock, logger=controller.logger) # how many standard deviations to clean up outliers
        channel.LastLogTime = int(round(time.time()*1000)) #convert time to milliseconds
        controller.mcp3008Dict [x] = channel


def readOutletPrefs(controller):
    controller.outletDict.clear()
    config = configparser.ConfigParser()
    config.read(defs_common.CONFIGFILENAME)
    # loop through each section and see if it is a ds18b20 temp probe
    for section in config:
        #if section.split("_")[1] == "":
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
            outlet.light_off            = defs_common.readINIfile(section, "light_off", "17:00", lock=controller.threadlock, logger=controller.logger)
            outlet.return_enable_feed_a = defs_common.readINIfile(section, "return_enable_feed_a", "False", lock=controller.threadlock, logger=controller.logger)
            outlet.return_feed_delay_a  = defs_common.readINIfile(section, "return_feed_delay_a", "0", lock=controller.threadlock, logger=controller.logger)
            outlet.return_enable_feed_b = defs_common.readINIfile(section, "return_enable_feed_b", "False", lock=controller.threadlock, logger=controller.logger)
            outlet.return_feed_delay_b  = defs_common.readINIfile(section, "return_feed_delay_b", "0", lock=controller.threadlock, logger=controller.logger)
            outlet.return_enable_feed_c = defs_common.readINIfile(section, "return_enable_feed_c", "False", lock=controller.threadlock, logger=controller.logger)
            outlet.return_feed_delay_c  = defs_common.readINIfile(section, "return_feed_delay_c", "0", lock=controller.threadlock, logger=controller.logger)
            outlet.return_enable_feed_d = defs_common.readINIfile(section, "return_enable_feed_d", "False", lock=controller.threadlock, logger=controller.logger)
            outlet.return_feed_delay_d  = defs_common.readINIfile(section, "return_feed_delay_d", "0", lock=controller.threadlock, logger=controller.logger)

            controller.outletDict[section] = outlet

            controller.logger.info("read outlet prefs from config: outletid = " + outlet.outletid + ", outletname = " + outlet.outletname)



def readTempProbes(controller):
    controller.threadlock.acquire()
    controller.tempProbeDict.clear()
    config = configparser.ConfigParser()
    config.read(defs_common.CONFIGFILENAME)
    # loop through each section and see if it is a ds18b20 temp probe
    for section in config:
        if section.split("_")[0] == "ds18b20":
            probe = tempProbeClass()
            probe.probeid = section.split("_")[1]
            probe.name = config[section]["name"]
            probe.lastLogTime = int(round(time.time()*1000)) #convert time to milliseconds
            controller.tempProbeDict [section.split("_")[1]] = probe

            controller.logger.info("read temperature probe from config: probeid = " + probe.probeid + ", probename = " + probe.name)
    controller.threadlock.release()
    
class analogChannelClass():
    # class for probes connected to mcp3008 a-d chip
    ch_num = ""
    ch_name = ""
    ch_enabled = ""
    ch_type = ""
    # list to hold the raw digital values
    ch_dvlist = []
    ch_numsamples = ""
    ch_sigma = ""
    LastLogTime = ""

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
