import sys
import time
from pprint import pp
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


def onDataQueueUpdated(queueName, queueSize):
    print("queueName = ", queueName, ", current queueSize = ", queueSize)

try:
    client = QutsClient.QutsClient("QUTS Sample")
except Exception as e:
    print("Exception starting client")

if client is None:
    print('\nClient did not instantiate')
else:
    print('\nInitialized Client')

client.setOnDataQueueUpdatedCallback(onDataQueueUpdated)

deviceManager = client.getDeviceManager()

time.sleep(1)

# try:
#     client2 = QutsClient.QutsClient("QUTS Sample")
# except Exception as e:
#     print("Exception starting client")

#########################################################
deviceList = deviceManager.getDeviceList()
print("\n\nList of Devices: ")
for item in deviceList:
    if -1 != item.description.find("Qualcomm USB Composite Device"):
        deviceId = item.deviceHandle
    print(item)
print("deviceId = ", deviceId)

listOfProtocols = deviceManager.getProtocolList(deviceId)
print("\n\nList of Protocols: ")
for item in listOfProtocols:
    if -1 != item.description.find("Qualcomm HS-USB Android DIAG"):
        diagProtocol = item.protocolHandle
    print(item)
print("diagProtocol = ", diagProtocol)

################################################################################


diagService = DiagService.DiagService.Client(
    client.createService(DiagService.constants.DIAG_SERVICE_NAME, deviceId)
)

diagService.initializeServiceByProtocol(diagProtocol)
# diagService.initializeService()

with open(r'C:\Users\FNH1SGH\Desktop\mydmc.dmc', 'rb') as f:
    diagService.setLoggingMask(f.read(), 2)  # 2 for dmc file
if 0 != diagService:
    diagService.getLastError()
# ##################################################################
#
deviceManager.startLogging()

# file = open('C:\dmc\test.dmc',"rb")
# contents = file.read()
# diagService.setLoggingMask(contents,2) # 2 for dmc_format

# ### Create dataqueue  - filters
diagPacketFilter = Common.ttypes.DiagPacketFilter()
diagPacketFilter.idOrNameMask = {}
# #
diagPacketFilter.idOrNameMask[Common.ttypes.DiagPacketType.LOG_PACKET] = [
    Common.ttypes.DiagIdFilterItem(idOrName="0x19c5"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19c6"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19c7"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19c8"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19c9"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19cb"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19cc"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19cd"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19d6"),
    Common.ttypes.DiagIdFilterItem(idOrName="0x19d8"),
]

diagPacketFilter.idOrNameMask[Common.ttypes.DiagPacketType.EVENT] = [
    Common.ttypes.DiagIdFilterItem(idOrName="1952"),
    Common.ttypes.DiagIdFilterItem(idOrName="289"),
    Common.ttypes.DiagIdFilterItem(idOrName="321"),
]

diagPacketFilter.idOrNameMask[Common.ttypes.DiagPacketType.DEBUG_MSG] = [
    # Common.ttypes.DiagIdFilterItem(idOrName="123/1"),
    # Common.ttypes.DiagIdFilterItem(idOrName="125/1"),
    # Common.ttypes.DiagIdFilterItem(idOrName="86/2"),
    Common.ttypes.DiagIdFilterItem(idOrName="53/0"),
    Common.ttypes.DiagIdFilterItem(idOrName="53/1"),
    Common.ttypes.DiagIdFilterItem(idOrName="53/2"),
    Common.ttypes.DiagIdFilterItem(idOrName="53/3"),
    Common.ttypes.DiagIdFilterItem(idOrName="53/4"),
    Common.ttypes.DiagIdFilterItem(idOrName="122/0"),
    Common.ttypes.DiagIdFilterItem(idOrName="122/1"),
    Common.ttypes.DiagIdFilterItem(idOrName="122/2"),
    Common.ttypes.DiagIdFilterItem(idOrName="122/3"),
    Common.ttypes.DiagIdFilterItem(idOrName="122/4"),
    Common.ttypes.DiagIdFilterItem(idOrName="123/0"),
    Common.ttypes.DiagIdFilterItem(idOrName="123/1"),
    Common.ttypes.DiagIdFilterItem(idOrName="123/2"),
    Common.ttypes.DiagIdFilterItem(idOrName="123/3"),
    Common.ttypes.DiagIdFilterItem(idOrName="123/4"),
    Common.ttypes.DiagIdFilterItem(idOrName="124/0"),
    Common.ttypes.DiagIdFilterItem(idOrName="124/1"),
    Common.ttypes.DiagIdFilterItem(idOrName="124/2"),
    Common.ttypes.DiagIdFilterItem(idOrName="124/3"),
    Common.ttypes.DiagIdFilterItem(idOrName="124/4"),
    Common.ttypes.DiagIdFilterItem(idOrName="125/0"),
    Common.ttypes.DiagIdFilterItem(idOrName="125/1"),
    Common.ttypes.DiagIdFilterItem(idOrName="125/2"),
    Common.ttypes.DiagIdFilterItem(idOrName="125/3"),
    Common.ttypes.DiagIdFilterItem(idOrName="125/4"),
]


# Create dataqueue - return type
returnObjDiag = Common.ttypes.DiagReturnConfig()
returnObjDiag.flags = (
    0
    | Common.ttypes.DiagReturnFlags.SESSION_INDEX
    | Common.ttypes.DiagReturnFlags.PROTOCOL_INDEX
    | Common.ttypes.DiagReturnFlags.RECEIVE_TIME_DATA
    | Common.ttypes.DiagReturnFlags.RECEIVE_TIME_STRING
    | Common.ttypes.DiagReturnFlags.PACKET_TYPE
    | Common.ttypes.DiagReturnFlags.PACKET_ID
    | Common.ttypes.DiagReturnFlags.PACKET_NAME
    | Common.ttypes.DiagReturnFlags.BINARY_PAYLOAD
    | Common.ttypes.DiagReturnFlags.PARSED_TEXT
    | Common.ttypes.DiagReturnFlags.TIME_STAMP_DATA
    | Common.ttypes.DiagReturnFlags.TIME_STAMP_STRING
    | Common.ttypes.DiagReturnFlags.SUBSCRIPTION_ID
    | Common.ttypes.DiagReturnFlags.PROCESSOR_ID
    | Common.ttypes.DiagReturnFlags.HW_TIME_STAMP_DATA
    | Common.ttypes.DiagReturnFlags.HW_TIME_STAMP_STRING
    | Common.ttypes.DiagReturnFlags.ULOG_SOURCE
    | Common.ttypes.DiagReturnFlags.MORE_RESPONSES_FLAG
    | Common.ttypes.DiagReturnFlags.SUMMARY_TEXT
    | Common.ttypes.DiagReturnFlags.QDSS_CHANNEL_ID
    | Common.ttypes.DiagReturnFlags.QDSS_MASTER_ID
    | Common.ttypes.DiagReturnFlags.QDSS_AT_ID
    | Common.ttypes.DiagReturnFlags.DEFAULT_FORMAT_TEXT
    | Common.ttypes.DiagReturnFlags.CALL_FRAME_NUMBER
    | Common.ttypes.DiagReturnFlags.TIME_STAMP_TOD_ADJUSTED_DATA
    | Common.ttypes.DiagReturnFlags.TIME_STAMP_TOD_ADJUSTED_STRING
    | Common.ttypes.DiagReturnFlags.PACKET_SIZE
    | Common.ttypes.DiagReturnFlags.QTRACE_TAG_LIST
    | Common.ttypes.DiagReturnFlags.MISCELLANEOUS_ID
    | Common.ttypes.DiagReturnFlags.QUERY_RESULT_PICKLED
    | Common.ttypes.DiagReturnFlags.FORMAT_STRING_HASH
    | Common.ttypes.DiagReturnFlags.ENCRYPTION_KEY_INFO
)

diagService.createDataQueue("data", diagPacketFilter, returnObjDiag)

print("sleeping 10 secs")
time.sleep(10)
diagPackets = diagService.getDataQueueItems("data", 1, 20)
while diagPackets:
    for i in range(len(diagPackets)):
        print(
            diagPackets[i].packetId,
            ' ',
            diagPackets[i].parsedText,
            " ",
            diagPackets[i].summaryText,
        )
    print("----------------------------------------------------")
    diagPackets = diagService.getDataQueueItems("data", 1, 20)

    # print([f"{k}: {v}" for k, v in diagPackets[i].__dict__])
    # pp(
        # diagPackets[i].packetId,
        # diagPackets[i].packetType,
        # diagPackets[i].timeStampData,
        # diagPackets[i].packetName,
        # diagPackets[i].summaryText,
        # diagPackets[i].binaryPayload,
        # diagPackets[i].ulogSource,
        # diagPackets[i].__dict__
    # )
#
# print("Total pkts", len(diagPackets))
# diagService.removeDataQueue("data")

qutsLogFileFolder = "C:\\temp\\testlog"
# deviceManager.saveLogFiles(qutsLogFileFolder)
deviceManager.saveLogFilesWithFilenames({562954248388608: r"C:\temp\testlog\fmz.hdf"})

diagService.destroyService()

client.stop()

print("All Done")
