import sys
import sys
import os
import time

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
import AdbService.AdbService
import AdbService.constants
import AdbService.ttypes


def getAdbService(client, device, protocol):
    ##print (protocol.protocolHandle)
    adbService = AdbService.AdbService.Client(
        client.createService(AdbService.constants.ADB_SERVICE_NAME, device)
    )
    if (
        0 != adbService.initializeService()
    ):  ##protocol.protocolHandle, Common.OpenProp.Read,Common.OpenProp.Read )):
        print("ADB init failed  ", adbService.getLastError())

    return adbService


def main(client):
    qutsLogFileFolder = "C:\\temp\\testlog"

    print("test started")
    devManager = client.getDeviceManager()
    deviceList = devManager.getDeviceList()
    if len(deviceList) == 0:
        ## wait for QUTS to get the list of devices.
        time.sleep(5)
        deviceList = devManager.getDeviceList()

    devices = devManager.getDevicesForService(AdbService.constants.ADB_SERVICE_NAME)
    ##print(devices)
    devManager.startLogging()
    ##print("Got device manager")
    protocolList = devManager.getProtocolList(devices[0])
    ##print(protocolList)
    for protocol in protocolList:
        ##print(protocol.protocolType)
        ##print(protocol.description)
        if protocol.protocolType == Common.ttypes.ProtocolType.PROT_ADB:

            adbService = getAdbService(client, devices[0], protocol)

            input = "adb devices"
            print("Get adb devices ")
            ##specify the values interested in
            returnObj = Common.ttypes.AdbReturnConfig()
            returnObj.flags = (
                Common.ttypes.AdbReturnFlags.PACKET_TEXT
                | Common.ttypes.AdbReturnFlags.RECEIVE_TIME_STRING
            )

            response = adbService.sendCommand(input, returnObj, 10000)
            print(
                "\n\nresponse =  ",
                response.packetText,
                "  received at ",
                response.receiveTimeString,
            )
            devManager.saveLogFiles(qutsLogFileFolder)
            adbService.destroyService()


if __name__ == '__main__':
    try:
        client = QutsClient.QutsClient("ADBServiceTest")

    except Exception as e:
        print("Exception starting client")
    main(client)
