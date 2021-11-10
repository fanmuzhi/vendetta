## For detailed description of the QUTS APIs, please refer to QUTS documentation at "C:\Program Files (x86)\Qualcomm\QUTS\QUTS_User_Guide.docm"
##This sample includes connecting to device, using Diag, sending commands and collecting logs.
import os
import sys
import time
import re

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


import DiagService.DiagService
import DiagService.constants
import DiagService.ttypes


global handle
global diagService


def CreateFilters(allFilters):
    diagPacketFilter = Common.ttypes.DiagPacketFilter()
    diagPacketFilter.idOrNameMask = {}
    for packetType in allFilters:
        ##print("Filters")
        ##print(packetType)
        ##print( allFilters[packetType])
        listOfID = []
        for id in allFilters[packetType]:  ##for string value create a IdOrName
            listOfID.append(Common.ttypes.DiagIdFilterItem(idOrName=id))
        diagPacketFilter.idOrNameMask[packetType] = listOfID
    return diagPacketFilter


def CreateDataQueueForMonitoring(diagService, allFilters, queueName):
    ### Createa data Queue. Reading will be done in the callback.
    diagPacketFilter = CreateFilters(allFilters)

    returnObjDiag = Common.ttypes.DiagReturnConfig()
    returnObjDiag.flags = (
        Common.ttypes.DiagReturnFlags.PARSED_TEXT
        | Common.ttypes.DiagReturnFlags.PACKET_NAME
        | Common.ttypes.DiagReturnFlags.PACKET_ID
        | Common.ttypes.DiagReturnFlags.PACKET_TYPE
        | Common.ttypes.DiagReturnFlags.TIME_STAMP_STRING
        | Common.ttypes.DiagReturnFlags.RECEIVE_TIME_STRING
        | Common.ttypes.DiagReturnFlags.SUMMARY_TEXT
    )

    errorCode = diagService.createDataQueue(queueName, diagPacketFilter, returnObjDiag)
    if errorCode != 0:
        print("Error  creating data queue", errorCode)
    else:
        print("Data queue Created")


def UpdateFiltersToQueue(diagService, allFilters, queueName, addOrRemove):
    diagPacketFilter = CreateFilters(allFilters)
    if addOrRemove == "add":
        print("Adding above filter")
        errorCode = diagService.addDataQueueFilter(queueName, diagPacketFilter)
    else:
        print("Removing above filter")
        errorCode = diagService.removeDataQueueFilter(queueName, diagPacketFilter)
    if errorCode != 0:
        print("Error  updating data queue", errorCode)
    else:
        print("Data queue updated with " + addOrRemove)


def onDataQueueUpdated(queueName, queueSize):
    print(queueName, " update ", queueSize)
    '''
    diagPackets = diagService.getDataQueueItems(queueName, queueSize, 2000)
	
    print (len(diagPackets))
    print(diagPackets)
    print("####################################################")
    '''


def onMessage(level, location, title, description):
    print("Message Received " + title + " " + description)


def sendRawRequestFunction(diagService, request):

    returnObj = Common.ttypes.DiagReturns()
    returnObj.flags = (
        Common.ttypes.DiagReturnFlags.RECEIVE_TIME_STRING
        | Common.ttypes.DiagReturnFlags.PARSED_TEXT
        | Common.ttypes.DiagReturnFlags.PACKET_NAME
        | Common.ttypes.DiagReturnFlags.PACKET_ID
        | Common.ttypes.DiagReturnFlags.PACKET_TYPE
        | Common.ttypes.DiagReturnFlags.TIME_STAMP_STRING
        | Common.ttypes.DiagReturnFlags.PROCESSOR_ID
    )

    response = diagService.sendRawRequest(request, returnObj, 500)
    ##print ("Response" , response)
    ##print("-----------------")


##Sample Commands
def FTMCommand(diagService):

    noOfTimeouts = 0
    noOfCmds = 0

    for i in range(1):
        request = bytes(
            [
                0x4B,
                0x0B,
                0x09,
                00,
                00,
                00,
                00,
                00,
                00,
                00,
                0x11,
                00,
                0x14,
                00,
                00,
                00,
                0x01,
                00,
                00,
                00,
            ]
        )
        sendRawRequestFunction(diagService, request)

        request = bytes(
            [
                0x73,
                0x00,
                0x00,
                0x00,
                0x03,
                0x00,
                0x00,
                0x00,
                0x01,
                0x00,
                0x00,
                0x00,
                0x2C,
                0x09,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x10,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ]
        )
        sendRawRequestFunction(diagService, request)
        request = bytes([0x4B, 0x0B, 0x25, 0x00, 0x04, 0x00, 0x00, 0x00, 0x0C, 0x00])
        sendRawRequestFunction(diagService, request)
        request = bytes(
            [
                0x4B,
                0x0B,
                0x25,
                0x00,
                0x00,
                0x00,
                0x44,
                0x00,
                0x0C,
                0x00,
                0x03,
                0x00,
                0x0A,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x4B,
                0x0B,
                0x25,
                0x00,
                0x0A,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x0E,
                0x00,
                0x01,
                0x00,
                0x00,
                0x00,
                0x4B,
                0x0B,
                0x25,
                0x00,
                0x01,
                0x00,
                0x00,
                0x00,
                0x0C,
                0x00,
                0x40,
                0x9C,
                0x00,
                0x00,
                0x0E,
                0x00,
                0x02,
                0x00,
                0x00,
                0x00,
                0x4B,
                0x0B,
                0x25,
                0x00,
                0x01,
                0x00,
                0x00,
                0x00,
                0x0C,
                0x00,
                0x40,
                0x9C,
                0x00,
                0x00,
            ]
        )
        sendRawRequestFunction(diagService, request)
        request = bytes([0x4B, 0x12, 0x5D, 0x00])
        sendRawRequestFunction(diagService, request)
        request = bytes([0x4B, 0x0B, 0x25, 0x00, 0x03, 0x00, 0x00, 0x00, 0x0C, 0x00])
        sendRawRequestFunction(diagService, request)


def sendDiagRequest(diagService):
    diagPackettype = Common.ttypes.DiagPacketType.REQUEST

    returnObj = Common.ttypes.DiagReturns()
    returnObj.flags = (
        Common.ttypes.DiagReturnFlags.PARSED_TEXT
        | Common.ttypes.DiagReturnFlags.PACKET_NAME
        | Common.ttypes.DiagReturnFlags.PACKET_ID
    )

    response = diagService.sendRequest(diagPackettype, "63", "", returnObj, 10000)
    ##print (response.packetId,  response.packetName, response.parsedText)
    '''
	response= diagService.sendRequest(diagPackettype,"54","",returnObj,10000)
	print (response.packetId, response.packetName,response.parsedText) 
 
	diagPackettype = Common.ttypes.DiagPacketType.SUBSYS_REQUEST
	response= diagService.sendRequest(diagPackettype,"18/41","01 02 03",returnObj,10000)
	##print (response.packetId,response.packetName,response.parsedText) 
	'''
    ##same as above but using string parameter
    diagPackettype = Common.ttypes.DiagPacketType.SUBSYS_REQUEST
    response = diagService.sendRequest(
        diagPackettype,
        "Diagnostic Services/Loopback Command On Modem Request",
        "01 02 03",
        returnObj,
        10000,
    )
    '''Sample V2 command
 	##same as above but using string parameter
	diagPackettype = Common.ttypes.DiagPacketType.SUBSYSV2_REQUEST
	response= diagService.sendRequest(diagPackettype,"UIM MMGSDI Get Info Request","01 02 03",returnObj,10000)
	'''


def execTest(quts_client):
    dataqueueName = "DataQueue1"

    ##Set the callback functions to receive notification whenever the Dataqueue is changed.
    quts_client.setOnDataQueueUpdatedCallback(onDataQueueUpdated)

    ##QUTS sends messages on the what is going on in the system.
    quts_client.setOnMessageCallback(onMessage)

    ##Get a handle to the device Manager. Device manager has all the device related info.
    devManager = quts_client.getDeviceManager()

    ##Get the list of devices connected to the PC that supports Diag.
    deviceList = devManager.getDevicesForService(
        DiagService.constants.DIAG_SERVICE_NAME
    )

    ##print the properties of the device

    devicehandle = deviceList[0]
    listOfProtocols = devManager.getProtocolList(devicehandle)
    for i in range(len(listOfProtocols)):
        if listOfProtocols[i].protocolType == Common.ttypes.ProtocolType.PROT_DIAG:
            print(
                devManager.getChipName(devicehandle, listOfProtocols[i].protocolHandle)
            )

    ##Get the DiagService for the device. This handle will be used for manipulating Diag (send/receive commands etc). The follwoing line get the first Diag device connected in the PC.
    diagService = DiagService.DiagService.Client(
        quts_client.createService(DiagService.constants.DIAG_SERVICE_NAME, devicehandle)
    )

    ##For a single modem device
    if 0 != diagService.initializeService():
        print("Diag init failed")
        return

    ##For Fusion devices where there is multiple Diag devices, you need to get the desired modem's protocolHandle
    ## For each differnt protocol handle that you need to use, CreateService with deviceHandle first and then using the service created, initializeServiceByProtocol using the protocol handle
    '''
    protList = devManager.getProtocolList(deviceList[0])

	##print(deviceList[x])

    for y in range(0, len(protList)  ):
        if(protList[y].protocolType == Common.ttypes.ProtocolType.PROT_DIAG and ("MDM" in   protList[y].description)):	
				##Get the DiagService for the device. This handle will be used for manipulating Diag (send/receive commands etc). The following line get the first Diag device connected in the PC.
            diagService =   DiagService.DiagService.Client(quts_client.createService(DiagService.constants.DIAG_SERVICE_NAME, deviceList[0])) 
            selectedProtocol = protList[y].protocolHandle;
            diagService.initializeServiceByProtocol(selectedProtocol);
            print("Using device , prot" , devManager.getChipName(deviceList[0], selectedProtocol))
             
	
	##Set log mask. For this, you can use the contents of the DMC/CFG file from QXDM
	##diagService.setLoggingMask
	'''
    ## all the data collected from this point will be saved in a HDF file when saveLogFiles is called.
    devManager.startLogging()

    ##Set the filters for items of interest.

    item = {}
    ##item[Common.ttypes.DiagPacketType.RESPONSE] = ["125","124"]
    ##item[Common.ttypes.DiagPacketType.SUBSYS_REQUEST] =  ["50/6"]
    ##item[Common.ttypes.DiagPacketType.SUBSYS_RESPONSE] =  [ "75/9483"]
    ##item[Common.ttypes.DiagPacketType.DEBUG_MSG] = ["0005/0002"]
    ##QXDM and the saved Log files show 33/64005.
    item[Common.ttypes.DiagPacketType.SUBSYS_RESPONSE] = [
        "18/2058",
        "11/37",
        "18/93",
        "75/9483",
    ]
    item[Common.ttypes.DiagPacketType.EVENT] = ["2803", "2804"]

    CreateDataQueueForMonitoring(diagService, item, dataqueueName)

    totalCount = 0
    ##sample diag command call
    sendDiagRequest(diagService)
    for count in range(1):
        FTMCommand(diagService)

    print("FTM commands sent")
    diagPackets = diagService.getDataQueueItems(dataqueueName, 20, 500)
    totalCount += len(diagPackets)
    for i in range(len(diagPackets)):
        print(
            diagPackets[i].packetId,
            " ",
            diagPackets[i].receiveTimeString,
            " ",
            diagPackets[i].packetName,
        )  ##, ' ' , diagPackets[i].summaryText )
    time.sleep(10)

    '''
	##Adding filters and removeing filters
    item = {}
    item[5] =  [ "115"]
    UpdateFiltersToQueue(diagService, item, dataqueueName, "add")
    item = {}
    item[Common.ttypes.DiagPacketType.SUBSYS_RESPONSE] =   [ "11/37","18/93"]
    UpdateFiltersToQueue(diagService, item, dataqueueName, "remove")
    FTMCommand(diagService)
	
    diagPackets = diagService.getDataQueueItems(dataqueueName, 300, 5000)
    print("Total pkts", len(diagPackets))
    print ("List packets ")
    for i in range(len(diagPackets)):
        ##print(diagPackets[i])
        print(diagPackets[i].packetId, " ",diagPackets[i].packetName, ' ' , diagPackets[i].summaryText )
        ##print("----------------------------------------------------")
 
 
    '''
    diagService.removeDataQueue(dataqueueName)
    print("Removed data queue")

    ##save the data. This saves all the data that was generated in teh device, not just the filtered data.
    qutsLogFileFolder = "C:\\temp\\testlog"

    HDF_path = devManager.saveLogFiles(qutsLogFileFolder)

    print(HDF_path)

    diagService.destroyService()


if __name__ == "__main__":
    quts_client = QutsClient.QutsClient("LogSessionLiveSample")
    execTest(quts_client)
