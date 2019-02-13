##############################################################################
# defs_common.py
#
# common functions used throughout application
#
# Written by ReefSpy for the ReefBerry Pi, (c) 2019
# www.youtube.com/reefspy
##############################################################################


from datetime import datetime
from colorama import Fore, Back, Style, init
import os.path
import configparser
from datetime import datetime
import logging


CONFIGFILENAME = "config.ini"

SCALE_C = 0
SCALE_F = 1

OUTLET_OFF = 1
OUTLET_AUTO = 2
OUTLET_ON = 3


def logtoconsole(text, *args, **kwargs):
    
    init(autoreset=True) # auto resets colors back to default after use

    # STYLE
    STYLE_RESET  = "\033[0m"      # reset all (colors and brightness)
    STYLE_BRIGHT = "\033[1m"      # bright
    STYLE_DIM    = "\033[2m"      # dim (looks same as normal brightness)
    STYLE_NORMAL = "\033[22m"     # normal brightness
      
    # FOREGROUND:
    FG_BLACK    = "\033[30m"      # black
    FG_RED      = "\033[31m"      # red
    FG_GREEN    = "\033[32m"      # green
    FG_YELLOW   = "\033[33m"      # yellow
    FG_BLUE     = "\033[34m"      # blue
    FG_MAGENTA  = "\033[35m"      # magenta
    FG_CYAN     = "\033[36m"      # cyan
    FG_WHITE    = "\033[37m"      # white
    FG_RESET    = "\033[39m"      # reset

    # BACKGROUND
    BG_BLACK    = "\033[40m"      # black
    BG_RED      = "\033[41m"      # red
    BG_GREEN    = "\033[42m"      # green
    BG_YELLOW   = "\033[43m"      # yellow
    BG_BLUE     = "\033[44m"      # blue
    BG_MAGENTA  = "\033[45m"      # magenta
    BG_CYAN     = "\033[46m"      # cyan
    BG_WHITE    = "\033[47m"      # white
    BG_RESET    = "\033[49m"      # reset

    style = ""
    fore = ""
    back = ""
    
    for key, value in kwargs.items():
        #print("{0} = {1}".format(key, value))
        if key=="Fore" or key=="fore" or key=="fg" or key=="foreground" or key=="Foreground":
            if value == "BLACK":
                fore = FG_BLACK
            elif value == "RED":
                fore = FG_RED
            elif value == "GREEN":
                fore = FG_GREEN
            elif value == "YELLOW":
                fore = FG_YELLOW
            elif value == "BLUE":
                fore = FG_BLUE
            elif value == "MAGENTA":
                fore = FG_MAGENTA
            elif value == "CYAN":
                fore = FG_CYAN
            elif value == "WHITE":
                fore = FG_WHITE
            elif value == "RESET":
                fore = FG_RESET
            else:
                fore = ""

        if key=="Back" or key=="back" or key=="bg" or key=="background" or key=="Background":
            if value == "BLACK":
                back = BG_BLACK
            elif value == "RED":
                back = BG_RED
            elif value == "GREEN":
                back = BG_GREEN
            elif value == "YELLOW":
                back = BG_YELLOW
            elif value == "BLUE":
                back = BG_BLUE
            elif value == "MAGENTA":
                back = BG_MAGENTA
            elif value == "CYAN":
                back = BG_CYAN
            elif value == "WHITE":
                back = BG_WHITE
            elif value == "RESET":
                back = BG_RESET
            else:
                back = ""
             
        if key=="Style" or key=="style":
            if value ==  "BRIGHT":
                style = STYLE_BRIGHT
            elif value == "DIM":
                style = STYLE_DIM
            elif value == "NORMAL":
                style = STYLE_NORMAL
            elif value == "RESET":
                style = STYLE_RESET
            else:
                style = ""
                      
    t = datetime.now()
    s = t.strftime('%Y-%m-%d %H:%M:%S,%f')
    s = s[:-3]
    
    print(fore + back + style + s + " " + text)
    #print(fore + back + style + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) + " " + text)
    

def logprobedata(log_prefix, data):
    # create time stamp
    formatted_date=datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f")
    formatted_date=str(formatted_date.strftime("%Y-%m-%d %H:%M:%S"))
    # write data to file
    log_file_name = log_prefix + datetime.now().strftime("%Y-%m-%d") + ".txt"
    log_dir = readINIfile("logs", "log_dir", "logs")
    #fh = open(str(config['logs']['log_dir']) + "/" + log_file_name, "a")
    fh = open(str(log_dir) + "/" + log_file_name, "a")
    fh.write(str(formatted_date) + "," + str(data) + "\n")
    fh.close()
        
    
def convertCtoF(temp_c):
    temp_f = float(temp_c) * 9.0 / 5.0 + 32.0
    return "{:.1f}".format(temp_f)


def convertFtoC(degreesF):
    val = (float(degreesF)-32) * (5/9)
    return val

def checkifconfigexists():
    if os.path.isfile(CONFIGFILENAME):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " +
                      CONFIGFILENAME + " exists, reading file")
    else:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " +
                      CONFIGFILENAME + " does not exists, creating file")
        f = open(CONFIGFILENAME,"w+")
        f.close()
        
        
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
        with open(CONFIGFILENAME,'w') as configfile:
            config.write(configfile)
    if not key in config[section]:
        config[section][key] = str(default)
        with open(CONFIGFILENAME,'w') as configfile:
            config.write(configfile)   
    if config[section][key] == "":
        config[section][key] = str(default)
        with open(CONFIGFILENAME,'w') as configfile:
            config.write(configfile)
            useDefault = True
    for keyarg, value in kwargs.items():
        if keyarg == "logger":
            logger = value
            logger.debug("readINIfile: " + "section=[" + section + "], key=[" + key + "], value=[" + config[section][key] + "]")
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
            config[str(section)].update({str(key):str(value)})
        except:
            config[str(section)] = {str(key):str(value)} # need this line if the key
                                                         # is not found so it will create it
        with open(CONFIGFILENAME,'w') as configfile:
            config.write(configfile)

        for keyarg, val in kwargs.items():
            if keyarg == "logger":
                logger = val
                logger.debug("writeINIfile: " + "section=[" + str(section) + "], key=[" + str(key) + "], value=[" + str(config[section][key]) + "]")

        if useThreadLock == True:
            lck.release()
            #logtoconsole("Write Lock Released", fg = "WHITE", bg="BLUE", style="BRIGHT")
            
        return True

    except:

        if useThreadLock == True:
            lck.release()
            #logtoconsole("Write Lock Released", fg = "WHITE", bg="BLUE", style="BRIGHT")
        return False
    

def removesectionfromINIfile(section):
    p = configparser.SafeConfigParser()
    with open(CONFIGFILENAME, "r") as f:
        p.readfp(f)

    p.remove_section(section)

    with open(CONFIGFILENAME, "w") as f:
        p.write(f)




