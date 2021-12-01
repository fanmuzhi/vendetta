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

import RawService.RawService
import RawService.constants
import RawService.ttypes

import binascii


def main():

    try:
        client = QutsClient.QutsClient("QUTS Sample")
    except Exception as e:
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

    deviceId = 281474976710656

    protocolList = deviceManager.getProtocolList(deviceId)
    print("\n\nProtocol List:")
    for element in protocolList:
        print(element)

    rawService = RawService.RawService.Client(
        client.createService(RawService.constants.RAW_SERVICE_NAME, deviceId)
    )

    diagHandle = 281496451547136
    adbProtocolHandle = 281509336449024
    rawService.initializeService(adbProtocolHandle, 3, 3)

    input = bytes('adb devices', 'utf-8')
    print("Get adb devices ")

    response = rawService.sendRequest(input, 10000)

    print("\n\nresponse =  ", response)
    print("\n\n All Done \n\n")

    time.sleep(2)


if __name__ == '__main__':
    main()
