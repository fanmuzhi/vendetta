import sys

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
import time

f_dmc = r'C:\Users\FNH1SGH\Desktop\mydmc.dmc'


def onMessage(level, location, title, description):
    print(title + " " + description)


client = QutsClient.QutsClient("Python test")

client.setOnMessageCallback(onMessage)

devices = client.getDeviceManager().getDevicesForService(
    DiagService.constants.DIAG_SERVICE_NAME
)

for device in devices:
    diagService = DiagService.DiagService.Client(
        client.createService(DiagService.constants.DIAG_SERVICE_NAME, device)
    )
    diagService.initializeService()

    diagService.setLoggingMask(
        QutsClient.readFile(f_dmc), Common.ttypes.LogMaskFormat.DMC_FORMAT
    )

    time.sleep(1000)
