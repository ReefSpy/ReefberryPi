import logging
import logging.handlers
import defs_common
import defs_Influx
import cls_Preferences
import mcp3008
import threading
import defs_mysql
from influxdb_client.client.write_api import SYNCHRONOUS
import RPi.GPIO as GPIO
import GPIO_config
import dht11
from datetime import datetime, timedelta
import ds18b20
import time
import numpy
import ph_sensor
import defs_outletcontrol
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import select
from sqlalchemy import update
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager

app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type, Authorization'
app.config["JWT_SECRET_KEY"] = "supersecret-reefberrypi-key"
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)

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

logger.info("*** Reefberry Pi controller startup ***")

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
#defs_mysql.readGlobalPrefs(mySQLDB, AppPrefs, logger)
defs_mysql.readGlobalPrefs_ex(sqlengine, AppPrefs, logger)
# temperature probes
#defs_mysql.readTempProbes(mySQLDB, AppPrefs, logger)
defs_mysql.readTempProbes_ex(sqlengine, AppPrefs, logger)
#defs_mysql.readOutletPrefs(mySQLDB, AppPrefs, logger)
defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, logger)
defs_mysql.readDHTSensor_ex(sqlengine, AppPrefs, logger)
defs_mysql.readMCP3008Prefs_ex(sqlengine, AppPrefs, logger)


# set up the GPIO
GPIO_config.initGPIO()

# dht11 temperature and humidity sensor
dht_sensor = dht11.DHT11(pin=GPIO_config.dht11)


def apploop():

    global AppPrefs
    
    logger.info("Starting App Cycle")

    while True:
        logger.debug ("******************************************************")
        logger.debug ("Start Loop")
        logger.debug ("******************************************************")
        
        ##########################################################################################
        # read each of the 8 channels on the mcp3008
        # channels (0-7)
        ##########################################################################################
        # only read the data at every ph_SamplingInterval (ie: 500ms or 1000ms)
        if (int(round(time.time()*1000)) - AppPrefs.dv_SamplingTimeSeed) > AppPrefs.dv_SamplingInterval:
            #for x in range (0,8):
            for ch in AppPrefs.mcp3008Dict:
                #if AppPrefs.mcp3008Dict[ch].ch_enabled.lower() == "true":
                logger.debug("mcp3008 ch" + str(AppPrefs.mcp3008Dict[ch].ch_num) + " " + str(AppPrefs.mcp3008Dict[ch].ch_name) + " = " + str(AppPrefs.mcp3008Dict[ch].lastValue))
                dv = mcp3008.readadc(int(AppPrefs.mcp3008Dict[ch].ch_num), GPIO_config.SPICLK, GPIO_config.SPIMOSI,
                                        GPIO_config.SPIMISO, GPIO_config.SPICS)
                logger.debug("CH" + str(AppPrefs.mcp3008Dict[ch].ch_num) + " = " + str(dv))
                AppPrefs.mcp3008Dict[ch].ch_dvlist.append(dv)
                # once we hit our desired sample size of ph_numsamples (ie: 120)
                # then calculate the average value
                if len(AppPrefs.mcp3008Dict[ch].ch_dvlist) >= int(AppPrefs.mcp3008Dict[ch].ch_numsamples):
                    # The probes may pick up noise and read very high or
                    # very low values that we know are not good values. We are going to use numpy
                    # to calculate the standard deviation and remove the outlying data that is
                    # Sigma standard deviations away from the mean.  This way these outliers
                    # do not affect our results
                    logger.debug("mcp3008 ch" + str(AppPrefs.mcp3008Dict[ch].ch_num) + " raw data " + str(AppPrefs.mcp3008Dict[ch].ch_name) + " " + str(AppPrefs.mcp3008Dict[ch].ch_dvlist))
                    dv_FilteredCounts = numpy.array(AppPrefs.mcp3008Dict[ch].ch_dvlist)
                    dv_FilteredMean = numpy.mean(dv_FilteredCounts, axis=0)
                    dv_FlteredSD = numpy.std(dv_FilteredCounts, axis=0)
                    dv_dvlistfiltered = [x for x in dv_FilteredCounts if
                                        (x > dv_FilteredMean - float(AppPrefs.mcp3008Dict[ch].ch_sigma) * dv_FlteredSD)]
                    dv_dvlistfiltered = [x for x in dv_dvlistfiltered if
                                        (x < dv_FilteredMean + float(AppPrefs.mcp3008Dict[ch].ch_sigma) * dv_FlteredSD)]

                    logger.debug("mcp3008 ch" + str(AppPrefs.mcp3008Dict[ch].ch_num) + " filtered " + str(AppPrefs.mcp3008Dict[ch].ch_name) + " " + str(dv_dvlistfiltered))
                
                    # calculate the average of our filtered list
                    try:
                        dv_AvgCountsFiltered = int(sum(dv_dvlistfiltered)/len(dv_dvlistfiltered))
                        print( "{:.2f}".format(dv_AvgCountsFiltered)) ## delete this line
                    except:
                        dv_AvgCountsFiltered = 1  # need to revisit this error handling. Exception thrown when all
                                                    # values were 1023
                        print("Error collecting data! " + "mcp3008 ch" + str(AppPrefs.mcp3008Dict[ch].ch_num))  

                    if AppPrefs.mcp3008Dict[ch].ch_type == "ph":
                        # bug, somtimes value is coming back high, like really high, like 22.0.  this is an impossible
                        # value since max ph is 14.  need to figure this out later, but for now, lets log this val to aid in
                        # debugging
                        orgval = dv_AvgCountsFiltered
                        
                        #convert digital value to ph
                        lowCal = AppPrefs.mcp3008Dict[ch].ch_ph_low
                        medCal = AppPrefs.mcp3008Dict[ch].ch_ph_med
                        highCal = AppPrefs.mcp3008Dict[ch].ch_ph_high
                        
                        dv_AvgCountsFiltered = ph_sensor.dv2ph(dv_AvgCountsFiltered, ch, lowCal, medCal, highCal)
                        dv_AvgCountsFiltered = float("{:.2f}".format(dv_AvgCountsFiltered))

                        if dv_AvgCountsFiltered > 14:
                            logger.error("Invalid PH value: " + str(dv_AvgCountsFiltered) + " " + str(orgval) + " " + str(dv_dvlistfiltered))
                           
                    # if enough time has passed (ph_LogInterval) then log the data to file
                    # otherwise just print it to console
                    timestamp = datetime.now()
                    if (int(round(time.time()*1000)) - AppPrefs.mcp3008Dict[ch].LastLogTime) > AppPrefs.dv_LogInterval:
                        # sometimes a high value, like 22.4 gets recorded, i need to fix this, but for now don't log that
##                            if ph_AvgFiltered < 14.0:  
               #         defs_common.logprobedata("mcp3008_ch" + str(AppPrefs.mcp3008Dict[ch].ch_num) + "_", "{:.2f}".format(dv_AvgCountsFiltered))
                        logger.info("mcp3008_ch" + str(AppPrefs.mcp3008Dict[ch].ch_num) + " = " + str("{:.2f}".format(dv_AvgCountsFiltered)))
                        Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "ph", "tags": {
                                        "appuid": AppPrefs.appuid, "probeid": "mcp3008_ch" + str(AppPrefs.mcp3008Dict[ch].ch_num)}, "fields": {"value": float("{:.2f}".format(dv_AvgCountsFiltered))}, "time": datetime.utcnow()}])
                        AppPrefs.mcp3008Dict[ch].LastLogTime = int(round(time.time()*1000))
                    else:
                        print(timestamp.strftime("%Y-%m-%d %H:%M:%S") + " dv = "
                                + "{:.2f}".format(dv_AvgCountsFiltered))

                    AppPrefs.mcp3008Dict[ch].lastValue = str(dv_AvgCountsFiltered)
                    # clear the list so we can populate it with new data for the next data set
                    AppPrefs.mcp3008Dict[ch].ch_dvlist.clear()
                    # record the new sampling time
                    AppPrefs.dv_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
    
                   
        
        
        
        ###################################################################
        # read temp probe list
        ###################################################################
        #defs_mysql.readTempProbes(mySQLDB, AppPrefs, logger)
        ###################################################################
        # ds18b20 Temperture sensor
        ###################################################################
        try:
            for tProbe in AppPrefs.tempProbeDict:
                dstempC = float(ds18b20.read_temp(
                    AppPrefs.tempProbeDict.get(tProbe).probeid.split("_")[1], "C"))
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
                    AppPrefs.tempProbeDict.get(tProbe).lastTemperature = str(dstempF)
                else:
                    AppPrefs.tempProbeDict.get(tProbe).lastTemperature = str(dstempC)

        except Exception as e:
            logger.error("Unable to read ds18b20 temperature! " + str(e))
        ###################################################################
        # dht11 temp and humidity data
        ###################################################################
        if AppPrefs.dht_enable == "true":
            result = dht_sensor.read()
            if result.is_valid():
                temp_c = result.temperature
                hum = result.humidity
                temp_f = float(defs_common.convertCtoF(temp_c))

                if AppPrefs.temperaturescale == "F":
                    AppPrefs.dhtDict.get("DHT-T").lastValue = str(temp_f)
                else: 
                    AppPrefs.dhtDict.get("DHT-T").lastValue = str(temp_c)

                AppPrefs.dhtDict.get("DHT-H").lastValue = str(hum)

                try:
                    # print("dht11 Temp C = " + str(temp_c) + " C")
                    Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "temperature_c", "tags": {
                                        "appuid": AppPrefs.appuid, "probeid": "DHT-T"}, "fields": {"value": float(temp_c)}, "time": datetime.utcnow()}])

                    
                    # print("dht11 Temp F =  " + str(temp_f) + " F")
                    Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "temperature_f", "tags": {
                                        "appuid": AppPrefs.appuid, "probeid": "DHT-T"}, "fields": {"value": temp_f}, "time": datetime.utcnow()}])

                    # print("dht11 Temp = " + str(temp_c) + "C / " + str(temp_f) + "F")
                    # print("dht11 Humidity = " + str(hum) + "%")
                    logger.debug("dht11 Temp = " + str(temp_c) +
                                "C / " + str(temp_f) + "F")
                    logger.debug("dht11 Humidity = " + str(hum) + "%")
                    Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "humidity", "tags": {
                                        "appuid": AppPrefs.appuid, "probeid": "DHT-H"}, "fields": {"value": hum}, "time": datetime.utcnow()}])
                except Exception as e:
                    logger.error("Error logging DHT data to InfluxDB!" + str(e))


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
            AppPrefs.logger.info("Feed Mode " + AppPrefs.feed_CurrentMode + " enabled")
            AppPrefs.feedTimeLeft = (int(AppPrefs.feed_ModeTotaltime)*1000) - (int(round(time.time()*1000)) - AppPrefs.feed_SamplingTimeSeed)
            
            if AppPrefs.feedTimeLeft <=0:
                # print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                #         " Feed Mode: " + self.AppPrefs.feed_CurrentMode + " COMPLETE" + Style.RESET_ALL)
                logging.info("Feed Mode " + AppPrefs.feed_CurrentMode + " Complete")
                AppPrefs.feed_CurrentMode = "CANCEL"
                # timestamp = datetime.now()

                # self.broadcastFeedStatus(self.AppPrefs.feed_CurrentMode, self.AppPrefs.feedTimeLeft)
                        
                AppPrefs.feed_ExtraTimeSeed = int(round(time.time()*1000))
                print ("Extra time starts at: " + str(AppPrefs.feed_ExtraTimeSeed) + " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:    
                # print (Fore.WHITE + Style.BRIGHT + datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                #         " Feed Mode: " + self.AppPrefs.feed_CurrentMode + " (" + self.AppPrefs.feed_ModeTotaltime + "s) " + "Time Remaining: " + str(round(self.AppPrefs.feedTimeLeft/1000)) + "s"
                #         + Style.RESET_ALL)
                # timestamp = datetime.now()
                logging.info("Feed Mode: " + AppPrefs.feed_CurrentMode + " (" + AppPrefs.feed_ModeTotaltime + "s) " + "Time Remaining: " + str(round(AppPrefs.feedTimeLeft/1000)) + "s")

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
             
                
                pin = GPIO_config.int_outletpins.get(AppPrefs.outletDict.get(outlet).outletid)

                # handle outlet actions based on settings
                # control type ALWAYS
                if AppPrefs.outletDict.get(outlet).control_type == "Always":
                    defs_outletcontrol.handle_outlet_always(AppPrefs, outlet, AppPrefs.outletDict.get(outlet).button_state, pin)
                # control type HEATER
                elif AppPrefs.outletDict.get(outlet).control_type == "Heater":
                    defs_outletcontrol.handle_outlet_heater(AppPrefs, outlet, AppPrefs.outletDict.get(outlet).button_state, pin)
                # control type RETURN PUMP
                elif AppPrefs.outletDict.get(outlet).control_type == "Return":
                    defs_outletcontrol.handle_outlet_returnpump(AppPrefs, outlet, AppPrefs.outletDict.get(outlet).button_state, pin)
                # contriol type SKIMMER
                elif AppPrefs.outletDict.get(outlet).control_type == "Skimmer":
                    defs_outletcontrol.handle_outlet_skimmer(AppPrefs, outlet, AppPrefs.outletDict.get(outlet).button_state, pin)
                # control type LIGHT
                elif AppPrefs.outletDict.get(outlet).control_type == "Light":
                    defs_outletcontrol.handle_outlet_light(AppPrefs, outlet, AppPrefs.outletDict.get(outlet).button_state, pin)
                # elif AppPrefs.outletDict.get(outlet).controltype == "PH":
                #     return defs_outletcontrolsim.handle_outlet_ph(self, outlet, button_state, pin)
            
        except Exception as e:
            logger.error("Error reading outlet data! " + str(e))
            
        
       
        ##########################################################################################
        # pause to slow down the loop
        ##########################################################################################
        logger.debug ("******************************************************")
        logger.debug ("End Loop")
        logger.debug ("******************************************************")
        time.sleep(.5)




#apploop()

# Start the main loop in a separate thread
import threading
thread = threading.Thread(target=apploop)
thread.start()

# Define the Flask routes
@app.route('/')
def index():
    return 'Hello, ReefberryPi!'

@app.route('/set_var1/<int:value>')
def set_var1(value):
    global var1
    var1 = value
    return f"var1 set to {value}"

@app.route('/set_var2/<int:value>')
def set_var2(value):
    global var2
    var2 = value
    return f"var2 set to {value}"

@app.route('/get_vars')
def get_vars():
    global var1, var2
    return jsonify({'var1': var1, 'var2': var2})

@app.route('/reloadprefs/')
def reloadprefs():
    global AppPrefs
    global mySQLDB
    global logger
    
    defs_mysql.readTempProbes_ex(sqlengine, AppPrefs, logger)
    defs_mysql.readGlobalPrefs_ex(sqlengine, AppPrefs, logger)
    defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, logger)
    return "Reload Prefs"

#####################################################################
# set_feedmode
# to start a feed mode.  Must specify Feed mode A, B, C, D or Cancel
#####################################################################
@app.route('/set_feedmode/<value>')
@cross_origin()
def set_feedmode(value):
    global AppPrefs
    AppPrefs.logger.info("Set feed mode: " + value)
    AppPrefs.feed_CurrentMode = value
    AppPrefs.feed_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
    AppPrefs.feed_PreviousMode = "CANCEL"

    response = jsonify({"msg": f'Set Feed Mode {value}',
                                "appuid": AppPrefs.appuid,
                                "feed_SamplingTimeSeed": AppPrefs.feed_SamplingTimeSeed
                              })
            

    response.status_code = 200 



    return response


     

#####################################################################
# set_outlet_light
# set the parameters for a light outlet
#####################################################################
@app.route('/set_outlet_light/', methods = ['GET'])
@cross_origin()
def set_outlet_light():
    global AppPrefs
    global sqlengine

    # build table object from table in DB
    metadata_obj = MetaData()
    outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)

    params = request.args.to_dict()
    
    print (params)

    AppPrefs.appuid = params["appuid"]
    AppPrefs.outletDict[params["outletid"]].outletname = params["outletname"]
    AppPrefs.outletDict[params["outletid"]].control_type = params["control_type"]
    AppPrefs.outletDict[params["outletid"]].enable_log = params["enable_log"]       
    AppPrefs.outletDict[params["outletid"]].button_state = params["button_state"] 
    AppPrefs.outletDict[params["outletid"]].light_on = params["light_on"] 
    AppPrefs.outletDict[params["outletid"]].light_off = params["light_off"] 
    
    stmt = (
        update(outlet_table)
        .where(outlet_table.c.outletid ==  AppPrefs.outletDict[params["outletid"]].outletid)
        .where(outlet_table.c.appuid == AppPrefs.appuid)
        .values(outletname = AppPrefs.outletDict[params["outletid"]].outletname,
                control_type = AppPrefs.outletDict[params["outletid"]].control_type,
                enable_log = AppPrefs.outletDict[params["outletid"]].enable_log,
                button_state = AppPrefs.outletDict[params["outletid"]].button_state,
                light_on = AppPrefs.outletDict[params["outletid"]].light_on,
                light_off = AppPrefs.outletDict[params["outletid"]].light_off
                )
    )
    conn = sqlengine.connect()

    conn.execute(stmt)
    conn.commit()
        
    return f"Looking for {params}"

#####################################################################
# get_outlet_list
# return list of outlets on the internal bus
#####################################################################
@app.route('/get_outlet_list/', methods = ['GET'])
@cross_origin()
def get_outlet_list():
    
    try:
        global AppPrefs
        
        outletdict = {}
        
        # loop through each outlet 
        for outlet in AppPrefs.outletDict:
#           convert temperature values to F if using Fahrenheit
            if AppPrefs.temperaturescale == "F":
                heater_on_x = defs_common.convertCtoF(AppPrefs.outletDict[outlet].heater_on)
                heater_off_x = defs_common.convertCtoF(AppPrefs.outletDict[outlet].heater_off)
            else:
                heater_on_x = AppPrefs.outletDict[outlet].heater_on
                heater_off_x = AppPrefs.outletDict[outlet].heater_off


            outletdict[outlet]={"outletid": AppPrefs.outletDict[outlet].outletid , 
                                "outletname": AppPrefs.outletDict[outlet].outletname, 
                                "control_type": AppPrefs.outletDict[outlet].control_type, 
                                "outletstatus": AppPrefs.outletDict[outlet].outletstatus,
                                "button_state": AppPrefs.outletDict[outlet].button_state,
                                "heater_on": heater_on_x,
                                "heater_off": heater_off_x,
                                "heater_probe": AppPrefs.outletDict[outlet].heater_probe,
                                "light_on": AppPrefs.outletDict[outlet].light_on,
                                "light_off": AppPrefs.outletDict[outlet].light_off,
                                "always_state": AppPrefs.outletDict[outlet].always_state,
                                "return_enable_feed_a": (AppPrefs.outletDict[outlet].return_enable_feed_a).lower() == "true",
                                "return_enable_feed_b": (AppPrefs.outletDict[outlet].return_enable_feed_b).lower() == "true",
                                "return_enable_feed_c": (AppPrefs.outletDict[outlet].return_enable_feed_c).lower() == "true",
                                "return_enable_feed_d": (AppPrefs.outletDict[outlet].return_enable_feed_d).lower() == "true",
                                "return_feed_delay_a": AppPrefs.outletDict[outlet].return_feed_delay_a,
                                "return_feed_delay_b": AppPrefs.outletDict[outlet].return_feed_delay_b,
                                "return_feed_delay_c": AppPrefs.outletDict[outlet].return_feed_delay_c,
                                "return_feed_delay_d": AppPrefs.outletDict[outlet].return_feed_delay_d,

                                "skimmer_enable_feed_a": (AppPrefs.outletDict[outlet].skimmer_enable_feed_a).lower() == "true",
                                "skimmer_enable_feed_b": (AppPrefs.outletDict[outlet].skimmer_enable_feed_b).lower() == "true",
                                "skimmer_enable_feed_c": (AppPrefs.outletDict[outlet].skimmer_enable_feed_c).lower() == "true",
                                "skimmer_enable_feed_d": (AppPrefs.outletDict[outlet].skimmer_enable_feed_d).lower() == "true",
                                "skimmer_feed_delay_a": AppPrefs.outletDict[outlet].skimmer_feed_delay_a,
                                "skimmer_feed_delay_b": AppPrefs.outletDict[outlet].skimmer_feed_delay_b,
                                "skimmer_feed_delay_c": AppPrefs.outletDict[outlet].skimmer_feed_delay_c,
                                "skimmer_feed_delay_d": AppPrefs.outletDict[outlet].skimmer_feed_delay_d,

                                }
            
                             

        if len(outletdict) < 8:
            return "Error getting list"     
        else:
            return outletdict    
    
    except Exception as e:
        AppPrefs.logger.error("get_outlet_list: " +  str(e))

#####################################################################
# get_tempprobe_list
# return list of ds18b20 temperature probes 
#####################################################################
@app.route('/get_tempprobe_list/', methods = ['GET'])
@cross_origin()
def get_tempprobe_list():
    
    try:
        global AppPrefs
        
        probedict = {}
        
        # loop through each section
        for probe in AppPrefs.tempProbeDict:
            probedict[probe]={"probetype": "ds18b20" , 
                              "probeid": AppPrefs.tempProbeDict[probe].probeid, 
                              "probename": AppPrefs.tempProbeDict[probe].name,
                              "sensortype": "temperature", 
                              "lastValue": AppPrefs.tempProbeDict[probe].lastTemperature}
            
        return probedict    
    
    except Exception as e:
        AppPrefs.logger.error("get_tempprobe_list: " +  str(e))

#####################################################################
# get_dht_sensor
# return values of dht temperature/humidity sensor if enabled
#####################################################################
@app.route('/get_dht_sensor/', methods = ['GET'])
@cross_origin()
def get_dht_sensor():
    
    try:
        global AppPrefs
        
        dhtdict = {}
        print(dhtdict)
        if AppPrefs.dht_enable == "true":
            dhtdict["DHT-T"]={"sensortype": AppPrefs.dhtDict["DHT-T"].sensortype , 
                                "probename": AppPrefs.dhtDict["DHT-T"].name,
                                "probeid": AppPrefs.dhtDict["DHT-T"].probeid, 
                                "probetype": "DHT", 
                                "lastValue": AppPrefs.dhtDict["DHT-T"].lastValue}
            dhtdict["DHT-H"]={"sensortype": AppPrefs.dhtDict["DHT-H"].sensortype , 
                                "probename": AppPrefs.dhtDict["DHT-H"].name,
                                "probeid": AppPrefs.dhtDict["DHT-H"].probeid, 
                                "probetype": "DHT", 
                                "lastValue": AppPrefs.dhtDict["DHT-H"].lastValue}
            
            return dhtdict    
        else:
            response = jsonify({"msg": 'DHT Disabled',
                                "dht_enable": 'false'
                            })

            response.status_code = 200  

            return response
           
    
    except Exception as e:
        AppPrefs.logger.error("get_dht_sensor: " +  str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500 
        return response

#####################################################################
# get_chartdata_24hr
# return array of chart data with date/time and values
# must specify ProbeID, and scale (temperature_c,
# temperature_f, or humidity)
#####################################################################
@app.route('/get_chartdata_24hr/<probeid>/<unit>', methods = ['GET'])
@cross_origin()
def get_chartdata_24hr(probeid, unit):

    try:
        global AppPrefs
        if unit == "temperature":
            if AppPrefs.temperaturescale =="F":
                unit = "temperature_f"
            else:
                unit = "temperature_c"

        bucket = "reefberrypi_probe_1dy"

        query_api = Influx_client.query_api()

        query = f'from(bucket: "reefberrypi_probe_1dy") \
        |> range(start: -24h) \
        |> filter(fn: (r) => r["_measurement"] == "{unit}") \
        |> filter(fn: (r) => r["_field"] == "value") \
        |> filter(fn: (r) => r["appuid"] == "{AppPrefs.appuid}") \
        |> filter(fn: (r) => r["probeid"] == "{probeid}") \
        |> aggregateWindow(every: 10m, fn: mean, createEmpty: false) \
        |> yield(name: "mean")'


        result = query_api.query(org=AppPrefs.influxdb_org, query=query)

        results = []
        for table in result:
            for record in table.records:
                results.append((record.get_time(), record.get_value()))

        # for result in results:
        #     format_string = '%Y-%m-%d %H:%M:%S'
        #     date_string = result[0].strftime(format_string)
        #     #print(date_string)
    
        return results

    except Exception as e:
        AppPrefs.logger.error("get_chartdata_24hr: " +  str(e))

#####################################################################
# get_chartdata_1hr
# return array of chart data with date/time and values
# must specify ProbeID, and scale (temperature_c,
# temperature_f, or humidity)
#####################################################################
@app.route('/get_chartdata_1hr/<probeid>/<unit>', methods = ['GET'])
@cross_origin()
def get_chartdata_1hr(probeid, unit):

    try:
        global AppPrefs
        if unit == "temperature":
            if AppPrefs.temperaturescale =="F":
                unit = "temperature_f"
            else:
                unit = "temperature_c"

        bucket = "reefberrypi_probe_1hr"

        query_api = Influx_client.query_api()

        query = f'from(bucket: "reefberrypi_probe_1hr") \
        |> range(start: -1h) \
        |> filter(fn: (r) => r["_measurement"] == "{unit}") \
        |> filter(fn: (r) => r["_field"] == "value") \
        |> filter(fn: (r) => r["appuid"] == "{AppPrefs.appuid}") \
        |> filter(fn: (r) => r["probeid"] == "{probeid}") \
        |> aggregateWindow(every: 30s, fn: mean, createEmpty: false) \
        |> yield(name: "mean")'


        result = query_api.query(org=AppPrefs.influxdb_org, query=query)

        results = []
        for table in result:
            for record in table.records:
                results.append((record.get_time(), record.get_value()))
    
        return results

    except Exception as e:
        AppPrefs.logger.error("get_chartdata_1hr: " +  str(e))

#####################################################################
# get_chartdata_1wk
# return array of chart data with date/time and values
# must specify ProbeID, and scale (temperature_c,
# temperature_f, or humidity)
#####################################################################
@app.route('/get_chartdata_1wk/<probeid>/<unit>', methods = ['GET'])
@cross_origin()
def get_chartdata_1wk(probeid, unit):

    try:
        global AppPrefs
        if unit == "temperature":
            if AppPrefs.temperaturescale =="F":
                unit = "temperature_f"
            else:
                unit = "temperature_c"

        bucket = "reefberrypi_probe_1wk"

        query_api = Influx_client.query_api()

        query = f'from(bucket: "reefberrypi_probe_1wk") \
        |> range(start: -7d) \
        |> filter(fn: (r) => r["_measurement"] == "{unit}") \
        |> filter(fn: (r) => r["_field"] == "value") \
        |> filter(fn: (r) => r["appuid"] == "{AppPrefs.appuid}") \
        |> filter(fn: (r) => r["probeid"] == "{probeid}") \
        |> aggregateWindow(every: 15m, fn: mean, createEmpty: false) \
        |> yield(name: "mean")'


        result = query_api.query(org=AppPrefs.influxdb_org, query=query)

        results = []
        for table in result:
            for record in table.records:
                results.append((record.get_time(), record.get_value()))
    
        return results

    except Exception as e:
        AppPrefs.logger.error("get_chartdata_1wk: " +  str(e))

#####################################################################
# get_chartdata_1mo
# return array of chart data with date/time and values
# must specify ProbeID, and scale (temperature_c,
# temperature_f, or humidity)
#####################################################################
@app.route('/get_chartdata_1mo/<probeid>/<unit>', methods = ['GET'])
@cross_origin()
def get_chartdata_1mo(probeid, unit):

    try:
        global AppPrefs
        if unit == "temperature":
            if AppPrefs.temperaturescale =="F":
                unit = "temperature_f"
            else:
                unit = "temperature_c"

        bucket = "reefberrypi_probe_1wk"

        query_api = Influx_client.query_api()

        query = f'from(bucket: "reefberrypi_probe_1mo") \
        |> range(start: -30d) \
        |> filter(fn: (r) => r["_measurement"] == "{unit}") \
        |> filter(fn: (r) => r["_field"] == "value") \
        |> filter(fn: (r) => r["appuid"] == "{AppPrefs.appuid}") \
        |> filter(fn: (r) => r["probeid"] == "{probeid}") \
        |> aggregateWindow(every: 1h, fn: mean, createEmpty: false) \
        |> yield(name: "mean")'


        result = query_api.query(org=AppPrefs.influxdb_org, query=query)

        results = []
        for table in result:
            for record in table.records:
                results.append((record.get_time(), record.get_value()))
    
        return results

    except Exception as e:
        AppPrefs.logger.error("get_chartdata_1mo: " +  str(e))
#####################################################################
# put_outlet_buttonstate
# change the value of button state
# must specify outlet ID and either ON, OFF, or AUTO
#####################################################################
@app.route('/put_outlet_buttonstate/<outletid>/<buttonstate>', methods = ['GET','PUT'])
@cross_origin()
def put_outlet_buttonstate(outletid, buttonstate):
    global logger

    try:
        global AppPrefs

        # build table object from table in DB
        metadata_obj = MetaData()

        outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)
        
        stmt = (
            update(outlet_table)
            .where(outlet_table.c.outletid == outletid)
            .where(outlet_table.c.appuid == AppPrefs.appuid)
            .values(button_state=buttonstate)
            )


        with sqlengine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

        #defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, logger)
        AppPrefs.outletDict[outletid].button_state = buttonstate
        AppPrefs.outletDict[outletid].outletstatus = buttonstate
       
        response = {}
        response = jsonify({"msg": 'Set outlet button state',
                            "appuid": AppPrefs.appuid,
                            "outletid": outletid,
                            "buttonstate": buttonstate
                            })

        response.status_code = 200      

        return response

    
    except Exception as e:
            AppPrefs.logger.error("put_outlet_buttonstate: " +  str(e))


#####################################################################
# set_probe_name
# set the name of the probe
# must specify ProbeID and Name
#####################################################################
@app.route('/set_probe_name/<probeid>/<probename>', methods = ['GET','PUT'])
@cross_origin()
def set_probe_name(probeid, probename):
    global logger

    try:
        global AppPrefs
        # build table object from table in DB
        metadata_obj = MetaData()
        probe_table = Table("probes", metadata_obj, autoload_with=sqlengine)
        
        stmt = (
            update(probe_table)
            .where(probe_table.c.probeid == probeid)
            .where(probe_table.c.appuid == AppPrefs.appuid)
            .values(name=probename)
            )


        with sqlengine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

        defs_mysql.readTempProbes_ex(sqlengine, AppPrefs, logger)
        defs_mysql.readDHTSensor_ex(sqlengine, AppPrefs, logger)
        defs_mysql.readMCP3008Prefs_ex(sqlengine, AppPrefs, logger)
       
        response = {}
        response = jsonify({"msg": 'Updated probe name',
                            "probeid": probeid,
                            "probename": probename,
                            })

        response.status_code = 200      
        return response
    
    except Exception as e:
        AppPrefs.logger.error("set_probe_name: " +  str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500 
        return response

#####################################################################
# set_outlet_params_light/<outletid>
# set the paramters for outlet of type: Light
# must specify outletid and deliver payload in json
#####################################################################

@app.route('/set_outlet_params_light/<outletid>' , methods=["PUT", "POST"])
@cross_origin()
def set_outlet_params_light(outletid):
    global logger

    try:
        global AppPrefs

        print(outletid)
        response = {}
        payload = request.get_json()
        print(payload)
        light_on = payload["light_on"]
        light_off = payload["light_off"]
        outletname = payload["outletname"]
        control_type = payload["control_type"]

        response = jsonify({"msg": 'Updated outlet data for type: Light',
                            "outletid": outletid,
                            "outletname": outletname,
                            "control_type": control_type,
                            "light_on": light_on,
                            "light_off": light_off,
                            })

        response.status_code = 200      

        # build table object from table in DB
        metadata_obj = MetaData()
        outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)
        
        stmt = (
            update(outlet_table)
            .where(outlet_table.c.outletid == outletid)
            .where(outlet_table.c.appuid == AppPrefs.appuid)
            .values(outletname=outletname, light_on=light_on, light_off=light_off, control_type=control_type )
            )

        with sqlengine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

        defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, logger)

        return response
    
    except Exception as e:
        AppPrefs.logger.error("set_outlet_params_light: " +  str(e))


#####################################################################
# set_outlet_params_always/<outletid>
# set the paramters for outlet of type: Always
# must specify outletid and deliver payload in json
#####################################################################     

@app.route('/set_outlet_params_always/<outletid>' , methods=["PUT", "POST"])
@cross_origin()
def set_outlet_params_always(outletid):
    global logger

    try:
        global AppPrefs

        print(outletid)
        response = {}
        payload = request.get_json()
        print(payload)
        always_state = payload["always_state"]
        outletname = payload["outletname"]
        control_type = payload["control_type"]

        response = jsonify({"msg": 'Updated outlet data for type: Always',
                            "outletid": outletid,
                            "outletname": outletname,
                            "control_type": control_type,
                            "always_state": always_state,
                            })

        response.status_code = 200      

        # build table object from table in DB
        metadata_obj = MetaData()
        outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)
        
        stmt = (
            update(outlet_table)
            .where(outlet_table.c.outletid == outletid)
            .where(outlet_table.c.appuid == AppPrefs.appuid)
            .values(outletname=outletname, always_state=always_state, control_type=control_type )
            )

        with sqlengine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

        defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, logger)

        return response
    
    except Exception as e:
        AppPrefs.logger.error("set_outlet_params_always: " +  str(e))

#####################################################################
# set_outlet_params_heater/<outletid>
# set the paramters for outlet of type: Heater
# must specify outletid and deliver payload in json
#####################################################################     

@app.route('/set_outlet_params_heater/<outletid>' , methods=["PUT", "POST"])
@cross_origin()
def set_outlet_params_heater(outletid):
    global logger

    try:
        global AppPrefs

        print(outletid)
        response = {}
        payload = request.get_json()
        print(payload)
        heater_on = payload["heater_on"]
        heater_off = payload["heater_off"]
        heater_probe = payload["heater_probe"]
        outletname = payload["outletname"]
        control_type = payload["control_type"]

        if AppPrefs.temperaturescale == "F":
            heater_on = defs_common.convertFtoC(heater_on)
            heater_off = defs_common.convertFtoC(heater_off)


        response = jsonify({"msg": 'Updated outlet data for type: Heater',
                            "outletid": outletid,
                            "outletname": outletname,
                            "control_type": control_type,
                            "heater_on": heater_on,
                            "heater_off": heater_off,
                            "heater_probe": heater_probe,
                            })

        response.status_code = 200      

        # build table object from table in DB
        metadata_obj = MetaData()
        outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)
        
       

        stmt = (
            update(outlet_table)
            .where(outlet_table.c.outletid == outletid)
            .where(outlet_table.c.appuid == AppPrefs.appuid)
            .values(outletname=outletname, heater_on=heater_on, heater_off=heater_off, heater_probe=heater_probe, control_type=control_type )
            )

        with sqlengine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

        defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, logger)

        return response
    
    except Exception as e:
        AppPrefs.logger.error("set_outlet_params_heater: " +  str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500 
        return response


#####################################################################
# set_outlet_params_return/<outletid>
# set the paramters for outlet of type: Return
# must specify outletid and deliver payload in json
#####################################################################     

@app.route('/set_outlet_params_return/<outletid>' , methods=["PUT", "POST"])
@cross_origin()
def set_outlet_params_return(outletid):
    global logger

    try:
        global AppPrefs

        print(outletid)
        response = {}
        payload = request.get_json()
        print(payload)
        return_enable_feed_a = payload["return_enable_feed_a"]
        return_enable_feed_b = payload["return_enable_feed_b"]
        return_enable_feed_c = payload["return_enable_feed_c"]
        return_enable_feed_d = payload["return_enable_feed_d"]
        return_feed_delay_a = payload["return_feed_delay_a"]
        return_feed_delay_b = payload["return_feed_delay_b"]
        return_feed_delay_c = payload["return_feed_delay_c"]
        return_feed_delay_d = payload["return_feed_delay_d"]
        outletname = payload["outletname"]
        control_type = payload["control_type"]

        response = jsonify({"msg": 'Updated outlet data for type: Return',
                            "outletid": outletid,
                            "outletname": outletname,
                            "control_type": control_type,
                            "return_enable_feed_a": return_enable_feed_a,
                            "return_enable_feed_b": return_enable_feed_b,
                            "return_enable_feed_c": return_enable_feed_c,
                            "return_enable_feed_d": return_enable_feed_d,
                            "return_feed_delay_a": return_feed_delay_a,
                            "return_feed_delay_b": return_feed_delay_b,
                            "return_feed_delay_c": return_feed_delay_c,
                            "return_feed_delay_d": return_feed_delay_d,
                            })

        response.status_code = 200      

        # build table object from table in DB
        metadata_obj = MetaData()
        outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)
        
        stmt = (
            update(outlet_table)
            .where(outlet_table.c.outletid == outletid)
            .where(outlet_table.c.appuid == AppPrefs.appuid)
            .values(outletname=outletname, 
                    control_type=control_type, 
                    return_enable_feed_a=return_enable_feed_a, 
                    return_enable_feed_b=return_enable_feed_b,
                    return_enable_feed_c=return_enable_feed_c,
                    return_enable_feed_d=return_enable_feed_d,
                    return_feed_delay_a=return_feed_delay_a,
                    return_feed_delay_b=return_feed_delay_b,
                    return_feed_delay_c=return_feed_delay_c,
                    return_feed_delay_d=return_feed_delay_d,
                        )
            )

        with sqlengine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

        defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, logger)

        return response
    
    except Exception as e:
        AppPrefs.logger.error("set_outlet_params_return: " +  str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500 
        return response

#####################################################################
# set_outlet_params_skimmer/<outletid>
# set the paramters for outlet of type: Skimmer
# must specify outletid and deliver payload in json
#####################################################################     

@app.route('/set_outlet_params_skimmer/<outletid>' , methods=["PUT", "POST"])
@cross_origin()
def set_outlet_params_skimmer(outletid):
    global logger

    try:
        global AppPrefs

        print(outletid)
        response = {}
        payload = request.get_json()
        print(payload)
        skimmer_enable_feed_a = payload["skimmer_enable_feed_a"]
        skimmer_enable_feed_b = payload["skimmer_enable_feed_b"]
        skimmer_enable_feed_c = payload["skimmer_enable_feed_c"]
        skimmer_enable_feed_d = payload["skimmer_enable_feed_d"]
        skimmer_feed_delay_a = payload["skimmer_feed_delay_a"]
        skimmer_feed_delay_b = payload["skimmer_feed_delay_b"]
        skimmer_feed_delay_c = payload["skimmer_feed_delay_c"]
        skimmer_feed_delay_d = payload["skimmer_feed_delay_d"]
        outletname = payload["outletname"]
        control_type = payload["control_type"]

        response = jsonify({"msg": 'Updated outlet data for type: Skimmer',
                            "outletid": outletid,
                            "outletname": outletname,
                            "control_type": control_type,
                            "skimmer_enable_feed_a": skimmer_enable_feed_a,
                            "skimmer_enable_feed_b": skimmer_enable_feed_b,
                            "skimmer_enable_feed_c": skimmer_enable_feed_c,
                            "skimmer_enable_feed_d": skimmer_enable_feed_d,
                            "skimmer_feed_delay_a": skimmer_feed_delay_a,
                            "skimmer_feed_delay_b": skimmer_feed_delay_b,
                            "skimmer_feed_delay_c": skimmer_feed_delay_c,
                            "skimmer_feed_delay_d": skimmer_feed_delay_d,
                            })

        response.status_code = 200      

        # build table object from table in DB
        metadata_obj = MetaData()
        outlet_table = Table("outlets", metadata_obj, autoload_with=sqlengine)
        
        stmt = (
            update(outlet_table)
            .where(outlet_table.c.outletid == outletid)
            .where(outlet_table.c.appuid == AppPrefs.appuid)
            .values(outletname=outletname, 
                    control_type=control_type, 
                    skimmer_enable_feed_a=skimmer_enable_feed_a, 
                    skimmer_enable_feed_b=skimmer_enable_feed_b,
                    skimmer_enable_feed_c=skimmer_enable_feed_c,
                    skimmer_enable_feed_d=skimmer_enable_feed_d,
                    skimmer_feed_delay_a=skimmer_feed_delay_a,
                    skimmer_feed_delay_b=skimmer_feed_delay_b,
                    skimmer_feed_delay_c=skimmer_feed_delay_c,
                    skimmer_feed_delay_d=skimmer_feed_delay_d,
                        )
            )

        with sqlengine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

        defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, logger)

        return response
    
    except Exception as e:
        AppPrefs.logger.error("set_outlet_params_skimmer: " +  str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500 
        return response

#####################################################################
# get_global_prefs/
# get the global paramters for the controlled
# things like temperature scale, etc...
#####################################################################     

@app.route('/get_global_prefs/' , methods=["GET"])
@cross_origin()
def get_global_prefs():
    global logger

    try:
        global AppPrefs

        response = {}
       

        response = jsonify({"msg": 'Global preferences delivered',
                            "appuid": AppPrefs.appuid,
                            "tempscale": AppPrefs.temperaturescale,
                            "dht_enable": AppPrefs.dht_enable,
                            "feed_CurrentMode": AppPrefs.feed_CurrentMode,
                            "feed_a_time": AppPrefs.feed_a_time,
                            "feed_b_time": AppPrefs.feed_b_time,
                            "feed_c_time": AppPrefs.feed_c_time,
                            "feed_d_time": AppPrefs.feed_d_time,
                            })

        response.status_code = 200      



        return response
    
    except Exception as e:
        AppPrefs.logger.error("get_global_prefs: " +  str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500 
        return response

#####################################################################
# set_global_prefs/
# set the global parameters such as temps scale C or F
# must specify outletid and deliver payload in json
#####################################################################     

@app.route('/set_global_prefs/' , methods=["PUT", "POST"])
@cross_origin()
def set_global_prefs():
    global logger

    try:
        global AppPrefs

        response = {}
        payload = request.get_json()
        print(payload)
        tempscale = payload["tempscale"]
        dht_enable = payload["dht_enable"]
        feed_a_time = payload["feed_a_time"]
        feed_b_time = payload["feed_b_time"]
        feed_c_time = payload["feed_c_time"]
        feed_d_time = payload["feed_d_time"]

        response = jsonify({"msg": 'Updated Global Prefs',
                            "tempscale": tempscale,
                            "dht_enable": dht_enable,
                            "feed_a_time": feed_a_time,
                            "feed_b_time": feed_b_time,
                            "feed_c_time": feed_c_time,
                            "feed_d_time": feed_d_time,
                            })

        response.status_code = 200      

        # build table object from table in DB
        metadata_obj = MetaData()
        global_table = Table("global", metadata_obj, autoload_with=sqlengine)
        
        stmt = (
            update(global_table)
            .where(global_table.c.appuid == AppPrefs.appuid)
            .values(tempscale=tempscale, 
                    dht_enable=dht_enable, 
                    feed_a_time=feed_a_time,
                    feed_b_time=feed_b_time,
                    feed_c_time=feed_c_time,
                    feed_d_time=feed_d_time,
                        )
            )

        with sqlengine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

        defs_mysql.readGlobalPrefs_ex(sqlengine, AppPrefs, logger)

        return response
    
    except Exception as e:
        AppPrefs.logger.error("set_global_prefs: " +  str(e))
        response = jsonify({"msg": str(e)})
        response.status_code = 500 
        return response

#####################################################################
# get_current_probs_stats/
# get the stats for the specified probe
# things like last value, probe name, etc....
#####################################################################     

@app.route('/get_current_probe_stats/<probeid>' , methods=["GET"])
@cross_origin()

def get_current_probe_stats(probeid):
    global logger

    try:
        global AppPrefs

        response = {}

        if probeid.startswith("ds"):
            response = jsonify({"msg": 'Current probe stats',
                                "appuid": AppPrefs.appuid,
                                "probename": AppPrefs.tempProbeDict[probeid].name,
                                "probeid": AppPrefs.tempProbeDict[probeid].probeid,
                                "lastValue": AppPrefs.tempProbeDict[probeid].lastTemperature,
                                "sensortype": "temperature",
                                "probetype": "ds18b20",
                                })

            response.status_code = 200   

        elif probeid.startswith("DHT"):
            response = jsonify({"msg": 'Current probe stats',
                                "appuid": AppPrefs.appuid,
                                "sensortype": AppPrefs.dhtDict[probeid].sensortype , 
                                "probename": AppPrefs.dhtDict[probeid].name,
                                "probeid": AppPrefs.dhtDict[probeid].probeid, 
                                "probetype": "DHT", 
                                "lastValue": AppPrefs.dhtDict[probeid].lastValue})

            response.status_code = 200 

        elif probeid.startswith("mcp3008"):
            response = jsonify({"msg": 'Current probe stats',
                                "appuid": AppPrefs.appuid,
                                "sensortype": AppPrefs.mcp3008Dict[probeid[-1]].ch_type , 
                                "probename": AppPrefs.mcp3008Dict[probeid[-1]].ch_name,
                                "probeid": probeid, 
                                "probetype": "analog", 
                                "lastValue": AppPrefs.mcp3008Dict[probeid[-1]].lastValue})
            

            response.status_code = 200 

        return response
    
    except Exception as e:
        AppPrefs.logger.error("get_current_probe_stats: " +  str(e))
        # response = jsonify({"msg": str(e)})
        response = jsonify(AppPrefs.tempProbeDict[probeid])
        response.status_code = 500 
        return response
    
#####################################################################
# get_current_outlet_stats/
# get the stats for the specified outlet
# things like last button state, status, etc....
#####################################################################     

@app.route('/get_current_outlet_stats/<outletid>' , methods=["GET"])
@cross_origin()

def get_current_outlet_stats(outletid):
    global logger

    try:
        global AppPrefs

        response = {}

        # convert temperature values to F if using Fahrenheit
        if AppPrefs.temperaturescale == "F":
            heater_on_x = defs_common.convertCtoF(AppPrefs.outletDict[outletid].heater_on)
            heater_off_x = defs_common.convertCtoF(AppPrefs.outletDict[outletid].heater_off)
        else:
            heater_on_x = AppPrefs.outletDict[outletid].heater_on
            heater_off_x = AppPrefs.outletDict[outletid].heater_off

        response = jsonify({"msg": 'Current outlet stats',
                            "appuid": AppPrefs.appuid,                   
                            "outletid": AppPrefs.outletDict[outletid].outletid , 
                            "outletname": AppPrefs.outletDict[outletid].outletname, 
                            "control_type": AppPrefs.outletDict[outletid].control_type, 
                            "outletstatus": AppPrefs.outletDict[outletid].outletstatus,
                            "button_state": AppPrefs.outletDict[outletid].button_state,
                            "heater_on": heater_on_x,
                            "heater_off": heater_off_x,
                            "heater_probe": AppPrefs.outletDict[outletid].heater_probe,
                            "light_on": AppPrefs.outletDict[outletid].light_on,
                            "light_off": AppPrefs.outletDict[outletid].light_off,
                            "always_state": AppPrefs.outletDict[outletid].always_state,
                            "return_enable_feed_a": (AppPrefs.outletDict[outletid].return_enable_feed_a).lower() == "true",
                            "return_enable_feed_b": (AppPrefs.outletDict[outletid].return_enable_feed_b).lower() == "true",
                            "return_enable_feed_c": (AppPrefs.outletDict[outletid].return_enable_feed_c).lower() == "true",
                            "return_enable_feed_d": (AppPrefs.outletDict[outletid].return_enable_feed_d).lower() == "true",
                            "return_feed_delay_a": AppPrefs.outletDict[outletid].return_feed_delay_a,
                            "return_feed_delay_b": AppPrefs.outletDict[outletid].return_feed_delay_b,
                            "return_feed_delay_c": AppPrefs.outletDict[outletid].return_feed_delay_c,
                            "return_feed_delay_d": AppPrefs.outletDict[outletid].return_feed_delay_d,

                            "skimmer_enable_feed_a": (AppPrefs.outletDict[outletid].skimmer_enable_feed_a).lower() == "true",
                            "skimmer_enable_feed_b": (AppPrefs.outletDict[outletid].skimmer_enable_feed_b).lower() == "true",
                            "skimmer_enable_feed_c": (AppPrefs.outletDict[outletid].skimmer_enable_feed_c).lower() == "true",
                            "skimmer_enable_feed_d": (AppPrefs.outletDict[outletid].skimmer_enable_feed_d).lower() == "true",
                            "skimmer_feed_delay_a": AppPrefs.outletDict[outletid].skimmer_feed_delay_a,
                            "skimmer_feed_delay_b": AppPrefs.outletDict[outletid].skimmer_feed_delay_b,
                            "skimmer_feed_delay_c": AppPrefs.outletDict[outletid].skimmer_feed_delay_c,
                            "skimmer_feed_delay_d": AppPrefs.outletDict[outletid].skimmer_feed_delay_d,
                            })

        response.status_code = 200      

        return response
    
    except Exception as e:
        AppPrefs.logger.error("get_current_outlet_stats: " +  str(e))
        # response = jsonify({"msg": str(e)})
        response = jsonify(AppPrefs.outletDict[outletid])
        response.status_code = 500 
        return response

#####################################################################
# get_probe_list
# return list of connected probes 
#####################################################################
@app.route('/get_probe_list/', methods = ['GET'])
@cross_origin()
def get_probe_list():
    
    try:
        global AppPrefs
        
        probedict = {}
        
        # loop through each section
        for probe in AppPrefs.tempProbeDict:
            probedict[probe]={"probetype": "ds18b20" , 
                              "probeid": AppPrefs.tempProbeDict[probe].probeid, 
                              "probename": AppPrefs.tempProbeDict[probe].name,
                              "sensortype": "temperature", 
                              "lastValue": AppPrefs.tempProbeDict[probe].lastTemperature}
        print(probedict)
        if AppPrefs.dht_enable == "true":
            probedict["DHT-T"]={"sensortype": AppPrefs.dhtDict["DHT-T"].sensortype , 
                                "probename": AppPrefs.dhtDict["DHT-T"].name,
                                "probeid": AppPrefs.dhtDict["DHT-T"].probeid, 
                                "probetype": "DHT", 
                                "lastValue": AppPrefs.dhtDict["DHT-T"].lastValue}
            probedict["DHT-H"]={"sensortype": AppPrefs.dhtDict["DHT-H"].sensortype , 
                                "probename": AppPrefs.dhtDict["DHT-H"].name,
                                "probeid": AppPrefs.dhtDict["DHT-H"].probeid, 
                                "probetype": "DHT", 
                                "lastValue": AppPrefs.dhtDict["DHT-H"].lastValue}
        for ch in AppPrefs.mcp3008Dict:
            #logger.info(ch)
            probedict["mcp3008_ch" + str(ch)] = {"sensortype": AppPrefs.mcp3008Dict[ch].ch_type , 
                                                "probename": AppPrefs.mcp3008Dict[ch].ch_name,
                                                    "probeid": "mcp3008_ch" + str(ch), 
                                                    "probetype": "analog", 
                                                    "lastValue": AppPrefs.mcp3008Dict[ch].lastValue}


        return probedict    
    
    except Exception as e:
        AppPrefs.logger.error("get_probe_list: " +  str(e))

#####################################################################
# get_token
# return login token
#####################################################################
@app.route('/get_token', methods = ['POST'])
@cross_origin()
def get_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username.lower() != "pi" or password != "reefberry":
        return {"msg": "Wrong username or password"}, 401

    access_token = create_access_token(identity=username)
    response = {"token":access_token}

    return response

#####################################################################
# get_outletchartdata
# return array of chart data with date/time and values
# must specify outletID, and time frame (24hr, 1wk, 1mo, etc...)
#####################################################################
@app.route('/get_outletchartdata/<outletid>/<timeframe>', methods = ['GET'])
@cross_origin()
def get_outletchartdata(outletid, timeframe):

    try:
        global AppPrefs

        
        bucket = "reefberrypi_outlet_3mo"

        query_api = Influx_client.query_api()

        query = f'from(bucket: "reefberrypi_outlet_3mo") \
        |> range(start: -{timeframe}) \
        |> filter(fn: (r) => r["_measurement"] == "outlet_state") \
        |> filter(fn: (r) => r["_field"] == "value") \
        |> filter(fn: (r) => r["appuid"] == "{AppPrefs.appuid}") \
        |> filter(fn: (r) => r["outletid"] == "{outletid}") \
        |> yield(name: "last")'


        result = query_api.query(org=AppPrefs.influxdb_org, query=query)

        results = []
        for table in result:
            for record in table.records:
                results.append((record.get_time(), record.get_value()))
    
        return results

    except Exception as e:
        AppPrefs.logger.error("get_outletchartdata: " +  str(e))
        return (str(e))

############################################################

if __name__ == '__main__':
    app.run()