import logging
import logging.handlers
import defs_common
import defs_Influx
import cls_Preferences
import mcp3008
import threading
import defs_mysql
import api_flask
from influxdb_client.client.write_api import SYNCHRONOUS
import RPi.GPIO as GPIO
import GPIO_config
import dht22
from datetime import datetime, timedelta, timezone
import ds18b20
import time
import numpy
import ph_sensor
import defs_outletcontrol
import version
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import select
from sqlalchemy import update
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, \
    unset_jwt_cookies, jwt_required, JWTManager
import json

app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type, Authorization'
app.config["JWT_SECRET_KEY"] = "supersecret-reefberrypi-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)

# reduce the Flask logging level to error.  Default is Info
flog = logging.getLogger('werkzeug')
flog.setLevel(logging.ERROR)


jwt = JWTManager(app)

logger = logging.getLogger()
LOG_FILEDIR = "logs"
LOG_FILENAME = "RBP_controller.log"
LOGLEVEL_CONSOLE = logging.DEBUG  # DEBUG, INFO, ERROR
LOGLEVEL_LOGFILE = logging.INFO

defs_common.initialize_logger(logger, LOG_FILEDIR, LOG_FILENAME,
                              LOGLEVEL_CONSOLE, LOGLEVEL_LOGFILE)

logger.info(
    "====================================================================")
logger.info("  ___          __ _                        ___ _ ")
logger.info(" | _ \___ ___ / _| |__  ___ _ _ _ _ _  _  | _ (_)")
logger.info(" |   / -_) -_)  _| '_ \/ -_) '_| '_| || | |  _/ |")
logger.info(" |_|_\___\___|_| |_.__/\___|_| |_|  \_, | |_| |_|")
logger.info("                                    |__/         ")
logger.info(
    "====================================================================")

logger.info("*** Reefberry Pi controller startup ***")
logger.info("version = " + version.CONTROLLER_VERSION)

threadlock = threading.Lock()

# read prefs
AppPrefs = cls_Preferences.AppPrefs(logger, threadlock)

# initialize InfluxDB
Influx_client = defs_Influx.InitInfluxDB(AppPrefs, logger)
Influx_write_api = Influx_client.write_api(write_options=SYNCHRONOUS)

AppPrefs.Influx_write_api = Influx_write_api

# initialize MySQL database
# mySQLDB = defs_mysql.initMySQL(AppPrefs, logger)
sqlengine = defs_mysql.initMySQL_ex(AppPrefs, logger)

# read preferences from DB
# defs_mysql.readGlobalPrefs(mySQLDB, AppPrefs, logger)
defs_mysql.readGlobalPrefs_ex(sqlengine, AppPrefs, logger)
# temperature probes
# defs_mysql.readTempProbes(mySQLDB, AppPrefs, logger)
defs_mysql.readTempProbes_ex(sqlengine, AppPrefs, logger)
# defs_mysql.readOutletPrefs(mySQLDB, AppPrefs, logger)
defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, logger)
defs_mysql.readDHTSensor_ex(sqlengine, AppPrefs, logger)
defs_mysql.readMCP3008Prefs_ex(sqlengine, AppPrefs, logger)


# set up the GPIO
GPIO_config.initGPIO()

# dht22 temperature and humidity sensor
dht22_sensor = dht22.DHT22

# MARK: App Loop


def apploop():

    global AppPrefs

    logger.info("Starting App Cycle")

    while True:
        logger.debug("******************************************************")
        logger.debug("Start Loop")
        logger.debug("******************************************************")

        ##########################################################################################
        # read each of the 8 channels on the mcp3008
        # channels (0-7)
        ##########################################################################################
        # only read the data at every ph_SamplingInterval (ie: 500ms or 1000ms)
        if (int(round(time.time()*1000)) - AppPrefs.dv_SamplingTimeSeed) > AppPrefs.dv_SamplingInterval:
            # for x in range (0,8):
            for ch in AppPrefs.mcp3008Dict:
                # if AppPrefs.mcp3008Dict[ch].ch_enabled.lower() == "true":
                logger.debug("mcp3008 ch" + str(AppPrefs.mcp3008Dict[ch].ch_num) + " " + str(
                    AppPrefs.mcp3008Dict[ch].ch_name) + " = " + str(AppPrefs.mcp3008Dict[ch].lastValue))
                dv = mcp3008.readadc(int(AppPrefs.mcp3008Dict[ch].ch_num), GPIO_config.SPICLK, GPIO_config.SPIMOSI,
                                     GPIO_config.SPIMISO, GPIO_config.SPICS)
                logger.debug(
                    "CH" + str(AppPrefs.mcp3008Dict[ch].ch_num) + " = " + str(dv))
                AppPrefs.mcp3008Dict[ch].ch_dvlist.append(dv)
######
                AppPrefs.mcp3008Dict[ch].ch_dvcallist.append(dv)

                if len(AppPrefs.mcp3008Dict[ch].ch_dvcallist) >= 120:
                    truncated_list = slice (1, 120) 
                    AppPrefs.mcp3008Dict[ch].ch_dvcallist = AppPrefs.mcp3008Dict[ch].ch_dvcallist[truncated_list]
                    AppPrefs.mcp3008Dict[ch].ch_dvcalFilteredCounts = numpy.array(AppPrefs.mcp3008Dict[ch].ch_dvcallist)
                    AppPrefs.mcp3008Dict[ch].ch_dvcalFilteredMean = int(numpy.mean(AppPrefs.mcp3008Dict[ch].ch_dvcalFilteredCounts, axis=0))
                    AppPrefs.mcp3008Dict[ch].ch_dvcalFilteredSD = "{:.2f}".format(float(numpy.std(AppPrefs.mcp3008Dict[ch].ch_dvcalFilteredCounts, axis=0)))

                    AppPrefs.logger.debug("mean = {:.2f}".format(AppPrefs.mcp3008Dict[ch].ch_dvcalFilteredMean))
                    AppPrefs.logger.debug("std. dev. = {:.2f}".format(float(AppPrefs.mcp3008Dict[ch].ch_dvcalFilteredSD)))

                    AppPrefs.logger.debug(AppPrefs.mcp3008Dict[ch].ch_dvcallist)

#####      
                # once we hit our desired sample size of ph_numsamples (ie: 120)
                # then calculate the average value
                if len(AppPrefs.mcp3008Dict[ch].ch_dvlist) >= int(AppPrefs.mcp3008Dict[ch].ch_numsamples):
                    # The probes may pick up noise and read very high or
                    # very low values that we know are not good values. We are going to use numpy
                    # to calculate the standard deviation and remove the outlying data that is
                    # Sigma standard deviations away from the mean.  This way these outliers
                    # do not affect our results
                    logger.debug("mcp3008 ch" + str(AppPrefs.mcp3008Dict[ch].ch_num) + " raw data " + str(
                        AppPrefs.mcp3008Dict[ch].ch_name) + " " + str(AppPrefs.mcp3008Dict[ch].ch_dvlist))
                    dv_FilteredCounts = numpy.array(
                        AppPrefs.mcp3008Dict[ch].ch_dvlist)
                    dv_FilteredMean = numpy.mean(dv_FilteredCounts, axis=0)
                    dv_FlteredSD = numpy.std(dv_FilteredCounts, axis=0)
                    dv_dvlistfiltered = [x for x in dv_FilteredCounts if
                                         (x > dv_FilteredMean - float(AppPrefs.mcp3008Dict[ch].ch_sigma) * dv_FlteredSD)]
                    dv_dvlistfiltered = [x for x in dv_dvlistfiltered if
                                         (x < dv_FilteredMean + float(AppPrefs.mcp3008Dict[ch].ch_sigma) * dv_FlteredSD)]

                    logger.debug("mcp3008 ch" + str(AppPrefs.mcp3008Dict[ch].ch_num) + " filtered " + str(
                        AppPrefs.mcp3008Dict[ch].ch_name) + " " + str(dv_dvlistfiltered))

                    # calculate the average of our filtered list
                    try:
                        dv_AvgCountsFiltered = int(
                            sum(dv_dvlistfiltered)/len(dv_dvlistfiltered))
                        # delete this line
                        logger.debug("{:.2f}".format(dv_AvgCountsFiltered))
                    except:
                        # need to revisit this error handling. Exception thrown when all
                        dv_AvgCountsFiltered = 1
                        # values were 1023
                        logger.error("Error collecting data! " + "mcp3008 ch" +
                                     str(AppPrefs.mcp3008Dict[ch].ch_num))

                    if AppPrefs.mcp3008Dict[ch].ch_type == "ph":
                        # bug, somtimes value is coming back high, like really high, like 22.0.  this is an impossible
                        # value since max ph is 14.  need to figure this out later, but for now, lets log this val to aid in
                        # debugging
                        orgval = dv_AvgCountsFiltered

                        # convert digital value to ph
                        lowCal = AppPrefs.mcp3008Dict[ch].ch_ph_low
                        medCal = AppPrefs.mcp3008Dict[ch].ch_ph_med
                        highCal = AppPrefs.mcp3008Dict[ch].ch_ph_high

                        dv_AvgCountsFiltered = ph_sensor.dv2ph(
                            dv_AvgCountsFiltered, ch, lowCal, medCal, highCal)
                        dv_AvgCountsFiltered = float(
                            "{:.2f}".format(dv_AvgCountsFiltered))

                        if dv_AvgCountsFiltered > 14:
                            logger.error("Invalid PH value: " + str(AppPrefs.mcp3008Dict[ch].ch_probeid) + " " + str(dv_AvgCountsFiltered) +
                                         " " + str(orgval) + " " + str(dv_dvlistfiltered))

                    # if enough time has passed (ph_LogInterval) then log the data to file
                    # otherwise just print it to console
                    timestamp = datetime.now()
                    if (int(round(time.time()*1000)) - AppPrefs.mcp3008Dict[ch].LastLogTime) > AppPrefs.dv_LogInterval:
                        # sometimes a high value, like 22.4 gets recorded, i need to fix this, but for now don't log that
                        # if ph_AvgFiltered < 14.0:
                       #         defs_common.logprobedata("mcp3008_ch" + str(AppPrefs.mcp3008Dict[ch].ch_num) + "_", "{:.2f}".format(dv_AvgCountsFiltered))
                        logger.debug("mcp3008_ch" + str(AppPrefs.mcp3008Dict[ch].ch_num) + " = " + str(
                            "{:.2f}".format(dv_AvgCountsFiltered)))
                        Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "ph", "tags": {
                            "appuid": AppPrefs.appuid, "probeid": "mcp3008_ch" + str(AppPrefs.mcp3008Dict[ch].ch_num)}, "fields": {"value": float("{:.2f}".format(dv_AvgCountsFiltered))}, "time": datetime.utcnow()}])
                        AppPrefs.mcp3008Dict[ch].LastLogTime = int(
                            round(time.time()*1000))
                    else:
                        logger.debug(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " dv = "
                                     + "{:.2f}".format(dv_AvgCountsFiltered))

                    AppPrefs.mcp3008Dict[ch].lastValue = str(
                        dv_AvgCountsFiltered)
                    # clear the list so we can populate it with new data for the next data set
                    AppPrefs.mcp3008Dict[ch].ch_dvlist.clear()
                    # record the new sampling time
                    AppPrefs.dv_SamplingTimeSeed = int(
                        round(time.time()*1000))  # convert time to milliseconds

        ##########################################################################################
        # ds18b20 Temperture sensors
        ##########################################################################################
        # reading ds18b20 is moved to its own thread DStemploop() which starts down below

        ##########################################################################################
        # dht22 temp and humidity data
        ##########################################################################################
        # reading DHT22 is moved to its own thread DHTloop() which starts down below

        ##########################################################################################
        # check if Feed mode is enabled
        ##########################################################################################

        if AppPrefs.feed_CurrentMode == "A":
            AppPrefs.feed_ModeTotaltime = AppPrefs.feed_a_time
        elif AppPrefs.feed_CurrentMode == "B":
            AppPrefs.feed_ModeTotaltime = AppPrefs.feed_b_time
        elif AppPrefs.feed_CurrentMode == "C":
            AppPrefs.feed_ModeTotaltime = AppPrefs.feed_c_time
        elif AppPrefs.feed_CurrentMode == "D":
            AppPrefs.feed_ModeTotaltime = AppPrefs.feed_d_time
        else:
            AppPrefs.feed_ModeTotaltime = "0"

        if AppPrefs.feed_CurrentMode != "CANCEL":
            AppPrefs.logger.info(
                "Feed Mode " + AppPrefs.feed_CurrentMode + " enabled")
            AppPrefs.feedTimeLeft = (int(AppPrefs.feed_ModeTotaltime)*1000) - (
                int(round(time.time()*1000)) - AppPrefs.feed_SamplingTimeSeed)

            if AppPrefs.feedTimeLeft <= 0:
                # print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                #         " Feed Mode: " + self.AppPrefs.feed_CurrentMode + " COMPLETE" + Style.RESET_ALL)
                logging.info("Feed Mode " +
                             AppPrefs.feed_CurrentMode + " Complete")
                AppPrefs.feed_CurrentMode = "CANCEL"
                # timestamp = datetime.now()

                # self.broadcastFeedStatus(self.AppPrefs.feed_CurrentMode, self.AppPrefs.feedTimeLeft)

                AppPrefs.feed_ExtraTimeSeed = int(round(time.time()*1000))
                print("Extra time starts at: " + str(AppPrefs.feed_ExtraTimeSeed) +
                      " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                # print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                #         " Feed Mode: " + self.AppPrefs.feed_CurrentMode + " (" + self.AppPrefs.feed_ModeTotaltime + "s) " + "Time Remaining: " + str(round(self.AppPrefs.feedTimeLeft/1000)) + "s"
                #         + Style.RESET_ALL)
                # timestamp = datetime.now()
                logging.info("Feed Mode: " + AppPrefs.feed_CurrentMode + " (" + AppPrefs.feed_ModeTotaltime +
                             "s) " + "Time Remaining: " + str(round(AppPrefs.feedTimeLeft/1000)) + "s")

                # self.broadcastFeedStatus(self.AppPrefs.feed_CurrentMode, round(self.AppPrefs.feedTimeLeft/1000))

        ##########################################################################################
        # Handle Outlets
        ##########################################################################################
        # read outlet prefs from DB
        try:
            # defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, logger)

            for outlet in AppPrefs.outletDict:
                # logger.info("[" + AppPrefs.outletDict.get(outlet).outletid + "] " + \
                #             AppPrefs.outletDict.get(outlet).outletname + " = " + \
                #             AppPrefs.outletDict.get(outlet).button_state  )

                pin = GPIO_config.int_outletpins.get(
                    AppPrefs.outletDict.get(outlet).outletid)

                # handle outlet actions based on settings
                # control type ALWAYS
                if AppPrefs.outletDict.get(outlet).control_type == "Always":
                    defs_outletcontrol.handle_outlet_always(
                        AppPrefs, outlet, AppPrefs.outletDict.get(outlet).button_state, pin)
                # control type HEATER
                elif AppPrefs.outletDict.get(outlet).control_type == "Heater":
                    defs_outletcontrol.handle_outlet_heater(
                        AppPrefs, outlet, AppPrefs.outletDict.get(outlet).button_state, pin)
                # control type RETURN PUMP
                elif AppPrefs.outletDict.get(outlet).control_type == "Return":
                    defs_outletcontrol.handle_outlet_returnpump(
                        AppPrefs, outlet, AppPrefs.outletDict.get(outlet).button_state, pin)
                # contriol type SKIMMER
                elif AppPrefs.outletDict.get(outlet).control_type == "Skimmer":
                    defs_outletcontrol.handle_outlet_skimmer(
                        AppPrefs, outlet, AppPrefs.outletDict.get(outlet).button_state, pin)
                # control type LIGHT
                elif AppPrefs.outletDict.get(outlet).control_type == "Light":
                    defs_outletcontrol.handle_outlet_light(
                        AppPrefs, outlet, AppPrefs.outletDict.get(outlet).button_state, pin)
                # control type PH
                elif AppPrefs.outletDict.get(outlet).control_type == "PH":
                    defs_outletcontrol.handle_outlet_ph(
                        AppPrefs, outlet, AppPrefs.outletDict.get(outlet).button_state, pin)

        except Exception as e:
            logger.error("Error reading outlet data! " + str(e))

        ##########################################################################################
        # pause to slow down the loop
        ##########################################################################################
        logger.debug("******************************************************")
        logger.debug("End Loop")
        logger.debug("******************************************************")
        time.sleep(1)

# MARK: DStemploop


def DStemploop():
    global AppPrefs
    global Influx_client
    global Influx_write_api

    while True:
        try:
            for tProbe in AppPrefs.tempProbeDict:
                try:
                    # dstempC = float(ds18b20.read_temp(
                    #     AppPrefs.tempProbeDict.get(tProbe).probeid.split("_")[1], "C"))

                    dstempC = float(ds18b20.read_temp(
                        AppPrefs.tempProbeDict.get(tProbe).serialnum, "C"))

                    # dstempC = float(ds18b20.read_temp("111", "C"))

                    # logger.info(str(dstempC) + " C")
                    # print("ds18b20 " + str(dstempC) + " C")
                    Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "temperature_c", "tags": {
                        "appuid": AppPrefs.appuid, "probeid": AppPrefs.tempProbeDict.get(tProbe).probeid}, "fields": {"value": dstempC}, "time": datetime.utcnow()}])

                    dstempF = float(defs_common.convertCtoF(dstempC))
                    # print("ds18b20 " + str(dstempF) + " F")
                    Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "temperature_f", "tags": {
                        "appuid": AppPrefs.appuid, "probeid": AppPrefs.tempProbeDict.get(tProbe).probeid}, "fields": {"value": dstempF}, "time": datetime.utcnow()}])

                    # print("ds18b20 Temp = " + str(dstempC) + "C / " + str(dstempF) + "F")
                    logger.debug(AppPrefs.tempProbeDict.get(tProbe).probeid + " Temp = " + str(dstempC) +
                                 "C / " + str(dstempF) + "F")

                    if AppPrefs.temperaturescale == "F":
                        AppPrefs.tempProbeDict.get(
                            tProbe).lastTemperature = str(dstempF)
                    else:
                        AppPrefs.tempProbeDict.get(
                            tProbe).lastTemperature = str(dstempC)

                except Exception as e:
                    logger.error(
                        "Unable to read ds18b20 temperature! " + str(e))
                    AppPrefs.tempProbeDict.get(
                        tProbe).lastTemperature = ""

        except Exception as e:
            logger.error("Error reading ds18b20 temperature! " + str(e))

        # slow down the loop
        time.sleep(1)

# MARK: DHTloop


def DHTloop():
    global AppPrefs
    global Influx_client
    global Influx_write_api

    ###################################################################
    # dht22 temp and humidity data
    ###################################################################
    while True:
        if AppPrefs.dht_enable == "true":
            try:
                # result = dht_sensor.read()
                hum, temp_c = dht22_sensor.read()
                # if result.is_valid():
                # temp_c = result.temperature
                # hum = result.humidity
                temp_f = float(defs_common.convertCtoF(temp_c))

                if AppPrefs.temperaturescale == "F":
                    AppPrefs.dhtDict.get("DHT-T").lastValue = str(temp_f)
                else:
                    AppPrefs.dhtDict.get("DHT-T").lastValue = str(temp_c)

                # sometimes we get an invalid reading for humidity, ignore any obviously bad reading
                if float(hum) <= 100:
                    AppPrefs.dhtDict.get("DHT-H").lastValue = str(hum)
            except Exception as e:
                logger.error(
                    "Error getting DHT data!" + str(e))
            try:
                Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "temperature_c", "tags": {
                    "appuid": AppPrefs.appuid, "probeid": "DHT-T"}, "fields": {"value": float(temp_c)}, "time": datetime.utcnow()}])

                Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "temperature_f", "tags": {
                    "appuid": AppPrefs.appuid, "probeid": "DHT-T"}, "fields": {"value": float(temp_f)}, "time": datetime.utcnow()}])

                logger.debug("dht22 Temp = " + str(temp_c) +
                             "C / " + str(temp_f) + "F")
                # sometimes we get an invalid reading for humidity, ignore any obviously bad reading
                if float(hum) <= 100:
                    logger.debug("dht22 Humidity = " + str(hum) + "%")
                    Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "humidity", "tags": {
                        "appuid": AppPrefs.appuid, "probeid": "DHT-H"}, "fields": {"value": float(hum)}, "time": datetime.utcnow()}])
                else:
                    logger.error(
                        "dht22 Humidity out of range, ignoring: " + str(hum) + "%")
            except Exception as e:
                logger.error(
                    "Error logging DHT data to InfluxDB!" + str(e))
            # slow down the loop
        time.sleep(1)



#########################################################################
# THREADS
#########################################################################


MAINthread = threading.Thread(target=apploop)
MAINthread.start()

DHTthread = threading.Thread(target=DHTloop)
DHTthread.start()

DSthread = threading.Thread(target=DStemploop)
DSthread.start()



# MARK: Flask API
#########################################################################
# FLASK
# Define the Flask routes
#########################################################################

#########################################################################
# refresh tokens
# Refresh the token after a request is made to a protected endpoint, 
# this ensures we won't get signed out prematurely
#########################################################################

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["token"] = access_token 
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response

###########################################################################
# just a simple endpoint.  Let people know the service is alive
###########################################################################

@app.route('/')
def index():
    return ('Hello from Reefberry Pi! <br> <br> controller version: ' + version.CONTROLLER_VERSION + '<br> <br> ><(((º>')



#####################################################################
# set_feedmode
# to start a feed mode.  Must specify Feed mode A, B, C, D or Cancel
#####################################################################


@app.route('/set_feedmode', methods=['POST'])
@cross_origin()
@jwt_required()
def set_feedmode():
    try:
        global AppPrefs

        value = api_flask.api_set_feed_mode(AppPrefs, sqlengine, request)

        response = {}
        response = jsonify({"msg": f'Set Feed Mode {value}',
                            "appuid": AppPrefs.appuid,
                            "feed_SamplingTimeSeed": AppPrefs.feed_SamplingTimeSeed
                            })
        response.status_code = 200
        return response

    except Exception as e:
        AppPrefs.logger.error("set_feedmode: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response


#####################################################################
# get_outlet_list
# return list of outlets on the internal bus
#####################################################################

@app.route('/get_outlet_list/', methods=['GET'])
@cross_origin()
@jwt_required()
def get_outlet_list():
    try:
        global AppPrefs
        outletlist = api_flask.api_get_outlet_list(AppPrefs, request)
        return outletlist

    except Exception as e:
        AppPrefs.logger.error("get_outlet_list: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response


#####################################################################
# get_chartdata_24hr
# return array of chart data with date/time and values
# must specify ProbeID, and scale (temperature_c,
# temperature_f, or humidity)
#####################################################################


@app.route('/get_chartdata_24hr/<probeid>/<unit>', methods=['GET'])
@cross_origin()
@jwt_required()
def get_chartdata_24hr(probeid, unit):

    global AppPrefs

    try:
        results = api_flask.api_get_chartdata_24hr(
            AppPrefs, Influx_client, probeid, unit, request)

        return results

    except Exception as e:
        AppPrefs.logger.error("get_chartdata_24hr: " + str(e))

#####################################################################
# get_chartdata_1hr
# return array of chart data with date/time and values
# must specify ProbeID, and scale (temperature_c,
# temperature_f, or humidity)
#####################################################################


@app.route('/get_chartdata_1hr/<probeid>/<unit>', methods=['GET'])
@cross_origin()
@jwt_required()
def get_chartdata_1hr(probeid, unit):
    global AppPrefs
    try:
        results = api_flask.api_get_chartdata_1hr(
            AppPrefs, Influx_client, probeid, unit, request)

        return results

    except Exception as e:
        AppPrefs.logger.error("get_chartdata_1hr: " + str(e))

#####################################################################
# get_chartdata_1wk
# return array of chart data with date/time and values
# must specify ProbeID, and scale (temperature_c,
# temperature_f, or humidity)
#####################################################################


@app.route('/get_chartdata_1wk/<probeid>/<unit>', methods=['GET'])
@cross_origin()
@jwt_required()
def get_chartdata_1wk(probeid, unit):
    global AppPrefs
    try:
        results = api_flask.api_get_chartdata_1wk(
            AppPrefs, Influx_client, probeid, unit, request)

        return results

    except Exception as e:
        AppPrefs.logger.error("get_chartdata_1wk: " + str(e))

#####################################################################
# get_chartdata_1mo
# return array of chart data with date/time and values
# must specify ProbeID, and scale (temperature_c,
# temperature_f, or humidity)
#####################################################################


@app.route('/get_chartdata_1mo/<probeid>/<unit>', methods=['GET'])
@cross_origin()
@jwt_required()
def get_chartdata_1mo(probeid, unit):
    global AppPrefs
    try:
        results = api_flask.api_get_chartdata_1mo(
            AppPrefs, Influx_client, probeid, unit, request)

        return results

    except Exception as e:
        AppPrefs.logger.error("get_chartdata_1mo: " + str(e))
#####################################################################
# set_outlet_buttonstate
# change the value of button state
# must specify outlet ID and either ON, OFF, or AUTO
#####################################################################


@app.route('/set_outlet_buttonstate/<outletid>/<buttonstate>', methods=['GET', 'PUT'])
@cross_origin()
@jwt_required()
def set_outlet_buttonstate(outletid, buttonstate):
    global AppPrefs
    try:

        response = api_flask.api_set_outlet_buttonstate(
            AppPrefs, sqlengine, outletid, buttonstate, request)
        return response

    except Exception as e:
        AppPrefs.logger.error("set_outlet_buttonstate: " + str(e))


#####################################################################
# set_probe_name
# set the name of the probe
# must specify ProbeID and Name
#####################################################################
@app.route('/set_probe_name/<probeid>/<probename>', methods=['GET', 'PUT'])
@cross_origin()
@jwt_required()
def set_probe_name(probeid, probename):
    global AppPrefs
    try:
        response = api_flask.api_set_probe_name(
            AppPrefs, sqlengine, probeid, probename, request)
        return response

    except Exception as e:
        AppPrefs.logger.error("set_probe_name: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

# #####################################################################
# # set_probe_enable_state
# # set the enable state of the probe
# # must specify ProbeID and true or false
# #####################################################################


# @app.route('/set_probe_enable_state/<probeid>/<enable>', methods=['PUT'])
# @cross_origin()
# def set_probe_enable_state(probeid, enable):
#     global AppPrefs
#     try:
#         response = api_flask.api_set_probe_enable_state(
#             AppPrefs, sqlengine, probeid, enable, request)
#         return response

#     except Exception as e:
#         AppPrefs.logger.error("set_probe_enable_state: " + str(e))
#         response = jsonify({"msg": str(e)})
#         response.status_code = 500
#         return response

#####################################################################
# set_mcp3008_enable_state
# set the enable state of the probe
# must specify ProbeID and true or false
#####################################################################


@app.route('/set_mcp3008_enable_state', methods=['POST'])
@cross_origin()
@jwt_required()
def set_mcp3008_enable_state():
    global AppPrefs
    try:

        response = api_flask.api_set_mcp3008_enable_state(
            AppPrefs, sqlengine, request)
        return response

    except Exception as e:
        AppPrefs.logger.error("set_mcp3008_enable_state: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# set_outlet_enable_state
# set the enable state of the outlet
# must specify ProbeID and true or false
#####################################################################


@app.route('/set_outlet_enable_state', methods=['POST'])
@cross_origin()
@jwt_required()
def set_outlet_enable_state():
    global AppPrefs
    try:

        response = api_flask.api_set_outlet_enable_state(
            AppPrefs, sqlengine, request)

        return response

    except Exception as e:
        AppPrefs.logger.error("set_outlet_enable_state: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# set_outlet_params_light/<outletid>
# set the paramters for outlet of type: Light
# must specify outletid and deliver payload in json
#####################################################################


@app.route('/set_outlet_params_light/<outletid>', methods=["PUT", "POST"])
@cross_origin()
@jwt_required()
def set_outlet_params_light(outletid):
    global AppPrefs
    try:
        response = api_flask.api_set_outlet_params_light(
            AppPrefs, sqlengine, outletid, request)

        return response

    except Exception as e:
        AppPrefs.logger.error("set_outlet_params_light: " + str(e))


#####################################################################
# set_outlet_params_always/<outletid>
# set the paramters for outlet of type: Always
# must specify outletid and deliver payload in json
#####################################################################

@app.route('/set_outlet_params_always/<outletid>', methods=["PUT", "POST"])
@cross_origin()
@jwt_required()
def set_outlet_params_always(outletid):
    global AppPrefs
    try:
        response = api_flask.api_set_outlet_params_always(AppPrefs, sqlengine, outletid, request)
        
        return response


    except Exception as e:
        AppPrefs.logger.error("set_outlet_params_always: " + str(e))

#####################################################################
# set_outlet_params_heater/<outletid>
# set the paramters for outlet of type: Heater
# must specify outletid and deliver payload in json
#####################################################################


@app.route('/set_outlet_params_heater/<outletid>', methods=["PUT", "POST"])
@cross_origin()
@jwt_required()
def set_outlet_params_heater(outletid):
    global AppPrefs
    try:
       
        response = api_flask.api_set_outlet_params_heater(AppPrefs, sqlengine, outletid, request)
        return response 
    

    except Exception as e:
        AppPrefs.logger.error("set_outlet_params_heater: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# set_outlet_params_ph/<outletid>
# set the paramters for outlet of type: PH
# must specify outletid and deliver payload in json
#####################################################################


@app.route('/set_outlet_params_ph/<outletid>', methods=["PUT", "POST"])
@cross_origin()
@jwt_required()
def set_outlet_params_ph(outletid):

    global AppPrefs
    try:
        
        response = api_flask.api_set_outlet_params_ph(AppPrefs, sqlengine, outletid, request)
        
        return response
        

    except Exception as e:
        AppPrefs.logger.error("set_outlet_params_ph: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response


#####################################################################
# set_outlet_params_return/<outletid>
# set the paramters for outlet of type: Return
# must specify outletid and deliver payload in json
#####################################################################

@app.route('/set_outlet_params_return/<outletid>', methods=["PUT", "POST"])
@cross_origin()
@jwt_required()
def set_outlet_params_return(outletid):

    global AppPrefs
    try:
        
        response = api_flask.api_set_outlet_params_return(AppPrefs, sqlengine, outletid, request)
        
        return response
        

    except Exception as e:
        AppPrefs.logger.error("set_outlet_params_return: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# set_outlet_params_skimmer/<outletid>
# set the paramters for outlet of type: Skimmer
# must specify outletid and deliver payload in json
#####################################################################


@app.route('/set_outlet_params_skimmer/<outletid>', methods=["PUT", "POST"])
@cross_origin()
@jwt_required()
def set_outlet_params_skimmer(outletid):

    global AppPrefs
    try:
        
        response = api_flask.api_set_outlet_params_skimmer(AppPrefs, sqlengine, outletid, request)
       
        return response
       

    except Exception as e:
        AppPrefs.logger.error("set_outlet_params_skimmer: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# get_global_prefs/
# get the global paramters for the controlled
# things like temperature scale, etc...
#####################################################################

@app.route('/get_global_prefs/', methods=["GET"])
@cross_origin()
@jwt_required()

def get_global_prefs():

    try:
        global AppPrefs
        globalPrefs = api_flask.api_get_global_prefs(
            AppPrefs, sqlengine, request)

        response = globalPrefs
        response.status_code = 200

        return response

    except Exception as e:
        AppPrefs.logger.error("get_global_prefs: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# set_global_prefs/
# set the global parameters such as temps scale C or F
# must specify outletid and deliver payload in json
#####################################################################


@app.route('/set_global_prefs/', methods=["PUT", "POST"])
@cross_origin()
@jwt_required()

def set_global_prefs():
    global AppPrefs
    try:
        
        response = api_flask.api_set_global_prefs(AppPrefs, sqlengine, request)
        return response
    
       
    except Exception as e:
        AppPrefs.logger.error("set_global_prefs: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# get_current_probs_stats/
# get the stats for the specified probe
# things like last value, probe name, etc....
#####################################################################


@app.route('/get_current_probe_stats/<probeid>', methods=["GET"])
@cross_origin()
@jwt_required()
def get_current_probe_stats(probeid):

    global AppPrefs
    try:
        
        response = api_flask.api_get_current_probe_stats(AppPrefs, probeid, request)
        return response


    except Exception as e:
        AppPrefs.logger.error("get_current_probe_stats: " + str(e))
        # response = jsonify({"msg": str(e)})
        response = jsonify(probeid)
        response.status_code = 500
        return response

#####################################################################
# get_current_outlet_stats/
# get the stats for the specified outlet
# things like last button state, status, etc....
#####################################################################


@app.route('/get_current_outlet_stats/<outletid>', methods=["GET"])
@cross_origin()
@jwt_required()
def get_current_outlet_stats(outletid):
    
    global AppPrefs
    try:
       
        response = api_flask.api_get_current_outlet_stats(AppPrefs, outletid, request)
        return response
        

    except Exception as e:
        AppPrefs.logger.error("get_current_outlet_stats: " + str(e))
        # response = jsonify({"msg": str(e)})
        response = jsonify(AppPrefs.outletDict[outletid])
        response.status_code = 500
        return response

#####################################################################
# get_probe_list
# return list of connected probes
#####################################################################


@app.route('/get_probe_list/', methods=['GET'])
@cross_origin()
@jwt_required()
def get_probe_list():
    global AppPrefs
    try:
     
        probedict = api_flask.api_get_probe_list(AppPrefs, request)
        
        return probedict

    except Exception as e:
        AppPrefs.logger.error("get_probe_list: " + str(e))

#####################################################################
# get_mcp3008_enable_state
# return list of mcp3008 probes and their enabled state
#####################################################################


@app.route('/get_mcp3008_enable_state/', methods=['GET'])
@cross_origin()
@jwt_required()
def get_mcp3008_enable_state():
    global AppPrefs
    try:
       
        probedict = api_flask.api_get_mcp3008_enable_state(AppPrefs, sqlengine, request)

        return probedict


    except Exception as e:
        AppPrefs.logger.error("get_mcp3008_enable_state: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# get_connected_temp_probes
# return list of ds18b20 temperature probes that are connected to the
# system and showing up in '/sys/bus/w1/devices/'
#####################################################################


@app.route('/get_connected_temp_probes/', methods=['GET'])
@cross_origin()
@jwt_required()
def get_connected_temp_probes():

    try:
        global AppPrefs
        probelist = api_flask.api_get_connected_temp_probes()
        return probelist

    except Exception as e:
        AppPrefs.logger.error("get_connected_temp_probes: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# get_assigned_temp_probes
# return list of ds18b20 temperature probes that that have been
# assigned to Probe IDs
#####################################################################


@app.route('/get_assigned_temp_probes/', methods=['GET'])
@cross_origin()
@jwt_required()
def get_assigned_temp_probes():

    try:
        global AppPrefs
        probelist = api_flask.api_get_assigned_temp_probes(
            AppPrefs, sqlengine, request)
        return probelist

    except Exception as e:
        AppPrefs.logger.error("get_assigned_temp_probes: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# set_connected_temp_probes
# assign the selected ds18b20 probes to Probe ID 1,2,3,4
#####################################################################


@app.route('/set_connected_temp_probes', methods=['POST'])
@cross_origin()
@jwt_required()

def set_connected_temp_probes():
    try:
        global AppPrefs

        api_flask.api_set_connected_temp_probes(AppPrefs, sqlengine, request)

        response = {}
        response = jsonify({"msg": 'Updated temperature probes',
                            })
        response.status_code = 200
        return response

    except Exception as e:
        AppPrefs.logger.error("set_connected_temp_probes: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# set_column_widget_order
# save the widget order to the column tables
#####################################################################


@app.route('/set_column_widget_order', methods=['POST'])
@cross_origin()
@jwt_required()

def set_column_widget_order():
    try:
        global AppPrefs

        api_flask.api_set_column_widget_order(AppPrefs, sqlengine, request)

        response = {}
        response = jsonify({"msg": 'Saved Column Order',
                            })
        response.status_code = 200
        return response

    except Exception as e:
        AppPrefs.logger.error("set_column_widget_order: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# get_outlet_enable_state
# return list of outlets with their enabled state
#####################################################################


@app.route('/get_outlet_enable_state/', methods=['GET'])
@cross_origin()
@jwt_required()
def get_outlet_enable_state():
    global AppPrefs

    try:
        
        response = api_flask.api_get_outlet_enable_state(AppPrefs, sqlengine, request)
        return response
    

    except Exception as e:
        AppPrefs.logger.error("get_outlet_enable_state: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# get_token
# return login token
#####################################################################


@app.route('/get_token', methods=['POST'])
@cross_origin()
def get_token():
    global AppPrefs
    # username = request.json.get("username", None)
    # password = request.json.get("password", None)
    # if username.lower() != "pi" or password != "reefberry":
    #     return {"msg": "Wrong username or password"}, 401

    # access_token = create_access_token(identity=username)
    # response = {"token": access_token}

    # return response
    try:
        response = api_flask.api_get_token(AppPrefs, sqlengine, request)
        return response
    except Exception as e:
        AppPrefs.logger.error("get_token: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# get_outletchartdata
# return array of chart data with date/time and values
# must specify outletID, and time frame (24hr, 1wk, 1mo, etc...)
#####################################################################


@app.route('/get_outletchartdata/<outletid>/<timeframe>', methods=['GET'])
@cross_origin()
@jwt_required()

def get_outletchartdata(outletid, timeframe):
    global AppPrefs
    try:
        
        results = api_flask.api_get_outletchartdata(AppPrefs, Influx_client, outletid, timeframe, request)

        return results

    except Exception as e:
        AppPrefs.logger.error("get_outletchartdata: " + str(e))
        return (str(e))

#####################################################################
# get_column_widget_order
# get widget order from th column tables
#####################################################################


@app.route('/get_column_widget_order/', methods=['GET'])
@cross_origin()
@jwt_required()
def get_column_widget_order():
    global AppPrefs
    try:
        
        widgetlist1, widgetlist2, widgetlist3 = api_flask.api_get_column_widget_order(
            AppPrefs, sqlengine, request)
        

        return {"column1": widgetlist1, "column2": widgetlist2, "column3": widgetlist3}

    except Exception as e:
        AppPrefs.logger.error("get_column_widget_order: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response


#####################################################################
# get_user_list
# return list of users that have access to this instance
#####################################################################


@app.route('/get_user_list/', methods=['GET'])
@cross_origin()
@jwt_required()

def get_user_list():
    global AppPrefs
    try:
        
        response = api_flask.api_get_user_list(AppPrefs, sqlengine, request)

        return response

    except Exception as e:
        AppPrefs.logger.error("get_user_list: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# set_add_user
# add new user to have access to this instance
#####################################################################


@app.route('/set_add_user', methods=['POST'])
@cross_origin()
@jwt_required()

def set_add_user():
    global AppPrefs
    try:
        
        response = api_flask.api_set_add_user(AppPrefs, sqlengine, request)

        return response

    except Exception as e:
        AppPrefs.logger.error("set_add_user: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# set_remove_user
# delete a user from this instance
#####################################################################


@app.route('/set_remove_user', methods=['POST'])
@cross_origin()
@jwt_required()

def set_remove_user():
    global AppPrefs
    try:
        
        response = api_flask.api_set_remove_user(AppPrefs, sqlengine, request)

        return response

    except Exception as e:
        AppPrefs.logger.error("set_remove_user: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# set_change_password
# change a user's password
#####################################################################


@app.route('/set_change_password', methods=['POST'])
@cross_origin()
@jwt_required()

def set_change_password():
    global AppPrefs
    try:
        
        response = api_flask.api_set_change_password(AppPrefs, sqlengine, request)

        return response

    except Exception as e:
        AppPrefs.logger.error("set_change_password: " + str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500
        return response

#####################################################################
# get_analog_cal_stats
# return stats that are used for calibration of an analog probe
# connected to tghe mcp3008 analog to digital converter
#####################################################################


@app.route('/get_analog_cal_stats/<channelid>', methods=['GET'])
@cross_origin()
@jwt_required()

def get_analog_cal_stats(channelid):
    global AppPrefs
    try:
        
        response = api_flask.api_get_analog_cal_stats(AppPrefs, sqlengine, request, channelid)

        return response

    except Exception as e:
        errString = str(type(e).__name__) + " – " + str(e)
        AppPrefs.logger.error("get_analog_cal_stats: " + errString)
        response = jsonify({"msg": "get_analog_cal_stats: " + errString})
        response.status_code = 500
        return response


#####################################################################
# set_analog_ph_cal
# set low, mid, or high target value for ph cal
#####################################################################


@app.route('/set_analog_ph_cal', methods=['POST'])
@cross_origin()
@jwt_required()

def set_analog_ph_cal():
    global AppPrefs
    try:
        
        response = api_flask.api_set_analog_ph_cal(AppPrefs, sqlengine, request)

        return response

    except Exception as e:
        errString = str(type(e).__name__) + " – " + str(e)
        AppPrefs.logger.error("set_analog_ph_cal: " + errString)
        response = jsonify({"msg": "set_analog_ph_cal: " + errString})
        response.status_code = 500
        return response


############################################################


#MARK: Run Application

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(AppPrefs.flask_port))
