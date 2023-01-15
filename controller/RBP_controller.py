from datetime import datetime, time, timedelta
from flask import Flask, jsonify
from multiprocessing import Process
import defs_common
import logging
import logging.handlers
import os.path
import ds18b20
import RPi.GPIO as GPIO
import GPIO_config
import time
from influxdb_client import InfluxDBClient, BucketRetentionRules
from influxdb_client.client.write_api import SYNCHRONOUS
import dht11
import defs_Influx
import cls_Preferences
import defs_mysql
import threading


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
mySQLDB = defs_mysql.initMySQL(AppPrefs, logger)

# read preferences from DB
# temperature probes
defs_mysql.readTempProbes(mySQLDB, AppPrefs, logger)
defs_mysql.readGlobalPrefs(mySQLDB, AppPrefs, logger)
defs_mysql.readOutletPrefs(mySQLDB, AppPrefs, logger)

app = Flask(__name__)


# set up the GPIO
GPIO_config.initGPIO()

# dht11 temperature and humidity sensor
dht_sensor = dht11.DHT11(pin=GPIO_config.dht11)


#####################################
# placeholder stuff to test Flask...
#####################################
outlets = [
    {
        'id': 1,
        'label': 'Return Pump'
    }
]


@app.route('/get_outlets', methods=['GET'])
def get_outlets():
    return jsonify({'outlets': outlets})


@app.route('/get_temp', methods=['GET'])
def get_temp():
    temperature = float(ds18b20.read_temp("111", "C"))
    logger.info(str(temperature))
    return jsonify({'temperature': temperature})


@app.route('/set_outlet_on', methods=['GET'])
def set_outlet_on():
    GPIO.output(19, True)
    logger.info("Outlet ON")
    return jsonify({'outlet state': "ON"})


@app.route('/set_outlet_off', methods=['GET'])
def set_outlet_off():
    GPIO.output(19, False)
    logger.info("Outlet OFF")
    return jsonify({'outlet state': "OFF"})

#####################################


def apploop():

    while True:
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
        except:
            logger.error("Unable to read ds18b20 temperature")
        ###################################################################
        # dht11 temp and humidity data
        ###################################################################
        result = dht_sensor.read()
        if result.is_valid():
            temp_c = result.temperature
            hum = result.humidity

            # print("dht11 Temp C = " + str(temp_c) + " C")
            Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "temperature_c", "tags": {
                                   "appuid": AppPrefs.appuid, "probeid": "dht11-temp"}, "fields": {"value": float(temp_c)}, "time": datetime.utcnow()}])

            temp_f = float(defs_common.convertCtoF(temp_c))
            # print("dht11 Temp F =  " + str(temp_f) + " F")
            Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "temperature_f", "tags": {
                                   "appuid": AppPrefs.appuid, "probeid": "dht11-temp"}, "fields": {"value": temp_f}, "time": datetime.utcnow()}])

            # print("dht11 Temp = " + str(temp_c) + "C / " + str(temp_f) + "F")
            # print("dht11 Humidity = " + str(hum) + "%")
            logger.debug("dht11 Temp = " + str(temp_c) +
                         "C / " + str(temp_f) + "F")
            logger.debug("dht11 Humidity = " + str(hum) + "%")
            Influx_write_api.write(defs_Influx.INFLUXDB_PROBE_BUCKET_1HR, AppPrefs.influxdb_org, [{"measurement": "humidity", "tags": {
                                   "appuid": AppPrefs.appuid, "probeid": "dht11-hum"}, "fields": {"value": hum}, "time": datetime.utcnow()}])

        ##########################################################################################
        # pause to slow down the loop
        ##########################################################################################
        time.sleep(2)


if __name__ == "__main__":

    p = Process(target=apploop)
    p.start()
    logger.info("Starting Flask Server...")
    # running FLASK dev server across network.  this is NOT secure!
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    p.join()
