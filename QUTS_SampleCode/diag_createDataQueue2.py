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
    if (-1 != item.description.find("MSM Diagnostics")):
        diagProtocol = item.protocolHandle
    print(item)


print("diagProtocol = ", diagProtocol)
diagService = DiagService.DiagService.Client(
    client.createService(DiagService.constants.DIAG_SERVICE_NAME, deviceId))

diagService.initializeServiceByProtocol(diagProtocol)

##################################################################

deviceManager.startLogging()



return_flags = Common.ttypes.DiagReturns()
return_flags.flags = 256


#file = open('C:\dmc\multisim2.dmc',"rb")
#contents = file.read()
#print("dmc contents = " , contents)
#diagService.setLoggingMask(contents,2) # 2 for dmc_format

### Create dataqueue  - filters
diagPacketFilter = Common.ttypes.DiagPacketFilter()
diagPacketFilter.idOrNameMask = {}

diagPacketFilter.idOrNameMask[Common.ttypes.DiagPacketType.LOG_PACKET] = [Common.ttypes.DiagIdFilterItem(idOrName="0x19D6"),
                                                                          Common.ttypes.DiagIdFilterItem(idOrName="0x158C")]

diagPacketFilter.idOrNameMask[Common.ttypes.DiagPacketType.EVENT] = [Common.ttypes.DiagIdFilterItem(idOrName="1952"),
                                                                     Common.ttypes.DiagIdFilterItem(idOrName="00289"),
                                                                     Common.ttypes.DiagIdFilterItem(idOrName="00321")]

diagPacketFilter.idOrNameMask[Common.ttypes.DiagPacketType.DEBUG_MSG] = [Common.ttypes.DiagIdFilterItem(idOrName="0123/0001"),
                                                                         Common.ttypes.DiagIdFilterItem(idOrName="0086/0002")]

diagPacketFilter.idOrNameMask[Common.ttypes.DiagPacketType.REQUEST] = [Common.ttypes.DiagIdFilterItem(idOrName="125"),
                                                                       Common.ttypes.DiagIdFilterItem(idOrName="99")]
diagPacketFilter.idOrNameMask[Common.ttypes.DiagPacketType.RESPONSE] = [Common.ttypes.DiagIdFilterItem(idOrName="125"),
                                                                        Common.ttypes.DiagIdFilterItem(idOrName="19")]



diagPacketFilter.subscriptionId  = [];


### Create dataqueue - return type
returnObjDiag = Common.ttypes.DiagReturnConfig()
returnObjDiag.flags = Common.ttypes.DiagReturnFlags.PARSED_TEXT | \
                      Common.ttypes.DiagReturnFlags.PACKET_NAME | \
                      Common.ttypes.DiagReturnFlags.PACKET_ID | \
                      Common.ttypes.DiagReturnFlags.PACKET_TYPE

#packetReturnConfig = LogSession.ttypes.PacketReturnConfig()
#packetReturnConfig.diagConfig = returnObjDiag

diagService.createDataQueue("data", diagPacketFilter, returnObjDiag);

time.sleep(30)

#deviceManager.logAnnotation("before reset",							1,							diagProtocol)

#deviceManager.resetPhone(deviceId, 60000)
#os.system("adb reboot")
#deviceManager.setOperatingMode(deviceId, diagProtocol, DeviceManager.ttypes.OperatingMode.ONLINE)


#deviceManager.logAnnotation("after reset",							1,							diagProtocol)
#time.sleep(30)

diagPackets = diagService.getDataQueueItems("data", 300, 2000)
for i in range(len(diagPackets)):
    print(diagPackets[i].packetId, ' ', diagPackets[i].receiveTimeString  )
    print("----------------------------------------------------")

print("Total pkts", len(diagPackets))

diagService.removeDataQueue("data")

qutsLogFileFolder = "C:\\temp\\testlog"
deviceManager.saveLogFiles(qutsLogFileFolder)

diagService.destroyService()


print("All Done")


