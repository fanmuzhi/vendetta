import sys
import time
import os
from lxml import etree

sys.path.append('/')
import QutsClient
import Common.ttypes


import GpsService.GpsService
import LogSession.LogSession


def makeXml(dataPackets):
    root = etree.Element('GPS')
    for packet in dataPackets:
        content = packet.nmeaPacket.packetText

        child1 = etree.Element('GPS_DT')
        root.append(child1)
        print("content = ", content)
        line = content.split('\n')

        for word in line:
            if line:
                items = word.split(':', 1)
                if len(items) == 2:

                    items[0] = items[0].replace(" ", "_")
                    items[0] = items[0].replace("#", "")
                    items[0] = items[0].replace("(", "_")
                    items[0] = items[0].replace(")", "")
                    items[0] = items[0].replace("/", "_")

                    if not items[0]:
                        items[0] = "None"
                    child2 = etree.Element(items[0])
                    items[1] = items[1].replace("\r", "")
                    child2.text = items[1]
                    child1.append(child2)
    s = etree.tostring(root, pretty_print=True)

    f = open(r"c:\temp\gps.xml", "w")
    result = s.decode("utf-8")
    f.write(result)
    f.close()

    return result


def onMessage(level, location, title, description):
    print("Message Received {} {} ".format(title, description))


def callbackOnDataView(viewname):
    print("data received ", viewname)


s = 0

try:
    client = QutsClient.QutsClient("QUTS Sample")
except Exception as e:
    print("Exception starting client")

if client is None:
    print('\nClient did not instantiate')
else:
    print('\nInitialized Client')

client.setOnMessageCallback(onMessage)
client.setOnDataViewUpdatedCallback(callbackOnDataView)

deviceManager = client.getDeviceManager()

time.sleep(2)

path = [
    os.getcwd()
    + r'\915c56b1-cc17-4300-adc2-ef84a427ebd1_50491_NMEA_Prolific_USB-to-Serial_Comm_Port_(COM21)_0.hdf'
]


logSession = client.openLogSession(path)

deviceList = logSession.getDeviceList()
print("\n\nList of Devices: ")


deviceId = deviceList[0].deviceHandle
print("deviceId = ", deviceId)

listOfProtocols = logSession.getProtocolList(deviceId)
nmeaProtocolHandle = None
nmeaDetectionString = "COM21"
print("\n\nList of Protocols: ")
for item in listOfProtocols:
    if -1 != item.description.find(
        nmeaDetectionString
    ):  # Use the gps device specific name filter here
        nmeaProtocolHandle = item.protocolHandle
    print(item)

if not nmeaProtocolHandle:
    raise Exception(
        "No NMEA protocol found matching description " + nmeaDetectionString
    )
print("nmeaProtocolHandle = ", nmeaProtocolHandle)


nmeaFilter = Common.ttypes.NmeaPacketFilter()
nmeaFilter.nameMask = [r'$GPGGA', r'$GPRMC', r'$GPGSA', r'$GPGSV']


dataPacketFilter = LogSession.ttypes.DataPacketFilter()
dataPacketFilter.protocolHandleList = [nmeaProtocolHandle]
dataPacketFilter.nmeaFilter = nmeaFilter


returnObjNmea = Common.ttypes.NmeaReturnConfig()
returnObjNmea.flags = (
    Common.ttypes.DiagReturnFlags.PARSED_TEXT
    | Common.ttypes.DiagReturnFlags.PACKET_NAME
    | Common.ttypes.DiagReturnFlags.PACKET_ID
    | Common.ttypes.DiagReturnFlags.PACKET_TYPE
)

packetReturnConfig = LogSession.ttypes.PacketReturnConfig()
packetReturnConfig.nmeaConfig = returnObjNmea

logSession.createDataView("data", dataPacketFilter, packetReturnConfig)

packetRange = LogSession.ttypes.PacketRange()
packetRange.indexType = LogSession.ttypes.IndexType.DATA_VIEW_INDEX
packetRange.beginIndex = 0
packetRange.endIndex = 100

dataPackets = logSession.getDataViewItems("data", packetRange)

print("Packets received ", len(dataPackets))


for item in dataPackets:
    print(item.nmeaPacket.packetText)
logSession.removeDataView("data")

print("\n====================================\n")

xmlResult = makeXml(dataPackets)

print(xmlResult)


print("Done")
