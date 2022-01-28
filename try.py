#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "try"
__version__ = "init"
__author__ = "@henry.fan"
import os
import sys
from pprint import pp
from libs.adb.adb import ADB
print(os.path.dirname(__file__))

sensor_collections = ('accel', 'gyro', 'mag')


def produce_var(string):
    try:
        var = eval(string)
    except (NameError, SyntaxError) as e:
        var = string
    return var


def is_a_range(l):
    if len(l) != 2:
        return False
    elif not all([isinstance(x, float) for x in l]):
        return False
    elif 0 not in l and sum(l) != 0:
        return False
    else:
        return True


def get_ranges(l: list):
    if is_a_range(l):
        return [abs(l[0])]
    elif all([is_a_range(x) for x in l]):
        return [abs(x[0]) for x in l]
    else:
        return []


l = [[-4.36332, 4.36332],
     [-8.72664, 8.72664],
     [-17.453279, 17.453279],
     [-34.906559, 34.906559]]
ranges = get_ranges(l)


if __name__ == "__main__":
    # print(sys.argv)
    adb = ADB()
    sensor_info_text = adb.adb_sensor_info()
    # ftxt = r'C:\Users\FNH1SGH\Desktop\sensor_info.txt'
    sensor_info_list = list()
    # with open(ftxt, 'r') as f:
    #     line = f.readline()
    sensor_info = dict()
    for line in sensor_info_text.splitlines():
        if line.startswith('SUID') and sensor_info:
            # if sensor_info:
            sensor_info_list.append(sensor_info)
            sensor_info = dict()
        try:
            k, v = [s.strip() for s in line.split('=') if line.count('=') == 1]
            sensor_info.update({produce_var(k): produce_var(v)})

        except ValueError as e:
            continue
        # line = f.readline()
    sensor_info_list = [sensor_info for sensor_info in sensor_info_list if sensor_info.get('VENDOR', '').lower() == 'bosch']
    sensor_info_list = [sensor_info for sensor_info in sensor_info_list if sensor_info.get('TYPE', '').lower() in sensor_collections]

    # sensor_info = sensor_info_lines
    pp(sensor_info_list)
