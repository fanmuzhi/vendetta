import sys
import time

sys.path.append('/')
sys.path.append('..\\..\\python')

import QutsClient
import Common.ttypes

import QmiService.QmiService
import QmiService.constants
import QmiService.ttypes

import ImageManagementService.ImageManagementService
import ImageManagementService.ttypes
import ImageManagementService.constants

import DiagService.DiagService
import DiagService.constants


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
options.layout = [
    Common.ttypes.LogLayout.LOG_DATETIME,
    Common.ttypes.LogLayout.LOG_MESSAGE,
    Common.ttypes.LogLayout.LOG_DATATYPE,
    Common.ttypes.LogLayout.LOG_DATALEN,
    Common.ttypes.LogLayout.LOG_DATA,
]
# options.savePath = 'c:\\temp'

areas = Common.ttypes.FunctionArea()

# deviceList = deviceManager.getDeviceList()
deviceList = client.getDeviceManager().getDevicesForService(
    ImageManagementService.constants.IMAGE_MANAGEMENT_SERVICE_NAME
)

print("\nList of Devices: ")
for device in deviceList:
    print("\nEnable Sahara/Firehose port trace for device: ")
    print(device)
    deviceManager.enableFunctionLog(
        device,
        [
            Common.ttypes.FunctionArea.FUNCTION_AREA_SAHARA_PORT_TRACE,
            Common.ttypes.FunctionArea.FUNCTION_AREA_FIREHOSE_PORT_TRACE,
            Common.ttypes.FunctionArea.FUNCTION_AREA_FIREHOSE_LOADER,
        ],
        options,
    )
    listOfProtocols = deviceManager.getProtocolList(device)

input("\nPress Enter to exit...")
