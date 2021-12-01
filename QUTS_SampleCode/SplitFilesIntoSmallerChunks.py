import os
import sys
import time
import shutil

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
    setup_handle_list = False
    diag_protocol_handle = None
    for i in range(len(listOfProtocols)):
        if listOfProtocols[i].protocolType == Common.ttypes.ProtocolType.PROT_DIAG:
            diag_protocol_handle = listOfProtocols[i].protocolHandle
    if diag_protocol_handle is None:
        print("Error:: diag_protocol_handle not found")
        exit(1)

    returnObjDiag = Common.ttypes.DiagReturnConfig()
    ##Add the fields you are interested in processing.
    returnObjDiag.flags = (
        Common.ttypes.DiagReturnFlags.PACKET_NAME
        | Common.ttypes.DiagReturnFlags.PACKET_ID
        | Common.ttypes.DiagReturnFlags.PACKET_TYPE
    )
    returnObjDiag.diagTimeSorted = False

    packetReturnConfig = LogSession.ttypes.PacketReturnConfig()
    packetReturnConfig.diagConfig = returnObjDiag

    ##Assumption is first protocol is diag
    logSession.createDefaultDataView("data", [diag_protocol_handle], packetReturnConfig)

    total_num_packets = logSession.getDataPacketCount(diag_protocol_handle)
    print(f'total number of packets {total_num_packets}')

    chunk_number = int(sys.argv[1])
    print(f'splitting the file into {chunk_number} chunks')
    chunk_size = int(total_num_packets / chunk_number)
    print(f'each file contains {chunk_size} or so packets')
    start_idx = 0
    temp_folder = sys.argv[2] + '\\' + 'splitted_files'
    for idx in range(chunk_number):
        if idx == chunk_number - 1:
            end_index = total_num_packets
        else:
            end_index = min(start_idx + chunk_size, total_num_packets)
        cur_chunk_indexes = range(start_idx, end_index)
        print(
            f"saving file with index from {start_idx} to {end_index} to {temp_folder}"
        )
        logSession.saveDataViewItemsByIndex(
            "data",
            temp_folder + '_' + str(start_idx) + '_' + str(end_index),
            cur_chunk_indexes,
        )
        start_idx = end_index

    print(f'files saved to {sys.argv[2]}')
    logSession.removeDataView("data")


def getLastError(logSession):
    print("Last Error ", logSession.getLastError())


def execTest(quts_client):
    time_start = time.time()

    filePath = os.path.join(os.getcwd(), "sample_hdf", "CAT4_RMNet_13.hdf")

    print(filePath)

    # QUTS LoadSession
    logSession = quts_client.openLogSession(
        [filePath]
    )  # Loads a list of ISF/HDF files. Can be file name or foldername.
    # GetDeviceDetails(logSession)
    if logSession == 0:
        print("Unable to open logSession")
        return False

    ProcessFiles(logSession)


if __name__ == "__main__":
    quts_client = QutsClient.QutsClient("LogSessionSample")  ##Initialize()
    num_arg = len(sys.argv)
    if num_arg < 3:
        print(
            'cmd line argument: <num of smaller files to split into> <destination folder to save file>'
        )
        exit(0)
    execTest(quts_client)
