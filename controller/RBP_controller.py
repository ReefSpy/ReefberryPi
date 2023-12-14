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

# set up the GPIO
GPIO_config.initGPIO()

# dht11 temperature and humidity sensor
dht_sensor = dht11.DHT11(pin=GPIO_config.dht11)