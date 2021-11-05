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




doRun = 1

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

    deviceList = deviceManager.getDevicesForService(QmiService.constants.QMI_SERVICE_NAME)
    print("Devices List: ", deviceList)

    deviceId = 281474976710656

    protocolList = deviceManager.getProtocolList(deviceId)
    print("Devices Location:")
    for element in protocolList:
        print(element)



    rawService = RawService.RawService.Client(
        client.createService(RawService.constants.RAW_SERVICE_NAME, deviceId))

    diagHandle = 281492156579840
    rawService.initializeService(diagHandle,3,3)

    input = bytearray(b'\x29\x04\x00')
    response = rawService.sendRequest(input, 3000)

    print("\n\nresponse =  ", response)
    print("\n\n All Done \n\n")

    time.sleep(2)

if __name__ == '__main__':
    main()



