#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "test_data_stream"
__version__ = "init"
__author__ = "@henry.fan"
import os
import itertools
import re
import csv

import pytest

import libs.config as cfg
from  libs.ssc_drva.ssc_drva import SscDrvaTest
import libs.quts as quts
from libs.data_process import std_sensor_event_log

using_ssc_drva_keys = [
    'sensor',
    'duration',
    'sample_rate',
    'factory_test',
    'hw_id',
    'delay',
]
driver_msg_log_headers = ['Timestamp', 'Name', 'Message']


def sscdrva_ids(param):
    return " ".join([str(k) + "-" + str(v) for k, v in param.items()])


def dyna_range_id_str(registry_dict):
    words = []
    for k, v in registry_dict.items():
        words.append(f'{k}.{cfg.res_values.get(k, {}).get(v, "unknown")}')
    return f"Range<{'_'.join(words)}>"


def match_summary_text(diag_service, re_pattern, data_queue='data'):
    diag_packets = diag_service.getDataQueueItems(data_queue, 1, 20)
    while diag_packets:
        if re.search(re_pattern, diag_packets[0].summaryText):
            found = True
            break
        diag_packets = diag_service.getDataQueueItems(data_queue, 1, 20)
    else:
        found = False
    return found


# def collect_sscdrva_result(
#     ssc_drva, quts_dev_mgr, quts_diag_service, data_queue, log_path, params
# ):
#     # productname = request.config.getoption("--product")
#     calib_sensor = None
#     diag_packets_list = []
#     bias_result = []
#     result = {
#         'params_set': params,
#         'diag_packets_list': diag_packets_list,
#         'bias_values': bias_result,
#         'hdf': None,
#         'drv_log': None,
#     }
#     file_name = f"{request.cls.__name__}-{request.node.name}"
#     hdflogfile = os.path.join(log_path, f'{file_name}.hdf')
#     drvlogfile = os.path.join(log_path, f'{file_name}.csv')
#
#     has_factory_test = any(
#         ['factory_test' in param for param in params if param]
#     )
#     hdf_logging = any(['sample_rate' in param for param in params if param])
#     has_calibration = False
#     if has_factory_test:
#         has_calibration = any(
#             [param.get('factory_test', -1) == 2 for param in params if param]
#         )
#         if has_calibration:
#             for param in params:
#                 if param and param.get('factory_test', -1) == 2:
#                     calib_sensor = param['sensor']
#                     prev_biasvals = utils.imu_bias_values(productname, calib_sensor)
#                     result['bias_values'].append(prev_biasvals)
#
#     if hdf_logging:
#         quts_dev_mgr.startLogging()
#
#     ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=params)
#     ssc_drva.ssc_drva_run(ssc_drva_cmd)
#
#     diag_packets = quts_diag_service.getDataQueueItems(data_queue, 1, 20)
#     while diag_packets:
#         diag_packets_list.append(diag_packets[0])
#         diag_packets = quts_diag_service.getDataQueueItems(data_queue, 1, 20)
#     if has_calibration and calib_sensor:
#         post_biasvals = utils.imu_bias_values(productname, calib_sensor)
#         bias_result.append(post_biasvals)
#     if hdf_logging:
#         device = quts.get_device_handle(quts_dev_mgr)
#         diag_protocol = quts.get_diag_protocal_handle(quts_dev_mgr, device)
#         quts_dev_mgr.saveLogFilesWithFilenames({diag_protocol: hdflogfile})
#         result.update({'hdf': hdflogfile})
#     result['drv_log'] = drvlogfile
#
#     return result


def verify_fac_test_result(collect_sscdrva_result):
    for params in collect_sscdrva_result['params_set']:
        if 'factory_test' in params:
            # fac_test = collect_sscdrva_result['params_set'][0]["factory_test"]
            fac_test = params["factory_test"]
            re_pattern = rf'Test level {fac_test}: PASS'
            for diag_packets in collect_sscdrva_result['diag_packets_list']:
                if re.search(re_pattern, diag_packets.summaryText):
                    found = True
                    break
            else:
                found = False
            with pytest.assume:
                assert found, f"key word f'Test level {fac_test}: PASS' not found "
            if fac_test == 2:
                prev_biasvals, post_biasvals = collect_sscdrva_result['bias_values']
                with pytest.assume:
                    assert [pre + 1 for pre in prev_biasvals] == list(
                        post_biasvals
                    ), f"bias values [x, y, z]: {prev_biasvals} is not updated after calibration"


def verify_stream_test_result(
    hdf_file,
    # collect_sscdrva_result,
    qseevt_open,
    ignore_odr_min=False,
    ignore_odr_max=False,
):
    # hdf_file = collect_sscdrva_result['hdf']
    csv_logs = qseevt_open.parse_hdf_to_csv(hdf_file)
    for csv_log in csv_logs:
        log_obj = std_sensor_event_log.SeeDrvLog(csv_log, skip_data=1)
        sensor_name = log_obj.sensor
        if not log_obj.odr or log_obj.dest_sensor != 'da_test':
            continue

        with pytest.assume:
            log_obj.check_odr(ignore_min=ignore_odr_min, ignore_max=ignore_odr_max)
        for axis in std_sensor_event_log.axises:
            col_name = f'{sensor_name.capitalize()} {axis.upper()} ({log_obj.unit})'
            with pytest.assume:
                log_obj.check_data_range(col_name, axis)
            with pytest.assume:
                log_obj.check_data_stddev(col_name, axis)
        if sensor_name == cfg.Sensor.mag.value:
            with pytest.assume:
                col_names = [
                    f'{sensor_name.capitalize()} {axis.upper()} ({log_obj.unit})'
                    for axis in std_sensor_event_log.axises
                ]
                log_obj.check_norm_ord(*col_names)

#
# class TestFactoryTest(object):
#     def test_factory_test(self, collect_sscdrva_result):
#         verify_fac_test_result(collect_sscdrva_result)


# @pytest.mark.usefixtures('reset_origin_registry')
# @pytest.mark.usefixtures('change_registry_res_value')
class TestBasicCases:
    def test_data_streaming(self,
                            sensor, odr, hw_id, ssc_drva,
                            quts_dev_mgr, quts_diag_service, log_path, qseevt_app
                            ):
        dur = 30
        params = (dict.fromkeys(using_ssc_drva_keys), None)
        params[0].update({
            'sensor': sensor,
            'sample_rate': odr,
            'duration': dur,
            'hw_id': hw_id
        })
        file_name = 'log'
        hdflogfile = os.path.join(log_path, f'{file_name}.hdf')
        drvlogfile = os.path.join(log_path, f'{file_name}.csv')
        with quts.logging_diag_hdf(quts_dev_mgr, hdflogfile),\
                quts.logging_data_queue(quts_diag_service, drvlogfile) as diag_packets_list:
            ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(params)
            print(ssc_drva_cmd)
            ssc_drva.ssc_drva_run(ssc_drva_cmd)
        verify_stream_test_result(hdflogfile, qseevt_app)
        with open(drvlogfile, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Timestamp', 'Name', 'Message'])
            writer.writeheader()
            for i, diag_packet in enumerate(diag_packets_list):
                writer.writerow(
                    dict(
                        zip(
                            driver_msg_log_headers,
                            [
                                diag_packet.receiveTimeString,
                                diag_packet.packetName,
                                diag_packet.summaryText,
                            ],
                        )
                    )
                )


    def test_factory_test(self, sensor, factest, hw_id):
        assert True


def test_internal_concurrency_stream(sensor, odr0, odr1, hw_id):
    assert True


def test_internal_concurrency_factest(sensor, odr, factest, hw_id):
    assert True


def test_external_concurrency(sensor0, odr0, sensor1, odr1, hw_id):
    assert True


def test_dual_hw(sensor0, odr0, hw_id0, sensor1, odr1, hw_id1):
    assert True
#
#
# class TestDataStream(object):
#     def test_data_stream(self, collect_sscdrva_result, qseevt_app):
#         verify_stream_test_result(collect_sscdrva_result, qseevt_app)
#
#
# class TestInternalConcurrency:
#     def test_internal_stream_concurrency(
#         self, collect_sscdrva_result, qseevt_app
#     ):
#         verify_stream_test_result(collect_sscdrva_result, qseevt_app)
#
#     def test_internal_stream_factory_concurrency(
#         self, collect_sscdrva_result, qseevt_app
#     ):
#         verify_fac_test_result(collect_sscdrva_result)
#         verify_stream_test_result(
#             collect_sscdrva_result, qseevt_app, ignore_odr_max=True
#         )
#
#
# class TestExternalConcurrency:
#     def test_external_concurrency(
#         self, collect_sscdrva_result, qseevt_app
#     ):
#         verify_stream_test_result(collect_sscdrva_result, qseevt_app)
#
#
# class TestDualHardwares:
#     def test_dual_hw_stream(
#         self, collect_sscdrva_result, qseevt_app,
#     ):
#         verify_stream_test_result(collect_sscdrva_result, qseevt_app)
#
#
# @pytest.mark.usefixtures('reset_origin_registry')
# @pytest.mark.usefixtures('change_registry_res_value')
# class TestDynaRange:
#     def test_factory_test(self, collect_sscdrva_result):
#         verify_fac_test_result(collect_sscdrva_result)
#
#     def test_data_stream(
#         self, collect_sscdrva_result, qseevt_app,
#     ):
#         verify_stream_test_result(collect_sscdrva_result, qseevt_app)
