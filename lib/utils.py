#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "utils"
__version__ = "init"
__author__ = "@henry.fan"

import os
import re
from datetime import datetime
import ctypes
import json
import time
from lib.ssc_drva.ssc_drva import SscDrvaParams
from lib.adb.adb import ADB
from lib import config as cfg
from lib.quts.quts import logging_diag_hdf

datetime_format = '%Y-%m-%d_%H-%M-%S'


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        return False


def file_exists(file):
    return os.path.exists(file)


def datetime_str():
    return datetime.now().strftime(datetime_format)


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


def collect_csvs(ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt, param_sets):
    filename = rf"C:\temp\testlog\{log_file_name(param_sets)}.hdf"
    ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
    # print(" ".join(ssc_drva_cmd))

    with logging_diag_hdf(quts_dev_mgr, filename):
        ssc_drva.ssc_drva_run(ssc_drva_cmd)
    qseevt.set_hdffile_text(filename)
    qseevt.set_sensor_info_file_text(info_file=sensor_info_txt)
    qseevt.run_log_analysis()
    while not qseevt.analyze_complete():
        time.sleep(0.1)
    parsed_folder = os.path.splitext(filename)[0]
    csv_data_logs = []
    for par, dirs, files in os.walk(parsed_folder):
        csv_data_logs += [os.path.join(par, f) for f in files if valid_csv_name(f)]

    return csv_data_logs


if __name__ == "__main__":
    print(datetime_str())
