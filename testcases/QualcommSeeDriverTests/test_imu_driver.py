#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "test_data_stream"
__version__ = "init"
__author__ = "@henry.fan"

# import os
# import re
import itertools
import pytest
from lib.data_process import std_sensor_event_log

# from lib.sensor_file.sensor_file import FacCalBias
from lib.utils import *

#
productname = 'bmi3x0'
# n_hw = 1
# hwid = list(range(n_hw))
# # sensor_list = ['accel', 'gyro']
# sensor_list = ['accel']
# streamtest_odr_list = [-2, 50, 100, 200, -1, -3.0]
# # streamtest_odr_list = [-2, 50]
# factest_type_list = [1, 2, 3]
# sensor_streamtest_dur = 10
# sensor_factest_dur = 5
# ssc_drva_delay = 2
# null_params = [None]


def id_names(param):
    return " ".join([str(k) + "-" + str(v) for k, v in param.items()])


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
    def test_factory_test(self, factorytest, ssc_drva, quts_diag_service, data_queue):
        sensor = factorytest[0]["sensor"]
        fac_test = factorytest[0]["factory_test"]
        prev_biasvals = imu_bias_values(productname, sensor)
        cmd = ssc_drva.set_ssc_drva_cmd(factorytest)
        ssc_drva.ssc_drva_run(cmd)
        with pytest.assume:
            assert match_summary_text(
                quts_diag_service, rf'Test level {fac_test}: PASS', data_queue
            ), f"key word f'Test level {fac_test}: PASS' not found "
        if fac_test == 2:
            post_biasvals = imu_bias_values(productname, sensor)
            with pytest.assume:
                assert [pre + 1 for pre in prev_biasvals] == list(
                    post_biasvals
                ), f"bias values [x, y, z]: {prev_biasvals} is not updated after calibration"


# @pytest.mark.skip
class TestDataStream(object):
    def test_data_stream(
        self, streamtest, ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt,
    ):
        param_sets = streamtest
        log_csv_list = collect_csvs(
            ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt, param_sets
        )
        for csv_log in log_csv_list:
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
        self, intern_conc_streamtest, ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt,
    ):
        param_sets = intern_conc_streamtest
        log_csv_list = collect_csvs(
            ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt, param_sets
        )
        for csv_log in log_csv_list:
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
        self,
        intern_conc_factest,
        ssc_drva,
        quts_dev_mgr,
        quts_diag_service,
        data_queue,
        qseevt,
        sensor_info_txt,
    ):
        param_sets = intern_conc_factest
        sensor = param_sets[0]["sensor"]
        fac_test = param_sets[1]["factory_test"]
        prev_biasvals = imu_bias_values(productname, sensor)
        log_csv_list = collect_csvs(
            ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt, param_sets
        )
        with pytest.assume:
            assert match_summary_text(
                quts_diag_service, rf'Test level {fac_test}: PASS', data_queue
            ), f"key word f'Test level {fac_test}: PASS' not found "
        if fac_test == 2:
            post_biasvals = imu_bias_values(productname, sensor)
            with pytest.assume:
                assert [pre + 1 for pre in prev_biasvals] == list(post_biasvals)
        for csv_log in log_csv_list:
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


# @pytest.mark.skipif(len(sensor_list) < 2, reason="at least 2 sensors needed in external concurrency test")
class TestExternalConcurrency:
    # @pytest.mark.skip
    def test_external_concurrency(
        self, extern_conc_streamtest, ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt,
    ):
        param_sets = extern_conc_streamtest
        log_csv_list = collect_csvs(
            ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt, param_sets
        )
        for csv_log in log_csv_list:
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


ranges = [
    {'accel': 0, 'gyro': 1},
    {'accel': 1, 'gyro': 2},
    {'accel': 2, 'gyro': 3},
    {'accel': 3, 'gyro': 4},
]


def resvalue_id_str(registry_dict):
    words = []
    for k, v in registry_dict.items():
        words.append(f'{k}.{cfg.res_values.get(k, {}).get(v, "unknown")}')
        # words.append(cfg.res_values.get(k, {}).get(v, "unknown"))
    return f"Range<{'_'.join(words)}>"


# @pytest.mark.skip
@pytest.mark.usefixtures('reset_origin_registry')
@pytest.mark.parametrize(
    'change_registry_res_value',
    ranges,
    ids=[resvalue_id_str(r) for r in ranges],
    indirect=True,
)
class TestDynaRange:
    @pytest.mark.usefixtures('change_registry_res_value')
    def test_factory_test(self, factorytest, ssc_drva, quts_diag_service, data_queue):
        sensor = factorytest[0]["sensor"]
        fac_test = factorytest[0]["factory_test"]
        prev_biasvals = imu_bias_values(productname, sensor)
        cmd = ssc_drva.set_ssc_drva_cmd(factorytest)
        ssc_drva.ssc_drva_run(cmd)
        with pytest.assume:
            assert match_summary_text(
                quts_diag_service, rf'Test level {fac_test}: PASS', data_queue
            ), f"key word f'Test level {fac_test}: PASS' not found "
        if fac_test == 2:
            post_biasvals = imu_bias_values(productname, sensor)
            with pytest.assume:
                assert [pre + 1 for pre in prev_biasvals] == list(
                    post_biasvals
                ), f"bias values [x, y, z]: {prev_biasvals} is not updated after calibration"

    @pytest.mark.usefixtures('change_registry_res_value')
    def test_data_stream(
        self, streamtest, ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt,
    ):
        param_sets = streamtest
        log_csv_list = collect_csvs(
            ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt, param_sets
        )
        for csv_log in log_csv_list:
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
