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
    tcpServerList = devManager.getTcpServerList()
    print("Tcp Server List = ", tcpServerList)

    print("All Done")


if __name__ == '__main__':
    try:
        client = QutsClient.QutsClient("TcpServerList")

    except Exception as e:
        print("Exception starting client")
    main(client)
