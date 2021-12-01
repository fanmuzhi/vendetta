import sys

## Quts path to select as per windows / linux
if sys.platform.startswith("linux"):
    sys.path.append('/opt/qcom/QUTS/Support/python')
elif sys.platform.startswith("win"):
    sys.path.append('/')
elif sys.platform.startswith("darwin"):
    sys.path.append('/Applications/Qualcomm/QUTS/QUTS.app/Contents/Support/python')
import os
import time
import QutsClient
import Common.ttypes
import LogSession.LogSession
import LogSession.constants
import LogSession.ttypes
import threading


# global variable to indicate viewsize and completion of dataViewUpdated callback
gDataViewItemCount = -1


def ProcessFiles(logSession, quts_client):
    dataPacketFilter = LogSession.ttypes.DataPacketFilter()

    ##Gets the list of devices used in collecting the data in the files in LogSession
    deviceList = logSession.getDeviceList()

    ##list of protocols used in the logSession
    listOfProtocols = logSession.getProtocolList(deviceList[0].deviceHandle)

    for i in range(len(listOfProtocols)):
        if listOfProtocols[i].protocolType == Common.ttypes.ProtocolType.PROT_DIAG:
            dataPacketFilter.protocolHandleList = [listOfProtocols[i].protocolHandle]
    ##Set filters for the actual Diag packets.
    diagPacketFilter = Common.ttypes.DiagPacketFilter()
    diagPacketFilter.idOrNameMask = {}

    logFilters = []

    ## idOrName & idOrNameMask update as per your requirement
    logFilters.append(Common.ttypes.DiagIdFilterItem(idOrName="0x1545"))
    logFilters.append(Common.ttypes.DiagIdFilterItem(idOrName="0x1546"))
    diagPacketFilter.idOrNameMask[Common.ttypes.DiagPacketType.LOG_PACKET] = logFilters

    ##apply all the filters.
    dataPacketFilter.diagFilter = diagPacketFilter
    returnObjDiag = Common.ttypes.DiagReturnConfig()

    ## Select flags as per your requirement
    returnObjDiag.flags = (
        Common.ttypes.DiagReturnFlags.PACKET_ID
        | Common.ttypes.DiagReturnFlags.PACKET_NAME
        | Common.ttypes.DiagReturnFlags.PACKET_SIZE
        | Common.ttypes.DiagReturnFlags.SUMMARY_TEXT
    )
    returnObjDiag.diagTimeSorted = False

    packetReturnConfig = LogSession.ttypes.PacketReturnConfig()
    packetReturnConfig.diagConfig = returnObjDiag

    logSession.createDataView("data", dataPacketFilter, packetReturnConfig)

    packetRange = LogSession.ttypes.PacketRange()
    packetRange.beginIndex = 0
    total_packets = logSession.getDataPacketCount(
        dataPacketFilter.protocolHandleList[0]
    )
    print("Total Count:", total_packets)

    print("registering callback")
    quts_client.setOnDataViewUpdatedCallback(onDataViewUpdated)
    while 0 > gDataViewItemCount:
        time.sleep(2)
        print("Waiting for finish of onDataViewUpdated callback")
    if 0 == gDataViewItemCount:
        print(
            "Zero items matched, please check item id, packet type & file path is proper"
        )
        sys.exit(0)
    else:
        print("Total items matched:", gDataViewItemCount)
    dataPackets = list()
    stepsize = 10000
    packetRange.beginIndex = 0
    packetRange.endIndex = 0

    while packetRange.endIndex < gDataViewItemCount:

        packetRange.endIndex = packetRange.beginIndex + stepsize
        if packetRange.endIndex > gDataViewItemCount:
            packetRange.endIndex = gDataViewItemCount
        dataPackets = logSession.getDataViewItems("data", packetRange)
        packetRange.beginIndex = packetRange.endIndex + 1
        if packetRange.beginIndex > gDataViewItemCount:
            packetRange.beginIndex = gDataViewItemCount
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


def onDataViewUpdated(viewName, viewSize, finished):
    print("On data view updated:", viewName, viewSize, finished)
    global gDataViewItemCount
    if finished == True:
        gDataViewItemCount = viewSize

    pass


def execTest():
    ## Update filepath where hdf / isf file is located
    if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
        filePath = os.getcwd() + "/sampleTestFile.isf"
    elif sys.platform == "win32":
        filePath = os.getcwd() + "\\sampleTestFile.isf"
    # filePath = r'C:\Program Files (x86)\Qualcomm\QUTS\SampleCode\Python\qbi.isf'
    filePath = r'C:\temp\testlog\6c9a0840-fbe9-43fc-a210-45ee7bdbafd7_50791_Diag_Qualcomm_HS-USB_Android_DIAG_901D_(COM4)_0.hdf'
    print('file', filePath)
    # quts_client = QutsClient.QutsClient("LogSessionSample", multiThreadedClient=true) ##Initialize()
    quts_client = QutsClient.QutsClient("LogSessionSample")  ##Initialize()
    print("Successfully created QUTS client")
    logSession = quts_client.openLogSession(
        [filePath]
    )  ##Loads a list of ISF/HDF files. Can be file name or foldername.
    if logSession == 0:
        print("Unable to open logSession")

        return False
    else:
        print("LogSession created successfully")
    ProcessFiles(logSession, quts_client)
    logSession.destroyLogSession()


if __name__ == '__main__':
    try:
        execTest()
    except Exception as e:
        print("Exception starting client")
