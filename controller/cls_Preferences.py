import configparser
import time
import defs_common
import random
import string
import version

# default values to put into config file
INFLUXDB_URL = "http:/localhost:8086"
INFLUXDB_TOKEN = "ENTER_TOKEN_HERE"
INFLUXDB_ORG = "reefberrypi"
MYSQL_HOST = "localhost"
MYSQL_USER = "pi"
MYSQL_PASSWORD = "reefberry"
MYSQL_DATABASE = "reefberrypi"
MYSQL_PORT = "3306"
FLASK_PORT = "5000"

# default Username and Password for newly created databases
RBP_DEFAULT_USERNAME = "pi"
RBP_DEFAULT_PASSWORD = "reefberry"


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
    ch_probeid=""
    LastLogTime = ""
    lastValue = ""
    ch_dvcallist = []
    ch_dvcalFilteredMean = ""
    ch_dvcalFilteredSD = ""
    ch_dvcalFilteredCounts = []


class tempProbeClass():
    name = ""
    probeid = ""
    lastTemperature = ""
    lastLogTime = ""
    serialnum = ""

# class dhtSensorClass():
#     temperature_name = ""
#     humidity_name = ""
#     lastTemperature = ""
#     lastHumidity = ""

class dhtSensorClass():
    name = ""
    probeid = ""
    lastValue = ""
    sensortype = ""
    probetype = ""

class outletPrefs():
    ischanged = ""
    outletid = ""
    outletname = ""
    control_type = ""
    always_state = ""
    enable_log = ""
    heater_probe = ""
    heater_on = ""
    heater_off = ""
    button_state = ""
    light_on = ""
    light_off = ""
    return_enable_feed_a = ""
    return_feed_delay_a = ""
    return_enable_feed_b = ""
    return_feed_delay_b = ""
    return_enable_feed_c = ""
    return_feed_delay_c = ""
    return_enable_feed_d = ""
    return_feed_delay_d = ""
    skimmer_enable_feed_a = ""
    skimmer_feed_delay_a = ""
    skimmer_enable_feed_b = ""
    skimmer_feed_delay_b = ""
    skimmer_enable_feed_c = ""
    skimmer_feed_delay_c = ""
    skimmer_enable_feed_d = ""
    skimmer_feed_delay_d = ""
    ph_probe = ""
    ph_high = ""
    ph_low = ""
    ph_onwhen = ""
    outletstatus = ""
    enabled = ""



class AppPrefs():

    def __init__(self, logger, threadlock):
        self.logger = logger
        self.threadlock = threadlock
        self.initDictionaries()
        self.readInitPrefs()
        # self.readAllPrefs()
        self.feed_CurrentMode = "CANCEL"
        self.feed_PreviousMode = "CANCEL"
        self.feed_ExtraTimeSeed = int(round(time.time()*1000))  #extra time after feed is over
        self.feed_ExtraTimeAdded = 0 # initialze to 0 extra time added
        self.feed_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
        self.feed_a_time = ""
        self.feed_b_time = ""
        self.feed_c_time = ""
        self.feed_d_time = ""
        self.dht_enable = ""
        self.app_description = ""
        self.controller_version = version.CONTROLLER_VERSION

        self.dv_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
        # self.dv_SamplingInterval = int(defs_common.readINIfile('mcp3008', 'dv_samplinginterval', "1000", lock=controller.threadlock, logger=controller.logger)) # milliseconds
        # self.dv_LogInterval = int(defs_common.readINIfile('mcp3008', 'dv_loginterval', "300000", lock=controller.threadlock, logger=controller.logger)) # milliseconds
        self.dv_SamplingInterval = 1000 # milliseconds
        self.dv_LogInterval = 60000 # milliseconds




    def initDictionaries(self):
        self.outletDict = {}
        self.mcp3008Dict = {}
        self.tempProbeDict = {}
        self.dhtDict = {}

    def readInitPrefs(self):
        self.logger.info("read global prefs")

        # we will use this UID if no UID is already present in the prefs file
        uid = ''.join(
            [random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ1234567890") for n in range(8)])

        ##########################################################################################
        # read these prefs from config file
        ##########################################################################################
        self.appuid = defs_common.readINIfile('global',
                                              'appuid',
                                              str(uid),
                                              )

        self.logger.info("Application UID: " + self.appuid)

        # Influx DB and MQTT server settings
        self.influxdb_host = defs_common.readINIfile('global',
                                                     'influxdb_host',
                                                     INFLUXDB_URL,
                                                     lock=self.threadlock,
                                                     logger=self.logger)

        self.influxdb_org = defs_common.readINIfile('global',
                                                    'influxdb_org',
                                                    INFLUXDB_ORG,
                                                    lock=self.threadlock,
                                                    logger=self.logger)

        self.influxdb_token = defs_common.readINIfile('global',
                                                      'influxdb_token',
                                                      INFLUXDB_TOKEN,
                                                      lock=self.threadlock,
                                                      logger=self.logger)

        self.mqtt_broker_host = defs_common.readINIfile('global',
                                                        'mqtt_broker_host',
                                                        "127.0.0.1",
                                                        lock=self.threadlock,
                                                        logger=self.logger)

        self.mysql_host = defs_common.readINIfile('global',
                                                  'mysql_host',
                                                  MYSQL_HOST,
                                                  lock=self.threadlock,
                                                  logger=self.logger)

        self.mysql_user = defs_common.readINIfile('global',
                                                  'mysql_user',
                                                  MYSQL_USER,
                                                  lock=self.threadlock,
                                                  logger=self.logger)

        self.mysql_password = defs_common.readINIfile('global',
                                                      'mysql_password',
                                                      MYSQL_PASSWORD,
                                                      lock=self.threadlock,
                                                      logger=self.logger)

        self.mysql_database = defs_common.readINIfile('global',
                                                      'mysql_database',
                                                      MYSQL_DATABASE,
                                                      lock=self.threadlock,
                                                      logger=self.logger)
        
        self.mysql_port = defs_common.readINIfile('global',
                                                      'mysql_port',
                                                      MYSQL_PORT,
                                                      lock=self.threadlock,
                                                      logger=self.logger)
        
        self.flask_port = defs_common.readINIfile('global',
                                                     'flask_port',
                                                      FLASK_PORT,
                                                      lock=self.threadlock,
                                                      logger=self.logger)
