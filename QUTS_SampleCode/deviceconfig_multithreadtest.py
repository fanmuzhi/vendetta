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

import DeviceConfigService.DeviceConfigService
import DeviceConfigService.constants
import DeviceConfigService.ttypes

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

    deviceId = 281474976710656
    qmiProtocol = 281479271677952

    deviceConfigService = DeviceConfigService.DeviceConfigService.Client(
    client.createService(DeviceConfigService.constants.DEVICE_CONFIG_SERVICE_NAME, deviceId))

    # deviceConfigService.initializeServiceByProtocol(diagProtocol, qmiProtocol)
    deviceConfigService.initializeService()

    ####################################
    global doRun
    #t1 = threading.Thread(target=task1,args=(deviceManager,))
    t2 = threading.Thread(target=task2,args=(deviceConfigService,))


    #t1.start()
    t2.start()


    time.sleep(3000)
    doRun=0
    print ("doRun set to 0")

    #t1.join()
    t2.join()

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



def task2(deviceConfigService):
    tid = threading.get_ident()
    print("\n", tid, ": thread started ")
    global doRun
    i = 0
    while (doRun == 1):

        print("\n", tid, ": thread started in while loop")
        response = deviceConfigService.backupToXqcn("000000", False, 100000, "")
        print("\n", i, ":", tid, ":response = ", response)

        errCode = deviceConfigService.restoreFromXqcn(response, "000000", True, False, 10000, "")
        print("\n", i, ":", tid, ":errCode = ", errCode)
        i += 1




if __name__ == '__main__':
    main()



