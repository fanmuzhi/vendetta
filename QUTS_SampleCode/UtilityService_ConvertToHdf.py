import os
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

import LogSession.LogSession
import LogSession.constants
import LogSession.ttypes

def execTest(quts_client, logPath):
    startTime = time.time()
    if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
        saveFolder = os.getcwd() + "/testlog"
    elif sys.platform == "win32":
        saveFolder = r"C:\temp\testlog\\"
    utilityService  = quts_client.getUtilityService()
    logFiles = utilityService.convertToHdf({logPath}, saveFolder)
    print("Saved log paths: ", logFiles)
    print("Elapsed time ", time.time() - startTime)

if __name__ == "__main__":
    quts_client = QutsClient.QutsClient("UtilityService_ConvertToHdfSample")
    print("Log path entered: " + sys.argv[1])
    execTest(quts_client, sys.argv[1])
    quts_client.stop()