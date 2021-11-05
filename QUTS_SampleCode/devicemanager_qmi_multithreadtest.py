import sys
import time
from dicttoxml import dicttoxml

if sys.platform.startswith("linux"):
    sys.path.append('/opt/qcom/QUTS/Support/python')
elif sys.platform.startswith("win"):
    sys.path.append('/')
elif sys.platform.startswith("darwin"):
    sys.path.append('/Applications/Qualcomm/QUTS/QUTS.app/Contents/Support/python')
    
import QutsClient
import Common.ttypes

import QmiService.QmiService
import QmiService.constants
import QmiService.ttypes

import threading

doRun = 1

def main():

    e = threading.Event()

    try:
        client = QutsClient.QutsClient("QUTS Sample", multithreadedClient=True)
    except Exception as e:
        print("Exception starting client")

    if client is None:
        print('\nClient did not instantiate')
    else:
        print('\nInitialized Client')

    deviceManager = client.getDeviceManager()

    time.sleep(2)

    deviceList = deviceManager.getServicesList()
    print("\n\nList of Services: ", deviceList)

    deviceList = deviceManager.getDevicesForService(QmiService.constants.QMI_SERVICE_NAME)
    print("Devices Location: ", deviceList)

    ####################################
    global doRun
    t1 = threading.Thread(target=task1,args=(deviceManager,))
    t2 = threading.Thread(target=task2,args=(deviceManager,))
    t3 = threading.Thread(target=task3, args=(deviceManager,client,))
    t4 = threading.Thread(target=task3, args=(deviceManager, client,))

    t3.start()
    t4.start()
    time.sleep(1.5)
    t1.start()
    t2.start()


    time.sleep(3000)
    doRun=0
    print ("doRun set to 0")

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    time.sleep(2)
    print("All Done")



def task1(deviceManager):
    tid = threading.get_ident()
    print("\n", tid, ": thread started ")
    global doRun
    j = 0
    while(doRun==1):
        print("\n", tid, ": thread started in while loop")
        servicesList = deviceManager.getServicesList()
        print("\n" ,j,":", tid, ": List of Services: ", servicesList)
        j += 1



def task2(deviceManager):
    tid = threading.get_ident()
    print("\n", tid, ": thread started ")
    global doRun
    i = 0
    while (doRun == 1):

        print("\n", tid, ": thread started in while loop")
        servicesList = deviceManager.getServicesList()

        print("\n", i, ":",tid, ": List of Services: ", servicesList)
        i += 1


def task3(deviceManager,client):
    tid = threading.get_ident()
    print("\n", tid, ": thread started ")
    global doRun
    while (doRun == 1):

        deviceList = deviceManager.getDevicesForService(QmiService.constants.QMI_SERVICE_NAME)
        print("\n", tid, ": Devices Location: ", deviceList)

        deviceList = deviceManager.getDeviceList()
        print("\n", tid, ": List of Devices: ", deviceList)

        deviceId = 281474976710656
        qmiProtocol = 281479271677952

        listOfProtocols = deviceManager.getProtocolList(deviceId)
        print("\n", tid, ": List of Protocols: ", str(listOfProtocols))

        qmiService = QmiService.QmiService.Client(
            client.createService(QmiService.constants.QMI_SERVICE_NAME, deviceId))

        return_flags = Common.ttypes.QmiReturns()
        return_flags.flags = 256  # Common.ttypes.QmiReturnFlags.PARSED_XML | Common.ttypes.QmiReturnFlags.PACKET_NAME

        qmiService.initializeServiceByProtocol(qmiProtocol, "WMS")

        ##########
        for i in range(1):
            print("======================================================================")
            print("loop no", i)
            wms_input = {
                'raw_message_data': {
                    'format': '6'
                    , 'len': '17'
                    , 'instance_0': 0
                    , 'instance_1': 1
                    , 'instance_2': 1
                    , 'instance_3': 10
                    , 'instance_4': 129
                    , 'instance_5': 152
                    , 'instance_6': 72
                    , 'instance_7': 70
                    , 'instance_8': 65
                    , 'instance_9': 36
                    , 'instance_10': 131
                    , 'instance_11': 0
                    , 'instance_12': 0
                    , 'instance_13': 3
                    , 'instance_14': 215
                    , 'instance_15': 0
                    , 'instance_16': 20
                }
            }
            input_xml = dicttoxml(wms_input, custom_root='opt', attr_type=False)
            input_xml = input_xml.decode("UTF-8")
            print(input_xml)
            qmiSamplereqId = 'wms_raw_send_req'
            response = qmiService.sendRequest(qmiSamplereqId, input_xml, return_flags, 7000)
            print("\n", tid, ": response = " , response)
            time.sleep(1)


    qmiService.destroyService()


def task4(deviceManager,client):
    tid = threading.get_ident()
    print("\n", tid, ": thread started ")
    global doRun
    while (doRun == 1):

        deviceList = deviceManager.getDevicesForService(QmiService.constants.QMI_SERVICE_NAME)
        print("\n", tid, ": Devices Location: ", deviceList)

        deviceList = deviceManager.getDeviceList()
        print("\n", tid, ": List of Devices: ", deviceList)

        deviceId = 281474976710656
        qmiProtocol = 281479271677952

        listOfProtocols = deviceManager.getProtocolList(deviceId)
        print("\n", tid, ": List of Protocols: ", str(listOfProtocols))

        qmiService = QmiService.QmiService.Client(
            client.createService(QmiService.constants.QMI_SERVICE_NAME, deviceId))

        return_flags = Common.ttypes.QmiReturns()
        return_flags.flags = 256  # Common.ttypes.QmiReturnFlags.PARSED_XML | Common.ttypes.QmiReturnFlags.PACKET_NAME

        qmiService.initializeServiceByProtocol(qmiProtocol, "WMS")

        ##########
        for i in range(1):
            print("======================================================================")
            print("loop no", i)
            wms_input = {
                'raw_message_data': {
                    'format': '6'
                    , 'len': '17'
                    , 'instance_0': 0
                    , 'instance_1': 1
                    , 'instance_2': 1
                    , 'instance_3': 10
                    , 'instance_4': 129
                    , 'instance_5': 152
                    , 'instance_6': 72
                    , 'instance_7': 70
                    , 'instance_8': 65
                    , 'instance_9': 36
                    , 'instance_10': 131
                    , 'instance_11': 0
                    , 'instance_12': 0
                    , 'instance_13': 3
                    , 'instance_14': 215
                    , 'instance_15': 0
                    , 'instance_16': 20
                }
            }
            input_xml = dicttoxml(wms_input, custom_root='opt', attr_type=False)
            input_xml = input_xml.decode("UTF-8")
            print(input_xml)
            qmiSamplereqId = 'wms_raw_send_req'
            response = qmiService.sendRequest(qmiSamplereqId, input_xml, return_flags, 7000)
            print("\n", tid, ": response = " , response)
            time.sleep(1)


    qmiService.destroyService()


if __name__ == '__main__':
    main()



