import re
import os
import time
from datetime import datetime


# function: read and parse sensor data file
def read_sensor(path):
    dt_string = datetime.now().strftime('%Y-%M-%d-%h:%m:%s')
    value = "U"
    try:
        f = open(path, "r")
        line = f.readline()
        if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
            line = f.readline()
            m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
            if m:
                value = str(float(m.group(2)) / 1000.0)
        f.close()
    except IOError as e:
        print(f'{dt_string} Error reading {path}: {e}')
    return value


# define pathes to 1-wire sensor data
pathes = (
    "/sys/bus/w1/devices/28-051686aa54ff/w1_slave"
)

# read sensor data
data = 'N'
for path in pathes:
    data += ':'
    data += read_sensor(path)
    time.sleep(1)

print(data)
