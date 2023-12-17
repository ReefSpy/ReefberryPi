##############################################################################
# defs_common.py
#
# common functions used throughout application
#
# Written by ReefSpy for the ReefBerry Pi, (c) 2023
# www.youtube.com/reefspy
##############################################################################

from datetime import datetime
import logging
import logging.handlers
import os.path
import configparser

CONFIGFILENAME = "config.ini"
SCALE_C = "C"
SCALE_F = "F"

def initialize_logger(logger, output_dir, output_file, loglevel_console, loglevel_logfile):

       
        logger.setLevel(logging.DEBUG)

        # check if log dir exists, if not create it
        if not os.path.exists(output_dir):
            print("Logfile directory not found")
            os.mkdir(output_dir)
            print(
                "Logfile directory created: " + os.getcwd() + "/" + str(output_dir))

        # create console handler and set level to info
        handler = logging.StreamHandler()
        handler.setLevel(loglevel_console)
        formatter = logging.Formatter('%(asctime)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # create log file handler and set level to info
        handler = logging.handlers.RotatingFileHandler(
            os.path.join(output_dir, output_file), maxBytes=2000000, backupCount=5)
        handler.setLevel(loglevel_logfile)
        formatter = logging.Formatter(
            '%(asctime)s <%(levelname)s> [%(threadName)s:%(module)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # create debug file handler and set level to debug
        # handler = logging.FileHandler(os.path.join(output_dir, "all.log"),handler.setLevel(logging.DEBUG)
        # formatter = logging.Formatter('%(asctime)s <%(levelname)s> [%(threadName)s:%(module)s] %(message)s')
        # handler.setFormatter(formatter)
        # logger.addHandler(handler)

def convertCtoF(temp_c):
    temp_f = float(temp_c) * 9.0 / 5.0 + 32.0
    return "{:.1f}".format(temp_f)

def readINIfile(section, key, default, *args, **kwargs):
    # try to read the value from the config file
    # if the value does not exist, lets write the default value into the
    # file and return the default, otherwise return what is saved
    # in the file
    useDefault = False
    useThreadLock = False

    # to prevent multiple threads from woking on the file at the same time, we will check
    # the thread lock
    for keyarg, value in kwargs.items():
        if keyarg == "lock":
            lck = value
            lck.acquire()
            useThreadLock = True
            #logtoconsole("Read Lock Aquired", fg = "WHITE", bg="MAGENTA", style="BRIGHT")

    config = configparser.ConfigParser()
    config.read(CONFIGFILENAME)

    if not section in config:
        config[section] = {}
        with open(CONFIGFILENAME, 'w') as configfile:
            config.write(configfile)
    if not key in config[section]:
        config[section][key] = str(default)
        with open(CONFIGFILENAME, 'w') as configfile:
            config.write(configfile)
    if config[section][key] == "":
        config[section][key] = str(default)
        with open(CONFIGFILENAME, 'w') as configfile:
            config.write(configfile)
            useDefault = True
    for keyarg, value in kwargs.items():
        if keyarg == "logger":
            logger = value
            logger.debug(
                "readINIfile: " + "section=[" + section + "], key=[" + key + "], value=[" + config[section][key] + "]")
            if useDefault == True:
                logger.debug("readINIfile **used default value**: " + default)

    if useThreadLock == True:
        lck.release()
        #logtoconsole("Read Lock Released", fg = "WHITE", bg="MAGENTA", style="BRIGHT")

    return config[section][key]


def writeINIfile(section, key, value, *args, **kwargs):

    useThreadLock = False

    # to prevent multiple threads from woking on the file at the same time, we will check
    # the thread lock
    for keyarg, val in kwargs.items():
        if keyarg == "lock":
            lck = val
            lck.acquire()
            useThreadLock = True
            #logtoconsole("Write Lock Aquired", fg = "WHITE", bg="BLUE", style="BRIGHT")

    try:
        config = configparser.ConfigParser()
        config.read(CONFIGFILENAME)

        try:
            config[str(section)].update({str(key): str(value)})
        except:
            # need this line if the key
            config[str(section)] = {str(key): str(value)}
            # is not found so it will create it
        with open(CONFIGFILENAME, 'w') as configfile:
            config.write(configfile)

        for keyarg, val in kwargs.items():
            if keyarg == "logger":
                logger = val
                logger.debug("writeINIfile: " + "section=[" + str(section) + "], key=[" + str(
                    key) + "], value=[" + str(config[section][key]) + "]")

        if useThreadLock == True:
            lck.release()
            #logtoconsole("Write Lock Released", fg = "WHITE", bg="BLUE", style="BRIGHT")

        return True

    except:

        if useThreadLock == True:
            lck.release()
            #logtoconsole("Write Lock Released", fg = "WHITE", bg="BLUE", style="BRIGHT")
        return False
