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
from lib.adb.adb import ADB
from lib.ssc_drva.ssc_drva import SscDrvaTest
from lib.quts.quts import *
from lib.seevt.seevt import Qseevt
from lib.utils import *

# myadb = ADB()

# common fixtures


@pytest.fixture(scope='session')
def isadmin():
    if is_admin():
        return True
    else:
        pytest.exit("please run this app as adminisitrator")


# adb fixtures
@pytest.fixture(scope="package")
def adb():
    adb = ADB()
    yield adb
    del adb


@pytest.fixture(scope='package')
def adb_root(adb):
    adb.adb_root()


@pytest.fixture(scope='package')
def adb_devices():
    adb.adb_devices()


# ssc_drva fixtures
@pytest.fixture(scope="package")
def ssc_drva(adb):
    ssc_drva = SscDrvaTest(adb)
    yield ssc_drva
    del ssc_drva


# @pytest.fixture()
# def aseemble_drva_cmd(ssc_drva, param_sets):
#     return ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)


@pytest.fixture(scope="package")
def ssc_drva_with_logging(generate_ssc_drva_hdf_log, ssc_drva, request):
    param_sets = request.param
    ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
    ssc_drva.ssc_drva_run(ssc_drva_cmd)
    return None


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


#
# @pytest.fixture(scope="package")
# def quts_diag_packet_filter():
#     diag_packet_filter = Common.ttypes.DiagPacketFilter()
#     diag_packet_filter.idOrNameMask = {}
#     yield diag_packet_filter
#     del diag_packet_filter
#
#
# @pytest.fixture(scope="package", autouse=True)
# def quts_init_diag_packet_filter_by_name_or_mask(quts_diag_packet_filter):
#     quts_diag_packet_filter.idOrNameMask[Common.ttypes.DiagPacketType.LOG_PACKET] = log_packet_filter_items
#     quts_diag_packet_filter.idOrNameMask[Common.ttypes.DiagPacketType.EVENT] = event_filter_items
#     quts_diag_packet_filter.idOrNameMask[Common.ttypes.DiagPacketType.DEBUG_MSG] = debug_filter_items
#
#
# @pytest.fixture(scope='package')
# def quts_return_obj_diag():
#     diag_return_obj = Common.ttypes.DiagReturnConfig()
#     yield diag_return_obj
#     del diag_return_obj
#
#
# @pytest.fixture(scope='package', autouse=True)
# def quts_init_diag_return_obj_flags(quts_return_obj_diag):
#     quts_return_obj_diag.flags = (
#             Common.ttypes.DiagReturnFlags.PARSED_TEXT
#             | Common.ttypes.DiagReturnFlags.PACKET_NAME
#             | Common.ttypes.DiagReturnFlags.PACKET_ID
#             | Common.ttypes.DiagReturnFlags.PACKET_TYPE
#             | Common.ttypes.DiagReturnFlags.SUBSCRIPTION_ID
#             | Common.ttypes.DiagReturnFlags.SUMMARY_TEXT
#     )


@pytest.fixture(scope='module')
def data_queue_for_monitoring(quts_diag_service, queuename="data"):
    items = {}
    items[Common.ttypes.DiagPacketType.LOG_PACKET] = log_packet_filter_item
    items[Common.ttypes.DiagPacketType.EVENT] = event_filter_item
    items[Common.ttypes.DiagPacketType.DEBUG_MSG] = debug_msg_filter_item
    create_data_queue_for_monitoring(quts_diag_service, items, queue_name=queuename)
    yield
    quts_diag_service.removeDataQueue(queuename)


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

    yield seevt

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

# stream test fixtures funcions
@pytest.fixture(scope='function')
def collect_stream_data_files(ssc_drva, quts_dev_mgr, qseevt, request):
    param_sets = request.param
    filename = rf"C:\temp\testlog\{datetime_str()}.hdf"
    ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
    with logging_diag_hdf(quts_dev_mgr, filename):
        ssc_drva.ssc_drva_run(ssc_drva_cmd)
    qseevt.set_hdffile_text(filename)
    qseevt.set_sensor_info_file_text(
        info_file=r"C:\Users\FNH1SGH\Desktop\bmi320_sensor_info.txt"
    )
    qseevt.run_log_analysis()
    while not qseevt.analyze_complete():
        time.sleep(0.1)

    return os.path.splitext(filename)[0]




