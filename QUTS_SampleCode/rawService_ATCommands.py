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
    client = QutsClient.QutsClient("QUTS Raw Service AT Command Sample")
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
    if -1 != item.description.find("Qualcomm"):
        deviceId = item.deviceHandle
    print(item)

print("deviceId = ", deviceId)


listOfProtocols = deviceManager.getProtocolList(deviceId)
print("\n\nList of Protocols: ")
for item in listOfProtocols:
    if -1 != item.description.find("Modem"):
        print(
            "Found HS-USB Modem Protocol handle ",
            item.description,
            "Handle",
            item.protocolHandle,
        )
        unknownProtocol = item.protocolHandle
    print(item)

print("unknownProtocol = ", unknownProtocol)

deviceManager.overrideUnknownProtocol(
    unknownProtocol, Common.ttypes.ProtocolType.PROT_DUN
)

protocolList = deviceManager.getProtocolList(deviceId)
print("Devices Location:")
for element in protocolList:
    print(element)


rawService = RawService.RawService.Client(
    client.createService(RawService.constants.RAW_SERVICE_NAME, deviceId)
)


rawService.initializeService(unknownProtocol, 3, 3)


input = bytearray(b'ATI\r\n')

print("AT Command input:", input)

response = rawService.sendRequest(input, 2000)

print("AT Command Response:", response)

rawService.destroyService()

client.stop()

print("\n\n All Done \n\n")
