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

import RawService.RawService
import RawService.constants


def onMessage(level, location, title, description):
    print("Message Received {} {} ".format(title, description))


try:
    client = QutsClient.QutsClient("QUTS Tcp Connection")
except Exception as e:
    print("Exception starting client")

if client is None:
    print('\nClient did not instantiate')
else:
    print('\nInitialized Client')

client.setOnMessageCallback(onMessage)

deviceManager = client.getDeviceManager()

time.sleep(2)


deviceList = client.getDeviceManager().getDevicesForService(
    RawService.constants.RAW_SERVICE_NAME
)

print("\nList of Devices: ")
for device in deviceList:
    print("\nDevice: ")
    print(device)
    listOfProtocols = deviceManager.getProtocolList(device)
    print("\nList of Protocols: ")
    for protocol in listOfProtocols:
        print(protocol)

options = Common.ttypes.TcpOptions()
options.description = '5g'
options.protocolType = Common.ttypes.ProtocolType.PROT_DIAG
options.isClient = True
# options.deviceHandle = deviceList[0]
options.adbSerialNumber = 'b0ac011'
options.chipSerialNumber = '5ee07610'

deviceManager.addTcpConnectionWithOptions('tbs-1241-5g', 2500, options)

input("\nPress Enter to continue...")

print("All Done")
