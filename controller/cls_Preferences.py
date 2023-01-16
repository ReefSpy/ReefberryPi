##############################################################################
# cls_Preferences.py
#
# preference class
#
# Written by ReefSpy for the ReefBerry Pi, (c) 2023
# www.youtube.com/reefspy
##############################################################################
import configparser
import time
import defs_common
import random
import string


# default values to put into onfig file
INFLUXDB_URL = "http://argon1.local:8086"
INFLUXDB_TOKEN = "lZqJh3rEn6y4jDZqgQG19Vck53e2oryHLgHWd3qhoYZbwqGNJlbCkArZsG643ldFrEWPjmxWRdgnrtBnogp0jw=="
INFLUXDB_ORG = "reefberrypi"
MYSQL_HOST = "192.168.4.217"
MYSQL_USER = "root"
MYSQL_PASSWORD = "raspberry"
MYSQL_DATABASE = "reefberrypi"


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


class AppPrefs():

    def __init__(self, logger, threadlock):
        self.logger = logger
        self.threadlock = threadlock
        self.initDictionaries()
        self.readInitPrefs()
        # self.readAllPrefs()

    def initDictionaries(self):
        self.outletDict = {}
        self.mcp3008Dict = {}
        self.tempProbeDict = {}

    def readInitPrefs(self):
        self.logger.info("read global prefs")

        # we will use this UID if no UID is already present in the prefs file
        uid = ''.join(
            [random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890") for n in range(8)])

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
