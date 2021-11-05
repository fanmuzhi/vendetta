#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "conftest.py"
__version__ = "init"
__author__ = "@henry.fan"

import contextlib
import os
import time
import pytest
import yaml

from lib.adb.adb import ADB
from lib.ssc_drva.ssc_drva import SscDrvaTest
from lib.quts.quts import *

# myadb = ADB()


# adb fixtures
@pytest.fixture(scope="session")
def adb():
    adb = ADB()
    yield adb
    del adb


@pytest.fixture(scope='session')
def adb_root(adb):
    adb.adb_root()


@pytest.fixture(scope='session')
def adb_devices():
    adb.adb_devices()


# ssc_drva fixtures
@pytest.fixture(scope="session")
def ssc_drva(adb):
    ssc_drva = SscDrvaTest(adb)
    yield ssc_drva
    del ssc_drva


# @pytest.fixture()
# def assemble_drva_cmd(ssc_drva, param_sets):
#     return ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)


@pytest.fixture(scope="function")
def ssc_drva_with_logging(generate_ssc_drva_hdf_log, ssc_drva, request):
    param_sets = request.param
    ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
    ssc_drva.ssc_drva_run(ssc_drva_cmd)
    return None


@pytest.fixture(scope='function')
def run_ssc_drva_test(ssc_drva, request):
    param_sets = request.param
    ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
    ssc_drva.ssc_drva_run(ssc_drva_cmd)
    return None


# quts fixtures
@pytest.fixture(scope="session")
def quts_client():
    client = QutsClient.QutsClient("QUTS Sample")
    yield client
    client.stop()
    del client


@pytest.fixture(scope='session')
def quts_set_all_callbacks(quts_client):
    set_all_callbacks(quts_client)


@pytest.fixture(scope="session")
def quts_diag_packet_filter():
    diag_packet_filter = Common.ttypes.DiagPacketFilter()
    diag_packet_filter.idOrNameMask = {}
    yield diag_packet_filter
    del diag_packet_filter


@pytest.fixture(scope="session", autouse=True)
def quts_init_diag_packet_filter_by_name_or_mask(quts_diag_packet_filter):
    quts_diag_packet_filter.idOrNameMask[Common.ttypes.DiagPacketType.LOG_PACKET] = log_packet_filter_items
    quts_diag_packet_filter.idOrNameMask[Common.ttypes.DiagPacketType.EVENT] = even_filter_items
    quts_diag_packet_filter.idOrNameMask[Common.ttypes.DiagPacketType.DEBUG_MSG] = debug_filter_items


@pytest.fixture(scope='session')
def quts_return_obj_diag():
    diag_return_obj = Common.ttypes.DiagReturnConfig()
    yield diag_return_obj
    del diag_return_obj


@pytest.fixture(scope='session', autouse=True)
def quts_init_diag_return_obj_flags(quts_return_obj_diag):
    quts_return_obj_diag.flags = (
            Common.ttypes.DiagReturnFlags.PARSED_TEXT
            | Common.ttypes.DiagReturnFlags.PACKET_NAME
            | Common.ttypes.DiagReturnFlags.PACKET_ID
            | Common.ttypes.DiagReturnFlags.PACKET_TYPE
            | Common.ttypes.DiagReturnFlags.SUBSCRIPTION_ID
            | Common.ttypes.DiagReturnFlags.SUMMARY_TEXT
    )


@pytest.fixture(scope="session", autouse=True)
def quts_dev_mgr(quts_client):
    dev_mgr = quts_client.getDeviceManager()
    return dev_mgr


@pytest.fixture(scope="session")
def quts_list_devices(quts_dev_mgr):
    device_list = quts_dev_mgr.getDeviceList()
    return device_list


@pytest.fixture(scope="function")
def quts_list_services(quts_dev_mgr):
    services_list = quts_dev_mgr.getServicesList()
    return services_list


@pytest.fixture(scope="function")
def quts_list_protocals(quts_dev_mgr):
    protocals = quts_dev_mgr.getServicesList()
    return protocals


@pytest.fixture(scope="session")
def quts_device_for_service(quts_dev_mgr):
    handle_list = quts_dev_mgr.getDevicesForService(DiagService.constants.DIAG_SERVICE_NAME)
    device_handle = handle_list[0]
    return device_handle


@pytest.fixture(scope="session", autouse=True)
def quts_device_service(quts_client, quts_device_for_service):
    dev_service = DeviceConfigService.DeviceConfigService.Client(
        quts_client.createService(DeviceConfigService.constants.DEVICE_CONFIG_SERVICE_NAME, quts_device_for_service))
    dev_service.initializeService()

    yield dev_service

    dev_service.destroyService()
    del dev_service


@pytest.fixture(scope="session")
def quts_diag_service(quts_client, quts_device_for_service):
    diag_service = DiagService.DiagService.Client(
        quts_client.createService(DiagService.constants.DIAG_SERVICE_NAME, quts_device_for_service)
    )
    diag_service.initializeService()

    yield diag_service

    diag_service.destroyService()
    del diag_service


@pytest.fixture(scope="session", autouse=True)
def quts_load_config(quts_diag_service):
    with open(r'C:\Users\FNH1SGH\Desktop\mydmc.dmc', 'rb') as f:
        quts_diag_service.setLoggingMask(f.read(), 2)  # 2 for dmc file
    if 0 != quts_diag_service:
        quts_diag_service.getLastError()


@pytest.fixture(scope="function")
def quts_start_logging(quts_dev_mgr):
    quts_dev_mgr.startLogging()


@pytest.fixture(scope='function')
def quts_save_log_files(quts_dev_mgr, request):
    foldername = request.param
    quts_dev_mgr.saveLogFiles(foldername)


@pytest.fixture(scope='function')
def generate_ssc_drva_hdf_log(quts_dev_mgr, ssc_drva, request):
    param_sets = request.param
    foldername = "C:\\temp\\testlog"
    ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
    with hdf_logging(quts_dev_mgr, foldername):
        ssc_drva.ssc_drva_run(ssc_drva_cmd)


@pytest.fixture(scope='function')
def generate_ssc_drva_data_packet(quts_diag_service, quts_diag_packet_filter, quts_return_obj_diag, ssc_drva, request):
    param_sets = request.param
    queuename = 'data'
    ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
    with data_queue_logging(quts_diag_service, queuename, quts_diag_packet_filter, quts_return_obj_diag):
        ssc_drva.ssc_drva_run(ssc_drva_cmd)

# @pytest.fixture(scope='function')
# def generate_ssc_drva_hdf_and_data_packet(quts_dev_mgr, ssc_drva, request):
#     param_sets = request.param
#     ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
#     with data_queue_logging(quts_diag_service, "data", quts_diag_packet_filter, quts_return_obj_diag,):
#         ssc_drva.ssc_drva_run(ssc_drva_cmd)