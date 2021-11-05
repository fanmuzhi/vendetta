import sys
import time
from dicttoxml import dicttoxml

if sys.platform.startswith("linux"):
    sys.path.append('/opt/qcom/QUTS/Support/python')
elif sys.platform.startswith("win"):
    sys.path.append('/')
elif sys.platform.startswith("darwin"):
    sys.path.append('/Applications/Qualcomm/QUTS/QUTS.app/Contents/Support/python')

import QutsClient
import Common.ttypes

import QmiService.QmiService
import QmiService.constants
import QmiService.ttypes

import AdbService.AdbService
import AdbService.constants
import AdbService.ttypes


def main():

    try:
        client = QutsClient.QutsClient("QUTS Sample")
    except Exception as e:
        client = None
        print("Exception starting client")

    if client is None:
        print('\nClient did not instantiate')
    else:
        print('\nInitialized Client')

    deviceManager = client.getDeviceManager()

    time.sleep(2)

    serviceList = deviceManager.getServicesList()
    print("\n\nList of Services: ", serviceList)

    deviceList = deviceManager.getDeviceList()
    print("\n\nDevices List: ")
    for element in deviceList:
        print(element)

    deviceId = 562949953421312

    protocolList = deviceManager.getProtocolList(deviceId)
    print("\n\nProtocol List:")
    for element in protocolList:
        print(element)

    adbService = AdbService.AdbService.Client(
        client.createService(AdbService.constants.ADB_SERVICE_NAME, deviceId)
    )

    adbProtocolHandle = 562958543355904
    adbService.initializeService()
    # adbService.initializeServiceByProtocol(adbProtocolHandle, 3, 3)

    # input_cmd = bytes('adb devices','utf-8')
    # input_cmd = "adb shell ssc_drva_test -sensor=pressure -duration=30 -sample_rate=-1"
    input_cmd = "adb shell"
    print("Get adb devices ")

    adbReturnConfig = Common.ttypes.AdbReturnConfig()
    adbReturnConfig.flags = (
        Common.ttypes.AdbReturnFlags.PACKET_TEXT
        | Common.ttypes.AdbReturnFlags.PROTOCOL_INDEX
        | Common.ttypes.AdbReturnFlags.RECEIVE_TIME_DATA
        | Common.ttypes.AdbReturnFlags.RECEIVE_TIME_STRING
        | Common.ttypes.AdbReturnFlags.SESSION_INDEX
    )

    response = adbService.sendCommand(input_cmd, adbReturnConfig, 10000)

    print("\n\nresponse =  ", response)

    print("\n\n Testing Async send/recv \n\n")

    tid = adbService.sendCommandAsync(input_cmd)

    status = adbService.isAsyncResponseFinished(tid)
    print("Async response finished? = ", status)

    responseAsyncAll = adbService.getAllResponsesAsync(tid, adbReturnConfig, 10000)
    print("\n\nAsync responses all =  ", responseAsyncAll)

    tid = adbService.sendCommandAsync(input_cmd)

    status = adbService.isAsyncResponseFinished(tid)
    print("Async response finished? = ", status)
    if not status:
        responseAsync = adbService.getResponseAsync(tid, adbReturnConfig, 10000)
        print("\n\nAsync response =  ", responseAsync)

    status = adbService.isAsyncResponseFinished(tid)
    print("Async response finished? = ", status)

    error = adbService.getLastError()
    device = adbService.getDevice()

    adbService.destroyService()
    print("error, device = ", error, device)

    print("\n\n All Done \n\n")

    time.sleep(2)


if __name__ == '__main__':
    main()
