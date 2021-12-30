#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "test_data_stream"
__version__ = "init"
__author__ = "@henry.fan"

import re

import pytest

import libs.config as cfg
from libs.data_process import std_sensor_event_log


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
    collect_sscdrva_result,
    qseevt_open,
    sensor_info_txt,
    ignore_odr_min=False,
    ignore_odr_max=False,
):
    hdf_file = collect_sscdrva_result['hdf']
    csv_logs = qseevt_open.parse_hdf_to_csv(hdf_file, sensor_info_txt)
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


class TestFactoryTest(object):
    def test_factory_test(self, collect_sscdrva_result):
        verify_fac_test_result(collect_sscdrva_result)


class TestDataStream(object):
    def test_data_stream(self, collect_sscdrva_result, qseevt_open, sensor_info_txt):
        verify_stream_test_result(collect_sscdrva_result, qseevt_open, sensor_info_txt)


class TestInternalConcurrency:
    def test_internal_stream_concurrency(
        self, collect_sscdrva_result, qseevt_open, sensor_info_txt
    ):
        verify_stream_test_result(collect_sscdrva_result, qseevt_open, sensor_info_txt)

    def test_internal_stream_factory_concurrency(
        self, collect_sscdrva_result, qseevt_open, sensor_info_txt
    ):
        verify_fac_test_result(collect_sscdrva_result)
        verify_stream_test_result(
            collect_sscdrva_result, qseevt_open, sensor_info_txt, ignore_odr_max=True
        )


class TestExternalConcurrency:
    def test_external_concurrency(
        self, collect_sscdrva_result, qseevt_open, sensor_info_txt
    ):
        verify_stream_test_result(collect_sscdrva_result, qseevt_open, sensor_info_txt)


class TestDualHardwares:
    def test_dual_hw_stream(
        self, collect_sscdrva_result, qseevt_open, sensor_info_txt,
    ):
        verify_stream_test_result(collect_sscdrva_result, qseevt_open, sensor_info_txt)


@pytest.mark.usefixtures('reset_origin_registry')
@pytest.mark.usefixtures('change_registry_res_value')
class TestDynaRange:
    def test_factory_test(self, collect_sscdrva_result):
        verify_fac_test_result(collect_sscdrva_result)

    def test_data_stream(
        self, collect_sscdrva_result, qseevt_open, sensor_info_txt,
    ):
        verify_stream_test_result(collect_sscdrva_result, qseevt_open, sensor_info_txt)
