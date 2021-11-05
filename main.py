# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import sys
import time
import re

import lib.quts
# The path where QUTS files are installed


import QutsClient
import DeviceConfigService.DeviceConfigService
import DeviceConfigService.constants
# import Common.ttypes
import DiagService.DiagService
import DiagService.constants
# import DiagService

if __name__ == '__main__':
    quts_client = QutsClient.QutsClient("QUTSSampleClient")
    devManager = quts_client.getDeviceManager()
    print(f'Service list:\n {devManager.getServicesList()}')

    deviceList = devManager.getDeviceList()
    for dev in deviceList:
        if dev.vid == '05C6' and dev.pid == '901D':
            print(f"Device Details: Serial Number {dev.serialNumber} Adb Serial Number {dev.adbSerialNumber}")
            break
    else:
        print('No valid device found')
        sys.exit(1)

    devices = devManager.getDevicesForService(DiagService.constants.DIAG_SERVICE_NAME)
    print(devices)
    devConfig = DeviceConfigService.DeviceConfigService.Client(
        quts_client.createService(DeviceConfigService.constants.DEVICE_CONFIG_SERVICE_NAME, devices[0]))
    dev_service = devConfig.initializeService()
    diag_service = DiagService.DiagService.Client(
        quts_client.createService(DiagService.constants.DIAG_SERVICE_NAME, devices[0])
    )
    diag_service.initializeService()
    with open(r'C:\Users\FNH1SGH\Desktop\mydmc.dmc', 'rb') as f:
        diag_service.setLoggingMask(f.read(), 2)  # 2 for dmc file
    if 0 != dev_service:
        diag_service.getLastError()
    # devices = devManager.getDevicesForService(DiagService.constants.DIAG_SERVICE_NAME)
    diag_service.destroyService()
    print('Finished')
