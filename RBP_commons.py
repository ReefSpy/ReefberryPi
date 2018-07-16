import configparser
from datetime import datetime

# initialize config file
config = configparser.ConfigParser()
config.read('ReefberryPi.ini')


def logprobedata(log_prefix, data):
    # create time stamp
    formatted_date=datetime.strptime(str(datetime.now()), "%Y-%m-%d %H:%M:%S.%f")
    formatted_date=str(formatted_date.strftime("%Y-%m-%d %H:%M:%S"))
    # write data to file
    log_file_name = log_prefix + datetime.now().strftime("%Y-%m-%d") + ".txt"
    fh = open(str(config['logs']['log_dir']) + "/" + log_file_name, "a")
    fh.write(str(formatted_date) + "," + str(data) + "\n")
    fh.close()
        
    
