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
import DeviceManager.ttypes


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

deviceId = 281474976710656
# diagProtocol = 281492156579840
diagProtocol = 0

listOfProtocols = deviceManager.getProtocolList(deviceId)
print("\n\nList of Protocols: ")
for item in listOfProtocols:
    print(item)

serviceList = deviceManager.getServicesList()
print("\n\nList of Services: ", serviceList)


# diagProtocolHandle = 281496451547136
diagProtocolHandle = 0

diagProtocolHandle = 562954248388608  # mdm
# diagProtocolHandle = 281483566645248 # apq
# 281496451547136


# enum OperatingMode   -> codes for set operating mode
# {
#   OFFLINE_ANALOG = 0,
#   OFFLINE_DIGITAL = 1,
#   OFFLINE_FACTORY_TEST = 3,
#   ONLINE = 4,
#   LOW_POWER = 5,
#   POWER_OFF = 6
# }


ret = deviceManager.setOperatingMode(
    deviceId, diagProtocolHandle, DeviceManager.ttypes.OperatingMode.ONLINE
)
print("ret = ", ret)

time.sleep(5)
opMode = deviceManager.getOperatingMode(deviceId, diagProtocolHandle)
print("opMode = ", opMode)

ret = deviceManager.setOperatingMode(
    deviceId, diagProtocolHandle, DeviceManager.ttypes.OperatingMode.LOW_POWER
)
print("ret = ", ret)
time.sleep(5)
opMode = deviceManager.getOperatingMode(deviceId, diagProtocolHandle)
print("opMode = ", opMode)


ret = deviceManager.setOperatingMode(
    deviceId, diagProtocolHandle, DeviceManager.ttypes.OperatingMode.OFFLINE_DIGITAL
)
print("ret = ", ret)
time.sleep(5)
opMode = deviceManager.getOperatingMode(deviceId, diagProtocolHandle)
print("opMode = ", opMode)


chipname = deviceManager.getChipName(deviceId, diagProtocol)
print("chipname = ", chipname)

#
status = deviceManager.checkSpc(deviceId, diagProtocol, "000000")
print("spc (000000) status = ", status)

print(deviceManager.getLastError())
status = deviceManager.checkSpc(deviceId, diagProtocol, "000001")
print("spc (000001) status = ", status)
print(deviceManager.getLastError())

chipname = deviceManager.getChipName(deviceId, diagProtocol)
print("chipname = ", chipname)


meid = deviceManager.getMeid(deviceId, 0)
print("meid = ", meid)

imei = deviceManager.getImei(deviceId, 0)
print("imei = ", imei)


print("All Done")
