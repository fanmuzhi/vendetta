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

import DiagService.DiagService
import DiagService.constants
import DiagService.ttypes

import LogSession.LogSession
import LogSession.constants
import LogSession.ttypes

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
    if -1 != item.description.find("Qualcomm"):
        deviceId = item.deviceHandle
    print(item)

print("deviceId = ", deviceId)


listOfProtocols = deviceManager.getProtocolList(deviceId)
print("\n\nList of Protocols: ")
for item in listOfProtocols:
    if -1 != item.description.find("Diagnostics"):
        diagProtocol = item.protocolHandle
    print(item)


print("diagProtocol = ", diagProtocol)
diagService = DiagService.DiagService.Client(
    client.createService(DiagService.constants.DIAG_SERVICE_NAME, deviceId)
)

diagService.initializeServiceByProtocol(diagProtocol)

##################################################################

deviceManager.startLogging()

input = bytearray(b'\x4B\x12\x26\x08\x00\x01')

returnObj = Common.ttypes.DiagReturns()
returnObj.flags = (
    Common.ttypes.DiagReturnFlags.BINARY_PAYLOAD
    | Common.ttypes.DiagReturnFlags.PARSED_TEXT
    | Common.ttypes.DiagReturnFlags.PACKET_NAME
    | Common.ttypes.DiagReturnFlags.PACKET_ID
    | Common.ttypes.DiagReturnFlags.PACKET_TYPE
    | Common.ttypes.DiagReturnFlags.TIME_STAMP_STRING
    | Common.ttypes.DiagReturnFlags.PROCESSOR_ID
)

response = diagService.sendRawRequest(input, returnObj, 500)

print("\n\nresponse =  ", response.binaryPayload)


qutsLogFileFolder = "C:\\temp\\testlog"
deviceManager.saveLogFiles(qutsLogFileFolder)

diagService.destroyService()

client.stop()

print("All Done")
