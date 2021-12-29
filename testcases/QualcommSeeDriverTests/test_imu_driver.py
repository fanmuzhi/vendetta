#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "test_data_stream"
__version__ = "init"
__author__ = "@henry.fan"

# import os
import sys

# import re
import pytest
from libs.data_process import std_sensor_event_log

# from libs.sensor_file.sensor_file import FacCalBias
from libs.utils import *


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


# @pytest.mark.skip
class TestFactoryTest(object):
    # @pytest.mark.skip
    def test_factory_test(self, collect_sscdrva_result):
        fac_test = collect_sscdrva_result['params_set'][0]["factory_test"]
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
        # print(collect_sscdrva_result)


# @pytest.mark.skip
class TestDataStream(object):
    def test_data_stream(self, collect_sscdrva_result, qseevt_open, sensor_info_txt):
        hdf_file = collect_sscdrva_result['hdf']
        csv_logs = qseevt_open.parse_hdf_to_csv(hdf_file, sensor_info_txt)
        for csv_log in csv_logs:
            log_obj = std_sensor_event_log.SeeDrvLog(csv_log, skip_data=1)
            sensor_name = log_obj.sensor
            if not log_obj.odr or log_obj.dest_sensor != 'da_test':
                continue

            with pytest.assume:
                log_obj.check_odr()
            for axis in std_sensor_event_log.axises:
                col_name = f'{sensor_name.capitalize()} {axis.upper()} ({log_obj.unit})'
                with pytest.assume:
                    log_obj.check_data_range(col_name, axis)
                with pytest.assume:
                    log_obj.check_data_stddev(col_name, axis)


# @pytest.mark.skip
class TestInternalConcurrency:
    # @pytest.mark.skip
    def test_internal_stream_concurrency(
        self, collect_sscdrva_result, qseevt_open, sensor_info_txt
    ):
        hdf_file = collect_sscdrva_result['hdf']
        csv_logs = qseevt_open.parse_hdf_to_csv(hdf_file, sensor_info_txt)

        for csv_log in csv_logs:
            log_obj = std_sensor_event_log.SeeDrvLog(csv_log, skip_data=1)
            sensor_name = log_obj.sensor
            if not log_obj.odr or log_obj.dest_sensor != 'da_test':
                continue

            with pytest.assume:
                log_obj.check_odr()
            for axis in std_sensor_event_log.axises:
                col_name = f'{sensor_name.capitalize()} {axis.upper()} ({log_obj.unit})'
                with pytest.assume:
                    log_obj.check_data_range(col_name, axis)
                with pytest.assume:
                    log_obj.check_data_stddev(col_name, axis)

    # @pytest.mark.skip
    def test_internal_stream_factory_concurrency(
        self, collect_sscdrva_result, qseevt_open, sensor_info_txt
    ):
        hdf_file = collect_sscdrva_result['hdf']
        csv_logs = qseevt_open.parse_hdf_to_csv(hdf_file, sensor_info_txt)
        fac_test = collect_sscdrva_result['params_set'][1]["factory_test"]
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
        for csv_log in csv_logs:
            log_obj = std_sensor_event_log.SeeDrvLog(csv_log, skip_data=1)
            sensor_name = log_obj.sensor
            if not log_obj.odr or log_obj.dest_sensor != 'da_test':
                continue

            with pytest.assume:
                log_obj.check_odr(ignore_max=True)
            for axis in std_sensor_event_log.axises:
                col_name = f'{sensor_name.capitalize()} {axis.upper()} ({log_obj.unit})'
                with pytest.assume:
                    log_obj.check_data_range(col_name, axis)
                with pytest.assume:
                    log_obj.check_data_stddev(col_name, axis)


class TestExternalConcurrency:
    # @pytest.mark.skip
    def test_external_concurrency(
        self, collect_sscdrva_result, qseevt_open, sensor_info_txt
    ):
        hdf_file = collect_sscdrva_result['hdf']
        csv_logs = qseevt_open.parse_hdf_to_csv(hdf_file, sensor_info_txt)
        for csv_log in csv_logs:
            log_obj = std_sensor_event_log.SeeDrvLog(csv_log, skip_data=1)
            sensor_name = log_obj.sensor
            if not log_obj.odr or log_obj.dest_sensor != 'da_test':
                continue

            with pytest.assume:
                log_obj.check_odr()
            for axis in std_sensor_event_log.axises:
                col_name = f'{sensor_name.capitalize()} {axis.upper()} ({log_obj.unit})'
                with pytest.assume:
                    log_obj.check_data_range(col_name, axis)
                with pytest.assume:
                    log_obj.check_data_stddev(col_name, axis)


class TestDualHardwares:

    def test_dual_hw_stream(
            self,
            collect_sscdrva_result,
            qseevt_open,
            sensor_info_txt,
    ):
        hdf_file = collect_sscdrva_result['hdf']
        csv_logs = qseevt_open.parse_hdf_to_csv(hdf_file, sensor_info_txt)
        for csv_log in csv_logs:
            log_obj = std_sensor_event_log.SeeDrvLog(csv_log, skip_data=1)
            sensor_name = log_obj.sensor
            if not log_obj.odr or log_obj.dest_sensor != 'da_test':
                continue

            with pytest.assume:
                log_obj.check_odr()
            for axis in std_sensor_event_log.axises:
                col_name = f'{sensor_name.capitalize()} {axis.upper()} ({log_obj.unit})'
                with pytest.assume:
                    log_obj.check_data_range(col_name, axis)
                with pytest.assume:
                    log_obj.check_data_stddev(col_name, axis)


# @pytest.mark.skip
@pytest.mark.usefixtures('reset_origin_registry')
@pytest.mark.usefixtures('change_registry_res_value')
class TestDynaRange:
    # @pytest.mark.usefixtures('change_registry_res_value')
    def test_factory_test(self, collect_sscdrva_result):
        fac_test = collect_sscdrva_result['params_set'][0]["factory_test"]
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

    # @pytest.mark.usefixtures('change_registry_res_value')
    def test_data_stream(
        self,
        collect_sscdrva_result,
        qseevt_open,
        sensor_info_txt,
    ):
        hdf_file = collect_sscdrva_result['hdf']
        csv_logs = qseevt_open.parse_hdf_to_csv(hdf_file, sensor_info_txt)
        for csv_log in csv_logs:
            log_obj = std_sensor_event_log.SeeDrvLog(csv_log, skip_data=1)
            sensor_name = log_obj.sensor
            if not log_obj.odr or log_obj.dest_sensor != 'da_test':
                continue

            with pytest.assume:
                log_obj.check_odr()
            for axis in std_sensor_event_log.axises:
                col_name = f'{sensor_name.capitalize()} {axis.upper()} ({log_obj.unit})'
                with pytest.assume:
                    log_obj.check_data_range(col_name, axis)
                with pytest.assume:
                    log_obj.check_data_stddev(col_name, axis)


# def main():
#     pytest.main(
#         args=argv,
#     )


if __name__ == '__main__':
    product = ''
    defualt_testpath = r'testcases\QualcommSeeDriverTests\test_imu_driver.py'
    default_args = [
        # '--lf',
        '-v',
        '--capture=sys',
        '--tb=native',
        # f'--html={utils.datetime_str()}_{product}_report.html',
        '-p',
        'no:faulthandler',
        '-W ignore::DeprecationWarning',
    ]

    argv = sys.argv[1:]

    # if not argv[0].startswith(defualt_testpath):
    #     argv = [defualt_testpath] + argv
    # if '--product' not in argv or '--product' == argv[-1]:
    #     print("argument --product not assigned")
    #     sys.exit(1)
    # elif not utils.get_sensorlist(argv[argv.index('--product') + 1]):
    #     print('invalid product name')
    #     sys.exit(1)
    # else:
    #     fhtmlreport = f'{utils.datetime_str()}_{product}_report.html'
    #     argv.append(f'--html={fhtmlreport}')
    #
    # for arg in default_args:
    #     if arg not in argv:
    #         argv.append(arg)
    # print(f'pytest {" ".join(argv)}')
    pytest.main(args=argv,)
