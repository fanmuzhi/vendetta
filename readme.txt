usage: eg: autotest_app_v.1.4.0.exe --product bmi3x0
other pytest command line arguments/flags are accepted and supported, eg: --co, --lf, etc.
Updates:
	v1.2.0 2022.01.20: support mag sensor if product includes mag sensor in like bmmXXX and bmxXXX
	
	v1.4.0 2022.01.20: 
		- retrieve existing sensor info from the ssc_sensor_info returned text for test generation and execution, replacing code formed sensor info in previous versions
		- executeble parameters for different sensors are not hardcoded in config.py but as configured in sensor info text, such as ODRs, Ranges, SelfTests, HW_ID, etc
		- app argument --nhw is removed and not used any more, this info is realtime readout from test device
		- fix test generated qualcomm logs and test report stored in different test result dir bug
	v1.5.0 2022.03.16
		- cover extra testcases for accel and gyro sensor described in Jira ticket [BPDD-1891]<https://rb-tracker.bosch.com/tracker06/browse/BPDD-1891>