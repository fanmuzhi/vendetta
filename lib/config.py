#!/usr/bin/env python
# encoding: utf-8
"""
# Description: project config file
"""
__filename__ = "config"
__author__ = "@henry.fan"
import os
from enum import Enum
import logging

path = os.path.dirname(__file__)
LOG_LEVEL = logging.INFO
datetime_format = '%Y%m%d%H%M%S'

if LOG_LEVEL > logging.DEBUG:
    ssc_drva_stdout = False
    minidm_stdout = False
else:
    ssc_drva_stdout = True
    minidm_stdout = True


class Product:
    bmi26x = 'bmi26x'


class ConfigFile:
    pass


class QcmBoard:
    name = ''
    vid = 1478
    manufacturer = 'Qualcomm Incorporated'
    registry_dir = r'/mnt/vendor/persist/sensors/registry/registry/'
    conf_dest_dir = r'/vendor/etc/sensors/config/'


class Mdm:
    minidm_dir = os.path.join(path, '..', 'Apps', 'mini-dm')
    minidm_exe = os.path.join(minidm_dir, 'mini-dm.exe')
    dlf_log_path = os.path.join(minidm_dir, 'dlf_logs')
    drv_log_path = os.path.join(minidm_dir, 'drv_logs')


class Sensor(Enum):
    acc = 'accel'
    gyr = 'gyro'
    sensor_temp = 'sensor_temperature'
    pre = 'pressure'
    mag = 'mag'
    hum = 'humidity'
    temp = 'ambient_temperature'
    ultra_violet = 'ultra_violet'
    proximity = 'proximity'
    ambient_light = 'ambient_light'
    rgb = 'rgb'
    hall = 'hall'
    motion_detect = 'motion_detect'


class Odr(Enum):
    odr_25hz = 25 * (2 ** 0)
    odr_50hz = 25 * (2 ** 1)
    odr_100hz = 25 * (2 ** 2)
    odr_200hz = 25 * (2 ** 3)
    odr_400hz = 25 * (2 ** 4)
    odr_max = -1
    odr_min = -2
    odr_sweep_ascend = -3.0
    odr_sweep_random = -3.2
    odr_sweep_descend = -3.1
    odr_random = -4


odr_to_interval = {
    Odr.odr_max: 2.5,
    Odr.odr_min: 40,
    Odr.odr_25hz: 4,
    Odr.odr_100hz: 10,
    Odr.odr_50hz: 20,
    Odr.odr_200hz: 5,
}


class AccRes(Enum):
    res_2g = 0
    res_4g = 1
    res_8g = 2
    res_16g = 3


class GyrRes(Enum):
    # res_125dps = 0
    res_250dps = 1
    res_500dps = 2
    res_1000dps = 3
    res_2000dps = 4


class MagRes(Enum):
    res_1 = 1
    res_2 = 2
    res_3 = 3
    res_4 = 4


res_idx_dict = {
    Sensor.acc.value: AccRes,
    Sensor.gyr.value: GyrRes,
    Sensor.mag.value: AccRes,
}


class FacTest(Enum):
    Fac_Software = 0
    HardwareSelfTest = 1
    Calibration = 2
    Connectivity = 3


if __name__ == '__main__':
    # sensors = [Sensor.acc.value, Sensor.gyr.value]
    a = [res_idx_dict[sensor.value] for sensor in [Sensor.acc, Sensor.gyr]]
    print(a)
    print(list(zip(*a)))
    # for sensor in sensors:
    #     res_idx_vals_list.append()
    #
    # print([idx for idx in zip(res_idx_dict[sensor]])
