import os.path
import configparser
from datetime import datetime

CONFIGFILENAME = "config.ini"
SCALE_C = 0
SCALE_F = 1

def checkifconfigexists():
    if os.path.isfile(CONFIGFILENAME):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " +
                      CONFIGFILENAME + " exists, reading file")
    else:
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " +
                      CONFIGFILENAME + " does not exists, creating file")
        f = open(CONFIGFILENAME,"w+")
        f.close()
        
        
def readINIfile(section, key, default):
    # try to read the value from the config file
    # if the value does not exist, lets write the default value into the
    # file and return the default, otherwise return what is saved
    # in the file
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
        #print ("value is empty")
        #value = default
        config[section][key] = str(default)
        with open(CONFIGFILENAME,'w') as configfile:
            config.write(configfile)
                   
    #value = config[section][key]   
    print (datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " readINIfile: " + "\n" +
           "                        [section] = " + section + "\n" +
           "                        [key] = " + key + "\n" +
           "                        [value] = " + config[section][key])
    return config[section][key] 

    
def writeINIfile(section, key, value):
    try:
        config = configparser.ConfigParser()
        config.read(CONFIGFILENAME)
        
        #config[str(section)] = {str(key):str(value)}
        config[str(section)].update({str(key):str(value)})
        with open(CONFIGFILENAME,'w') as configfile:
            config.write(configfile)
        return True
    except:
        return False
    

def removesectionfromINIfile(section):
    p = configparser.SafeConfigParser()
    with open(CONFIGFILENAME, "r") as f:
        p.readfp(f)

    print(p.sections())
    p.remove_section(section)
    print(p.sections())

    with open(CONFIGFILENAME, "w") as f:
        p.write(f)

