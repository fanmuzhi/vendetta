## For detailed description of the QUTS APIs, please refer to QUTS documentation at "C:\Program Files (x86)\Qualcomm\QUTS\QUTS_User_Guide.docm"
##This sample includes connecting to device, using Diag, sending commands and collecting logs.
import os
import sys
import time
import re

##The path where QUTS files are installed
if sys.platform.startswith("linux"):
    sys.path.append('/opt/qcom/QUTS/Support/python')
elif sys.platform.startswith("win"):
    sys.path.append('/')
elif sys.platform.startswith("darwin"):
    sys.path.append('/Applications/Qualcomm/QUTS/QUTS.app/Contents/Support/python')
import QutsClient
import Common.ttypes
import DeviceConfigService.DeviceConfigService
import DeviceConfigService.constants
import DeviceConfigService.ttypes


import DiagService.DiagService
import DiagService.constants
import DiagService.ttypes


global handle
global diagService


def onMessage(level, location, title, description):
    print("Message Received " + title + " " + description)


def setNVData(devConfig):
    ##sets the NV item id 10 with value 21
    ##] DeviceConfigService.nvSetItem(nvItemIdOrName = 10, valueList = 0,21-CDMA And WLAN Only, subscriptionId = -1)
    errorCode = devConfig.nvSetItem("10", "0,21", -1)
    if errorCode != 0:
        print("  Error in set NV ", devConfig.getLastError())
    else:
        print("NV item set")


def getNVData(devConfig):
    try:
        nvItems = devConfig.nvGetAllItems()
        print("NV Item count ", len(nvItems))
        for x in range(1, 10):
            try:
                print(nvItems[x].id, " ", nvItems[x].name)
                print("def", devConfig.nvGetItemDefinition(nvItems[x].name))

                nvReturnObj = DeviceConfigService.ttypes.NvReturns()
                nvReturnObj.flags = DeviceConfigService.ttypes.NvReturnFlags.JSON_TEXT

                nvdata = devConfig.nvReadItem(nvItems[x].name, -1, 0, nvReturnObj)

                if nvdata == 'False':
                    devConfig.getLastError()
                    print("Couldn't read NV Item")
                else:
                    print("JSON data", nvdata.parsedJson, " Text ", nvdata.parsedText)
            except Exception as e:
                print("Exception in NV  ")
                print(str(e))

            print("-----------------------")

    except Exception as e:
        print("Exception in NV handling ")
        print(str(e))
        retValue = False
    finally:

        return True


def execTest(quts_client):

    ##QUTS sends messages on the what is going on in the system.
    quts_client.setOnMessageCallback(onMessage)

    ##Get a handle to the device Manager. Device manager has all the device related info.
    devManager = quts_client.getDeviceManager()

    deviceList = devManager.getDeviceList()
    ##gets the list of all the devices connected to the system

    print(
        "Device Details",
        " Serial Number ",
        deviceList[0].serialNumber,
        "  ",
        " Adb Serial Number ",
        deviceList[0].adbSerialNumber,
    )

    ##get the list of Qualcomm supported devices
    devices = quts_client.getDeviceManager().getDevicesForService(
        DeviceConfigService.constants.DEVICE_CONFIG_SERVICE_NAME
    )

    ##Get the list of devices connected to the PC that supports Diag.
    deviceList = devManager.getDevicesForService(
        DiagService.constants.DIAG_SERVICE_NAME
    )
    devConfig = DeviceConfigService.DeviceConfigService.Client(
        quts_client.createService(
            DeviceConfigService.constants.DEVICE_CONFIG_SERVICE_NAME, devices[0]
        )
    )
    if 0 != devConfig.initializeService():
        devConfig.getLastError()

    ##getNVData(devConfig)

    setNVData(devConfig)

    devConfig.destroyService()


if __name__ == "__main__":
    quts_client = QutsClient.QutsClient("NV Sample")
    execTest(quts_client)
