import sys
import time

from sys import platform
if platform == "linux" or platform == "linux2":
    sys.path.append('/opt/qcom/QUTS/Support/python')
elif platform == "win32":
    sys.path.append('/')

import QutsClient
import Common.ttypes

import GpsService.GpsService
import GpsService.constants

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
options.level = Common.ttypes.LogLevel.LOG_DATA
options.format = Common.ttypes.LogFormat.LOG_CSV
options.layout = [Common.ttypes.LogLayout.LOG_DATETIME, Common.ttypes.LogLayout.LOG_MESSAGE, Common.ttypes.LogLayout.LOG_DATATYPE, Common.ttypes.LogLayout.LOG_DATALEN, Common.ttypes.LogLayout.LOG_DATA]
#options.savePath = 'c:\\temp'

deviceList = client.getDeviceManager().getDevicesForService(GpsService.constants.GPS_SERVICE_NAME)

print("\nList of Devices: ")
for device in deviceList:
    print("\nDevice: ")
    print(device)
    listOfProtocols = deviceManager.getProtocolList(device)
    print("\nScan for Gps protocols: ")
    for protocol in listOfProtocols:
        if(protocol.protocolType == 8):  #Gps type
            print("\nEnable port trace for protocol: ")
            print(protocol)
            deviceManager.enableProtocolLog(protocol.protocolHandle, options)

input("\nPress Enter to exit...")





