#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "quts"
__version__ = "init"
__author__ = "@henry.fan"

import sys
import contextlib

# The path where QUTS files are installed
quts_path = ''
if sys.platform.startswith("linux"):
    quts_path = '/opt/qcom/QUTS/Support/python'
elif sys.platform.startswith("win"):
    quts_path = r'C:\Program Files (x86)\Qualcomm\QUTS\Support\python'
elif sys.platform.startswith("darwin"):
    quts_path = '/Applications/Qualcomm/QUTS/QUTS.app/Contents/Support/python'
if quts_path and quts_path not in sys.path:
    sys.path.append(quts_path)


import QutsClient
import Common.ttypes
import DeviceConfigService.DeviceConfigService
import DeviceConfigService.constants

# import DeviceManager.DeviceManager
import DeviceManager.constants
import DiagService.DiagService
import DiagService.constants


cur_txt = r'C:\Users\FNH1SGH\Desktop\a.txt'
log_packet_filter_item = [
    "0x19c5",
    "0x19c6",
    "0x19c7",
    "0x19c8",
    "0x19c9",
    "0x19cb",
    "0x19cc",
    "0x19cd",
    "0x19d6",
    "0x19d8",
]
event_filter_item = [
    "1952",
    "289",
    "321",
]

debug_msg_filter_item = [
    "53/0",
    "53/1",
    "53/2",
    "53/3",
    "53/4",
    "122/0",
    "122/1",
    "122/2",
    "122/3",
    "122/4",
    "123/0",
    "123/1",
    "123/2",
    "123/3",
    "123/4",
    "124/0",
    "124/1",
    "124/2",
    "124/3",
    "124/4",
    "125/0",
    "125/1",
    "125/2",
    "125/3",
    "125/4",
]


def on_message(level, location, title, description):
    print(f"Message Received {level, location, title, description}")


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


def on_logsession_missing_qshrink_hash_file():
    pass


def on_async_response():
    pass


def on_data_queue_updated(queue_name, queue_size):
    print("QueueName = ", queue_name, ", current queueSize = ", queue_size)
    # global cur_txt
    # with open(cur_txt, 'a') as f:
    #     diagPackets = DiagService.DiagService.getDataQueueItems("data", 1, 10)
    #     f.write(diagPackets[0].__dict__)


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


def quts_client(name):
    return QutsClient.QutsClient(name)


def device_service(quts_client_obj, quts_device_handle):
    return DeviceConfigService.DeviceConfigService.Client(
        quts_client_obj.createService(
            DeviceConfigService.constants.DEVICE_CONFIG_SERVICE_NAME,
            quts_device_handle,
        )
    )


def diagservice_client(quts_client_obj, quts_device_handle):
    return DiagService.DiagService.Client(
        quts_client_obj.createService(
            DiagService.constants.DIAG_SERVICE_NAME, quts_device_handle
        )
    )


def set_all_callbacks(quts_client_obj):
    quts_client_obj.setOnMessageCallback(on_message)
    quts_client_obj.setOnDeviceConnectedCallback(on_device_connected)
    quts_client_obj.setOnDeviceDisconnectedCallback(on_device_disconnected)
    quts_client_obj.setOnDeviceModeChangeCallback(on_device_mode_change)
    quts_client_obj.setOnProtocolAddedCallback(on_protocol_added)
    quts_client_obj.setOnProtocolRemovedCallback(on_protocol_removed)
    quts_client_obj.setOnProtocolStateChangeCallback(on_protocol_state_change)
    # quts_client_obj.setOnProtocolFlowControlStatusChangeCallback()
    # quts_client_obj.setOnProtocolLockStatusChangeCallback()
    # quts_client_obj.setOnProtocolMbnDownloadStatusChangeCallback()
    # quts_client_obj.setOnClientCloseRequestCallback()
    quts_client_obj.setOnMissingQShrinkHashFileCallback(on_missing_qshrink_hash_file)
    quts_client_obj.setOnLogSessionMissingQShrinkHashFileCallback(
        on_logsession_missing_qshrink_hash_file
    )
    quts_client_obj.setOnAsyncResponseCallback(on_async_response)
    quts_client_obj.setOnDataQueueUpdatedCallback(on_data_queue_updated)
    quts_client_obj.setOnDataViewUpdatedCallback(on_data_view_updated)
    quts_client_obj.setOnServiceAvailableCallback(on_service_available)
    quts_client_obj.setOnServiceEndedCallback(on_service_ended)
    quts_client_obj.setOnServiceEventCallback(on_service_event)
    quts_client_obj.setOnQShrinkStateUpdated(on_qshrink_state_updated)
    # quts_client.setOnDecryptionKeyStatusUpdateCallback()
    quts_client_obj.setOnLogSessionDecryptionKeyStatusUpdateCallback(
        on_logsession_missing_qshrink_hash_file
    )


def get_device_handle(device_manager):
    device_handle = None
    # handle_list = device_manager.getDevicesForService(DiagService.constants.DIAG_SERVICE_NAME)
    for item in device_manager.getDeviceList():
        if "Qualcomm USB Composite Device" in item.description:
            device_handle = item.deviceHandle
            break
    return device_handle


def get_diag_protocal_handle(device_manager, device_handle):
    protocol_handle = None
    list_of_protocols = device_manager.getProtocolList(device_handle)
    for item in list_of_protocols:
        if "Qualcomm HS-USB Android DIAG" in item.description:
            protocol_handle = item.protocolHandle
            break
    return protocol_handle


def create_filters(all_filters):
    diag_packet_filter = Common.ttypes.DiagPacketFilter()
    diag_packet_filter.idOrNameMask = {}
    for packetType in all_filters:
        list_of_id = []
        for item_id in all_filters[packetType]:  # for string value create a IdOrName
            list_of_id.append(Common.ttypes.DiagIdFilterItem(idOrName=item_id))
        diag_packet_filter.idOrNameMask[packetType] = list_of_id
    return diag_packet_filter


def create_data_queue_for_monitoring(diag_service, queue_name):
    #  Create a data Queue. Reading will be done in the callback.
    all_filters = dict()
    all_filters[Common.ttypes.DiagPacketType.LOG_PACKET] = log_packet_filter_item
    all_filters[Common.ttypes.DiagPacketType.EVENT] = event_filter_item
    all_filters[Common.ttypes.DiagPacketType.DEBUG_MSG] = debug_msg_filter_item
    diag_packet_filter = create_filters(all_filters)

    return_obj_diag = Common.ttypes.DiagReturnConfig()
    return_obj_diag.flags = (
        0
        | Common.ttypes.DiagReturnFlags.PARSED_TEXT
        | Common.ttypes.DiagReturnFlags.PACKET_NAME
        | Common.ttypes.DiagReturnFlags.PACKET_ID
        | Common.ttypes.DiagReturnFlags.PACKET_TYPE
        | Common.ttypes.DiagReturnFlags.TIME_STAMP_STRING
        | Common.ttypes.DiagReturnFlags.RECEIVE_TIME_STRING
        | Common.ttypes.DiagReturnFlags.SUMMARY_TEXT
    )

    error_code = diag_service.createDataQueue(
        queue_name, diag_packet_filter, return_obj_diag
    )
    return error_code


def update_filters_to_queue(diag_service, all_filters, queue_name, add_or_remove):
    diag_packet_filter = create_filters(all_filters)
    if add_or_remove == "add":
        print("Adding above filter")
        error_code = diag_service.addDataQueueFilter(queue_name, diag_packet_filter)
    else:
        print("Removing above filter")
        error_code = diag_service.removeDataQueueFilter(queue_name, diag_packet_filter)
    if error_code != 0:
        print("Error  updating data queue", error_code)
    else:
        print("Data queue updated with " + add_or_remove)


@contextlib.contextmanager
def logging_diag_hdf(dev_mgr: DeviceManager.DeviceManager.Client, hdf_file):
    dev_mgr.startLogging()
    yield
    device = get_device_handle(dev_mgr)
    diag_protocol = get_diag_protocal_handle(dev_mgr, device)
    dev_mgr.saveLogFilesWithFilenames({diag_protocol: hdf_file})


@contextlib.contextmanager
def logging_data_queue(
    diag_service, queue_name, count=300000, timeout=20,
):
    items = dict()
    items[Common.ttypes.DiagPacketType.LOG_PACKET] = log_packet_filter_item
    items[Common.ttypes.DiagPacketType.EVENT] = event_filter_item
    items[Common.ttypes.DiagPacketType.DEBUG_MSG] = debug_msg_filter_item
    # create_data_queue_for_monitoring(diag_service, items, 'data')
    # diag_service.createDataQueue(queue_name, diag_packet_filter, return_obj_diag)
    diag_packets = diag_service.getDataQueueItems(queue_name, count, timeout)
    yield diag_packets
    # for diag_packet in diag_packets:
    #     if diag_packet.packetId == '125/1':
    #         print(diag_packet.summaryText)

    # diag_service.removeDataQueue(queue_name)


if __name__ == "__main__":
    pass
