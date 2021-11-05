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
 


s = 0

def onserviceevent(service_name, event_id, event_description):
    print ('on_service_event:service name: {0} occurred {1}  : {2}'.format(service_name,event_id,event_description))

def onDataQueueUpdated(queueName, queueSize):
    print("On data queue", queueName, " update ", queueSize)
    global s
    s = queueSize
	
def onMessage(level, location, title, description):
	logger.info ("Message Received {} {} ".format( title , description))
	

try:
    client = QutsClient.QutsClient("QUTS Sample")
except Exception as e:
    print("Exception starting client")

if client is None:
    print('\nClient did not instantiate')
else:
    print('\nInitialized Client')

client.setOnDataQueueUpdatedCallback(onDataQueueUpdated)

client.setOnServiceEventCallback(onserviceevent)
client.setOnMessageCallback(onMessage)
 
 
 
deviceList =  client.getDeviceManager().getDevicesForService(QmiService.constants.QMI_SERVICE_NAME)
print("Devices Location", deviceList[0])


qmiService = QmiService.QmiService.Client(
    client.createService(QmiService.constants.QMI_SERVICE_NAME, deviceList[0]))



return_flags = Common.ttypes.QmiReturns()
return_flags.flags = Common.ttypes.QmiReturnFlags.PARSED_XML | Common.ttypes.QmiReturnFlags.PACKET_NAME
filter = Common.ttypes.QmiPacketFilter()
qmi_indication_filter = []

filter.idOrNameMask = {
    Common.ttypes.QmiPacketType.QMI_INDICATION: qmi_indication_filter}
	
qmiService.initializeService("36")
indication_list = ['pdc_get_default_config_info_ind_msg']  


for indication in indication_list:
    qmi_indication_filter.append(indication)
filter.idOrNameMask = {
    Common.ttypes.QmiPacketType.QMI_INDICATION: qmi_indication_filter}
print ("indications response")
print (qmiService.createIndicationQueue('pdc',filter,return_flags ))
 

pdc_input = {
    'config_type': {
        'config_type': '0',
    },
	'ind_token': {
        'ind_token': '1',
    }
}
input_xml = dicttoxml(pdc_input, custom_root='opt', attr_type=False)
input_xml = input_xml.decode("UTF-8")
print (input_xml)
 
qmiSamplereqId = 'pdc_get_default_config_info_req_msg'  
response = qmiService.sendRequest(qmiSamplereqId, input_xml, return_flags, 7000)

for i in range(10):
    time.sleep(1)
    
    if s != 0:
        print("indication message")
        print (qmiService.getIndications('pdc', s,1000))
        s = 0
 
qmiService.destroyService()

print("All Done")
	

