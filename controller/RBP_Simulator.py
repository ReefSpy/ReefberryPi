#!/usr/bin/python3

##############################################################################
# RBP_controller.py
#
# this module will pull data from the various input probes, control outlets,
# log data, and communicate with the messaging queue
#
# Written by ReefSpy for the ReefBerry Pi, (c) 2020
# www.youtube.com/reefspy
##############################################################################

from datetime import datetime, timedelta, time
from influxdb import InfluxDBClient
from colorama import Fore, Back, Style
import paho.mqtt.client as mqtt
import queue
import time
import threading
import logging
import logging.handlers
import configparser
import os.path
import defs_common
import cls_Preferences
# import GPIO_config
import ds18b20
# import RPi.GPIO as GPIO
# import dht11
import numpy
import ph_sensor
# import mcp3008
import json
import defs_outletcontrolsim
import jsonpickle


class RBP_controller:

    def __init__(self):

        defs_common.logtoconsole(
            "Application Start", fg="WHITE", style="BRIGHT")

        # self.threads = []
        self.queue = queue.Queue()

        self.threadlock = threading.Lock()

        LOG_FILEDIR = "logs"
        LOG_FILENAME = "RBP_controller.log"
        LOGLEVEL_CONSOLE = logging.DEBUG  # DEBUG, INFO, ERROR
        LOGLEVEL_LOGFILE = logging.INFO

        self.initialize_logger(LOG_FILEDIR, LOG_FILENAME,
                               LOGLEVEL_CONSOLE, LOGLEVEL_LOGFILE)

        self.logger.info("Reefberry Pi controller startup...")

        # read prefs
        self.AppPrefs = cls_Preferences.AppPrefs(self)
        self.refreshPrefs = False

        #AppPrefsJSON = jsonpickle.encode(self.AppPrefs)

        self.INFLUXDB_HOST = self.AppPrefs.influxdb_host
        self.INFLUXDB_PORT = self.AppPrefs.influxdb_port
        self.INFLUXDB_DBNAME = "reefberrypi"

        self.MQTT_BROKER_HOST = self.AppPrefs.mqtt_broker_host
        self.MQTT_USERNAME = "pi"
        self.MQTT_PASSWORD = "reefberry"

        # set up the GPIO
        # GPIO_config.initGPIO()

        # dht11 temperature and humidity sensor
        # self.dht_sensor = dht11.DHT11(pin=GPIO_config.dht11)

        # connect to InfluxDB
        self.InfluxDBclient = self.ConnectInfluxDB(
            self.INFLUXDB_HOST, self.INFLUXDB_PORT, self.INFLUXDB_DBNAME)

        # connect to MQTT broker
        # create new instance and assign the AppUID to it
        # self.MQTTclient = MyMQTTClass(self.AppPrefs.appuid)
        self.MQTTclient = mqtt.Client(self.AppPrefs.appuid)
        self.MQTTclient.on_connect = self.on_connect
        self.MQTTclient.on_message = self.on_message

        self.MQTTclient.on_publish = self.on_publish
        self.MQTTclient.on_subscribe = self.on_subscribe
        self.MQTTclient.on_log = self.on_log

        self.MQTTclient.username_pw_set(self.MQTT_USERNAME, self.MQTT_PASSWORD)
        self.MQTTclient.connect(self.MQTT_BROKER_HOST)
        self.MQTTclient.subscribe("reefberrypi/rpc")

        self.MQTTclient.loop_start()

        # self.threadManager()
        self.apploop()

    # MQTT callback functions
    def on_connect(self, mqttc, obj, flags, rc):
        print("rc: "+str(rc))

    def on_message(self, mqttc, obj, msg):
        # print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        self.logger.info("[MQTT Rx] " + str(msg.topic
                                            ) + " " + str(msg.payload.decode()))

        body = str(msg.payload.decode())
        print(body)
        body = json.loads(body)
        print(body)
        response = ""

        if str(body["rpc_req"]) == "get_probelist":
            defs_common.logtoconsole(
                "RPC: " + str(body["rpc_req"]), fg="GREEN", style="BRIGHT")
            self.logger.info("RPC: " + str(body["rpc_req"]))
            probelist = self.get_probelist()
            response = {
                "probelist": probelist,
                "uuid": str(body["uuid"]),
            }

            response = json.dumps(response)
            self.logger.debug(str(response))
            self.logger.info(str(response))

        elif str(body["rpc_req"]) == "get_outletlist":
            defs_common.logtoconsole(
                "RPC: " + str(body["rpc_req"]), fg="GREEN", style="BRIGHT")
            self.logger.info("RPC: " + str(body["rpc_req"]))
            outletlist = self.get_outletlist()
            # print(outletlist)
            # print (Fore.GREEN + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #        + " RPC: " + str(body["rpc_req"]) + Style.RESET_ALL)
            response = {
                "outletlist": outletlist,
                "uuid": str(body["uuid"]),

            }

            response = json.dumps(response)
            self.logger.debug(str(response))

        elif str(body["rpc_req"]) == "set_outletoperationmode":
            defs_common.logtoconsole(
                "set_outletoperationmode " + str(body), fg="GREEN", style="BRIGHT")
            self.logger.info("set_outletoperationmode " + str(body))
            outlet = str(str(body["bus"]) + "_outlet" + str(body["outletnum"]))
            outletnum = str(str(body["bus"]) +
                            "_outlet_" + str(body["outletnum"]))
            mode = str(body["opmode"]).upper()

            # bad things happened when I tried to control outlets from this thread
            # allow control to happen in the other thread by just changing the dictionary value
            self.AppPrefs.int_outlet_buttonstates[str(
                outlet) + "_buttonstate"] = mode

            self.broadcastOutletStatus(outlet,
                                       self.AppPrefs.outletDict[outletnum].outletname,
                                       "int",
                                       self.AppPrefs.outletDict[outletnum].control_type,
                                       self.AppPrefs.int_outlet_buttonstates.get(
                                           outletnum + "_buttonstate"),
                                       "STATEUNKNOWN",
                                       "Waiting...",
                                       str(body["uuid"]))

        elif str(body["rpc_req"]) == "get_probedata24h_ex":
            defs_common.logtoconsole("RPC: " + str(body["rpc_req"]) + " [" + str(
                body["probetype"]) + ", " + str(body["probeid"]) + "]", fg="GREEN", style="BRIGHT")
            self.logger.info("RPC: " + str(body["rpc_req"]) + " [" + str(
                body["probetype"]) + ", " + str(body["probeid"]) + "]")
            #probelogdata = self.get_probedata24h(str(body["probetype"]), str(body["probeid"]))
            probelogdata = self.get_probedatadays(str(body["probetype"]), str(
                body["probeid"]), 2)  # 2 days to ensure you get yesterdays data too

            try:
                response = {"probedata": {
                    "datetime": probelogdata[0],
                    "probevalue": probelogdata[1],
                    "probetype": str(body["probetype"]),
                    "probeid": str(body["probeid"]),
                },
                    "uuid": str(body["uuid"])
                }
                response = json.dumps(response)
                self.logger.debug(str(response))
            except:
                pass

        elif str(body["rpc_req"]) == "set_feedmode":
            defs_common.logtoconsole(
                "set_feedmode " + str(body), fg="GREEN", style="BRIGHT")
            self.logger.info("set_feedmode " + str(body))
            self.AppPrefs.feed_SamplingTimeSeed = int(
                round(time.time()*1000))  # convert time to milliseconds
            defs_common.logtoconsole(
                "Mode is " + str(body["feedmode"]), fg="BLUE", style="BRIGHT")

            self.AppPrefs.feed_CurrentMode = str(body["feedmode"])
            self.AppPrefs.feed_PreviousMode = "CANCEL"

            # if feed mode was cancelled, broadcast it out
            if self.AppPrefs.feed_CurrentMode == "CANCEL":
                self.broadcastFeedStatus(
                    self.AppPrefs.feed_CurrentMode, "0", "")

        elif str(body["rpc_req"]) == "set_writeinifile":
            # write values to the configuration file
            defs_common.logtoconsole(
                "set_writeinifile " + str(body), fg="GREEN", style="BRIGHT")
            self.logger.debug("set_writeinifile " + str(body))

            changerequest = {}
            changerequest["section"] = str(body["section"])
            changerequest["key"] = str(body["key"])
            changerequest["value"] = str(body["value"])
            self.queue.put(changerequest)

        elif str(body["rpc_req"]) == "get_readinifile":
            # read values from the configuration file
            defs_common.logtoconsole(
                "get_readinifile " + str(body), fg="GREEN", style="BRIGHT")
            self.logger.debug("get_readinifile " + str(body))

            # do the read here
            returnval = defs_common.readINIfile(str(body["section"]), str(body["key"]), str(
                body["defaultval"]), lock=self.threadlock, logger=self.logger)

            # respond with result here...
            response = {
                "readinifile": returnval,
                "uuid": str(body["uuid"])
            }

            response = json.dumps(response)
            self.logger.debug(str(response))

        elif str(body["rpc_req"]) == "get_appconfig":
            # read values from the configuration file
            defs_common.logtoconsole(
                "get_appconfig " + str(body), fg="GREEN", style="BRIGHT")
            self.logger.debug("get_appconfig " + str(body))

            # do the read here
            # returnval = defs_common.readINIfile(str(body["section"]), str(body["key"]), str(
            #    body["defaultval"]), lock=self.threadlock, logger=self.logger)

            returnval = jsonpickle.encode(self.AppPrefs)

            # respond with result here...
            response = {
                "get_appconfig": returnval,
                "uuid": str(body["uuid"])
            }

            response = json.dumps(response)
            self.logger.debug(str(response))

        try:
            if response != "":
                message = response
                self.logger.info("[MQTT Tx] " + message)
                self.MQTTclient.publish("reefberrypi/demo", message)

        except:
            print("error with RPC publish")

    def on_publish(self, mqttc, obj, mid):
        # print("mid: "+str(mid))
        return

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        # print(string)
        return

    def ConnectInfluxDB(self, host, port, dbname):
        try:
            client = InfluxDBClient(host, port)
            self.logger.info("Connected to InfluxDB at " + host + ":" + port)
            self.InitInfluxDB(client, dbname)
            return client
        except ConnectionError:
            self.logger.error("InfluxDB Connection Error")
        except Exception as e:
            self.logger.error("InfluxDB Error on Connect")
            self.logger.error(str(e))

    def InitInfluxDB(self, client, dbname):
        self.logger.info("Initialize InfluxDB: " + dbname)
        client.create_database(dbname)
        client.switch_database(dbname)

        # create retetion policies
        client.create_retention_policy(
            "one_day", "24h", "1", dbname, default=True)
        client.create_retention_policy(
            "three_days", "3d", "1", dbname, default=False)
        client.create_retention_policy(
            "one_week", "1w", "1", dbname, default=False)
        client.create_retention_policy(
            "three_months", "12w", "1", dbname, default=False)

        # create continuous queries
        ################################################################################
        # downsample data to every 5 minutes and retain for 3 days
        ################################################################################
        # probedata
        select_clause = """SELECT
                            mean("value") as "mean_value"
                            INTO "three_days"."probedata_downsample_5m"
                            FROM "probedata"
                            GROUP BY time(5m), *
                            """
        client.create_continuous_query(
            'cq_probedata_5m', select_clause, dbname)

        ################################################################################
        # downsample data to every 10 minutes and retain for 1 week
        ################################################################################
        # probedata
        select_clause = """SELECT
                            mean("value") as "mean_value"
                            INTO "one_week"."probedata_downsample_10m"
                            FROM "probedata"
                            GROUP BY time(10m), *
                            """
        client.create_continuous_query(
            'cq_probedata_10m', select_clause, dbname)

        ################################################################################
        # downsample data to every 15 minutes and retain for 3 months
        ################################################################################
        # probedata
        select_clause = """SELECT
                            mean("value") as "mean_value"
                            INTO "three_months"."probedata_downsample_15m"
                            FROM "probedata"
                            GROUP BY time(15m), *
                            """
        client.create_continuous_query(
            'cq_probedata_15m', select_clause, dbname)

# def WriteDataInfluxDB (self, json_data):
# try:
# bRetVal = self.InfluxDBclient.write_points(json_data)
# if bRetVal == False:
# self.logger.error("Error writing temperature to InfluxDB!")
##
# else:
# self.logger.info("Write point to InfluxDB")
# except ConnectionError:
# self.logger.error("InfluxDB Connection Error - Reconnecting...")
# self.InfluxDBclient = self.ConnectInfluxDB(self.INFLUXDB_HOST, self.INFLUXDB_PORT, self.INFLUXDB_DBNAME)
# except Exception as e:
# self.logger.error("InfluxDB Error writing")
# self.logger.error(e)
# self.InfluxDBclient = self.ConnectInfluxDB(self.INFLUXDB_HOST, self.INFLUXDB_PORT, self.INFLUXDB_DBNAME)

    def WriteProbeDataInfluxDB(self, probeid, value):
        try:
            json_body = [
                {
                    "measurement": "probedata",
                    "tags": {
                        "appuid": self.AppPrefs.appuid,
                        "probeid": probeid
                    },
                    "time": datetime.utcnow(),
                    "fields": {
                        "value": float(value),
                    }
                }
            ]

            bRetVal = self.InfluxDBclient.write_points(json_body)
            if bRetVal == False:
                self.logger.error(
                    "Error writing temperature to InfluxDB! [" + str(probeid) + "] " + str(value))
            else:
                self.logger.info(
                    "Write point to InfluxDB [" + probeid + "] " + str(value))
        except ConnectionError:
            self.logger.error("InfluxDB Connection Error - Reconnecting...")
            self.InfluxDBclient = self.ConnectInfluxDB(
                self.INFLUXDB_HOST, self.INFLUXDB_PORT, self.INFLUXDB_DBNAME)
        except Exception as e:
            self.logger.error(
                "InfluxDB Error writing [" + str(probeid) + "] " + str(value))
            self.logger.error(e)
            self.InfluxDBclient = self.ConnectInfluxDB(
                self.INFLUXDB_HOST, self.INFLUXDB_PORT, self.INFLUXDB_DBNAME)

    def broadcastProbeStatus(self, probetype, probeid, probeval, probename):
        message = {
            "status_currentprobeval":
            {
                "probetype": str(probetype),
                "probeid": str(probeid),
                "probeval": str(probeval),
                "probename": str(probename)
            }
        }

        message = json.dumps(message)
        self.logger.info("[MQTT Tx] " + message)
        # self.MQTTclient.publish("reefberrypi/demo", probeid + " : " + probeval)
        self.MQTTclient.publish("reefberrypi/demo", message)

    def broadcastFeedStatus(self, feedmode, timeremaining, uuid):
        message = {
            "status_feedmode":
            {
                "feedmode": str(feedmode),
                "timeremaining": str(timeremaining),
            },
            "uuid": str(uuid)
        }

        message = json.dumps(message)

        self.logger.info("[MQTT Tx] " + message)
        self.MQTTclient.publish("reefberrypi/demo", message)

    def broadcastOutletStatus(self, outletid, outletname, outletbus, control_type, button_state, outletstate, statusmsg, uuid):
        # print(uuid)
        message = {
            "status_currentoutletstate":
            {
                "outletid": str(outletid),
                "outletname": str(outletname),
                "outletbus": str(outletbus),
                "control_type": str(control_type),
                "button_state": str(button_state),
                "outletstate": str(outletstate),
                "statusmsg": str(statusmsg)
            },
            "uuid": str(uuid)
        }

        message = json.dumps(message)

        #self.logger.debug("[MQTT Tx] " + message)
        self.MQTTclient.publish("reefberrypi/demo", message)

    def get_probelist(self):
        probedict = {}
        config = configparser.ConfigParser()
        config.read(defs_common.CONFIGFILENAME)
        # loop through each section and see if it is a ds18b20 temp probe
        for section in config:
            # print(section)
            if section.split("_")[0] == "ds18b20":
                probetype = section.split("_")[0]
                probeid = section
                probename = config[section]["name"]
                sensortype = "temperature"
                probedict[probeid] = {"probetype": probetype, "probeid": probeid,
                                      "probename": probename, "sensortype": sensortype}

            if section == "dht11/22":
                if config[section]["enabled"] == "True":
                    probetype = "dht"
                    probeid = "dht_t"
                    probename = config[section]["temperature_name"]
                    sensortype = "temperature"
                    probedict[probeid] = {
                        "probetype": probetype, "probeid": probeid, "probename": probename, "sensortype": sensortype}

                    probetype = "dht"
                    probeid = "dht_h"
                    probename = config[section]["humidity_name"]
                    sensortype = "humidity"
                    probedict[probeid] = {
                        "probetype": probetype, "probeid": probeid, "probename": probename, "sensortype": sensortype}

            if section == "mcp3008":
                for x in range(0, 8):
                    if config[section]["ch" + str(x) + "_enabled"] == "True":
                        probetype = "mcp3008"
                        probeid = "mcp3008_ch" + str(x)
                        probename = config[section]["ch" + str(x) + "_name"]
                        sensortype = config[section]["ch" + str(x) + "_type"]
                        probedict[probeid] = {
                            "probetype": probetype, "probeid": probeid, "probename": probename, "sensortype": sensortype}

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
                # print (outletname)
                outletdict[outletid] = {"outletid": outletid, "outletname": outletname,
                                        "outletbus": outletbus, "control_type": control_type}

        return outletdict

    def initialize_logger(self, output_dir, output_file, loglevel_console, loglevel_logfile):

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # check if log dir exists, if not create it
        if not os.path.exists(output_dir):
            defs_common.logtoconsole("Logfile directory not found")
            os.mkdir(output_dir)
            defs_common.logtoconsole(
                "Logfile directory created: " + os.getcwd() + "/" + str(output_dir))

        # create console handler and set level to info
        self.handler = logging.StreamHandler()
        self.handler.setLevel(loglevel_console)
        self.formatter = logging.Formatter('%(asctime)s %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

        # create log file handler and set level to info
        self.handler = logging.handlers.RotatingFileHandler(
            os.path.join(output_dir, output_file), maxBytes=2000000, backupCount=5)
        self.handler.setLevel(loglevel_logfile)
        self.formatter = logging.Formatter(
            '%(asctime)s <%(levelname)s> [%(threadName)s:%(module)s] %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

        # create debug file handler and set level to debug
        # handler = logging.FileHandler(os.path.join(output_dir, "all.log"),handler.setLevel(logging.DEBUG)
        # formatter = logging.Formatter('%(asctime)s <%(levelname)s> [%(threadName)s:%(module)s] %(message)s')
        # handler.setFormatter(formatter)
        # logger.addHandler(handler)

    def outlet_control(self, bus, outletnum):  # bus = "int" or "ext"

        outlet = str(bus + "_outlet_" + outletnum)
        # controltype = defs_common.readINIfile(outlet, "control_type", "Always", lock=self.threadlock, logger=self.logger)
        controltype = self.AppPrefs.outletDict[outlet].control_type

        # pin = GPIO_config.int_outletpins.get(outlet)
        pin = 0

        if outlet == "int_outlet_1":
            button_state = self.AppPrefs.int_outlet_buttonstates.get(
                "int_outlet1_buttonstate")
        elif outlet == "int_outlet_2":
            button_state = self.AppPrefs.int_outlet_buttonstates.get(
                "int_outlet2_buttonstate")
        elif outlet == "int_outlet_3":
            button_state = self.AppPrefs.int_outlet_buttonstates.get(
                "int_outlet3_buttonstate")
        elif outlet == "int_outlet_4":
            button_state = self.AppPrefs.int_outlet_buttonstates.get(
                "int_outlet4_buttonstate")
        elif outlet == "int_outlet_5":
            button_state = self.AppPrefs.int_outlet_buttonstates.get(
                "int_outlet5_buttonstate")
        elif outlet == "int_outlet_6":
            button_state = self.AppPrefs.int_outlet_buttonstates.get(
                "int_outlet6_buttonstate")
        elif outlet == "int_outlet_7":
            button_state = self.AppPrefs.int_outlet_buttonstates.get(
                "int_outlet7_buttonstate")
        elif outlet == "int_outlet_8":
            button_state = self.AppPrefs.int_outlet_buttonstates.get(
                "int_outlet8_buttonstate")
        else:
            button_state = "OFF"

        curstate = self.AppPrefs.outletDict[outlet].button_state
        if curstate != button_state:
            changerequest = {}
            changerequest["section"] = outlet
            changerequest["key"] = "button_state"
            changerequest["value"] = button_state
            self.logger.debug("outlet_control: change " + outlet +
                              " button_state to " + button_state + " (from " + curstate + ")")
            self.queue.put(changerequest)
            # testing to see if this works...
            self.AppPrefs.outletDict[outlet].button_state = button_state

        # control type ALWAYS
        if controltype == "Always":
            return defs_outletcontrolsim.handle_outlet_always(self, outlet, button_state, pin)
        # control type HEATER
        elif controltype == "Heater":
            return defs_outletcontrolsim.handle_outlet_heater(self, outlet, button_state, pin)
        # control type RETURN PUMP
        elif controltype == "Return Pump":
            return defs_outletcontrolsim.handle_outlet_returnpump(self, outlet, button_state, pin)
        elif controltype == "Skimmer":
            return defs_outletcontrolsim.handle_outlet_skimmer(self, outlet, button_state, pin)
        elif controltype == "Light":
            return defs_outletcontrolsim.handle_outlet_light(self, outlet, button_state, pin)
        elif controltype == "pH Control":
            return defs_outletcontrolsim.handle_outlet_ph(self, outlet, button_state, pin)

    def get_probedatadays(self, probetype, probeid, numdays):
        if probetype == "":
            return

        #days_to_plot = 2
        days_to_plot = numdays

        xList = []  # datetime
        yList = []  # temp in C or other probe data
        zList = []  # temp in F
        for d in reversed(range(0, days_to_plot)):

            DateSeed = datetime.now() - timedelta(days=d)
            TimeSeed = datetime.now()
            LogFileName = probeid + "_" + \
                DateSeed.strftime("%Y-%m-%d") + ".txt"
            #print(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " Reading data points from: %s" % LogFileName)
            self.logger.info("Reading data points from: %s" % LogFileName)

            try:
                pullData = open("logs/" + LogFileName, "r").read()
                dataList = pullData.split('\n')

                for index, eachLine in enumerate(dataList):
                    if len(eachLine) > 1:
                        if probetype == "ds18b20" or probeid == "dht_t":
                            x, y, z = eachLine.split(',')
                        else:
                            x, y = eachLine.split(',')
                        x = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
                        if numdays == 2:  # if 2 days, just give the 24 hour daya meaning ignore data befor now time
                            # in yesterdays log file (0 is today, 1 is yesterday etc...)
                            if d == 1:
                                # we only want data for last 24 hours, so ignore values created before that
                                if x.strftime("%H:%M:%S") >= TimeSeed.strftime("%H:%M:%S"):
                                    #print("D=0" + " x= " + str(x.strftime("%H:%M:%S")) + " TimeSeed = " + str(TimeSeed.strftime("%H:%M:%S")))
                                    xList.append(x.strftime(
                                        "%Y-%m-%d %H:%M:%S"))
                                    yList.append(y)
                                    if probetype == "ds18b20" or probeid == "dht_t":
                                        zList.append(z)
                            else:
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
            if str(defs_common.readINIfile("global", "tempscale", str(defs_common.SCALE_C), lock=self.threadlock, logger=self.logger)) == str(defs_common.SCALE_F):
                return xList, zList
            else:
                return xList, yList
        else:
            return xList, yList

    # def threadManager(self):
        # connection1= pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        # channel1 = connection1.channel()
        # connection2= pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        # channel2 = connection2.channel()
        # connection3= pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        # channel3 = connection3.channel()

        # t1 = threading.Thread(target=self.handle_rpc, args=(channel1,))
        # t1.daemon = True
        # self.threads.append(t1)
        # t1.start()

        # t2 = threading.Thread(target=self.apploop)
        # t2.daemon = True
        # self.threads.append(t2)
        # t2.start()

        # t3 = threading.Thread(target=self.handle_mqtt, args=(channel3,))
        # t3.daemon = True
        # self.threads.append(t3)
        # t3.start()

        # for t in self.threads:
        #    t.join()
############################################################################################################################
#
#  Main application loop
#
############################################################################################################################

    def apploop(self):
        while True:
            # defs_common.logtoconsole("app loop")

            ##########################################################################################
            # read ds18b20 temperature sensor
            #
            # we support multiple probes, so work from the probe dictionary and get data
            # for each
            ##########################################################################################
            # read data from the temperature probes
            if (int(round(time.time()*1000)) - self.AppPrefs.ds18b20_SamplingTimeSeed) > self.AppPrefs.ds18b20_SamplingInterval:
                for p in self.AppPrefs.tempProbeDict:
                    try:
                        timestamp = datetime.now()
                        # dstempC = float(ds18b20.read_temp(
                        #    self.AppPrefs.tempProbeDict[p].probeid, "C"))
                        dstempC = 25
                        dstempF = defs_common.convertCtoF(float(dstempC))
                        dstempF = float(dstempF)
                        tempData = str(dstempC) + "," + str(dstempF)

                        if str(self.AppPrefs.temperaturescale) == str(defs_common.SCALE_F):
                            broadcasttemp = str("%.1f" % dstempF)
                        else:
                            broadcasttemp = str("%.1f" % dstempC)

                        # self.tempProbeDict[p].lastLogTime = self.ds18b20_LastLogTimeDict

                        if (int(round(time.time()*1000)) - int(self.AppPrefs.tempProbeDict[p].lastLogTime)) > self.AppPrefs.ds18b20_LogInterval:
                            # log and broadcast temperature value
                            defs_common.logprobedata(
                                "ds18b20_" + self.AppPrefs.tempProbeDict[p].probeid + "_", tempData)
                            defs_common.logtoconsole("***Logged*** [ds18b20_" + self.AppPrefs.tempProbeDict[p].probeid + "] " +
                                                     self.AppPrefs.tempProbeDict[p].name + str(" = {:.1f}".format(dstempC)) + " C | " + str("{:.1f}".format(dstempF)) +
                                                     " F", fg="CYAN", style="BRIGHT")
                            self.logger.info(str("***Logged*** [ds18b20_" + self.AppPrefs.tempProbeDict[p].probeid + "] " +
                                                 self.AppPrefs.tempProbeDict[p].name + str(" = {:.1f}".format(dstempC)) + " C | " + str("{:.1f}".format(dstempF))) +
                                             " F")
                            # log to InfluxDB
                            # self.WriteDataInfluxDB(json_body)
                            self.WriteProbeDataInfluxDB(
                                "ds18b20_" + self.AppPrefs.tempProbeDict[p].probeid, dstempC)
                            # self.broadcastProbeStatus("ds18b20", "ds18b20_" + self.AppPrefs.tempProbeDict[p].probeid, str(broadcasttemp), self.AppPrefs.tempProbeDict[p].name)

                            # self.ds18b20_LastLogTimeDict = int(round(time.time()*1000))
                            self.AppPrefs.tempProbeDict[p].lastLogTime = int(
                                round(time.time()*1000))

                            # self.AppPrefs.tempProbeDict[p].lastTemperature = dstempC
                            self.AppPrefs.tempProbeDict[p].lastTemperature = broadcasttemp
                        else:
                            self.logger.info(str("[ds18b20_" + self.AppPrefs.tempProbeDict[p].probeid + "] " +
                                                 self.AppPrefs.tempProbeDict[p].name + str(" = {:.1f}".format(dstempC)) + " C | " + str("{:.1f}".format(dstempF))) +
                                             " F")

                            # broadcast temperature value
                            # self.MQTTclient.publish("reefberrypi/demo",str(dstempC))
                            self.broadcastProbeStatus("ds18b20", "ds18b20_" + str(
                                self.AppPrefs.tempProbeDict[p].probeid), str(broadcasttemp), self.AppPrefs.tempProbeDict[p].name)
                            self.AppPrefs.tempProbeDict[p].lastTemperature = broadcasttemp
                    except Exception as e:
                        defs_common.logtoconsole(str(
                            "<<<Error>>> Can not read ds18b20_" + self.AppPrefs.tempProbeDict[p].probeid + " temperature data!"), fg="WHITE", bg="RED", style="BRIGHT")
                        self.logger.error("<<<Error>>> Can not read ds18b20_" +
                                          self.AppPrefs.tempProbeDict[p].probeid + " temperature data!")
                        self.logger.error(e)
                # record the new sampling time
                self.AppPrefs.ds18b20_SamplingTimeSeed = int(
                    round(time.time()*1000))  # convert time to milliseconds

            ################################################################################################################
            # read dht11 temperature and humidity sensor
            #
            # these sensors are slow to refresh and should not be read more
            # than once every second or two (ie: dht_SamplingInterval = 3000ms or 5000ms for 3s or 5s) would be safe
            ################################################################################################################
            if self.AppPrefs.DHT_Sensor.get("enabled") == "True":
                if (int(round(time.time()*1000)) - self.AppPrefs.DHT_Sensor.get("dht11_samplingtimeseed")) > int(self.AppPrefs.DHT_Sensor.get("dht11_samplinginterval")):
                    # let's read the dht11 temp and humidity data
                    # result = self.dht_sensor.read()
                    # if result.is_valid():
                    # temp_c = result.temperature
                    temp_c = 26
                    temp_f = defs_common.convertCtoF(float(temp_c))
                    temp_f = float(temp_f)
                    # hum = result.humidity
                    hum = 40
                    timestamp = datetime.now()

                    if str(self.AppPrefs.temperaturescale) == str(defs_common.SCALE_F):
                        broadcasttemp = str("%.1f" % temp_f)
                    else:
                        broadcasttemp = str("%.1f" % temp_c)

                    if (int(round(time.time()*1000)) - self.AppPrefs.DHT_Sensor.get("dht11_lastlogtime")) > int(self.AppPrefs.DHT_Sensor.get("dht11_loginterval")):
                        tempData = str("{:.1f}".format(
                            temp_c)) + "," + str(temp_f)

                        # log and broadcast temperature value
                        defs_common.logprobedata("dht_t_", tempData)
                        defs_common.logtoconsole("***Logged*** [dht_t] " + self.AppPrefs.DHT_Sensor.get(
                            "temperature_name") + " = %.1f C" % temp_c + " | %.1f F" % temp_f, fg="CYAN", style="BRIGHT")
                        self.logger.info(str("***Logged*** [dht_t] " + self.AppPrefs.DHT_Sensor.get(
                            "temperature_name") + " = %.1f C" % temp_c + " | %.1f F" % temp_f))
                        self.broadcastProbeStatus("dht", "dht_t", str(
                            broadcasttemp), self.AppPrefs.DHT_Sensor.get("temperature_name"))

                        # log to InfluxDB
                        # self.WriteDataInfluxDB(json_body)
                        self.WriteProbeDataInfluxDB("dht_t", temp_c)

                        # log and broadcast humidity value
                        defs_common.logprobedata(
                            "dht_h_", "{:.0f}".format(hum))
                        defs_common.logtoconsole("***Logged*** [dht_h] " + self.AppPrefs.DHT_Sensor.get(
                            "humidity_name") + " = %d %%" % hum, fg="CYAN", style="BRIGHT")
                        self.logger.info(str(
                            "***Logged*** [dht_h] " + self.AppPrefs.DHT_Sensor.get("humidity_name") + " = %d %%" % hum))
                        self.broadcastProbeStatus("dht", "dht_h", str(
                            hum), self.AppPrefs.DHT_Sensor.get("humidity_name"))

                        # log to InfluxDB
                        # self.WriteDataInfluxDB(json_body)
                        self.WriteProbeDataInfluxDB("dht_h", hum)

                        self.AppPrefs.DHT_Sensor["dht11_lastlogtime"] = int(
                            round(time.time()*1000))
                    else:
                        self.logger.info(str("[dht_t] " + self.AppPrefs.DHT_Sensor.get(
                            "temperature_name") + " = %.1f C" % temp_c + " | %.1f F" % temp_f))
                        self.logger.info(str(
                            "[dht_h] " + self.AppPrefs.DHT_Sensor.get("humidity_name") + " = %d %%" % hum))

                        # broadcast humidity value
                        self.broadcastProbeStatus("dht", "dht_h", str(
                            hum), self.AppPrefs.DHT_Sensor.get("humidity_name"))
                        # broadcast temperature value
                        self.broadcastProbeStatus("dht", "dht_t", str(
                            broadcasttemp), self.AppPrefs.DHT_Sensor.get("temperature_name"))

                    # record the new sampling time
                    self.AppPrefs.DHT_Sensor["dht11_samplingtimeseed"] = int(
                        round(time.time()*1000))  # convert time to milliseconds

            ##########################################################################################
            # read each of the 8 channels on the mcp3008
            # channels (0-7)
            ##########################################################################################
            # only read the data at every ph_SamplingInterval (ie: 500ms or 1000ms)
            if (int(round(time.time()*1000)) - self.AppPrefs.dv_SamplingTimeSeed) > self.AppPrefs.dv_SamplingInterval:
                # for x in range (0,8):
                for ch in self.AppPrefs.mcp3008Dict:
                    if self.AppPrefs.mcp3008Dict[ch].ch_enabled == "True":
                        # defs_common.logtoconsole(str(self.mcp3008Dict[ch].ch_num) + " " + str(self.mcp3008Dict[ch].ch_name) + " " + str(self.mcp3008Dict[ch].ch_enabled) + " " + str(len(self.mcp3008Dict[ch].ch_dvlist)))
                        # dv = mcp3008.readadc(int(self.AppPrefs.mcp3008Dict[ch].ch_num), GPIO_config.SPICLK, GPIO_config.SPIMOSI,
                        #                     GPIO_config.SPIMISO, GPIO_config.SPICS)
                        dv = 256
                        self.AppPrefs.mcp3008Dict[ch].ch_dvlist.append(dv)
                        # self.logger.info(str(self.mcp3008Dict[ch].ch_num) + " " + str(self.mcp3008Dict[ch].ch_name) + " " + str(self.mcp3008Dict[ch].ch_dvlist))
                    # once we hit our desired sample size of ph_numsamples (ie: 120)
                    # then calculate the average value
                    if len(self.AppPrefs.mcp3008Dict[ch].ch_dvlist) >= int(self.AppPrefs.mcp3008Dict[ch].ch_numsamples):
                        # The probes may pick up noise and read very high or
                        # very low values that we know are not good values. We are going to use numpy
                        # to calculate the standard deviation and remove the outlying data that is
                        # Sigma standard deviations away from the mean.  This way these outliers
                        # do not affect our results
                        self.logger.info("mcp3008 ch" + str(self.AppPrefs.mcp3008Dict[ch].ch_num) + " raw data " + str(
                            self.AppPrefs.mcp3008Dict[ch].ch_name) + " " + str(self.AppPrefs.mcp3008Dict[ch].ch_dvlist))
                        dv_FilteredCounts = numpy.array(
                            self.AppPrefs.mcp3008Dict[ch].ch_dvlist)
                        dv_FilteredMean = numpy.mean(dv_FilteredCounts, axis=0)
                        dv_FlteredSD = numpy.std(dv_FilteredCounts, axis=0)
                        dv_dvlistfiltered = [x for x in dv_FilteredCounts if
                                             (x > dv_FilteredMean - float(self.AppPrefs.mcp3008Dict[ch].ch_sigma) * dv_FlteredSD)]
                        dv_dvlistfiltered = [x for x in dv_dvlistfiltered if
                                             (x < dv_FilteredMean + float(self.AppPrefs.mcp3008Dict[ch].ch_sigma) * dv_FlteredSD)]

                        self.logger.info("mcp3008 ch" + str(self.AppPrefs.mcp3008Dict[ch].ch_num) + " filtered " + str(
                            self.AppPrefs.mcp3008Dict[ch].ch_name) + " " + str(dv_dvlistfiltered))

                        # calculate the average of our filtered list
                        try:
                            dv_AvgCountsFiltered = int(
                                sum(dv_dvlistfiltered)/len(dv_dvlistfiltered))
                            # delete this line
                            print("{:.2f}".format(dv_AvgCountsFiltered))
                        except:
                            # need to revisit this error handling. Exception thrown when all
                            dv_AvgCountsFiltered = 1
                            # values were 1023
                            print("Error collecting data")

                        # self.mcp3008Dict[ch].ch_dvlist.clear()  ## delete  this line

                        if self.AppPrefs.mcp3008Dict[ch].ch_type == "pH":
                            # bug, somtimes value is coming back high, like really high, like 22.0.  this is an impossible
                            # value since max ph is 14.  need to figure this out later, but for now, lets log this val to aid in
                            # debugging
                            orgval = dv_AvgCountsFiltered

                            # convert digital value to ph
                            lowCal = self.AppPrefs.mcp3008Dict[ch].ch_ph_low
                            medCal = self.AppPrefs.mcp3008Dict[ch].ch_ph_med
                            highCal = self.AppPrefs.mcp3008Dict[ch].ch_ph_high

                            dv_AvgCountsFiltered = ph_sensor.dv2ph(
                                dv_AvgCountsFiltered, ch, lowCal, medCal, highCal)
                            dv_AvgCountsFiltered = float(
                                "{:.2f}".format(dv_AvgCountsFiltered))

                            if dv_AvgCountsFiltered > 14:
                                self.logger.error("Invalid PH value: " + str(
                                    dv_AvgCountsFiltered) + " " + str(orgval) + " " + str(dv_dvlistfiltered))
                                defs_common.logtoconsole("Invalid PH value: " + str(dv_AvgCountsFiltered) + " " + str(
                                    orgval) + " " + str(dv_dvlistfiltered), fg="RED", style="BRIGHT")

                        # if enough time has passed (ph_LogInterval) then log the data to file
                        # otherwise just print it to console
                        timestamp = datetime.now()
                        if (int(round(time.time()*1000)) - self.AppPrefs.mcp3008Dict[ch].LastLogTime) > self.AppPrefs.dv_LogInterval:
                            # sometimes a high value, like 22.4 gets recorded, i need to fix this, but for now don't log that
                            # if ph_AvgFiltered < 14.0:
                            # RBP_commons.logprobedata(config['logs']['ph_log_prefix'], "{:.2f}".format(ph_AvgFiltered))
                            # log data to InfluxDB
                            self.WriteProbeDataInfluxDB(
                                "mcp3008_ch" + str(self.AppPrefs.mcp3008Dict[ch].ch_num), "{:.2f}".format(dv_AvgCountsFiltered))
                            defs_common.logprobedata(
                                "mcp3008_ch" + str(self.AppPrefs.mcp3008Dict[ch].ch_num) + "_", "{:.2f}".format(dv_AvgCountsFiltered))
                            defs_common.logtoconsole("***Logged*** dv = " + "{:.2f}".format(dv_AvgCountsFiltered),
                                                     fg="CYAN", style="BRIGHT")
                           # print(timestamp.strftime(Fore.CYAN + Style.BRIGHT + "%Y-%m-%d %H:%M:%S") + " ***Logged*** dv = "
                           #       + "{:.2f}".format(dv_AvgCountsFiltered) + Style.RESET_ALL)
                            self.AppPrefs.mcp3008Dict[ch].LastLogTime = int(
                                round(time.time()*1000))
                        else:
                            print(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " dv = "
                                  + "{:.2f}".format(dv_AvgCountsFiltered))

                        self.broadcastProbeStatus("mcp3008", "mcp3008_ch" + str(self.AppPrefs.mcp3008Dict[ch].ch_num), str(
                            dv_AvgCountsFiltered), str(self.AppPrefs.mcp3008Dict[ch].ch_name))
                        self.AppPrefs.mcp3008Dict[ch].lastValue = str(
                            dv_AvgCountsFiltered)
                        # clear the list so we can populate it with new data for the next data set
                        self.AppPrefs.mcp3008Dict[ch].ch_dvlist.clear()
                        # record the new sampling time
                        self.AppPrefs.dv_SamplingTimeSeed = int(
                            round(time.time()*1000))  # convert time to milliseconds

            ##########################################################################################
            # check if Feed mode is enabled
            #
            ##########################################################################################

            if self.AppPrefs.feed_CurrentMode == "A":
                #self.AppPrefs.feed_ModeTotaltime = defs_common.readINIfile("feed_timers", "feed_a", "60", lock=self.threadlock, logger=self.logger)
                self.AppPrefs.feed_ModeTotaltime = self.AppPrefs.feed_a_time
            elif self.AppPrefs.feed_CurrentMode == "B":
                #self.AppPrefs.feed_ModeTotaltime = defs_common.readINIfile("feed_timers", "feed_b", "60", lock=self.threadlock, logger=self.logger)
                self.AppPrefs.feed_ModeTotaltime = self.AppPrefs.feed_b_time
            elif self.AppPrefs.feed_CurrentMode == "C":
                #self.AppPrefs.feed_ModeTotaltime = defs_common.readINIfile("feed_timers", "feed_c", "60", lock=self.threadlock, logger=self.logger)
                self.AppPrefs.feed_ModeTotaltime = self.AppPrefs.feed_c_time
            elif self.AppPrefs.feed_CurrentMode == "D":
                #self.AppPrefs.feed_ModeTotaltime = defs_common.readINIfile("feed_timers", "feed_d", "60", lock=self.threadlock, logger=self.logger)
                self.AppPrefs.feed_ModeTotaltime = self.AppPrefs.feed_d_time
            else:
                self.AppPrefs.feed_ModeTotaltime = "0"

            if self.AppPrefs.feed_CurrentMode != "CANCEL":
                self.AppPrefs.feedTimeLeft = (int(self.AppPrefs.feed_ModeTotaltime)*1000) - (
                    int(round(time.time()*1000)) - self.AppPrefs.feed_SamplingTimeSeed)
                if self.AppPrefs.feedTimeLeft <= 0:
                    defs_common.logtoconsole("Feed Mode: " + self.AppPrefs.feed_CurrentMode + " COMPLETE",
                                             fg="WHITE", style="BRIGHT")
                    # print(Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                    #      " Feed Mode: " + self.AppPrefs.feed_CurrentMode + " COMPLETE" + Style.RESET_ALL)
                    self.AppPrefs.feed_CurrentMode = "CANCEL"
                    timestamp = datetime.now()

                    self.broadcastFeedStatus(
                        self.AppPrefs.feed_CurrentMode, self.AppPrefs.feedTimeLeft, "")

                    self.AppPrefs.feed_ExtraTimeSeed = int(
                        round(time.time()*1000))
                    print("Extra time starts at: " + str(self.AppPrefs.feed_ExtraTimeSeed) +
                          " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:

                    defs_common.logtoconsole("Feed Mode: " + self.AppPrefs.feed_CurrentMode +
                                             " (" + self.AppPrefs.feed_ModeTotaltime + "s) " +
                                             "Time Remaining: " +
                                             str(round(
                                                 self.AppPrefs.feedTimeLeft/1000)) + "s",
                                             fg="WHITE", style="BRIGHT")
                    # print(Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                    #      " Feed Mode: " + self.AppPrefs.feed_CurrentMode +
                    #      " (" + self.AppPrefs.feed_ModeTotaltime + "s) " +
                    #      "Time Remaining: " +
                    #      str(round(self.AppPrefs.feedTimeLeft/1000)) + "s"
                    #      + Style.RESET_ALL)

                    timestamp = datetime.now()

                    self.broadcastFeedStatus(self.AppPrefs.feed_CurrentMode, round(
                        self.AppPrefs.feedTimeLeft/1000), "")

            ##########################################################################################
            # handle outlet states (turn outlets on or off)
            #
            ##########################################################################################
            # outlet1_control()
            # do each of the outlets on the internal bus (outlets 1-8)
            for x in range(1, 9):
                status = self.outlet_control("int", str(x))

                self.broadcastOutletStatus("int_outlet_" + str(x),
                                           self.AppPrefs.outletDict["int_outlet_" + str(
                                               x)].outletname,
                                           "int",
                                           self.AppPrefs.outletDict["int_outlet_" + str(
                                               x)].control_type,
                                           self.AppPrefs.int_outlet_buttonstates.get(
                                               "int_outlet" + str(x) + "_buttonstate"),
                                           "STATEUNKNOWN",
                                           status,
                                           "")

              #  self.logger.debug("int_outlet_" + str(x) +
              #                    " [label: " + self.AppPrefs.outletDict["int_outlet_" + str(x)].outletname +
              #                    "] [type: " + self.AppPrefs.outletDict["int_outlet_" + str(x)].control_type +
              #                    "] [button: " + self.AppPrefs.outletDict["int_outlet_" + str(x)].button_state +
              #                    "] [status: " + str(status) + "]" +
              #                    " [pin: " + "0" + "]")

            ##########################################################################################
            # update configuration file with any change requests sitting in the queue
            ##########################################################################################

            if self.queue.qsize() > 0:
                updatedPrefs = set({})
                for i in range(0, self.queue.qsize()):
                    msg = self.queue.get(0)
                    self.logger.info(
                        "Configuration update: [" + msg["section"] + "] [ " + msg["key"] + "] = " + msg["value"])
                    defs_common.writeINIfile(
                        msg["section"], msg["key"], msg["value"], lock=self.threadlock, logger=self.logger)
                    updatedPrefs.add(msg["section"])
                    # print (msg)
                    # print (self.queue.qsize())

                self.refreshPrefs = True
                # if a new value is written to the config, we also have to load it into memory into our
                # AppPref class so this new setting will be used in the next cycle
                self.logger.info(str(updatedPrefs))
                # update the section here...
                for sec in updatedPrefs:
                    self.AppPrefs.reloadPrefSection(self, sec)

               # # if a change was made, broadcast it out...
               # returnval = jsonpickle.encode(self.AppPrefs)

               # # respond with result here...
               # response = {
               #     "get_appconfig": returnval,
               #     "uuid": ""
               # }
               # response = json.dumps(response)
               # self.logger.debug(str(response))

               # if response != "":
               #     self.logger.info("[MQTT Tx] " + response)
               #     self.MQTTclient.publish("reefberrypi/demo", response)

            ##########################################################################################
            # pause to slow down the loop
            ##########################################################################################
            time.sleep(.5)


root = RBP_controller()
