import sys
import os
import time
import datetime
import time
import six

# import DeviceConfigTestCases as devConfig
# import DiagTestCases as QXDMService


from sys import platform
if platform == "linux" or platform == "linux2":
    sys.path.append('/opt/qcom/QUTS/Support/python')
elif platform == "win32":
    sys.path.append('/')
	
import QutsClient
import Common.ttypes

import DiagService.DiagService
import DiagService.constants
import DiagService.ttypes

import QXDMService.QxdmService
import QXDMService.constants
import QXDMService.ttypes

import threading


def main(client, argv):
    devManager = client.getDeviceManager()

    # get only the devices that support Diag, because the current QXDM plugin commands are meant for Diag only.
    deviceList = devManager.getDevicesForService(DiagService.constants.DIAG_SERVICE_NAME)
    protList = devManager.getProtocolList(deviceList[0])
    print("First device in device list: {}".format(deviceList[0]))

    length = len(protList)
    diagProtocolHandle = -1

    for i in range(length):
        if (protList[i].protocolType == 0):  # diag type
            diagProtocolHandle = protList[i].protocolHandle
            print("Found diag Handle " + str(diagProtocolHandle) + " description " + protList[i].description)

    if (diagProtocolHandle == -1):
        print("No diag protocol handle found..returning")
        return

    ## create the QXDM for the device
    qxdmService = QXDMService.QxdmService.Client(
        client.createService(QXDMService.constants.QXDM_SERVICE_NAME, deviceList[0]))

    # # Start the service for the protocol in the selected device
    # if(0 != qxdmService.initializeServiceByProtocol(diagProtocolHandle)):
    #     print("Error in initializeServiceByProtocol")
    #     return
    # else:
    #     print("Initialized Service by protocol successfully")

    if (0 != qxdmService.startQXDM(diagProtocolHandle)):
        print("Error in start QXDM")  # Starts diag service on this prot handle
    else:
        print("Diag Service started on handle " + str(diagProtocolHandle))

    commandList = [
        b'send_data 75 13 100 0 12 50 241 3 0 0 4 64 0 255 7 5 0 255 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 255 0 0 0 0 0 0 0 0 0 0 0 0',
        b'send_data 75 13 8 0',
        b'send_data 75 13 100 0 0 1 5 0 0 0',
        b'send_data 75 13 100 0 1 1 241 3 0 0 0',
        b'send_data 75 13 100 0 7 1 241 3 0 0',
        b'send_data 75 13 100 0 10 1 2 1 0 0 182 4 0 0 30 50 0 0 0 1 0 0 0 127 150 152 0 241 3 0 0 0 0 0 0 0 0 0 0 212 12 168 192 47 19 0 0',
        b'send_data 75 113 0 0 1 0 1 0 0 0 0 0 0 0 136 19 0 0 0 0 0 0 1 0 0 0 1 0 0 0',
        b'send_data 75 113 0 0 1 0 1 0 0 0 1 0 0 0 100 0 0 0 0 0 128 246 112 23 0 0 0 0 0 0',
        b'send_data 75 113 0 0 2 0 1 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
        b'QSHRequest cfg l2lb 0xA6 0x2',
        b'QSHRequest cfg l2lb 0x0D',
        b'QSHRequest cfg l2lb 0xBB 0x0 0xFA00',
        b'QSHRequest cfg l2lb 0x2 0x0013',
        b'QSHRequest cfg l2lb 0x101 0xFA00',
    #   b'run C:\\Dropbox\\send_data.scr',
        b'mode lpm',
        b'mode online',
    #   b'echo this is my log', #Not supported
        b'RequestNVItemRead /nv/item_files/modem/mmode/lte_bandpref',
        b'RequestNVItemWrite /nv/item_files/modem/mmode/lte_bandpref 1']

    commandListLength = len(commandList)

    print("Length of commandlist " + str(commandListLength))

    for i in range(commandListLength):
        if 0 == qxdmService.sendCommand(commandList[i]):
            print("Send Command Successful: {}".format(commandList[i]))
        else:
            print("Send Command Failed: {}".format(commandList[i]))
        #time.sleep(1)

    # done using the service. This will close the QXDM plugin exe that QUTS started.

    qxdmService.destroyService()


if __name__ == '__main__':
    client = QutsClient.QutsClient("TestAutomation")
    main(client, sys.argv[1:])
