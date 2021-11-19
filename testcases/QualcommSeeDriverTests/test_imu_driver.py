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

# import time

productname = r'bmi3x0'
sensors = ['accel', 'gyro']
sample_rates = [25, 50, 100, 200, -1, -3.0]
fac_tests = [1, 2, 3]
fac_test_duration = 5
single_sensor_stream_duration = 10
internal_conc_delay = 2
internal_conc_stream_duration = 10
external_conc_stream_duration = 10
external_conc_delay = 2
iteration_count = 1
concurrent_stream_factory_interval_limit = 600


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
    @pytest.mark.parametrize(
        'factest', fac_tests, ids=[cfg.FacTest(fac_test).name for fac_test in fac_tests]
    )
    @pytest.mark.parametrize('sensor', sensors, ids=sensors)
    def test_factory_test(
        self, ssc_drva, quts_diag_service, data_queue, sensor, factest
    ):
        param_sets = (
            {'sensor': sensor, 'factory_test': factest, 'duration': fac_test_duration},
            None,
        )
        prev_biasvals = imu_bias_values(productname, sensor)
        cmd = ssc_drva.set_ssc_drva_cmd(param_sets)
        ssc_drva.ssc_drva_run(cmd)
        with pytest.assume:
            assert match_summary_text(
                quts_diag_service, rf'Test level {factest}: PASS', data_queue
            ), f"key word f'Test level {factest}: PASS' not found "
        if factest == 2:
            post_biasvals = imu_bias_values(productname, sensor)
            with pytest.assume:
                assert [pre + 1 for pre in prev_biasvals] == list(
                    post_biasvals
                ), f"bias values [x, y, z]: {prev_biasvals} is not updated after calibration"


internal_cuncurrency_samplerates = [(-1, -2), (-3.1, -3.2)]
external_cuncurrency_samplerates = [(-1, -2), (-1, -3.1), (-2, -3.2), (-3.0, -3.2)]


@pytest.mark.skip
class TestDataStream(object):
    @pytest.mark.parametrize(
        'samplerate', sample_rates, ids=[cfg.Odr(sr).name for sr in sample_rates]
    )
    @pytest.mark.parametrize('sensor', sensors, ids=sensors)
    def test_data_stream(
        self,
        ssc_drva,
        quts_dev_mgr,
        qseevt,
        sensor_info_txt,
        sensor,
        samplerate,
        duration=single_sensor_stream_duration,
    ):
        param_sets = (
            {'sensor': sensor, 'sample_rate': samplerate, 'duration': duration},
            None,
        )
        log_csv_list = collect_csvs(
            ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt, param_sets
        )
        for csv_log in log_csv_list:
            log_obj = std_sensor_event_log.SeeDrvLog(csv_log, skip_data=1)
            sensor_name = log_obj.sensor
            if not log_obj.odr or log_obj.dest_sensor != 'da_test':
                continue
            odr = log_obj.odr
            stats = log_obj.data_df.describe()
            unit = std_sensor_event_log.unit[sensor_name]

            with pytest.assume:
                col_name = 'interval'
                intv = std_sensor_event_log.calc_interval_ms(odr)
                l_limit = 0 * intv
                h_limit = 1.8 * intv
                intv_min = stats[col_name]['min']
                intv_max = stats[col_name]['max']
                assert (
                    l_limit <= stats[col_name]['min'] < stats[col_name]['max'] < h_limit
                ), f'{sensor_name} time interval [{intv_min}, {intv_max}] data out of range [{l_limit} {h_limit}] in <{csv_log}>'
            for axis in std_sensor_event_log.axises:
                col_name = f'{sensor_name.capitalize()} {axis.upper()} ({unit})'
                with pytest.assume:
                    l_limit = (
                        std_sensor_event_log.data_bases[sensor_name][axis]
                        - std_sensor_event_log.data_offsets[sensor_name][axis]
                    )
                    h_limit = (
                        std_sensor_event_log.data_bases[sensor_name][axis]
                        + std_sensor_event_log.data_offsets[sensor_name][axis]
                    )
                    data_min, data_max = stats[col_name]['min'], stats[col_name]['max']
                    assert (
                        l_limit <= data_min < data_max <= h_limit
                    ), f"{sensor_name} {axis} axis data [{data_min}, {data_max}] out of range [{l_limit}, {h_limit}] in {csv_log}"
                with pytest.assume:
                    stddev = stats[col_name]['std']
                    l_limit = 0
                    # h_limit = 0
                    h_limit = std_sensor_event_log.stddev_limits[sensor_name][axis]
                    assert (
                        l_limit <= stddev <= h_limit
                    ), f"{sensor_name} {axis} axis std_dev {stddev} exceeds limit {h_limit} in {csv_log}"


@pytest.mark.skip
class TestConcurrency:
    # @pytest.mark.skip
    @pytest.mark.parametrize(
        'samplerate0, samplerate1',
        internal_cuncurrency_samplerates,
        ids=[
            f'{cfg.Odr(sr0).name}-{cfg.Odr(sr1).name}'
            for sr0, sr1 in internal_cuncurrency_samplerates
        ],
    )
    @pytest.mark.parametrize('sensor', sensors, ids=sensors)
    def test_internal_concurrency(
        self,
        ssc_drva,
        quts_dev_mgr,
        qseevt,
        sensor_info_txt,
        sensor,
        samplerate0,
        samplerate1,
        duration0=10,
        duration1=10,
        delay=internal_conc_delay,
    ):
        param_sets = (
            {'sensor': sensor, 'sample_rate': samplerate0, 'duration': duration0},
            {
                'sensor': sensor,
                'sample_rate': samplerate1,
                'duration': duration1,
                'delay': delay,
            },
        )
        log_csv_list = collect_csvs(
            ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt, param_sets
        )
        for csv_log in log_csv_list:
            log_obj = std_sensor_event_log.SeeDrvLog(csv_log, skip_data=1)
            sensor_name = log_obj.sensor
            odr = log_obj.odr
            stats = log_obj.data_df.describe()
            unit = std_sensor_event_log.unit[sensor_name]

            with pytest.assume:
                col_name = 'interval'
                intv = std_sensor_event_log.calc_interval_ms(odr)
                l_limit = 0 * intv
                h_limit = 1.8 * intv
                intv_min = stats[col_name]['min']
                intv_max = stats[col_name]['max']
                assert (
                    l_limit <= stats[col_name]['min'] < stats[col_name]['max'] < h_limit
                ), f'{sensor_name} time interval [{intv_min}, {intv_max}] data out of range [{l_limit} {h_limit}] in <{csv_log}>'
            for axis in std_sensor_event_log.axises:
                col_name = f'{sensor_name.capitalize()} {axis.upper()} ({unit})'
                with pytest.assume:
                    l_limit = (
                        std_sensor_event_log.data_bases[sensor_name][axis]
                        - std_sensor_event_log.data_offsets[sensor_name][axis]
                    )
                    h_limit = (
                        std_sensor_event_log.data_bases[sensor_name][axis]
                        + std_sensor_event_log.data_offsets[sensor_name][axis]
                    )
                    data_min, data_max = stats[col_name]['min'], stats[col_name]['max']
                    assert (
                        l_limit <= data_min < data_max <= h_limit
                    ), f"{sensor_name} {axis} axis data [{data_min}, {data_max}] out of range [{l_limit}, {h_limit}] in {csv_log}"
                with pytest.assume:
                    stddev = stats[col_name]['std']
                    l_limit = 0
                    # h_limit = 0
                    h_limit = std_sensor_event_log.stddev_limits[sensor_name][axis]
                    assert (
                        l_limit <= stddev <= h_limit
                    ), f"{sensor_name} {axis} axis std_dev {stddev} exceeds limit {h_limit} in {csv_log}"

    # @pytest.mark.skip
    @pytest.mark.parametrize(
        'samplerate0, samplerate1',
        external_cuncurrency_samplerates,
        ids=[
            f'{cfg.Odr(sr0).name}-{cfg.Odr(sr1).name}'
            for sr0, sr1 in external_cuncurrency_samplerates
        ],
    )
    @pytest.mark.parametrize(
        'sensor0, sensor1',
        itertools.permutations(sensors),
        ids=[f'{s0}-{s1}' for s0, s1 in itertools.permutations(sensors)],
    )
    def test_external_concurrency(
        self,
        ssc_drva,
        quts_dev_mgr,
        qseevt,
        sensor_info_txt,
        sensor0,
        sensor1,
        samplerate0,
        samplerate1,
        duration0=external_conc_stream_duration,
        duration1=external_conc_stream_duration,
        delay=external_conc_delay,
    ):
        param_sets = (
            {'sensor': sensor0, 'sample_rate': samplerate0, 'duration': duration0},
            {
                'sensor': sensor1,
                'sample_rate': samplerate1,
                'duration': duration1,
                'iteration': iteration_count,
                'delay': delay,
            },
        )
        log_csv_list = collect_csvs(
            ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt, param_sets
        )
        for csv_log in log_csv_list:
            log_obj = std_sensor_event_log.SeeDrvLog(csv_log, skip_data=1)
            sensor_name = log_obj.sensor
            odr = log_obj.odr
            stats = log_obj.data_df.describe()
            unit = std_sensor_event_log.unit[sensor_name]

            with pytest.assume:
                col_name = 'interval'
                intv = std_sensor_event_log.calc_interval_ms(odr)
                l_limit = 0 * intv
                h_limit = 1.8 * intv
                intv_min = stats[col_name]['min']
                intv_max = stats[col_name]['max']
                assert (
                    l_limit <= stats[col_name]['min'] < stats[col_name]['max'] < h_limit
                ), f'{sensor_name} time interval [{intv_min}, {intv_max}] data out of range [{l_limit} {h_limit}] in <{csv_log}>'
            for axis in std_sensor_event_log.axises:
                col_name = f'{sensor_name.capitalize()} {axis.upper()} ({unit})'
                with pytest.assume:
                    l_limit = (
                        std_sensor_event_log.data_bases[sensor_name][axis]
                        - std_sensor_event_log.data_offsets[sensor_name][axis]
                    )
                    h_limit = (
                        std_sensor_event_log.data_bases[sensor_name][axis]
                        + std_sensor_event_log.data_offsets[sensor_name][axis]
                    )
                    data_min, data_max = stats[col_name]['min'], stats[col_name]['max']
                    assert (
                        l_limit <= data_min < data_max <= h_limit
                    ), f"{sensor_name} {axis} axis data [{data_min}, {data_max}] out of range [{l_limit}, {h_limit}] in {csv_log}"
                with pytest.assume:
                    stddev = stats[col_name]['std']
                    l_limit = 0
                    # h_limit = 0
                    h_limit = std_sensor_event_log.stddev_limits[sensor_name][axis]
                    assert (
                        l_limit <= stddev <= h_limit
                    ), f"{sensor_name} {axis} axis std_dev {stddev} exceeds limit {h_limit} in {csv_log}"

    # @pytest.mark.skip
    @pytest.mark.parametrize(
        'factest',
        fac_tests[1:],
        ids=[cfg.FacTest(fac_test).name for fac_test in fac_tests[1:]],
    )
    @pytest.mark.parametrize(
        'samplerate', [cfg.Odr.odr_max.value], ids=[cfg.Odr.odr_max.name]
    )
    @pytest.mark.parametrize('sensor', sensors, ids=sensors)
    def test_internal_stream_factorytest_concurrency(
        self,
        ssc_drva,
        quts_dev_mgr,
        quts_diag_service,
        data_queue,
        qseevt,
        sensor_info_txt,
        sensor,
        samplerate,
        factest,
        duration0=single_sensor_stream_duration,
        duration1=fac_test_duration,
        delay=external_conc_delay,
    ):
        param_sets = (
            {'sensor': sensor, 'sample_rate': samplerate, 'duration': duration0},
            {
                'sensor': sensor,
                'factory_test': factest,
                'duration': duration1,
                'delay': delay,
            },
        )
        prev_biasvals = imu_bias_values(productname, sensor)
        # ssc_drva.ssc_drva_run(cmd)
        log_csv_list = collect_csvs(
            ssc_drva, quts_dev_mgr, qseevt, sensor_info_txt, param_sets
        )
        with pytest.assume:
            assert match_summary_text(
                quts_diag_service, rf'Test level {factest}: PASS', data_queue
            ), f"key word f'Test level {factest}: PASS' not found "
        if factest == 2:
            post_biasvals = imu_bias_values(productname, sensor)
            with pytest.assume:
                assert [pre + 1 for pre in prev_biasvals] == list(post_biasvals)
        for csv_log in log_csv_list:
            log_obj = std_sensor_event_log.SeeDrvLog(csv_log, skip_data=1)
            sensor_name = log_obj.sensor
            odr = log_obj.odr
            stats = log_obj.data_df.describe()
            unit = std_sensor_event_log.unit[sensor_name]

            with pytest.assume:
                col_name = 'interval'
                intv = std_sensor_event_log.calc_interval_ms(odr)
                l_limit = 0 * intv
                # h_limit = 1.8 * intv
                h_limit = concurrent_stream_factory_interval_limit
                intv_min = stats[col_name]['min']
                intv_max = stats[col_name]['max']
                # intv_max = stats[col_name]['max']
                assert (
                    l_limit <= stats[col_name]['min'] < stats[col_name]['max'] < h_limit
                ), f'{sensor_name} time interval [{intv_min}, {intv_max}] data out of range [{l_limit} {h_limit}] in <{csv_log}>'
            for axis in std_sensor_event_log.axises:
                col_name = f'{sensor_name.capitalize()} {axis.upper()} ({unit})'
                with pytest.assume:
                    l_limit = (
                        std_sensor_event_log.data_bases[sensor_name][axis]
                        - std_sensor_event_log.data_offsets[sensor_name][axis]
                    )
                    h_limit = (
                        std_sensor_event_log.data_bases[sensor_name][axis]
                        + std_sensor_event_log.data_offsets[sensor_name][axis]
                    )
                    data_min, data_max = stats[col_name]['min'], stats[col_name]['max']
                    assert (
                        l_limit <= data_min < data_max <= h_limit
                    ), f"{sensor_name} {axis} axis data [{data_min}, {data_max}] out of range [{l_limit}, {h_limit}] in {csv_log}"
                with pytest.assume:
                    stddev = stats[col_name]['std']
                    l_limit = 0
                    # h_limit = 0
                    h_limit = std_sensor_event_log.stddev_limits[sensor_name][axis]
                    assert (
                        l_limit <= stddev <= h_limit
                    ), f"{sensor_name} {axis} axis std_dev {stddev} exceeds limit {h_limit} in {csv_log}"


class TestMultiHardware:
    pass
