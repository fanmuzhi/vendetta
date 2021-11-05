import sys
import time

sys.path.append('/')
sys.path.append('..\\..\\python')

import QutsClient
import Common.ttypes

import RawService.RawService
import RawService.constants

def onMessage(level, location, title, description):
    print("Message Received {} {} ".format(title, description))

try:
    client = QutsClient.QutsClient("QUTS logger")
except Exception as e:
    print("Exception starting client")

if client is None:
    print('\nClient did not instantiate')
else:
    print('\nInitialized Client')

client.setOnMessageCallback(onMessage)

deviceManager = client.getDeviceManager()

time.sleep(2)

options = Common.ttypes.LogOptions()
options.level = Common.ttypes.LogLevel.LOG_ALL
options.format = Common.ttypes.LogFormat.LOG_CSV
options.layout = [Common.ttypes.LogLayout.LOG_DATETIME, Common.ttypes.LogLayout.LOG_MESSAGE, Common.ttypes.LogLayout.LOG_DATATYPE, Common.ttypes.LogLayout.LOG_DATALEN, Common.ttypes.LogLayout.LOG_DATA]
#options.savePath = 'c:\\temp'

areas = Common.ttypes.FunctionArea()

#deviceList = deviceManager.getDeviceList()
deviceList = client.getDeviceManager().getDevicesForService(RawService.constants.RAW_SERVICE_NAME)

print("\nList of Devices: ")
for device in deviceList:
    print("\nDevice: ")
    print(device)
    deviceManager.enableFunctionLog(device, [Common.ttypes.FunctionArea.FUNCTION_AREA_SAHARA_PORT_TRACE, Common.ttypes.FunctionArea.FUNCTION_AREA_FIREHOSE_PORT_TRACE, Common.ttypes.FunctionArea.FUNCTION_AREA_FIREHOSE_LOADER, Common.ttypes.FunctionArea.FUNCTION_AREA_QDSS_DIAG_RAW_TRACE], options)
    listOfProtocols = deviceManager.getProtocolList(device)
    print("\nList of Protocols: ")
    for protocol in listOfProtocols:
        print(protocol)
        if(protocol.protocolType == 0):  #diag type
            deviceManager.enableProtocolLog(protocol.protocolHandle, options)
        if(protocol.protocolType == 1):  #qmi type
            deviceManager.enableProtocolLog(protocol.protocolHandle, options)

print("All Done")





