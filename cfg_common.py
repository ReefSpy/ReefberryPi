import os.path
import configparser

CONFIGFILENAME = "config.ini"
SCALE_C = 0
SCALE_F = 1

def checkifconfigexists():
    if os.path.isfile(CONFIGFILENAME):
        print (CONFIGFILENAME + " exists")
    else:
        print (CONFIGFILENAME + " does not exist")
        f = open(CONFIGFILENAME,"w+")
        f.close()
        print (CONFIGFILENAME + " does not exist")
        print (CONFIGFILENAME + " created")
        
        
def readINIfile(section, key, value, default):
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
        value = default
        config[section][key] = str(default)
        with open(CONFIGFILENAME,'w') as configfile:
            config.write(configfile)
                   
    value = config[section][key]   
    print ("readINIfile: " + "\n" +
           "    [section] = " + section + "\n" +
           "    [key] = " + key + "\n" +
           "    [value] = " + value)
    return config[section][key] 
    
    

def writeINIfile(section, key, value):
    try:
        config = configparser.ConfigParser()
        config.read(CONFIGFILENAME)
        config[str(section)][str(key)] = str(value)
        with open(CONFIGFILENAME,'w') as configfile:
            config.write(configfile)
        return True
    except:
        return False
    
