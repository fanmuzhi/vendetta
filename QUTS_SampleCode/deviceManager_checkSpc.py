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


def onMessage(level, location, title, description):
    print("Message Received {} {} ".format(title, description))


s = 0

try:
    client = QutsClient.QutsClient("QUTS Sample")
except Exception as e:
    print("Exception starting client")

if client is None:
    print('\nClient did not instantiate')
else:
    print('\nInitialized Client')

client.setOnMessageCallback(onMessage)

deviceManager = client.getDeviceManager()

time.sleep(2)

deviceList = deviceManager.getDeviceList()
print("\n\nList of Devices: ")
for item in deviceList:
    print(item)

deviceId = 562949953421312
# diagProtocol = 281492156579840
diagProtocol = 0

listOfProtocols = deviceManager.getProtocolList(deviceId)
print("\n\nList of Protocols: ")
for item in listOfProtocols:
    print(item)

serviceList = deviceManager.getServicesList()
print("\n\nList of Services: ", serviceList)


status = deviceManager.checkSpc(deviceId, diagProtocol, "000000")
print("spc (000000) status = ", status)

status = deviceManager.checkSpc(deviceId, diagProtocol, "000001")
print("spc (000001) status = ", status)

chipname = deviceManager.getChipName(deviceId, diagProtocol)
print("chipname = ", chipname)


print("All Done")
