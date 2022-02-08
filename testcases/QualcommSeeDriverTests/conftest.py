#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "conftest.py"
__version__ = "init"
__author__ = "@henry.fan"
import csv
import itertools
import json
import os
import re

import pytest

import libs.config as cfg
from libs import utils
from libs import qseevt
import libs.quts as quts

from libs.adb.adb import ADB
from libs.ssc_drva.ssc_drva import SscDrvaTest

sensor_info_list = utils.sensor_info_list()

ll = [
  #   {'SUID': 45140206676225902424422602651988808301,
  # 'NAME': 'bmi263',
  # 'VENDOR': 'BOSCH',
  # 'TYPE': 'mag',
  # 'AVAILABLE': 'true',
  # 'VERSION': '1.1.37',
  # 'API': 'sns_mag.proto',
  # 'RATES': [25.0, 50.0, 100.0],
  # 'RESOLUTIONS': 0.3,
  # 'RANGES': [-1300.0, 1300.0],
  # 'DRI': 'true',
  # 'FIFO_SIZE': 146,
  # 'STREAM_TYPE': 'streaming',
  # 'STREAM_SYNC': 'false',
  # 'DYNAMIC': 'false',
  # 'EVENT_SIZE': 16,
  # 'OP_MODES': '[LPM, NORMAL, OFF]',
  # 'HW_ID': 0,
  # 'RIGID_BODY': 'display',
  # 'PLACEMENT': [0.1, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  # 'PHYSICAL_SENSOR': 'true',
  # 'PHYSICAL_SENSOR_TESTS': [3, 1],
  # 'SELECTED_RESOLUTION': 0.3,
  # 'SELECTED_RANGE': [-1300.0, 1300.0]},

 {'SUID': 131046396229003214259151716237223825521,
  'NAME': 'bmi263',
  'VENDOR': 'BOSCH',
  'TYPE': 'gyro',
  'AVAILABLE': 'true',
  'VERSION': '1.1.37',
  'API': 'sns_gyro.proto',
  'RATES': [25.0, 50.0, 100.0, 200.0, 400.0],
  'RESOLUTIONS': [0.000133, 0.000266, 0.000533, 0.001065],
  'RANGES': [[-4.36332, 4.36332],
             [-8.72664, 8.72664],
             [-17.453279, 17.453279],
             [-34.906559, 34.906559]],
  'DRI': 'true',
  'FIFO_SIZE': 146,
  'STREAM_TYPE': 'streaming',
  'STREAM_SYNC': 'false',
  'DYNAMIC': 'false',
  'EVENT_SIZE': 16,
  'OP_MODES': '[LPM, NORMAL, OFF]',
  'ACTIVE_CURRENT': [6, 900, 900],
  'SLEEP_CURRENT': 6,
  'HW_ID': 0,
  'RIGID_BODY': 'display',
  'PLACEMENT': [0.1, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  'PHYSICAL_SENSOR': 'true',
  'PHYSICAL_SENSOR_TESTS': [3, 2, 1],
  'SELECTED_RESOLUTION': 0.001065,
  'SELECTED_RANGE': [-34.906559, 34.906559]},

 {'SUID': 317125108042284131473205661129850952667,
  'NAME': 'bmi263',
  'VENDOR': 'BOSCH',
  'TYPE': 'accel',
  'AVAILABLE': 'true',
  'VERSION': '1.1.37',
  'API': 'sns_accel.proto',
  'RATES': [25.0, 50.0, 100.0, 200.0, 400.0],
  'RESOLUTIONS': [0.000598, 0.001196, 0.002393, 0.004786],
  'RANGES': [[-19.6133, 19.6133],
             [-39.226601, 39.226601],
             [-78.453201, 78.453201],
             [-156.906403, 156.906403]],
  'DRI': 'true',
  'FIFO_SIZE': 146,
  'STREAM_TYPE': 'streaming',
  'STREAM_SYNC': 'false',
  'DYNAMIC': 'false',
  'EVENT_SIZE': 16,
  'OP_MODES': '[LPM, NORMAL, OFF]',
  'ACTIVE_CURRENT': [6, 180, 6],
  'SLEEP_CURRENT': 6,
  'HW_ID': 0,
  'RIGID_BODY': 'display',
  'PLACEMENT': [0.1, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
  'PHYSICAL_SENSOR': 'true',
  'PHYSICAL_SENSOR_TESTS': [3, 2, 1],
  'SELECTED_RESOLUTION': 0.004786,
  'SELECTED_RANGE': [-156.906403, 156.906403]},

 #  {'SUID': 45140206676225902424422602651988808301,
 #  'NAME': 'bmi263',
 #  'VENDOR': 'BOSCH',
 #  'TYPE': 'mag',
 #  'AVAILABLE': 'true',
 #  'VERSION': '1.1.37',
 #  'API': 'sns_mag.proto',
 #  'RATES': [25.0, 50.0, 100.0],
 #  'RESOLUTIONS': 0.3,
 #  'RANGES': [-1300.0, 1300.0],
 #  'DRI': 'true',
 #  'FIFO_SIZE': 146,
 #  'STREAM_TYPE': 'streaming',
 #  'STREAM_SYNC': 'false',
 #  'DYNAMIC': 'false',
 #  'EVENT_SIZE': 16,
 #  'OP_MODES': '[LPM, NORMAL, OFF]',
 #  'HW_ID': 1,
 #  'RIGID_BODY': 'display',
 #  'PLACEMENT': [0.1, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
 #  'PHYSICAL_SENSOR': 'true',
 #  'PHYSICAL_SENSOR_TESTS': [3, 1],
 #  'SELECTED_RESOLUTION': 0.3,
 #  'SELECTED_RANGE': [-1300.0, 1300.0]},
 #
 # {'SUID': 131046396229003214259151716237223825521,
 #  'NAME': 'bmi263',
 #  'VENDOR': 'BOSCH',
 #  'TYPE': 'gyro',
 #  'AVAILABLE': 'true',
 #  'VERSION': '1.1.37',
 #  'API': 'sns_gyro.proto',
 #  'RATES': [25.0, 50.0, 100.0, 200.0, 400.0],
 #  'RESOLUTIONS': [0.000133, 0.000266, 0.000533, 0.001065],
 #  'RANGES': [[-4.36332, 4.36332],
 #             [-8.72664, 8.72664],
 #             [-17.453279, 17.453279],
 #             [-34.906559, 34.906559]],
 #  'DRI': 'true',
 #  'FIFO_SIZE': 146,
 #  'STREAM_TYPE': 'streaming',
 #  'STREAM_SYNC': 'false',
 #  'DYNAMIC': 'false',
 #  'EVENT_SIZE': 16,
 #  'OP_MODES': '[LPM, NORMAL, OFF]',
 #  'ACTIVE_CURRENT': [6, 900, 900],
 #  'SLEEP_CURRENT': 6,
 #  'HW_ID': 1,
 #  'RIGID_BODY': 'display',
 #  'PLACEMENT': [0.1, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
 #  'PHYSICAL_SENSOR': 'true',
 #  'PHYSICAL_SENSOR_TESTS': [3, 2, 1],
 #  'SELECTED_RESOLUTION': 0.001065,
 #  'SELECTED_RANGE': [-34.906559, 34.906559]},
 #
 # {'SUID': 317125108042284131473205661129850952667,
 #  'NAME': 'bmi263',
 #  'VENDOR': 'BOSCH',
 #  'TYPE': 'accel',
 #  'AVAILABLE': 'true',
 #  'VERSION': '1.1.37',
 #  'API': 'sns_accel.proto',
 #  'RATES': [25.0, 50.0, 100.0, 200.0, 400.0],
 #  'RESOLUTIONS': [0.000598, 0.001196, 0.002393, 0.004786],
 #  'RANGES': [[-19.6133, 19.6133],
 #             [-39.226601, 39.226601],
 #             [-78.453201, 78.453201],
 #             [-156.906403, 156.906403]],
 #  'DRI': 'true',
 #  'FIFO_SIZE': 146,
 #  'STREAM_TYPE': 'streaming',
 #  'STREAM_SYNC': 'false',
 #  'DYNAMIC': 'false',
 #  'EVENT_SIZE': 16,
 #  'OP_MODES': '[LPM, NORMAL, OFF]',
 #  'ACTIVE_CURRENT': [6, 180, 6],
 #  'SLEEP_CURRENT': 6,
 #  'HW_ID': 1,
 #  'RIGID_BODY': 'display',
 #  'PLACEMENT': [0.1, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
 #  'PHYSICAL_SENSOR': 'true',
 #  'PHYSICAL_SENSOR_TESTS': [3, 2, 1],
 #  'SELECTED_RESOLUTION': 0.004786,
 #  'SELECTED_RANGE': [-156.906403, 156.906403]}
     ]
# sensor_info_list = ll

fdmc = os.path.join(os.path.dirname(__file__), 'mydmc.dmc')
extra_odrs = [-3.0, -3.1, -3.2]
streamtest_odr_list = [-2, 50, 100, 200, -1, -3.0]
factest_type_list = [1, 2, 3]
sensor_streamtest_dur = 30
sensor_factest_dur = 5
ssc_drva_delay = 2
null_params = [None]
test_result_root_dir = r'c:\SeeTests'

res_squence = [
    {cfg.Sensor.acc.value: 0, cfg.Sensor.gyr.value: 1, cfg.Sensor.mag.value: 1},
    {cfg.Sensor.acc.value: 1, cfg.Sensor.gyr.value: 2, cfg.Sensor.mag.value: 2},
    {cfg.Sensor.acc.value: 2, cfg.Sensor.gyr.value: 3, cfg.Sensor.mag.value: 3},
    {cfg.Sensor.acc.value: 3, cfg.Sensor.gyr.value: 4, cfg.Sensor.mag.value: 4},
]

using_ssc_drva_keys = [
    'sensor',
    'duration',
    'sample_rate',
    'factory_test',
    'hw_id',
    'delay',
]

ranges = [
    {'accel': 0, 'gyro': 1},
    {'accel': 1, 'gyro': 2},
    {'accel': 2, 'gyro': 3},
    {'accel': 3, 'gyro': 4},
]

driver_msg_log_headers = ['Timestamp', 'Name', 'Message']


def pytest_addoption(parser):
    parser.addoption(
        "--product",
        action="store",
        default="",
        help="Product name in registry file, eg: 'bmi3x0'",
    )
    parser.addoption(
        "--platform",
        action="store",
        default="hdk8350",
        help="qualcomm dev board, default=hdk8350",
    )
    parser.addoption(
        "--nhw",
        action="store",
        default=1,
        help="numbers of sensor hardware connected, default: 1",
    )
    # parser.addoption(
    #     "--log_dir",
    #     action="store",
    #     # default=default_log_dir,
    #     help="Customize a location to save test log files",
    # )
    # parser.addoption(
    #     "--report_dir",
    #     action="store",
    #     default=default_report_dir,
    #     help="Customize an location to save test report logs",
    # )


def resvalue_id_str(registry_dict):
    words = []
    for k, v in registry_dict.items():
        words.append(f'{k}.{cfg.res_values.get(k, {}).get(v, "unknown")}')
        # words.append(cfg.res_values.get(k, {}).get(v, "unknown"))
    return f"{'-'.join(words)}"


def extern_conc_streamtest_odr_to_dur(odr):
    if isinstance(odr, int):
        return 100
    else:
        return 10


def setup_param_sets(params_list):
    """
     :param params_list:
        eg:{
             'sensor': ('gyro', 'gyro'),
             'duration': (30, 5),
             'sample_rate': (-1, None),
             'factory_test': (None, 2),
             'hw_id': (0, 0),
             'delay': (None, 2)
         }
     # :return: param_sets
     """
    param_sets = [dict(), dict()]
    for k, v in params_list.items():
        if v is not None:
            for i in range(2):
                if v[i] is not None:
                    param_sets[i].update({k: v[i]})
    return param_sets


def test_case_id_str(pairs):
    id_word_list = []
    for i in range(2):
        if pairs['sensor'][i]:
            id_word_list.append(pairs['sensor'][i])
        if pairs['sample_rate'] and pairs['sample_rate'][i] is not None:
            id_word_list.append(cfg.Odr(pairs['sample_rate'][i]).name)
        if pairs['factory_test'] and pairs['factory_test'][i] is not None:
            id_word_list.append(cfg.FacTest(pairs['factory_test'][i]).name)
        if pairs['hw_id'] and pairs['hw_id'][i] is not None:
            id_word_list.append(f"hw{pairs['hw_id'][i]}")
    id_str = '-'.join(id_word_list)
    return id_str


def match_summary_text(diag_service, re_pattern, data_queue='data'):
    diag_packets = diag_service.getDataQueueItems(data_queue, 1, 20)
    while diag_packets:
        if re.search(re_pattern, diag_packets[0].summaryText):
            found = True
            break
        diag_packets = diag_service.getDataQueueItems(data_queue, 1, 20)
    else:
        found = False
    return found


def hws_sensors():
    sensors_of_hw = dict()
    for sensor_info in sensor_info_list:
        if sensor_info['HW_ID'] not in sensors_of_hw:
            sensors_of_hw[sensor_info['HW_ID']] = list()
        sensors_of_hw[sensor_info['HW_ID']].append(sensor_info['TYPE'])
    return sensors_of_hw

a = hws_sensors()
print(a)

# @pytest.fixture(scope='package', autouse=True)
# def sensor_list(request):
#     product = request.config.getoption("--product")
#     sensor_list = utils.get_sensorlist(product)
#     if not sensor_list:
#         pytest.exit("invalid product to test ")
#     else:
#         return sensor_list


def pytest_generate_tests(metafunc):
    # fixturename = ''
    # params_list = []
    # productname = getattr(metafunc.config.option, 'product', "")
    # nhw = int(getattr(metafunc.config.option, 'nhw', 1))
    # hw_ids = list(range(nhw))
    # sensor_list = utils.get_sensorlist(productname)
    sensor_info_list = ll

    if 'test_data_streaming' == metafunc.definition.name:
        params = []
        for sensor_info in sensor_info_list:
            sensor = sensor_info['TYPE']
            odrs = sensor_info['RATES'] + extra_odrs
            hw_id = sensor_info['HW_ID']
            params.extend(list(itertools.product([sensor], odrs, [hw_id])))

        if all(fix in metafunc.fixturenames for fix in ['sensor', 'odr', 'hw_id']):
            ids = [f'{param[0]}-{cfg.Odr(param[1]).name}-hw_{param[2]}' for param in params]
            metafunc.parametrize('sensor, odr, hw_id', params, ids=ids)

    if "test_factory_test" == metafunc.definition.name:
        params = []
        for sensor_info in sensor_info_list:
            sensor = sensor_info['TYPE']
            factests = sensor_info['PHYSICAL_SENSOR_TESTS']
            hw_id = sensor_info['HW_ID']
            params.extend(list(itertools.product([sensor], factests, [hw_id])))

        if all(fix in metafunc.fixturenames for fix in ['sensor', 'factest', 'hw_id']):
            ids = [f'{param[0]}-{cfg.FacTest(param[1]).name}-hw_{param[2]}' for param in params]
            metafunc.parametrize('sensor, factest, hw_id', params, ids=ids)

    if "test_internal_concurrency_stream" == metafunc.definition.name:
        params = []
        for sensor_info in sensor_info_list:
            sensor = sensor_info['TYPE']
            hw_id = sensor_info['HW_ID']
            params.extend([(sensor, -1, -2, hw_id)])
            params.extend([(sensor, -3.0, -3.1, hw_id)])

        if all(fix in metafunc.fixturenames for fix in ['sensor', 'odr0', 'odr1', 'hw_id']):
            ids = [f'{param[0]}-{cfg.Odr(param[1]).name}-{cfg.Odr(param[2]).name}-hw_{param[3]}' for param in params]
            metafunc.parametrize('sensor, odr0, odr1, hw_id', params, ids=ids)

    if "test_internal_concurrency_factest" == metafunc.definition.name:
        params = []
        for sensor_info in sensor_info_list:
            sensor = sensor_info['TYPE']
            factests = sensor_info['PHYSICAL_SENSOR_TESTS']

            hw_id = sensor_info['HW_ID']
            params.extend(list(itertools.product([sensor], [cfg.Odr.odr_max.value], factests, [hw_id])))

        if all(fix in metafunc.fixturenames for fix in ['sensor', 'odr', 'factest', 'hw_id']):
            ids = [f'{param[0]}-{cfg.Odr(param[1]).name}-{cfg.FacTest(param[2]).name}-hw_{param[3]}' for param in
                   params]
            metafunc.parametrize('sensor, odr, factest, hw_id', params, ids=ids)

    if "test_external_concurrency" == metafunc.definition.name:
        params = []
        external_sensor_info = [sensor_info for sensor_info in itertools.permutations(sensor_info_list, 2) if sensor_info[0]['HW_ID'] == sensor_info[1]['HW_ID']]
        for extern_info in external_sensor_info:
            sensor0, sensor1 = extern_info[0]['TYPE'], extern_info[1]['TYPE']
            odrs = [(-1, -2), (-1, -3.1), (-2, -3.2), (-3.0, -3.1)]
            hw_id = extern_info[0]['HW_ID']
            params.extend(list(itertools.product([(sensor0, sensor1)], odrs, [hw_id])))
        if all(fix in metafunc.fixturenames for fix in ['sensor0', 'odr0', 'sensor1', 'odr1', 'hw_id']):
            ids = [f'{param[0][0]}-{cfg.Odr(param[1][0]).name}-{param[0][1]}-{cfg.Odr(param[1][1]).name}-hw_{param[2]}' for param in
                   params]
            metafunc.parametrize('sensor0, odr0, sensor1, odr1, hw_id', [(param[0][0], param[1][0], param[0][1], param[1][1], param[2]) for param in params], ids=ids)

    if "test_dual_hw" == metafunc.definition.name:
        params = []
        dualhw_sensor_info = [sensor_info for sensor_info in itertools.permutations(sensor_info_list, 2) if (sensor_info[0]['HW_ID'], sensor_info[1]['HW_ID']) == (0, 1)]
        for extern_info in dualhw_sensor_info:
            sensor0, sensor1 = extern_info[0]['TYPE'], extern_info[1]['TYPE']
            if sensor0 == sensor1:
                odrs = [(-1, -2), (-3.0, -3.1)]
            else:
                odrs = [(-3.2, -3.2), (-2, -1)]
            # odrs = [(-1, -2), (-1, -3.1), (-2, -3.2), (-3.0, -3.1)]
            hw_id0, hw_id1 = extern_info[0]['HW_ID'], extern_info[1]['HW_ID']
            params.extend(list(itertools.product([(sensor0, sensor1)], odrs, [(hw_id0, hw_id1)])))
        if all(fix in metafunc.fixturenames for fix in ['sensor0', 'odr0', 'hw_id0', 'sensor1', 'odr1', 'hw_id1']):
            ids = [f'{param[0][0]}-{cfg.Odr(param[1][0]).name}-hw_{param[2][0]}-{param[0][1]}-{cfg.Odr(param[1][1]).name}-hw_{param[2][1]}' for param in
                   params]
            metafunc.parametrize('sensor0, odr0, hw_id0, sensor1, odr1, hw_id1', [(param[0][0], param[1][0], param[2][0], param[0][1], param[1][1], param[2][1]) for param in params], ids=ids)

    #     # fixturename = 'factorytest'
    #     params_sensor = list(itertools.product(sensor_list, [None]))
    #     params_factest_type = list(itertools.product(factest_type_list, [None]))
    #     params_odr = null_params
    #     params_dur = list(itertools.product([sensor_factest_dur], [None]))
    #     params_hwid = list(itertools.product(hw_ids, [None]))
    #     params_delay = null_params
    #
    #     params_list = list(
    #         itertools.product(
    #             params_sensor,
    #             params_dur,
    #             params_odr,
    #             params_factest_type,
    #             params_hwid,
    #             params_delay,
    #         )
    #     )
    #
    # if "test_data_stream" == metafunc.definition.name:
    #     params_sensor = list(itertools.product(sensor_list, [None]))
    #     params_dur = list(itertools.product([sensor_streamtest_dur], [None]))
    #     if "change_registry_res_value" in metafunc.fixturenames:
    #         params_odr = list(
    #             itertools.product(
    #                 [cfg.Odr.odr_max.value, cfg.Odr.odr_min.value], [None]
    #             )
    #         )
    #     else:
    #         params_odr = list(itertools.product(streamtest_odr_list, [None]))
    #
    #     # if "dynarange" in metafunc.fixturenames:
    #     #     params_sensor = list(itertools.product(sensor_list, [None]))
    #     params_factest_type = null_params
    #     params_hwid = list(itertools.product(hw_ids, [None]))
    #     params_delay = null_params
    #     params_list = list(
    #         itertools.product(
    #             params_sensor,
    #             params_dur,
    #             params_odr,
    #             params_factest_type,
    #             params_hwid,
    #             params_delay,
    #         )
    #     )
    #
    # if 'test_internal_stream_concurrency' == metafunc.definition.name:
    #     params_sensor = [tuple(itertools.repeat(sensor, 2)) for sensor in sensor_list]
    #     params_dur = [(30, 30)]
    #     params_odr = [(-1, -2), (-3.1, -3.2)]
    #     params_factest_type = null_params
    #     params_hwid = list(zip(*[hw_ids] * 2))
    #     params_delays = list(itertools.product([None], [ssc_drva_delay]))
    #     params_list = list(
    #         itertools.product(
    #             params_sensor,
    #             params_dur,
    #             params_odr,
    #             params_factest_type,
    #             params_hwid,
    #             params_delays,
    #         )
    #     )
    #
    # if 'test_internal_stream_factory_concurrency' == metafunc.definition.name:
    #     params_sensor = [tuple(itertools.repeat(sensor, 2)) for sensor in sensor_list]
    #     params_odr = list(itertools.product([-1], [None]))
    #     params_factest_type = list(itertools.product([None], [1, 2]))
    #     params_dur = [(30, 5)]
    #     params_hwid = list(zip(*[hw_ids] * 2))
    #     params_delays = list(itertools.product([None], [ssc_drva_delay]))
    #     params_list = list(
    #         itertools.product(
    #             params_sensor,
    #             params_dur,
    #             params_odr,
    #             params_factest_type,
    #             params_hwid,
    #             params_delays,
    #         )
    #     )
    #
    # if "test_external_concurrency" == metafunc.definition.name:
    #     if len(sensor_list) < 2:
    #         pytest.skip("skip")
    #     params_sensor = list(itertools.permutations(sensor_list, 2))
    #     # params_dur = null_params
    #     params_odr = [(-1, -2), (-1, -3.1), (-2, -3.2), (-3.0, -3.1)]
    #     params_factest_type = null_params
    #     params_hwid = list(zip(*[hw_ids] * 2))
    #     params_delays = list(itertools.product([None], [ssc_drva_delay]))
    #     params_list = []
    #     for odr in params_odr:
    #         params_dur = [
    #             (
    #                 extern_conc_streamtest_odr_to_dur(odr[0]),
    #                 extern_conc_streamtest_odr_to_dur(odr[1]),
    #             )
    #         ]
    #         params_list.extend(
    #             list(
    #                 itertools.product(
    #                     params_sensor,
    #                     params_dur,
    #                     [odr],
    #                     params_factest_type,
    #                     params_hwid,
    #                     params_delays,
    #                 )
    #             )
    #         )
    #
    # if (
    #     int(getattr(metafunc.config.option, 'nhw', 1)) >= 2
    #     and "TestDualHardwares" == metafunc.cls.__name__
    # ):
    #     # if int(getattr(metafunc.config.option, 'nhw', 1)) < 2:
    #     #     pytest.skip("skip")
    #     # else:
    #     # return
    #     # else:
    #
    #     params_list = [
    #         (('accel', 'accel'), (60, 60), (-1, -2), None, (0, 1), None),
    #         (('gyro', 'gyro'), (60, 60), (-1, -2), None, (0, 1), None),
    #         (('accel', 'accel'), (10, 10), (-3.0, -3.1), None, (0, 1), (None, 2)),
    #         (('gyro', 'gyro'), (10, 10), (-3.0, -3.1), None, (0, 1), (None, 2)),
    #         (('accel', 'gyro'), (10, 10), (-3.2, -3.2), None, (0, 1), (None, 2)),
    #         (('accel', 'gyro'), (30, 30), (-2, -1), None, (0, 1), (None, 2)),
    #         (('gyro', 'accel'), (30, 30), (-2, -1), None, (0, 1), (None, 2)),
    #     ]
    if "change_registry_res_value" in metafunc.fixturenames:
        range_vals = []
        sensors = set()
        for sensor_info in sensor_info_list:
            sensors.add(sensor_info['TYPE'])
        sensors = list(sensors)
        ranges = []
        for sensor in sensors:
            if sensor == 'accel':
                ranges.append([0, 1, 2, 3])
            if sensor == 'gyro':
                ranges.append([1, 2, 3, 4])
            if sensor == 'mag':
                ranges.append([0] * 4)
        rvs = list(zip(*ranges))

        # acc_range_idx_start = 0
        # gyr_range_idx_start = 1
        # mag_range_idx_start = 0
        #
        # n_acc_ranges = n_gyr_ranges = 4
        # n_mag_ranges = 1
        # acc_range_types = list(range(acc_range_idx_start, acc_range_idx_start + n_acc_ranges))
        # gyr_range_types = list(range(gyr_range_idx_start, gyr_range_idx_start + n_gyr_ranges))
        # mag_range_types = list(range(mag_range_idx_start, mag_range_idx_start + n_mag_ranges)) * n_acc_ranges
        # vals = list(zip(acc_range_types, gyr_range_types, mag_range_types))
        # # args = [cfg.res_values[sensor].keys() for sensor in sensor_list]
        # # rvs = list(zip(*args))
        # # range_vals = [dict(zip(sensor_list, t)) for t in rvs]
        # sensors = [cfg.Sensor.acc.value, cfg.Sensor.gyr.value, cfg.Sensor.mag.value]
        #     if sensor == cfg.Sensor.acc.value: acc_range_types = [0, 1, 2, 3]
        # gyr_range_types = [1, 2, 3, 4]
        # mag_range_types = [0] * len(acc_range_types)
        # vals = list(zip(acc_range_types, gyr_range_types, mag_range_types))

        range_vals = [dict(zip(sensors, t)) for t in rvs]

        metafunc.parametrize(
            'change_registry_res_value',
            range_vals,
            ids=[resvalue_id_str(r) for r in range_vals],
            scope='class',
            indirect=True,
        )
    # params_sets_list = [
    #     setup_param_sets(dict(zip(using_ssc_drva_keys, param))) for param in params_list
    # ]
    # ids = [
    #     test_case_id_str(dict(zip(using_ssc_drva_keys, param))) for param in params_list
    # ]
    # if 'collect_sscdrva_result' in metafunc.fixturenames:
    #     metafunc.parametrize(
    #         'collect_sscdrva_result', params_sets_list, ids=ids, indirect=True,
    #     )


# @pytest.fixture()
# def collect_sscdrva_result(
#     ssc_drva, quts_dev_mgr, quts_diag_service, data_queue, log_path, request
# ):
#     productname = request.config.getoption("--product")
#     calib_sensor = None
#     diag_packets_list = []
#     bias_result = []
#     result = {
#         'params_set': request.param,
#         'diag_packets_list': diag_packets_list,
#         'bias_values': bias_result,
#         'hdf': None,
#         'drv_log': None,
#     }
#     file_name = f"{request.cls.__name__}-{request.node.name}"
#     hdflogfile = os.path.join(log_path, f'{file_name}.hdf')
#     drvlogfile = os.path.join(log_path, f'{file_name}.csv')
#
#     has_factory_test = any(
#         ['factory_test' in param for param in request.param if param]
#     )
#     hdf_logging = any(['sample_rate' in param for param in request.param if param])
#     has_calibration = False
#     if has_factory_test:
#         has_calibration = any(
#             [param.get('factory_test', -1) == 2 for param in request.param if param]
#         )
#         if has_calibration:
#             for param in request.param:
#                 if param and param.get('factory_test', -1) == 2:
#                     calib_sensor = param['sensor']
#                     prev_biasvals = utils.imu_bias_values(productname, calib_sensor)
#                     result['bias_values'].append(prev_biasvals)
#
#     if hdf_logging:
#         quts_dev_mgr.startLogging()
#
#     ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=request.param)
#     ssc_drva.ssc_drva_run(ssc_drva_cmd)
#
#     diag_packets = quts_diag_service.getDataQueueItems(data_queue, 1, 20)
#     while diag_packets:
#         diag_packets_list.append(diag_packets[0])
#         diag_packets = quts_diag_service.getDataQueueItems(data_queue, 1, 20)
#     if has_calibration and calib_sensor:
#         post_biasvals = utils.imu_bias_values(productname, calib_sensor)
#         bias_result.append(post_biasvals)
#     if hdf_logging:
#         device = quts.get_device_handle(quts_dev_mgr)
#         diag_protocol = quts.get_diag_protocal_handle(quts_dev_mgr, device)
#         quts_dev_mgr.saveLogFilesWithFilenames({diag_protocol: hdflogfile})
#         result.update({'hdf': hdflogfile})
#     result['drv_log'] = drvlogfile
#
#     return result
#
#
# @pytest.fixture(autouse=True)
# def save_drv_msglog(collect_sscdrva_result):
#     yield
#     with open(collect_sscdrva_result['drv_log'], 'w', newline='') as f:
#         writer = csv.DictWriter(f, fieldnames=driver_msg_log_headers)
#         writer.writeheader()
#         for i, diag_packet in enumerate(collect_sscdrva_result['diag_packets_list']):
#             writer.writerow(
#                 dict(
#                     zip(
#                         driver_msg_log_headers,
#                         [
#                             diag_packet.receiveTimeString,
#                             diag_packet.packetName,
#                             diag_packet.summaryText,
#                         ],
#                     )
#                 )
#             )


@pytest.fixture(scope='session', autouse=True)
def isadmin():
    if utils.is_admin():
        return True
    else:
        pytest.exit("Please run this app as adminisitrator")


@pytest.fixture(scope='package', autouse=True)
def log_path(request):
    # log_path = request.config.getoption("--log_dir")
    product = request.config.getoption("--product")
    test_info = f'{product}_{utils.datetime_str()}'
    log_path = os.path.join(test_result_root_dir, test_info, 'log')
    os.makedirs(log_path, exist_ok=True)
    yield log_path
    # os.makedirs(default_report_dir, exist_ok=True)


# adb fixtures
@pytest.fixture(scope="session", autouse=True)
def adb():
    if not ADB.adb_devices():
        pytest.exit("No ADB devices found")
        # pytest.exit(ADB.adb_devices())
    adb = ADB()
    adb.adb_root()
    yield adb
    del adb


# ssc_drva fixtures
@pytest.fixture(scope="package")
def ssc_drva(adb):
    ssc_drva = SscDrvaTest(adb)
    yield ssc_drva
    del ssc_drva


@pytest.fixture(scope="package")
def quts_client():
    client = quts.quts_client("BST MEMS Sensor Driver Test")
    yield client
    client.stop()
    del client


@pytest.fixture(scope='package')
def quts_set_all_callbacks(quts_client):
    quts.set_all_callbacks(quts_client)


@pytest.fixture(scope='function')
def data_queue(quts_diag_service):
    queuename = 'data'
    error_code = quts.create_data_queue_for_monitoring(
        quts_diag_service, queue_name=queuename
    )
    if error_code != 0:
        pytest.exit("Error  creating data queue error code: {error_code}")
    # else:
    #     print("Data queue Created")
    yield queuename
    quts_diag_service.removeDataQueue(queuename)
    # del items


@pytest.fixture(scope="package", autouse=True)
def quts_dev_mgr(quts_client):
    dev_mgr = quts_client.getDeviceManager()
    return dev_mgr


@pytest.fixture(scope="package", autouse=True)
def quts_list_devices(quts_dev_mgr):
    device_list = quts_dev_mgr.getDeviceList()
    if not device_list:
        pytest.exit("No device found")


@pytest.fixture(scope="function", autouse=True)
def quts_list_services(quts_dev_mgr):
    services_list = quts_dev_mgr.getServicesList()
    if not services_list:
        pytest.exit("No service found")


@pytest.fixture(scope="package", autouse=True)
def quts_device_handle(quts_dev_mgr):
    device_handle = quts.get_device_handle(quts_dev_mgr)
    if not device_handle:
        pytest.exit("No Qualcomm USB Composite Device Found")
    yield device_handle
    del device_handle


@pytest.fixture(scope="package", autouse=True)
def quts_list_protocals(quts_dev_mgr, quts_device_handle):
    protocol_handle = None
    if not quts.get_diag_protocal_handle(quts_dev_mgr, quts_device_handle):
        pytest.exit("No Qualcomm USB Composite Protocal Found")
    yield protocol_handle
    del protocol_handle


@pytest.fixture(scope="package", autouse=True)
def quts_device_service(quts_client, quts_device_handle):
    dev_service = quts.device_service(quts_client, quts_device_handle)
    if not dev_service:
        pytest.exit("No Qualcomm USB Composite Device Found")
    dev_service.initializeService()

    yield dev_service

    dev_service.destroyService()
    del dev_service


@pytest.fixture(scope="package")
def quts_diag_service(quts_client, quts_device_handle):
    diag_service = quts.diagservice_client(quts_client, quts_device_handle)
    diag_service.initializeService()

    yield diag_service

    diag_service.destroyService()
    del diag_service


@pytest.fixture(scope="package", autouse=True)
def quts_load_config(quts_diag_service):
    with open(fdmc, 'rb') as f:
        quts_diag_service.setLoggingMask(f.read(), 2)  # 2 for dmc file
    if 0 != quts_diag_service:
        quts_diag_service.getLastError()


@pytest.fixture(scope='package')
def qseevt_app(check_protos, sensor_info_file):
    if not check_protos:
        pytest.exit(
            'No Protos imported for QSEEVT tool, please import .protos in QSEEVT'
        )
    seevt = qseevt.Qseevt(cfg.seevt_exe)
    seevt.run()
    seevt.enter_log_analysis_window()
    seevt.minimize()
    seevt.set_sensor_info_file_text(info_file=sensor_info_file)
    yield seevt

    seevt.close()
    del seevt


@pytest.fixture(scope='package')
def check_protos():
    if not os.path.exists(cfg.seevt_protos_dir) or not os.listdir(cfg.seevt_protos_dir):
        return False
    if not os.path.exists(r'C:\ProgramData\Qualcomm\Qualcomm_SEEVT\Protos.config'):
        return False
    return True


@pytest.fixture(scope='package', autouse=True)
def sensor_info_text(adb):
    text = adb.adb_sensor_info()
    if text:
        yield text
    else:
        pytest.exit('Cannot get ssc_sensor_info text')


@pytest.fixture(scope='package', autouse=True)
def sensor_info_file(sensor_info_text):
    filename = os.path.join(os.path.dirname(__file__), 'sensorinfo.txt')
    with open(filename, 'w') as f:
        f.write(sensor_info_text)
    yield filename
    os.remove(filename)


@pytest.fixture(scope='package', autouse=True)
def filter_sensorinfo_dict(sensor_info_text):
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
    yield sensor_info_list
    del sensor_info_list


@pytest.fixture(scope='package', autouse=True)
def sensor_registry(adb, request):
    productname = request.config.getoption("--product")
    platform = request.config.getoption("--platform")
    hw_ids = set()
    for sensor_info in sensor_info_list:
        hw_ids.add(sensor_info['HW_ID'])
    hw_ids = sorted(list(hw_ids))
    registries = {}
    for ihw in hw_ids:
        text = adb.adb_cat(
            rf'/vendor/etc/sensors/config/{cfg.platform_code[platform]}_hdk_{productname}_{ihw}.json'
        )
        ihw_reg = json.loads(text)
        if not ihw_reg:
            pytest.exit('cannot load the registry file from the system')
        registries.update({ihw: ihw_reg})
    yield registries
    del registries, ihw_reg


@pytest.fixture(scope='package')
def reset_origin_registry(adb, sensor_registry, request):
    yield
    platform = request.config.getoption("--platform")
    productname = request.config.getoption("--product")
    for ihw, registry in sensor_registry.items():
        reg_file_name = rf'./{cfg.platform_code[platform]}_hdk_{productname}_{ihw}.json'
        with open(reg_file_name, 'w') as f:
            json.dump(registry, f)
        adb.push_registry_file(reg_file_name)
        os.remove(reg_file_name)
    adb.adb_sync()
    adb.adb_reboot()
    adb.adb_root()
    print('origin registry reset')


@pytest.fixture()
def change_registry_res_value(adb, sensor_registry, request):
    """
    [
        {'accel': 1, 'gyro': 2,},
        {'accel': 2, 'gyro': 3,},
    ]
    :return:
    """
    platform = request.config.getoption("--platform")
    productname = request.config.getoption("--product")
    for ihw, registry in sensor_registry.items():
        new_regi = registry.copy()
        for sensor, res_val in request.param.items():
            if f'.{sensor}' in new_regi[f'{productname}_{ihw}']:
                new_regi[f'{productname}_{ihw}'][f'.{sensor}']['.config']['res_idx'][
                    'data'
                ] = str(res_val)
        reg_file_name = rf'./{cfg.platform_code[platform]}_hdk_{productname}_{ihw}.json'
        with open(reg_file_name, 'w') as f:
            json.dump(new_regi, f)
        adb.push_registry_file(reg_file_name)
        os.remove(reg_file_name)
    adb.adb_sync()
    adb.adb_reboot()
    adb.adb_root()
    yield
