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
    if -1 != item.description.find("0035"):  # 0035 = lahaina
        deviceId = item.deviceHandle
    print(item)

deviceId = 562949953421312
print("deviceId = ", deviceId)

listOfProtocols = deviceManager.getProtocolList(deviceId)
print("\n\nList of Protocols: ")
for item in listOfProtocols:
    if -1 != item.description.find("Diagnostics"):
        diagProtocol = item.protocolHandle
    print(item)
    print("state = ", item.protocolState)
diagProtocol = 562954248388608

print("diagProtocol = ", diagProtocol)


diagService = DiagService.DiagService.Client(
    client.createService(DiagService.constants.DIAG_SERVICE_NAME, deviceId)
)

diagService.initializeServiceByProtocol(diagProtocol)

##################################################################

deviceManager.startLogging()
#
diagPacketMap = Common.ttypes.DiagPacketMap()

diagPacketMap.subIdTypeIdMaskMap = {}

subId = -1
diagPacketMap.subIdTypeIdMaskMap[subId] = {}
diagPacketMap.subIdTypeIdMaskMap[subId][
    Common.ttypes.DiagPacketType.LOG_PACKET
] = Common.ttypes.DiagPacketIdList()
diagPacketMap.subIdTypeIdMaskMap[subId][
    Common.ttypes.DiagPacketType.LOG_PACKET
].idOrName = ["0x1375", "0x158C"]


diagPacketMap.subIdTypeIdMaskMap[subId][
    Common.ttypes.DiagPacketType.EVENT
] = Common.ttypes.DiagPacketIdList()
diagPacketMap.subIdTypeIdMaskMap[subId][Common.ttypes.DiagPacketType.EVENT].idOrName = [
    "1952",
    "289",
    "321",
]


diagPacketMap.subIdTypeIdMaskMap[subId][
    Common.ttypes.DiagPacketType.DEBUG_MSG
] = Common.ttypes.DiagPacketIdList()
diagPacketMap.subIdTypeIdMaskMap[subId][
    Common.ttypes.DiagPacketType.DEBUG_MSG
].idOrName = ["7/2", "7/1"]

diagPacketMap.subIdTypeIdMaskMap[subId][
    Common.ttypes.DiagPacketType.QTRACE
] = Common.ttypes.DiagPacketIdList()
diagPacketMap.subIdTypeIdMaskMap[subId][
    Common.ttypes.DiagPacketType.QTRACE
].idOrName = ["64/1", "105/3"]


utilityService = client.getUtilityService()

time.sleep(2)
format = Common.ttypes.LogMaskFormat().CFG_FORMAT

cfgContents = utilityService.generateCfg(diagPacketMap, format)

print("cfgContents = ", cfgContents)

byteArray = bytearray(cfgContents)
newFile = open(r'C:\Users\FNH1SGH\Desktop\mydmc', "rb")
# newFile.write(byteArray)

file = open(r'C:\Users\FNH1SGH\Desktop\mydmc', "rb")
contents = file.read()
diagService.setLoggingMask(
    contents, 2
)  # 2 for dmc_format. # 1 for cfg2_format, # 0 for cfg_format

time.sleep(2)
format = Common.ttypes.LogMaskFormat().CFG_FORMAT

extracted = utilityService.extractFromCfg(cfgContents, format)


for type in extracted.subIdTypeIdMaskMap[-1]:
    print("type = ", type, ": ", extracted.subIdTypeIdMaskMap[-1][type])


time.sleep(10)

qutsLogFileFolder = "C:\\temp\\testlog"
deviceManager.saveLogFiles(qutsLogFileFolder)


diagService.destroyService()


print("All Done")
