#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "conftest.py"
__version__ = "init"
__author__ = "@henry.fan"

# import contextlib
import os
# import sys
# import time
import pytest

# import yaml

import lib.seevt.seevt
# from lib.adb.adb import ADB
from lib.ssc_drva.ssc_drva import SscDrvaTest
from lib.quts.quts import *
from lib.seevt.seevt import Qseevt
from lib.sensor_file.sensor_file import FacCalBias
from lib.utils import *


@pytest.fixture(scope='session', autouse=True)
def isadmin():
    if is_admin():
        return True
    else:
        pytest.exit("Please run this app as adminisitrator")


# adb fixtures
@pytest.fixture(scope="session", autouse=True)
def adb():
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

# @pytest.fixture(scope="package")
# def ssc_drva_with_logging(generate_ssc_drva_hdf_log, ssc_drva, request):
#     param_sets = request.param
#     ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
#     ssc_drva.ssc_drva_run(ssc_drva_cmd)
#     return None


@pytest.fixture(scope='package')
def run_ssc_drva_test(ssc_drva, request):
    param_sets = request.param
    ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
    ssc_drva.ssc_drva_run(ssc_drva_cmd)
    return None


# quts fixtures
@pytest.fixture(scope="package")
def quts_client():
    client = QutsClient.QutsClient("QUTS Sample")
    yield client
    client.stop()
    del client


@pytest.fixture(scope='package')
def quts_set_all_callbacks(quts_client):
    set_all_callbacks(quts_client)


@pytest.fixture(scope='function')
def data_queue(quts_diag_service, request):
    print('#################', request)
    queuename = 'data'
    items = dict()
    items[Common.ttypes.DiagPacketType.LOG_PACKET] = log_packet_filter_item
    items[Common.ttypes.DiagPacketType.EVENT] = event_filter_item
    items[Common.ttypes.DiagPacketType.DEBUG_MSG] = debug_msg_filter_item
    error_code = create_data_queue_for_monitoring(quts_diag_service, items, queue_name=queuename)
    if error_code != 0:
        pytest.exit("Error  creating data queue error code: {error_code}")
    # else:
    #     print("Data queue Created")
    yield queuename
    quts_diag_service.removeDataQueue(queuename)
    del items


@pytest.fixture(scope="package", autouse=True)
def quts_dev_mgr(quts_client):
    dev_mgr = quts_client.getDeviceManager()
    return dev_mgr


@pytest.fixture(scope="package")
def quts_list_devices(quts_dev_mgr):
    device_list = quts_dev_mgr.getDeviceList()
    return device_list


@pytest.fixture(scope="function")
def quts_list_services(quts_dev_mgr):
    services_list = quts_dev_mgr.getServicesList()
    return services_list


@pytest.fixture(scope="package")
def quts_device_handle(quts_dev_mgr):
    device_handle = get_device_handle(quts_dev_mgr)
    if not device_handle:
        pytest.exit("No Qualcomm USB Composite Device Found")
    yield device_handle
    del device_handle


@pytest.fixture(scope="package")
def quts_list_protocals(quts_dev_mgr, quts_device_handle):
    protocol_handle = None
    if not get_diag_protocal_handle(quts_dev_mgr, quts_device_handle):
        pytest.exit("No Qualcomm USB Composite Device Found")
    yield protocol_handle
    del protocol_handle


@pytest.fixture(scope="package", autouse=True)
def quts_device_service(quts_client, quts_device_handle):
    dev_service = DeviceConfigService.DeviceConfigService.Client(
        quts_client.createService(
            DeviceConfigService.constants.DEVICE_CONFIG_SERVICE_NAME,
            quts_device_handle,
        )
    )
    dev_service.initializeService()

    yield dev_service

    dev_service.destroyService()
    del dev_service


@pytest.fixture(scope="package")
def quts_diag_service(quts_client, quts_device_handle):
    diag_service = DiagService.DiagService.Client(
        quts_client.createService(
            DiagService.constants.DIAG_SERVICE_NAME, quts_device_handle
        )
    )
    diag_service.initializeService()

    yield diag_service

    diag_service.destroyService()
    del diag_service


@pytest.fixture(scope="package", autouse=True)
def quts_load_config(quts_diag_service):
    with open(r'C:\Users\FNH1SGH\Desktop\mydmc.dmc', 'rb') as f:
        quts_diag_service.setLoggingMask(f.read(), 2)  # 2 for dmc file
    if 0 != quts_diag_service:
        quts_diag_service.getLastError()


@pytest.fixture(scope='function')
def generate_ssc_drva_hdf_log(quts_dev_mgr, ssc_drva, request):
    param_sets = request.param
    filename = rf"C:\temp\testlog\{datetime_str()}.hdf"
    ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
    with logging_diag_hdf(quts_dev_mgr, filename):
        ssc_drva.ssc_drva_run(ssc_drva_cmd)
    return filename


@pytest.fixture(scope='function')
def generate_ssc_drva_data_packet(
    quts_diag_service, ssc_drva, request
):
    param_sets = request.param
    queuename = 'data'
    ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
    with logging_data_queue(
        quts_diag_service, queuename
    ):
        ssc_drva.ssc_drva_run(ssc_drva_cmd)


# @pytest.fixture(scope='function')
# def generate_ssc_drva_hdf_and_data_packet(quts_dev_mgr, ssc_drva, request):
#     param_sets = request.param
#     ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
#     with logging_data_queue(quts_diag_service, "data", quts_diag_packet_filter, quts_return_obj_diag,):
#         ssc_drva.ssc_drva_run(ssc_drva_cmd)


# QSEEVT(qualcomm SEE verification tool) fixtures


@pytest.fixture(scope='package')
def qseevt(isadmin):
    seevt = Qseevt(lib.seevt.seevt.seevt_exe)
    seevt.run()
    seevt.enter_log_analysis_window()
    seevt.minimize()
    yield seevt

    seevt.close()
    del seevt


# @pytest.fixture(scope='package', autouse=True)
# def qseevt_init_analysis_window(qseevt):
#     qseevt.run()
#     qseevt.enter_log_analysis_window()
#     qseevt.set_sensor_info_file_text(
#         info_file=r"C:\Users\FNH1SGH\Desktop\bmi320_sensor_info.txt"
#     )
#     yield qseevt
#     qseevt.close()
#

# general test fixtures funcions

@pytest.fixture(scope='package', autouse=True)
def sensor_info_txt(adb):
    text = adb.adb_sensor_info()
    if text:
        filename = os.path.join(os.path.dirname(__file__), 'sensorinfo.txt')
        with open(filename, 'w') as f:
            f.write(text)
        yield filename
        os.remove(filename)
    else:
        pytest.exit('Cannot get ssc_sensor_info text')


def param_to_ids(param_sets):
    ids = []
    for param_set in param_sets:
        sensor0, samplerate0 = param_set[0]['sensor'], param_set[0]['sample_rate']
        id_str = f'{sensor0}-{samplerate0}'
        if len(param_set) >= 2:
            sensor1, samplerate1 = param_set[1]['sensor'], param_set[1]['sample_rate']

            id_str += f' {sensor1}-{samplerate1}'
        ids.append(id_str)
    return ids


@pytest.fixture(scope='function', ids=param_to_ids)
def param_sets(request):
    sensor_pair = request.param[0]
    sample_rate_pair = request.param[1]
    # duration = request.param.get('duration', 5)
    duration = (5, 5) if len(request.param) <= 2 else request.param[2]
    param_sets = []
    for i in range(len(sensor_pair)):
        param_i = {
                'sensor': sensor_pair[i],
                'sample_rate': sample_rate_pair[i],
                'duration': duration[i],
            }
        param_sets.append(param_i)
    yield param_sets


test_data = {
        'sensors': ['accel', 'gyro'],
        'sample_rates': [25, 50, 100, 200],
        'durations': [5]
    }


#
# @pytest.fixture(scope='function', params=test_data)
# def stream_data_csv_files(ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt, request):
#     print(request.param)
#     sensor = request.param['sensors']
#     sample_rate = request.param['sample_rates']
#     duration = request.param.get('duration', 5)
#     param_sets = (
#         {
#             'sensor': sensor,
#             'sample_rate': sample_rate,
#             'duration': duration},
#         None
#     )
#     csvs = collect_csvs(ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt, param_sets)
#     yield csvs
#     # filename = rf"C:\temp\testlog\{log_file_name(param_sets)}.hdf"
#     # ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
#     # with logging_diag_hdf(quts_dev_mgr, filename):
#     #     ssc_drva.ssc_drva_run(ssc_drva_cmd)
#     # qseevt.set_hdffile_text(filename)
#     # qseevt.set_sensor_info_file_text(
#     #     info_file=sensor_info_txt
#     # )
#     # qseevt.run_log_analysis()
#     # while not qseevt.analyze_complete():
#     #     time.sleep(0.1)
#     # parsed_folder = os.path.splitext(filename)[0]
#     # return collect_csvs(parsed_folder)


@pytest.fixture(scope='function')
def bias(request):
    param_sets = request.param
    sensor = param_sets[0].get('sensor')

    bias_folder = r'mnt/vendor/persist/sensors/registry/registry'
    productname = r'bmi3x0'
    biasfile = rf'{bias_folder}/{productname}_0_platform.{sensor}.fac_cal.bias'
    bias = FacCalBias(biasfile)
    # biasver_vals = bias.read_imu_bias_values(sensor)
    yield bias
    del bias, productname, sensor, bias_folder, biasfile


@pytest.fixture(scope='function')
def test_case_info():
    pass




