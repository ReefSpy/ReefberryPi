import os
import glob
from datetime import time

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


def read_temp_raw(device_file):
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp(probeid, scale):

    try:
        base_dir = '/sys/bus/w1/devices/'
        # device_folder = glob.glob(base_dir + '28*')[0]
        device_folder = glob.glob(base_dir + probeid)[0]
        device_file = device_folder + '/w1_slave'
    except:
        print("Exception ds18b20.py")

    lines = read_temp_raw(device_file)

    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()

    equals_pos = lines[1].find('t=')

    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        if scale == "F":
            return "{:.1f}".format(temp_f)
        if scale == "C":
            return "{:.1f}".format(temp_c)
        else:
            return temp_c, temp_f
