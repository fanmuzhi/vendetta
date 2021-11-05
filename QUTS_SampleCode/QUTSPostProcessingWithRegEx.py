import os
import sys
import time
import re

##quts

if sys.platform.startswith("linux"):
    sys.path.append('/opt/qcom/QUTS/Support/python')
elif sys.platform.startswith("win"):
    sys.path.append('/')
elif sys.platform.startswith("darwin"):
    sys.path.append('/Applications/Qualcomm/QUTS/QUTS.app/Contents/Support/python')
import QutsClient
import Common.ttypes
import LogSession.LogSession
import LogSession.constants
import LogSession.ttypes


DIAG_Response = ['0124']


def GetDeviceDetails(logSession):
    deviceList = logSession.getDeviceList()
    print("DeviceList", deviceList)


def ProcessFiles(logSession):

    dataPacketFilter = LogSession.ttypes.DataPacketFilter()

    ##Gets the list of devices used in collecting the data in the files in LogSession
    deviceList = logSession.getDeviceList()

    ##list of protocols used in the logSession
    listOfProtocols = logSession.getProtocolList(deviceList[0].deviceHandle)

    ##Get the Diag protocols handle.
    for i in range(len(listOfProtocols)):
        if listOfProtocols[i].protocolType == Common.ttypes.ProtocolType.PROT_DIAG:
            dataPacketFilter.protocolHandleList = [listOfProtocols[i].protocolHandle]

    ##Set filters for the actual Diag packets.
    diagPacketFilter = Common.ttypes.DiagPacketFilter()
    diagPacketFilter.idOrNameMask = {}

    ##Create various types of filters
    ##Every filter needs to have a Packet type.
    ##For each packtype define either the ID to be filtered or filter by applying regex or both/

    ##filtering for log with id or name
    logFilters = []
    logFilters.append(Common.ttypes.DiagIdFilterItem(idOrName="0x1545"))
    logFilters.append(
        Common.ttypes.DiagIdFilterItem(idOrName="QBI Context 0 TX Message")
    )
    ##logFilters.append(Common.ttypes.DiagIdFilterItem(regexFilter="Version 141"))
    diagPacketFilter.idOrNameMask[Common.ttypes.DiagPacketType.LOG_PACKET] = logFilters

    '''
    ##filtering with multiple messages for same packettype. filter by ID or name 
	## this filter will include items that matches any of the following filters
    debugFilters = []
    debugFilters.append(Common.ttypes.DiagIdFilterItem(idOrName="LTE ML1/High"))
    debugFilters.append(Common.ttypes.DiagIdFilterItem(idOrName="9504/0002"))
    debugFilters.append(Common.ttypes.DiagIdFilterItem(idOrName="LTE MACCTRL/High",summaryRegexFilter="lte_mac_qos.c   4808")) ##
    diagPacketFilter.idOrNameMask[Common.ttypes.DiagPacketType.DEBUG_MSG] = debugFilters
	'''

    ##apply all the filters.
    dataPacketFilter.diagFilter = diagPacketFilter
    returnObjDiag = Common.ttypes.DiagReturnConfig()
    ##Add the fields you are interested in processing.
    returnObjDiag.flags = (
        Common.ttypes.DiagReturnFlags.PARSED_TEXT
        | Common.ttypes.DiagReturnFlags.PACKET_NAME
        | Common.ttypes.DiagReturnFlags.PACKET_ID
        | Common.ttypes.DiagReturnFlags.PACKET_TYPE
    )
    returnObjDiag.diagTimeSorted = False

    packetReturnConfig = LogSession.ttypes.PacketReturnConfig()
    packetReturnConfig.diagConfig = returnObjDiag

    logSession.createDataView("data", dataPacketFilter, packetReturnConfig)

    packetRange = LogSession.ttypes.PacketRange()
    packetRange.beginIndex = 0
    ##packetRange.count = 1
    packetRange.endIndex = logSession.getDataPacketCount(
        dataPacketFilter.protocolHandleList[0]
    )

    startTime = time.time()
    dataPackets = logSession.getDataViewItems("data", packetRange)
    print("Elapsed time ", time.time() - startTime)

    print("Packets matched ", len(dataPackets))
    ##DataPackets has a collection of different types of packets for each protocol such Diag. QMI etc.
    ''' Print 
    for i in range(len(dataPackets)):
       if(dataPackets[i].diagPacket is not None): 
            print(dataPackets[i].diagPacket.packetId,  ' ',dataPackets[i].diagPacket.parsedText )
    '''
    logSession.removeDataView("data")
    return dataPackets


def getLastError(logSession):
    print("Last Error ", logSession.getLastError())


def execTest(quts_client):
    time_start = time.time()

    if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
        filePath = os.getcwd() + "/sampleTestFile.isf"
    elif sys.platform == "win32":
        filePath = os.getcwd() + "\\sampleTestFile.isf"

    print(filePath)

    ##QUTS LoadSession
    logSession = quts_client.openLogSession(
        [filePath]
    )  ##Loads a list of ISF/HDF files. Can be file name or foldername.
    ##GetDeviceDetails(logSession)
    if logSession == 0:
        print("Unable to open logSession")

        return False

    ProcessFiles(logSession)


if __name__ == "__main__":
    quts_client = QutsClient.QutsClient("LogSessionSample")  ##Initialize()
    execTest(quts_client)
