#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "utils"
__version__ = "init"
__author__ = "@henry.fan"

import ctypes
import json
import os
import re
import time
from datetime import datetime

from libs import config as cfg
from libs.adb.adb import ADB

# from libs.quts.quts import logging_diag_hdf
from libs.ssc_drva.ssc_drva import SscDrvaParams

datetime_format = '%Y%m%d_%H%M%S'
adb = ADB()


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print(e)
        return False


def datetime_str():
    return datetime.now().strftime(datetime_format)


def sensor_info_list():
    sensor_info_text = adb.adb_sensor_info()
    def produce_var(string):
        try:
            var = eval(string)
        except (NameError, SyntaxError):
            var = string
        return var

    sensor_collections = ('accel', 'gyro', 'mag')
    sensor_info_list = list()
    sensor_info = dict()
    for line in sensor_info_text.splitlines():
        if line.startswith('SUID') and sensor_info:
            sensor_info_list.append(sensor_info)
            sensor_info = dict()
        try:
            k, v = [s.strip() for s in line.split('=') if line.count('=') == 1]
            sensor_info.update({produce_var(k): produce_var(v)})

        except ValueError:
            continue
    # hw_ids = [sensor_info['HW_ID'] for sensor_info in sensor_info_list if sensor_info.get('HW_ID', None) is not None]
    sensor_info_list = [sensor_info for sensor_info in sensor_info_list if
                        sensor_info.get('VENDOR', '').lower() == 'bosch']
    sensor_info_list = [sensor_info for sensor_info in sensor_info_list if
                        sensor_info.get('TYPE', '').lower() in sensor_collections]
    return sensor_info_list


def get_sensorlist(productname: str):
    if productname.lower().startswith('bmi'):
        sensor_list = [
            cfg.Sensor.acc.value,
            cfg.Sensor.gyr.value,
        ]
    elif productname.lower().startswith('bma'):
        sensor_list = [cfg.Sensor.acc.value]
    elif productname.lower().startswith('bmg'):
        sensor_list = [cfg.Sensor.gyr.value]
    elif productname.lower().startswith('bmm'):
        sensor_list = [cfg.Sensor.mag.value]
    elif productname.lower().startswith('bmx'):
        sensor_list = [
            cfg.Sensor.acc.value,
            cfg.Sensor.gyr.value,
            cfg.Sensor.mag.value,
        ]
    else:
        sensor_list = []
    return sensor_list


def log_file_name(params_sets):
    if all(params_sets):
        log_name = 'Concurrency'
    elif 'sample_rate' in params_sets[0]:
        log_name = 'Stream'
    elif 'factory_test' in params_sets[0]:
        log_name = cfg.FacTest(params_sets[0].get('factory_test')).name
    else:
        log_name = 'Unknown'

    for param_set in params_sets:
        if not param_set:
            continue
        log_name += '_'
        log_name += '_'.join(
            [
                f'{SscDrvaParams.valid_keys_and_sort.get(k, "unknowntag")}={v}'
                for k, v in param_set.items()
            ]
        )
    log_time = f'{datetime.now().strftime(datetime_format)}'
    log_name = f'{log_time}_{log_name}'
    return log_name


def valid_csv_name(csv_name):
    if os.path.splitext(csv_name)[1] != '.csv':
        return False
    elif (
        'resampler' in csv_name.lower() or '[std_sensor_event]' not in csv_name.lower()
    ):
        return False
    else:
        pattern = (
            r'^SensorAPI_([A-Z|a-z]+)_S\d+_I\d+_D\d+_R\d+_\[std_sensor_event\].csv'
        )
        m = re.match(pattern, csv_name)
        return True if m else False


def imu_bias_values(productname, sensor):
    # if not sensor:
    #     return tuple()
    bias_folder = r'mnt/vendor/persist/sensors/registry/registry'
    biasfile = rf'{bias_folder}/{productname}_0_platform.{sensor}.fac_cal.bias'

    cat = ADB().adb_cat(biasfile)
    json_buffer = json.loads(cat.decode())
    root = list(json_buffer.keys())[0]
    return (
        int(json_buffer[root]['x']['ver']),
        int(json_buffer[root]['y']['ver']),
        int(json_buffer[root]['z']['ver']),
    )


# def collect_csvs(ssc_drva, quts_dev_mgr, qseevt, sensor_info_text, param_sets):
#     log_path = r"C:\temp\testlog"
#     file_name = rf"{log_file_name(param_sets)}.hdf"
#     logfile = os.path.join(log_path, file_name)
#     ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
#     # print(" ".join(ssc_drva_cmd))
#
#     with logging_diag_hdf(quts_dev_mgr, logfile):
#         ssc_drva.ssc_drva_run(ssc_drva_cmd)
#     qseevt.set_hdffile_text(logfile)
#     qseevt.set_sensor_info_file_text(info_file=sensor_info_text)
#     qseevt.run_log_analysis()
#     while not qseevt.analyze_complete():
#         time.sleep(0.1)
#     parsed_folder = os.path.splitext(logfile)[0]
#     csv_data_logs = []
#     for par, dirs, files in os.walk(parsed_folder):
#         csv_data_logs += [os.path.join(par, f) for f in files if valid_csv_name(f)]
#
#     return csv_data_logs


if __name__ == "__main__":
    print(datetime_str())
