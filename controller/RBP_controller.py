import logging
import logging.handlers
import defs_common
import defs_Influx
import cls_Preferences
import threading
import defs_mysql
from influxdb_client.client.write_api import SYNCHRONOUS
import RPi.GPIO as GPIO
import GPIO_config
import dht11
from datetime import datetime
import ds18b20
import time
import defs_outletcontrol
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import select
from sqlalchemy import update

app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

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


# set up the GPIO
GPIO_config.initGPIO()

# dht11 temperature and humidity sensor
dht_sensor = dht11.DHT11(pin=GPIO_config.dht11)


def apploop():

    global AppPrefs
    
    while True:
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
                
                AppPrefs.tempProbeDict.get(tProbe).lastTemperature = str(dstempC)
        except Exception as e:
            logger.error("Unable to read ds18b20 temperature! " + str(e))
        ###################################################################
        # dht11 temp and humidity data
        ###################################################################
        if AppPrefs.dht_enable == "True":
            result = dht_sensor.read()
            if result.is_valid():
                temp_c = result.temperature
                hum = result.humidity

                AppPrefs.dhtDict.get("DHT-T").lastValue = str(temp_c)
                AppPrefs.dhtDict.get("DHT-H").lastValue = str(hum)
                try:
                    # print("dht11 Temp C = " + str(temp_c) + " C")
                    Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "temperature_c", "tags": {
                                        "appuid": AppPrefs.appuid, "probeid": "DHT-T"}, "fields": {"value": float(temp_c)}, "time": datetime.utcnow()}])

                    temp_f = float(defs_common.convertCtoF(temp_c))
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
    AppPrefs.feed_CurrentMode = value
    AppPrefs.feed_SamplingTimeSeed = int(round(time.time()*1000)) #convert time to milliseconds
    return f"AppPrefs.feed_CurrentMode set to {value}"

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
            outletdict[outlet]={"outletid": AppPrefs.outletDict[outlet].outletid , 
                                "outletname": AppPrefs.outletDict[outlet].outletname, 
                                "control_type": AppPrefs.outletDict[outlet].control_type, 
                                "outletstatus": AppPrefs.outletDict[outlet].outletstatus,
                                "button_state": AppPrefs.outletDict[outlet].button_state,
                                "heater_on": AppPrefs.outletDict[outlet].heater_on,
                                "heater_off": AppPrefs.outletDict[outlet].heater_off,
                                "light_on": AppPrefs.outletDict[outlet].light_on,
                                "light_off": AppPrefs.outletDict[outlet].light_off,
                                "always_state": AppPrefs.outletDict[outlet].always_state,

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
        if AppPrefs.dht_enable == "True":
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
            return "DHT Disabled"    
    
    except Exception as e:
        AppPrefs.logger.error("get_dht_sensor: " +  str(e))

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

        for result in results:
            format_string = '%Y-%m-%d %H:%M:%S'
            date_string = result[0].strftime(format_string)
            #print(date_string)
    
        return results

    except Exception as e:
        AppPrefs.logger.error("get_chartdata_24hr: " +  str(e))

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

        defs_mysql.readOutletPrefs_ex(sqlengine, AppPrefs, logger)
       
        return "OK"
    
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
       
        return "OK"
    
    except Exception as e:
            AppPrefs.logger.error("set_probe_name: " +  str(e))

###############################################

if __name__ == '__main__':
    app.run()