import sys
if sys.platform.startswith("linux"):
    sys.path.append('/opt/qcom/QUTS/Support/python')
elif sys.platform.startswith("win"):
    sys.path.append('/')
elif sys.platform.startswith("darwin"):
    sys.path.append('/Applications/Qualcomm/QUTS/QUTS.app/Contents/Support/python')

import QutsClient
import DeviceConfigService.DeviceConfigService
import DeviceConfigService.constants
import DeviceConfigService.ttypes
import traceback
import time

try:
    client = QutsClient.QutsClient("Test Sample")
    time.sleep(5)
    devmgr = client.getDeviceManager()
    deviceList = devmgr.getDeviceList()
    dev = 0;
    for device in deviceList:
        if(device.description.find('Qualcomm') != -1):
            print ("=====Qualcomm Device=====")
            print (device.description)
            print ("Device Serial Number", device.serialNumber)
            print ("Adb Serial Number", device.adbSerialNumber)
            dev=device.deviceHandle
            break;

    devCfg=DeviceConfigService.DeviceConfigService.Client(client.createService(DeviceConfigService.constants.DEVICE_CONFIG_SERVICE_NAME, dev))
    if (devCfg == None or 0 != devCfg.initializeService()):
        print(self.clientName, serviceName, "init failed")

    try:
        if (devCfg.checkSpc("000000")):
            err = devCfg.efsPutFile(r"/nv/text.txt", bytes(b'x00x01'), DeviceConfigService.ttypes.FileSystem.FS_PRIMARY)
            if(err != 0):
                print(err)
    except Exception as e:
        print("Exception", devCfg.getLastError())
            

except Exception as e:
    print(traceback.format_exc())