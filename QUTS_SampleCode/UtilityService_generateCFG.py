import sys
import time

#sys.path.append('C:\Program Files (x86)\Qualcomm\QUTS\Support\python')
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
    if(-1 != item.description.find("Qualcomm")):
        deviceId= item.deviceHandle
    print(item)

print("deviceId = ", deviceId)
#deviceId = 562949953421312
#deviceId = 844424930131968
#diagProtocol = 562958543355904

#diagProtocol = 562958543355904


listOfProtocols = deviceManager.getProtocolList(deviceId)
print("\n\nList of Protocols: ")
for item in listOfProtocols:
    if (-1 != item.description.find("Diagnostics")):
        diagProtocol = item.protocolHandle
    print(item)


print("diagProtocol = ", diagProtocol)
diagService = DiagService.DiagService.Client(
    client.createService(DiagService.constants.DIAG_SERVICE_NAME, deviceId))

diagService.initializeServiceByProtocol(diagProtocol)

##################################################################

deviceManager.startLogging()

diagPacketMap = Common.ttypes.DiagPacketMap()

diagPacketMap.subIdTypeIdMaskMap = {}

subId = 2
diagPacketMap.subIdTypeIdMaskMap[subId] = {}
diagPacketMap.subIdTypeIdMaskMap[subId][Common.ttypes.DiagPacketType.LOG_PACKET] = Common.ttypes.DiagPacketIdList()
diagPacketMap.subIdTypeIdMaskMap[subId][Common.ttypes.DiagPacketType.LOG_PACKET].idOrName = ["0x1375", "0x158C"]


diagPacketMap.subIdTypeIdMaskMap[subId][Common.ttypes.DiagPacketType.EVENT] = Common.ttypes.DiagPacketIdList()
diagPacketMap.subIdTypeIdMaskMap[subId][Common.ttypes.DiagPacketType.EVENT].idOrName =  ["1952","00289","00321"]


diagPacketMap.subIdTypeIdMaskMap[subId][Common.ttypes.DiagPacketType.DEBUG_MSG] = Common.ttypes.DiagPacketIdList()
diagPacketMap.subIdTypeIdMaskMap[subId][Common.ttypes.DiagPacketType.DEBUG_MSG].idOrName= ["00007/02","00007/01"]

utilityService  = client.getUtilityService()

format = Common.ttypes.LogMaskFormat().CFG2_FORMAT

cfgContents = utilityService.generateCfg(diagPacketMap, format )

print("cfgContents = ", cfgContents);

byteArray = bytearray(cfgContents);
newFile = open("c:\\temp\cfgFile.cfg2", "wb")
newFile.write(byteArray);

diagService.setLoggingMask(cfgContents,1) # 2 for dmc_format. # 1 for cfg2_format, # 0 for cfg_format

time.sleep(10)

qutsLogFileFolder = "C:\\temp\\testlog"
deviceManager.saveLogFiles(qutsLogFileFolder)

diagService.destroyService()

client.stop()

print("All Done")


