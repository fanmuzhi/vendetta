import sys
import time

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


def main(client):
    print("test started")
    devManager = client.getDeviceManager()
    deviceList = devManager.getDeviceList()
    if len(deviceList) == 0:
        ## wait for QUTS to get the list of devices.
        time.sleep(5)
        deviceList = devManager.getDeviceList()

    devices = devManager.getDevicesForService(DiagService.constants.DIAG_SERVICE_NAME)
    ##print(devices)
    ##print("Got device manager")
    for device in devices:
        protocolList = devManager.getProtocolList(device)
        ##print(protocolList)
        for protocol in protocolList:
            if protocol.protocolType == Common.ttypes.ProtocolType.PROT_DIAG:
                print(protocol)
                imageInfo = devManager.getDeviceImageInfoByProtocol(
                    protocol.protocolHandle
                )
                print("imageInfo = ", imageInfo)

    print("All Done")


if __name__ == '__main__':
    try:
        client = QutsClient.QutsClient("ImageInfoTest")

    except Exception as e:
        print("Exception starting client")
    main(client)
