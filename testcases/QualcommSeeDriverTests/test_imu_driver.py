#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "test_data_stream"
__version__ = "init"
__author__ = "@henry.fan"
import os
import re

import pytest

import libs.config as cfg
import libs.quts as quts
from libs.data_process import std_sensor_event_log
from libs import utils

using_ssc_drva_keys = [
    'sensor',
    'duration',
    'sample_rate',
    'factory_test',
    'hw_id',
    'delay',
]
driver_msg_log_headers = ['Timestamp', 'Name', 'Message']


def found_pass_in_log(fac_test, diag_packets_list):
    re_pattern = rf'Test level {fac_test}: PASS'
    return any(
        re.search(re_pattern, diag_packets.summaryText)
        for diag_packets in diag_packets_list
    )
    # with pytest.assume:
    #     assert found, f"key word f'Test level {fac_test}: PASS' not found "


def bias_ver_updated(prev_biasvals, post_bias):
    with pytest.assume:
        return [pre + 1 for pre in prev_biasvals] == list(post_bias)


# def odr_in_range(log_obj, ignore_min=False, ignore_max=False):
#     col_name = 'interval'
#     intv = std_sensor_event_log.calc_interval_ms(log_obj.odr)
#     l_limit = 0 * intv if not ignore_min else -float('inf')
#     h_limit = 1.8 * intv if not ignore_max else float('inf')
#     intv_min = log_obj.stats[col_name]['min']
#     intv_max = log_obj.stats[col_name]['max']
#     assert (
#             l_limit
#             <= log_obj.stats[col_name]['min']
#             < log_obj.stats[col_name]['max']
#             < h_limit
#     ), f'{log_obj.sensor} time interval [{intv_min}, {intv_max}] data out of range [{l_limit} {h_limit}] in <{os.path.relpath(log_obj.csv_file)}>'


def verify_csv_data(
    csv_log, ignore_odr_min=False, ignore_odr_max=False,
):

    log_obj = std_sensor_event_log.SeeDrvLog(csv_log, skip_data=1)
    if not log_obj.odr or log_obj.dest_sensor != 'da_test':
        return

    with pytest.assume:
        log_obj.odr_in_range(ignore_min=ignore_odr_min, ignore_max=ignore_odr_max)
    for axis in std_sensor_event_log.axises:
        col_name = f'{log_obj.sensor.capitalize()} {axis.upper()} ({log_obj.unit})'
        with pytest.assume:
            log_obj.check_data_range(col_name, axis)
        with pytest.assume:
            log_obj.check_data_stddev(col_name, axis)
    if log_obj.sensor == cfg.Sensor.mag.value:
        with pytest.assume:
            col_names = [
                f'{log_obj.sensor.capitalize()} {axis.upper()} ({log_obj.unit})'
                for axis in std_sensor_event_log.axises
            ]
            log_obj.check_norm_ord(*col_names)


@pytest.mark.usefixtures('reset_origin_registry')
@pytest.mark.usefixtures('change_registry_res_value')
class TestBasicCases:
    def test_factory_test(
        self,
        productname,
        sensor,
        factest,
        hw_id,
        ssc_drva,
        quts_diag_service,
        diag_packets_list,
    ):
        dur = 5
        params = (dict.fromkeys(using_ssc_drva_keys), None)
        params[0].update(
            {'sensor': sensor, 'factory_test': factest, 'duration': dur, 'hw_id': hw_id}
        )
        prev_biasvals = utils.imu_bias_values(productname, sensor)
        with quts.logging_data_queue(quts_diag_service, diag_packets_list):
            ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(params)
            ssc_drva.ssc_drva_run(ssc_drva_cmd)
        post_biasvals = utils.imu_bias_values(productname, sensor)
        assert found_pass_in_log(
            factest, diag_packets_list
        ), f"key word f'Test level {factest}: PASS' not found "
        if factest == 2:
            assert bias_ver_updated(
                prev_biasvals, post_biasvals
            ), f"bias values [x, y, z]: {prev_biasvals} is not updated after calibration"

    def test_data_streaming(
        self,
        sensor,
        odr,
        hw_id,
        ssc_drva,
        quts_dev_mgr,
        quts_diag_service,
        diag_packets_list,
        qseevt_app,
        log_path,
        log_file_name,
    ):
        dur = 30
        params = (dict.fromkeys(using_ssc_drva_keys), None)
        params[0].update(
            {'sensor': sensor, 'sample_rate': odr, 'duration': dur, 'hw_id': hw_id}
        )
        hdflogfile = os.path.join(log_path, f'{log_file_name}.hdf')
        with quts.logging_diag_hdf(quts_dev_mgr, hdflogfile), quts.logging_data_queue(
            quts_diag_service, diag_packets_list
        ):
            ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(params)
            ssc_drva.ssc_drva_run(ssc_drva_cmd)
        csv_logs = qseevt_app.parse_hdf_to_csv(hdflogfile)
        assert csv_logs, f'No csv files is parsed from hdf: {hdflogfile}'
        for csv_log in csv_logs:
            verify_csv_data(csv_log)


def test_internal_concurrency_stream(
    sensor,
    odr0,
    odr1,
    hw_id,
    ssc_drva,
    quts_dev_mgr,
    quts_diag_service,
    diag_packets_list,
    qseevt_app,
    log_path,
    log_file_name,
):
    dur = 30
    params = (dict.fromkeys(using_ssc_drva_keys), dict.fromkeys(using_ssc_drva_keys))
    params[0].update(
        {'sensor': sensor, 'sample_rate': odr0, 'duration': dur, 'hw_id': hw_id}
    )
    params[1].update(
        {
            'sensor': sensor,
            'sample_rate': odr1,
            'duration': dur,
            'hw_id': hw_id,
            'delay': 2,
        }
    )
    hdflogfile = os.path.join(log_path, f'{log_file_name}.hdf')
    with quts.logging_diag_hdf(quts_dev_mgr, hdflogfile), quts.logging_data_queue(
        quts_diag_service, diag_packets_list
    ):
        ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(params)
        ssc_drva.ssc_drva_run(ssc_drva_cmd)
    csv_logs = qseevt_app.parse_hdf_to_csv(hdflogfile)
    assert csv_logs, f'No csv files is parsed from hdf: {hdflogfile}'
    for csv_log in csv_logs:
        verify_csv_data(csv_log)


def test_internal_concurrency_factest(
    productname,
    sensor,
    odr,
    factest,
    hw_id,
    ssc_drva,
    quts_dev_mgr,
    quts_diag_service,
    diag_packets_list,
    qseevt_app,
    log_path,
    log_file_name,
):
    dur_stream, dur_factest = 30, 5
    params = (dict.fromkeys(using_ssc_drva_keys), dict.fromkeys(using_ssc_drva_keys))
    params[0].update(
        {'sensor': sensor, 'sample_rate': odr, 'duration': dur_stream, 'hw_id': hw_id}
    )
    params[1].update(
        {
            'sensor': sensor,
            'factory_test': factest,
            'duration': dur_factest,
            'hw_id': hw_id,
            'delay': 2,
        }
    )
    hdflogfile = os.path.join(log_path, f'{log_file_name}.hdf')
    prev_biasvals = utils.imu_bias_values(productname, sensor)

    with quts.logging_diag_hdf(quts_dev_mgr, hdflogfile), quts.logging_data_queue(
        quts_diag_service, diag_packets_list
    ):
        ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(params)
        ssc_drva.ssc_drva_run(ssc_drva_cmd)
    post_biasvals = utils.imu_bias_values(productname, sensor)
    assert found_pass_in_log(
        factest, diag_packets_list
    ), f"key word f'Test level {factest}: PASS' not found "
    if factest == 2:
        assert bias_ver_updated(
            prev_biasvals, post_biasvals
        ), f"bias values [x, y, z]: {prev_biasvals} is not updated after calibration"
    csv_logs = qseevt_app.parse_hdf_to_csv(hdflogfile)
    assert csv_logs, f'No csv files is parsed from hdf: {hdflogfile}'
    for csv_log in csv_logs:
        verify_csv_data(csv_log, ignore_odr_max=True)


def test_external_concurrency(
    sensor0,
    odr0,
    sensor1,
    odr1,
    hw_id,
    ssc_drva,
    quts_dev_mgr,
    quts_diag_service,
    diag_packets_list,
    qseevt_app,
    log_path,
    log_file_name,
):

    params = (dict.fromkeys(using_ssc_drva_keys), dict.fromkeys(using_ssc_drva_keys))
    params[0].update(
        {
            'sensor': sensor0,
            'sample_rate': odr0,
            'duration': 100 if isinstance(odr0, int) else 10,
            'hw_id': hw_id,
        }
    )
    params[1].update(
        {
            'sensor': sensor1,
            'sample_rate': odr1,
            'duration': 100 if isinstance(odr1, int) else 10,
            'hw_id': hw_id,
            'delay': 2,
        }
    )
    hdflogfile = os.path.join(log_path, f'{log_file_name}.hdf')
    with quts.logging_diag_hdf(quts_dev_mgr, hdflogfile), quts.logging_data_queue(
        quts_diag_service, diag_packets_list
    ):
        ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(params)
        ssc_drva.ssc_drva_run(ssc_drva_cmd)
    csv_logs = qseevt_app.parse_hdf_to_csv(hdflogfile)
    assert csv_logs, f'No csv files is parsed from hdf: {hdflogfile}'
    for csv_log in csv_logs:
        verify_csv_data(csv_log)


def test_dual_hw(
    sensor0,
    odr0,
    hw_id0,
    sensor1,
    odr1,
    hw_id1,
    ssc_drva,
    quts_dev_mgr,
    quts_diag_service,
    diag_packets_list,
    qseevt_app,
    log_path,
    log_file_name,
):

    params = (dict.fromkeys(using_ssc_drva_keys), dict.fromkeys(using_ssc_drva_keys))
    params[0].update(
        {
            'sensor': sensor0,
            'sample_rate': odr0,
            'duration': 30 if isinstance(odr0, int) else 10,
            'hw_id': hw_id0,
        }
    )
    params[1].update(
        {
            'sensor': sensor1,
            'sample_rate': odr1,
            'duration': 30 if isinstance(odr1, int) else 10,
            'hw_id': hw_id1,
            'delay': 2,
        }
    )
    hdflogfile = os.path.join(log_path, f'{log_file_name}.hdf')
    with quts.logging_diag_hdf(quts_dev_mgr, hdflogfile), quts.logging_data_queue(
        quts_diag_service, diag_packets_list
    ):
        ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(params)
        ssc_drva.ssc_drva_run(ssc_drva_cmd)
    csv_logs = qseevt_app.parse_hdf_to_csv(hdflogfile)
    assert csv_logs, f'No csv files is parsed from hdf: {hdflogfile}'
    for csv_log in csv_logs:
        verify_csv_data(csv_log)
