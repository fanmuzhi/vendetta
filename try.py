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


l = [
    [-4.36332, 4.36332],
    [-8.72664, 8.72664],
    [-17.453279, 17.453279],
    [-34.906559, 34.906559],
]
ranges = get_ranges(l)

if __name__ == "__main__":
    # # print(sys.argv)
    # adb = ADB()
    # sensor_info_text = adb.adb_sensor_info()
    # # ftxt = r'C:\Users\FNH1SGH\Desktop\sensor_info.txt'
    # sensor_info_list = list()
    # # with open(ftxt, 'r') as f:
    # #     line = f.readline()
    # sensor_info = dict()
    # for line in sensor_info_text.splitlines():
    #     if line.startswith('SUID') and sensor_info:
    #         # if sensor_info:
    #         sensor_info_list.append(sensor_info)
    #         sensor_info = dict()
    #     try:
    #         k, v = [s.strip() for s in line.split('=') if line.count('=') == 1]
    #         sensor_info.update({produce_var(k): produce_var(v)})
    #
    #     except ValueError as e:
    #         continue
    #     # line = f.readline()
    # sensor_info_list = [sensor_info for sensor_info in sensor_info_list if sensor_info.get('VENDOR', '').lower() == 'bosch']
    # sensor_info_list = [sensor_info for sensor_info in sensor_info_list if sensor_info.get('TYPE', '').lower() in sensor_collections]
    #
    # # sensor_info = sensor_info_lines
    # pp(sensor_info_list)
    # l = []
    # l.sort()
    # coding: utf-8

    sensor_type = ['accel', 'gyro', 'mag', 'pressure', 'sensor_temperature']
    odr_dict = {
        'accel': [25, 50, 100, 200, 400],
        'gyro': [25, 50, 100, 200, 400, 800],
        'mag': [25, 50, 100],
        'pressure': [25, 50],
        'sensor_temperature': [25],
    }

    odr_sweap = {'ascend': -3.0, 'descend': -3.1, 'random': -3.2}
    fac_test = {3: 'Connectivity', 2: 'Calibration', 1: 'HW/SW_self'}
    fac_test_dict = {
        'accel': [3, 2, 1],
        'gyro': [3, 2, 1],
        'mag': [3, 1],
        'pressure': [3, 1],
        'sensor_temperature': [3],
    }

    accel_range = {0: '2g', 1: '4g', 2: '8g', 3: '16g'}
    gyro_range = {1: '250dps', 2: '500dps', 3: '1000dps', 4: '2000dps'}

    test_duration = {'odr_sweap': 10, 'odr_dict': 30, 'fac_test': 5}

    ##Sanity_Test_Cases
    # odr_list
    for x in sensor_type:
        # print x
        # print odr_dict[x]
        for y in odr_dict[x]:
            print(x + '_' + str(y))

    # odr_sweap
    for x in sensor_type:
        for y in dict.keys(odr_sweap):
            print(x + '_' + y)

    # fac test
    for x in sensor_type:
        for y in fac_test_dict[x]:
            print(x + '_' + fac_test[y])

    ##Internal_Concurrency_Test_Cases
    # two clients max and min
    for x in sensor_type:
        print(x + '_' + str(max(odr_dict[x])) + '_' + x + '_' + str(min(odr_dict[x])))

    # two clients max and fac test
    for x in sensor_type:
        for y in fac_test_dict[x]:
            print(x + '_' + str(max(odr_dict[x])) + '_' + fac_test[y])

    # two clients max and sweap
    for x in sensor_type:
        for y in dict.keys(odr_sweap):
            # print len(dict.keys(odr_sweap))
            print(x + '_' + str(max(odr_dict[x])) + '_' + x + '_' + y)
            print(x + '_' + str(min(odr_dict[x])) + '_' + x + '_' + y)

    # two client sweap
    for x in sensor_type:
        for i in range(len(dict.keys(odr_sweap))):
            for j in range(i + 1, len(dict.keys(odr_sweap))):
                if j >= len(dict.keys(odr_sweap)):
                    break
                else:
                    print(
                        x
                        + '_'
                        + dict.keys(odr_sweap)[i]
                        + '_'
                        + x
                        + '_'
                        + dict.keys(odr_sweap)[j]
                    )

    ##External_Concurrency_Test_Cases
    # Max ODR concurrency Min ODR
    for i in range(len(sensor_type)):
        for j in range(i + 1, len(sensor_type)):
            # print i
            # print j
            if j >= len(sensor_type):
                break
            else:
                print(
                    sensor_type[i]
                    + '_'
                    + str(max(odr_dict[sensor_type[i]]))
                    + '_'
                    + sensor_type[j]
                    + '_'
                    + str(min(odr_dict[sensor_type[j]]))
                )
                print(
                    sensor_type[i]
                    + '_'
                    + str(min(odr_dict[sensor_type[i]]))
                    + '_'
                    + sensor_type[j]
                    + '_'
                    + str(max(odr_dict[sensor_type[j]]))
                )

    # Min ODR concurrency ODR sweap
    for i in range(len(sensor_type)):
        for j in range(i + 1, len(sensor_type)):
            if j >= len(sensor_type):
                break
            else:
                for y in dict.keys(odr_sweap):
                    print(
                        sensor_type[i]
                        + '_'
                        + str(min(odr_dict[sensor_type[i]]))
                        + '_'
                        + sensor_type[j]
                        + '_'
                        + y
                    )
                    print(
                        sensor_type[j]
                        + '_'
                        + str(min(odr_dict[sensor_type[j]]))
                        + '_'
                        + sensor_type[i]
                        + '_'
                        + y
                    )

    # All sensors max odr Concurrency fac
    if 'accel' in sensor_type and 'gyro' in sensor_type and 'mag' in sensor_type:
        sensor_type = ['accel', 'gyro', 'mag']
        # print sensor_type
        for x in sensor_type:
            for y in fac_test_dict[x]:
                print(
                    sensor_type[0]
                    + str(max(odr_dict[sensor_type[0]]))
                    + sensor_type[1]
                    + str(max(odr_dict[sensor_type[1]]))
                    + sensor_type[2]
                    + str(max(odr_dict[sensor_type[2]]))
                    + '_'
                    + x
                    + '_'
                    + fac_test[y]
                )

    elif 'accel' in sensor_type and 'gyro' in sensor_type and 'mag' not in sensor_type:
        sensor_type = ['accel', 'gyro']
        # print sensor_type
        for x in sensor_type:
            for y in fac_test_dict[x]:
                print(
                    sensor_type[0]
                    + str(max(odr_dict[sensor_type[0]]))
                    + sensor_type[1]
                    + str(max(odr_dict[sensor_type[1]]))
                    + '_'
                    + x
                    + '_'
                    + fac_test[y]
                )

    ## Range
    if 'accel' in sensor_type and 'gyro' in sensor_type:
        for i in range(len(dict.values(accel_range))):
            # print i
            for j in range(len(dict.values(gyro_range))):
                # print j
                if i == j:
                    print(
                        dict.values(accel_range)[i]
                        + '_'
                        + dict.values(gyro_range)[j]
                        + '_'
                        + 'accel'
                        + '_'
                        + str(min(odr_dict['accel']))
                    )
                    print(
                        dict.values(accel_range)[i]
                        + '_'
                        + dict.values(gyro_range)[j]
                        + '_'
                        + 'accel'
                        + '_'
                        + str(max(odr_dict['accel']))
                    )
                    print(
                        dict.values(accel_range)[i]
                        + '_'
                        + dict.values(gyro_range)[j]
                        + '_'
                        + 'gyro'
                        + '_'
                        + str(min(odr_dict['gyro']))
                    )
                    print(
                        dict.values(accel_range)[i]
                        + '_'
                        + dict.values(gyro_range)[j]
                        + '_'
                        + 'gyro'
                        + '_'
                        + str(max(odr_dict['gyro']))
                    )
                    for x in fac_test_dict['accel']:
                        print(
                            dict.values(accel_range)[i]
                            + '_'
                            + dict.values(gyro_range)[j]
                            + '_'
                            + 'accel'
                            + '_'
                            + fac_test[x]
                        )
                    for y in fac_test_dict['gyro']:
                        print(
                            dict.values(accel_range)[i]
                            + '_'
                            + dict.values(gyro_range)[j]
                            + '_'
                            + 'gyro'
                            + '_'
                            + fac_test[y]
                        )
    elif 'accel' in sensor_type and 'gyro' not in sensor_type:
        for i in range(len(dict.values(acc_range))):
            print(
                'accel'
                + '_'
                + dict.values(accel_range)[i]
                + '_'
                + str(min(odr_dict['accel']))
            )
            print(
                'accel'
                + '_'
                + dict.values(accel_range)[i]
                + '_'
                + str(max(odr_dict['accel']))
            )
            for x in fac_test_dict['accel']:
                print(dict.values(acc_range)[i] + '_' + 'acc' + '_' + fac_test[x])

    elif 'accel' not in sensor_type and 'gyro' in sensor_type:
        for j in range(len(dict.values(gyro_range))):
            print(
                'gyro'
                + '_'
                + dict.values(gyro_range)[j]
                + '_'
                + str(min(odr_dict['gyro']))
            )
            print(
                'gyro'
                + '_'
                + dict.values(gyro_range)[j]
                + '_'
                + str(max(odr_dict['gyro']))
            )
            for y in fac_test_dict['gyro']:
                print(dict.values(gyro_range)[j] + '_' + 'gyro' + '_' + fac_test[y])
