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

returnconfig = Common.ttypes.DiagReturns()
returnconfig.flags = (
    Common.ttypes.DiagReturnFlags.BINARY_PAYLOAD
    | Common.ttypes.DiagReturnFlags.PARSED_TEXT
    | Common.ttypes.DiagReturnFlags.PACKET_NAME
    | Common.ttypes.DiagReturnFlags.PACKET_ID
    | Common.ttypes.DiagReturnFlags.PACKET_TYPE
    | Common.ttypes.DiagReturnFlags.TIME_STAMP_STRING
    | Common.ttypes.DiagReturnFlags.PROCESSOR_ID
)

input = bytearray(
    b'\x80\x1F\x01\x80\x7B\x22\x63\x70\x22\x3A\x22\x34\x22\x2C\x22\x78\x69\x64\x22\x3A\x22\x33\x22\x7D\x00'
)
tid = diagService.sendRawRequestAsync(input)

response = diagService.getResponseAsync(tid, returnconfig, 3000)
print("\n\nresponse 1 =  ", response.binaryPayload)

response = diagService.getResponseAsync(tid, returnconfig, 3000)
print("\n\nresponse 2 =  ", response.binaryPayload)


qutsLogFileFolder = "C:\\temp\\testlog"
deviceManager.saveLogFiles(qutsLogFileFolder)

diagService.destroyService()

client.stop()

print("All Done")
