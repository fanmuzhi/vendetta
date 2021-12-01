import os
import sys
import time
import threading
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

result_available = threading.Event()


def onDataViewUpdated(viewName, dataViewSize, isDataViewCreationFinished):
    global dataViewItemCount
    global end_index
    # print(f"current dataview count={dataViewSize}, isDataViewCreationFinished={isDataViewCreationFinished}")
    if isDataViewCreationFinished or end_index < dataViewSize:
        result_available.set()  # send a signal that data is available
    if (
        isDataViewCreationFinished
    ):  # this will not execute if script finishes before dataviewCreation is finised
        print("total packet count is: ", dataViewSize)


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
    ##For each packtype define either the ID to be filtered or filter by applying regex or both

    ##filtering for log with id or name
    logFilters = []
    logFilters.append(Common.ttypes.DiagIdFilterItem(idOrName="0x1545"))
    logFilters.append(Common.ttypes.DiagIdFilterItem(idOrName="0x1546"))
    diagPacketFilter.idOrNameMask[Common.ttypes.DiagPacketType.LOG_PACKET] = logFilters

    ##apply all the filters.
    dataPacketFilter.diagFilter = diagPacketFilter

    ## define what needs to be returned
    returnObjDiag = Common.ttypes.DiagReturnConfig()

    ##Add the fields you are interested in processing.
    returnObjDiag.flags = (
        Common.ttypes.DiagReturnFlags.PARSED_TEXT
        | Common.ttypes.DiagReturnFlags.PACKET_NAME
        | Common.ttypes.DiagReturnFlags.PACKET_ID
        | Common.ttypes.DiagReturnFlags.PACKET_TYPE
    )

    ## For any given id, list the fields you are interested in. Multiple packets with its own list of fields can be provided.
    diagReturns = Common.ttypes.DiagReturns()
    diagReturns.flags = returnObjDiag.flags
    ## the fields listed in queries will be displayedin the JSON query output
    diagReturns.queries = [
        '."msg_type"',
        '."msg_length"',
        '."service_type"',
    ]  ## ['."Cyclic Shift of DMRS Symbols Slot 0"', '."Cyclic Shift of DMRS Symbols Slot 1"' ]

    diagReturns1 = Common.ttypes.DiagReturns()
    diagReturns1.flags = returnObjDiag.flags
    ## the fields listed in queries will be displayedin the JSON query output
    diagReturns1.queries = ['."status"']
    returnObjDiag.fieldQueries = {
        Common.ttypes.DiagPacketType.LOG_PACKET: {
            '0x1545': diagReturns,
            '0x1546': diagReturns1,
        }
    }

    packetReturnConfig = LogSession.ttypes.PacketReturnConfig()
    packetReturnConfig.diagConfig = returnObjDiag

    packetReturnConfig = LogSession.ttypes.PacketReturnConfig()
    packetReturnConfig.diagConfig = returnObjDiag

    logSession.createDataView("data", dataPacketFilter, packetReturnConfig)

    total_count = logSession.getDataViewItemCount("data")
    print(f"total packet count = {total_count}")

    packetRange = LogSession.ttypes.PacketRange()
    '''
    packetRange.indexType = LogSession.ttypes.PROTOCOL_INDEX 
    packetRange.beginIndex = 0
    ## use either count or endIndex
    ##packetRange.count = 1 
    packetRange.endIndex = logSession.getDataPacketCount(dataPacketFilter.protocolHandleList[0])
    '''
    ##getting 10 to 15th item in the returned data
    packetRange.indexType = LogSession.ttypes.IndexType.DATA_VIEW_INDEX
    packetRange.beginIndex = 0
    packetRange.count = logSession.getDataPacketCount(
        dataPacketFilter.protocolHandleList[0]
    )

    global end_index
    end_index = packetRange.beginIndex + packetRange.count

    print("start:  waiting for data packets to be available in dataview")
    start = time.time()
    result_available.wait()
    print(
        "end:  waiting for data packets to be available in dataview. Duration: ",
        time.time() - start,
    )

    dataPackets = logSession.getDataViewItems("data", packetRange)

    print("Packets matched ", len(dataPackets))
    ##DataPackets has a collection of different types of packets for each protocol such Diag. QMI etc.

    for i in range(len(dataPackets)):
        if dataPackets[i].diagPacket is not None:
            print(
                dataPackets[i].diagPacket.packetId,
                ' \n',
                dataPackets[i].diagPacket.packetName,
                '\n ',
                dataPackets[i].diagPacket.packetType,
                '\n ',
                dataPackets[i].diagPacket.queryResultJson,
            )

    logSession.removeDataView("data")
    return dataPackets


def GetDiagDataForMultipleFilters(logSession, allFilters):

    diagPacketFilter = Common.ttypes.DiagPacketFilter()
    deviceList = logSession.getDeviceList()
    ##print(deviceList)
    protocolList = logSession.getProtocolList(deviceList[0].deviceHandle)
    diagPacketFilter.idOrNameMask = {}
    for packetType in allFilters:
        ##print(packetType)
        ##print(allFilters[packetType])
        listOfID = []
        for id in allFilters[packetType]:  ##for string value create a IdOrName
            listOfID.append(Common.ttypes.DiagIdFilterItem(idOrName=id))
        diagPacketFilter.idOrNameMask[packetType] = listOfID

    dataPacketFilter = LogSession.ttypes.DataPacketFilter()
    dataPacketFilter.protocolHandleList = [protocolList[0].protocolHandle]
    dataPacketFilter.diagFilter = diagPacketFilter

    returnObjDiag = Common.ttypes.DiagReturnConfig()
    returnObjDiag.flags = (
        Common.ttypes.DiagReturnFlags.PARSED_TEXT
        | Common.ttypes.DiagReturnFlags.SUMMARY_TEXT
        | Common.ttypes.DiagReturnFlags.RECEIVE_TIME_STRING
        | Common.ttypes.DiagReturnFlags.PACKET_NAME
        | Common.ttypes.DiagReturnFlags.PACKET_ID
        | Common.ttypes.DiagReturnFlags.PACKET_TYPE
    )
    diagReturns = Common.ttypes.DiagReturns()
    diagReturns.flags = returnObjDiag.flags
    ## the fields listed in queries will be displayedin the JSON query output
    diagReturns.queries = [
        '."msg_type"',
        '."msg_length"',
        '."service_type"',
    ]  ## ['."Cyclic Shift of DMRS Symbols Slot 0"', '."Cyclic Shift of DMRS Symbols Slot 1"' ]
    ##diagReturns.queries = ['."Serving Cell ID = 3"']
    returnObjDiag.fieldQueries = {
        Common.ttypes.DiagPacketType.LOG_PACKET: {'0x1545': diagReturns}
    }

    packetReturnConfig = LogSession.ttypes.PacketReturnConfig()
    packetReturnConfig.diagConfig = returnObjDiag

    logSession.createDataView("data", dataPacketFilter, packetReturnConfig)

    packetRange = LogSession.ttypes.PacketRange()
    packetCount = logSession.getDataPacketCount(protocolList[0].protocolHandle)
    print("Total packets ", packetCount)
    ##rolling index
    time_start = time.time()
    packetRange.beginIndex = 0
    ##packetRange.count = 1
    packetRange.endIndex = packetCount
    for i in range(len(dataPackets)):
        if not dataPackets[i].diagPacket.packetName:
            continue
        else:
            print(
                "Id:",
                dataPackets[i].diagPacket.packetId,
                "Name:",
                dataPackets[i].diagPacket.packetName,
                "Summary:",
                dataPackets[i].diagPacket.summaryText,
            )

    print("Total time ", time.time() - time_start)
    print("Total packets received ", totalPackets)
    logSession.removeDataView("data")
    return dataPackets


def TestCommands(quts_client, logSession):

    item = {}
    ##item[Common.ttypes.DiagPacketType.RESPONSE] = ["115"]
    ##item[Common.ttypes.DiagPacketType.SUBSYS_RESPONSE] =   [ "75/9483", "18/2048", "33/64005"]
    ##item[Common.ttypes.DiagPacketType.LOG_PACKET] =   [ "0xB134","0xB11C","0xB13D" , "0xB139"]
    item[Common.ttypes.DiagPacketType.LOG_PACKET] = ["0x1545"]  ## "0xB139"]
    ##item[Common.ttypes.DiagPacketType.DEBUG_MSG] =   [ "32/3"]
    ##item[Common.ttypes.DiagPacketType.EVENT] =   [ "2693"]
    dataPackets = GetDiagDataForMultipleFilters(logSession, item)


def getLastError(logSession):
    print("Last Error ", logSession.getLastError())


def execTest(quts_client):
    time_start = time.time()

    if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
        ISF_path = os.getcwd() + "/sampleTestFile.isf"
    elif sys.platform == "win32":
        ISF_path = os.getcwd() + "\\sampleTestFile.isf"

    print(ISF_path)
    # ISF_path = r'C:\Users\FNH1SGH\Documents\My Received Files\pre_tem.hdf'

    start = time.time()
    ##QUTS LoadSession
    logSession = quts_client.openLogSession([ISF_path])  ##Loads a list of ISF/HDF files
    end = time.time()
    print("\n Load time", end - start)

    quts_client.setOnDataViewUpdatedCallback(onDataViewUpdated)

    ##GetDeviceDetails(logSession)
    if logSession == 0:
        print("Unable to open logSession")

        return False

    ##TestCommands(quts_client,logSession)
    ProcessFiles(logSession)


if __name__ == "__main__":
    quts_client = QutsClient.QutsClient("LogSessionSample")  ##Initialize()
    execTest(quts_client)
