import sys
import time


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


#########################################################
deviceList = deviceManager.getDeviceList()
print("\n\nList of Devices: ")
for item in deviceList:
    if (-1 != item.description.find("Qualcomm")):
        deviceId = item.deviceHandle
    print(item)

print("deviceId = ", deviceId)


listOfProtocols = deviceManager.getProtocolList(deviceId)
print("\n\nList of Protocols: ")
for item in listOfProtocols:
    if (-1 != item.description.find("Diagnostics")):
        diagProtocol = item.protocolHandle
    print(item)

print("diagProtocol = ", diagProtocol)



protocolList = deviceManager.getProtocolList(deviceId)
print("Devices Location:")
for element in protocolList:
    print(element)



rawService = RawService.RawService.Client(
    client.createService(RawService.constants.RAW_SERVICE_NAME, deviceId))


rawService.initializeService(diagProtocol,3,3)

input = bytearray(b'\x80\x1F\x01\x80\x7B\x22\x63\x70\x22\x3A\x22\x34\x22\x2C\x22\x78\x69\x64\x22\x3A\x22\x33\x22\x7D\x00')
tid = rawService.sendRequestAsync(input)

response =  rawService.getResponseAsync(tid, 3000)
print("\n\nresponse 1 =  ", response)

response = rawService.getResponseAsync(tid, 3000)
print("\n\nresponse 2 =  ", response)


rawService.destroyService()

client.stop()

print("\n\n All Done \n\n")









