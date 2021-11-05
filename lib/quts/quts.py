#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "quts"
__version__ = "init"
__author__ = "@henry.fan"

import contextlib
import sys
import time

# The path where QUTS files are installed
if sys.platform.startswith("linux"):
    sys.path.append('/opt/qcom/QUTS/Support/python')
elif sys.platform.startswith("win"):
    sys.path.append(r'C:\Program Files (x86)\Qualcomm\QUTS\Support\python')
elif sys.platform.startswith("darwin"):
    sys.path.append('/Applications/Qualcomm/QUTS/QUTS.app/Contents/Support/python')


import QutsClient
import Common.ttypes

import DeviceConfigService.DeviceConfigService
import DeviceConfigService.constants
import DeviceManager.DeviceManager
import DiagService.DiagService
import DiagService.constants

cur_txt = r'C:\Users\FNH1SGH\Desktop\a.txt'

log_packet_filter_items = [
    Common.ttypes.DiagIdFilterItem(idOrName="0x19c5"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19c6"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19c7"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19c8"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19c9"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19cb"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19cc"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19cd"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19d6"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19d8"),
]

even_filter_items = [
    Common.ttypes.DiagIdFilterItem(idOrName="1952"),
    Common.ttypes.DiagIdFilterItem(idOrName="289"),
    Common.ttypes.DiagIdFilterItem(idOrName="321"),
]

debug_filter_items = [
    Common.ttypes.DiagIdFilterItem(idOrName="53/0"),
    Common.ttypes.DiagIdFilterItem(idOrName="53/1"),
    Common.ttypes.DiagIdFilterItem(idOrName="53/2"),
    Common.ttypes.DiagIdFilterItem(idOrName="53/3"),
    Common.ttypes.DiagIdFilterItem(idOrName="53/4"),
    Common.ttypes.DiagIdFilterItem(idOrName="122/0"),
    Common.ttypes.DiagIdFilterItem(idOrName="122/1"),
    Common.ttypes.DiagIdFilterItem(idOrName="122/2"),
    Common.ttypes.DiagIdFilterItem(idOrName="122/3"),
    Common.ttypes.DiagIdFilterItem(idOrName="122/4"),
    Common.ttypes.DiagIdFilterItem(idOrName="123/0"),
    Common.ttypes.DiagIdFilterItem(idOrName="123/1"),
    Common.ttypes.DiagIdFilterItem(idOrName="123/2"),
    Common.ttypes.DiagIdFilterItem(idOrName="123/3"),
    Common.ttypes.DiagIdFilterItem(idOrName="123/4"),
    Common.ttypes.DiagIdFilterItem(idOrName="124/0"),
    Common.ttypes.DiagIdFilterItem(idOrName="124/1"),
    Common.ttypes.DiagIdFilterItem(idOrName="124/2"),
    Common.ttypes.DiagIdFilterItem(idOrName="124/3"),
    Common.ttypes.DiagIdFilterItem(idOrName="124/4"),
    Common.ttypes.DiagIdFilterItem(idOrName="125/0"),
    Common.ttypes.DiagIdFilterItem(idOrName="125/1"),
    Common.ttypes.DiagIdFilterItem(idOrName="125/2"),
    Common.ttypes.DiagIdFilterItem(idOrName="125/3"),
    Common.ttypes.DiagIdFilterItem(idOrName="125/4"),
]


def on_message():
    pass


def on_device_connected():
    pass


def on_device_disconnected():
    pass


def on_device_mode_change():
    pass


def on_protocol_added():
    pass


def on_protocol_removed():
    pass


def on_protocol_state_change():
    pass


def on_missing_qshrink_hash_file():
    pass


def on_logsession_missing_qshrink_hash_File():
    pass


def on_async_response():
    pass


def on_data_queue_updated(queue_name, queue_size):
    print("queueName = ", queue_name, ", current queueSize = ", queue_size)
    global cur_txt
    with open(cur_txt, 'a') as f:
        diagPackets = DiagService.DiagService.getDataQueueItems("data", 1, 10)
        f.write(diagPackets[0].__dict__)


def on_data_view_updated():
    pass


def on_service_available():
    pass


def on_service_ended():
    pass


def on_service_event():
    pass


def on_qshrink_state_updated():
    pass


def set_all_callbacks(quts_client):
    quts_client.setOnMessageCallback(on_message)
    quts_client.setOnDeviceConnectedCallback(on_device_connected)
    quts_client.setOnDeviceDisconnectedCallback(on_device_disconnected)
    quts_client.setOnDeviceModeChangeCallback(on_device_mode_change)
    quts_client.setOnProtocolAddedCallback(on_protocol_added)
    quts_client.setOnProtocolRemovedCallback(on_protocol_removed)
    quts_client.setOnProtocolStateChangeCallback(on_protocol_state_change)
    # quts_client.setOnProtocolFlowControlStatusChangeCallback()
    # quts_client.setOnProtocolLockStatusChangeCallback()
    # quts_client.setOnProtocolMbnDownloadStatusChangeCallback()
    # quts_client.setOnClientCloseRequestCallback()
    quts_client.setOnMissingQShrinkHashFileCallback(on_missing_qshrink_hash_file)
    quts_client.setOnLogSessionMissingQShrinkHashFileCallback(on_logsession_missing_qshrink_hash_File)
    quts_client.setOnAsyncResponseCallback(on_async_response)
    quts_client.setOnDataQueueUpdatedCallback(on_data_queue_updated)
    quts_client.setOnDataViewUpdatedCallback(on_data_view_updated)
    quts_client.setOnServiceAvailableCallback(on_service_available)
    quts_client.setOnServiceEndedCallback(on_service_ended)
    quts_client.setOnServiceEventCallback(on_service_event)
    quts_client.setOnQShrinkStateUpdated(on_qshrink_state_updated)
    # quts_client.setOnDecryptionKeyStatusUpdateCallback()
    quts_client.setOnLogSessionDecryptionKeyStatusUpdateCallback(on_logsession_missing_qshrink_hash_File)


@contextlib.contextmanager
def hdf_logging(quts_dev_mgr: DeviceManager.DeviceManager.Client, foldername):
    quts_dev_mgr.startLogging()
    yield
    quts_dev_mgr.saveLogFiles(foldername)


@contextlib.contextmanager
def data_queue_logging(
    diag_service,
    queue_name,
    diag_packet_filter,
    return_obj_diag,
    count=300000,
    timeout=200,
):
    diag_service.createDataQueue(queue_name, diag_packet_filter, return_obj_diag)
    yield
    diag_packets = diag_service.getDataQueueItems(queue_name, count, timeout)
    # for diag_packet in diag_packets:
    #     if diag_packet.packetId == '125/1':
    #         print(diag_packet.summaryText)

    diag_service.removeDataQueue(queue_name)


# class Quts(object):
#
#     def __init__(self):
#         # try:
#         self.client = None
#         self.dev_manager = None
#         # self.init_client()
#         # self.dev_manager = self.device_manager()
#         # self.device_handle = self.get_device_for_service(DiagService.constants.DIAG_SERVICE_NAME)[0]
#
#         self.setup_callbacks()
#         # except Exception as e:
#         #     print(e)
#
#     def init_client(self):
#         try:
#             self.client = QutsClient.QutsClient("QUTS Sample")
#         except Exception as e:
#             print(e)
#
#     def device_manager(self):
#         self.client.getDeviceManager()
#         time.sleep(1)
#
#     def list_devices(self):
#         return self.dev_manager.getDeviceList()
#
#     def list_services(self):
#         return self.dev_manager.getServicesList()
#
#     def list_protocals(self, device_id):
#         return self.dev_manager.getProtocolList(device_id)
#
#     def get_device_for_service(self, service_name):
#         return self.dev_manager.getDevicesForService(service_name)
#
#     def init_dev_service(self, device_handle):
#         dev_config = DeviceConfigService.DeviceConfigService.Client(
#             self.client.createService(DeviceConfigService.constants.DEVICE_CONFIG_SERVICE_NAME, device_handle))
#         dev_service = dev_config.initializeService()
#         return dev_service
#
#     def init_diag_service(self, device_handle, diag_protocal_handle=None):
#         diag_service = DiagService.DiagService.Client(
#             self.client.createService(DiagService.constants.DIAG_SERVICE_NAME, device_handle)
#         )
#         if not diag_protocal_handle:
#             diag_service.initializeService()
#         else:
#             diag_service.initializeServiceByProtocol(diag_protocal_handle)
#         return diag_service
#
#     def setup_callbacks(self):
#         self.client.setOnDataQueueUpdatedCallback(on_data_queue_callback)
#
#     def stop_quts_client(self):
#         self.client.stop()


# client = init_quts_client()
# client.setOnDataQueueUpdatedCallback(on_data_queue_callback)
if __name__ == "__main__":
    quts_obj = Quts()
    services = quts_obj.list_services()
    print(services)
