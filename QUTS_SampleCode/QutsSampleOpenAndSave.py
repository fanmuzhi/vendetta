## For detailed description of the QUTS APIs, please refer to QUTS documentation at "C:\Program Files (x86)\Qualcomm\QUTS\QUTS_User_Guide.docm"
##This sample includes connecting to device, using Diag, sending commands and collecting logs.
import os
import sys
import time
import re
 
##The path where QUTS files are installed
from sys import platform
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

def execTest(quts_client, logPath):
    
    print("Opening log path: ", logPath)
    logSession = quts_client.openLogSession({logPath})
    
    ##save the data. This saves all the data that was generated in teh device, not just the filtered data. 
	## the files in the folder can be .hdf, .isf, .bin or .qmdl2
    if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
        qutsLogFileFolder = os.getcwd() + "/testlog"
    elif sys.platform == "win32":
        qutsLogFileFolder = "C:\\temp\\testlog"
    logFiles = logSession.saveLogFiles(qutsLogFileFolder) 
    print("Saved log paths: ", logFiles)
 
if __name__ == "__main__":
    quts_client = QutsClient.QutsClient("OpenAndSaveSample")
    # sys.argv[1] = os.curdir
    print("Log path entered: " + sys.argv[1])
    execTest(quts_client, sys.argv[1])