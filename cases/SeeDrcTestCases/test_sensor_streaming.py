#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "test_sensor_streaming"
__version__ = "init"
__author__ = "@henry.fan"

import os
import re

import pytest
from lib.data_process import std_sensor_event_log
from lib.sensor_file.sensor_file import FacCalBias
from lib.quts.quts import debug_msg_filter_item
from lib.utils import *
sample_rate = 50

list_params = [
    (
        {
            'sensor': 'accel',
            'duration': 5,
            'sample_rate': 50,
        },
        None
    ),
    (
        {
            'sensor': 'gyro',
            'duration': 5,
            'sample_rate': 50,
        },
        {
            'sensor': 'accel',
            'duration': 5,
            'sample_rate': 50,
            'delay': 3
        }
    )
]


factest_params = [
    (
        {
            'sensor': 'accel',
            'duration': 8,
            'factory_test': 2,
        },
        None
    ),
    (
        {
            'sensor': 'gyro',
            'duration': 8,
            'factory_test': 2,
        },
        None
    )
]


class TestSensorStream(object):
    @pytest.mark.skip
    @pytest.mark.parametrize(
        'collect_stream_data_files',
        list_params,
        indirect=True,
    )
    def test_sensor_streaming(self, collect_stream_data_files):
        for csv_log in collect_stream_data_files:
            log_obj = std_sensor_event_log.SeeDrvLog(csv_log, skip_data=1)
            sensor = log_obj.sensor
            stats = log_obj.data_df.describe()
            unit = std_sensor_event_log.unit[sensor]

            with pytest.assume:
                col_name = 'interval'
                intv = std_sensor_event_log.calc_interval_ms(50)
                l_limit = 0 * intv
                h_limit = 1.8 * intv
                assert l_limit <= stats[col_name]['min'] < stats[col_name]['max'] < h_limit
            for axis in std_sensor_event_log.axises:
                col_name = f'{sensor.capitalize()} {axis.upper()} ({unit})'
                with pytest.assume:
                    l_limit = std_sensor_event_log.data_bases[sensor][axis] - std_sensor_event_log.data_offsets[sensor][axis]
                    h_limit = std_sensor_event_log.data_bases[sensor][axis] + std_sensor_event_log.data_offsets[sensor][axis]
                    data_min, data_max = stats[col_name]['min'], stats[col_name]['max']
                    assert l_limit <= data_min < data_max <= h_limit, f"{sensor} {axis} axis data out of range"
                with pytest.assume:
                    l_limit = 0
                    h_limit = std_sensor_event_log.stddev_limits[sensor][axis]
                    assert l_limit <= stats[col_name]['std'] <= h_limit, f"{sensor} {axis} axis std_dev value out of range"


class TestSensorFactoryTest(object):
    @pytest.mark.parametrize(
        'param_sets',
        factest_params,
    )
    def test_sensor_factorytest(self, ssc_drva, quts_diag_service, data_queue, param_sets):
        sensor = param_sets[0].get('sensor')
        factest = param_sets[0]["factory_test"]
        productname = r'bmi3x0'
        prev_biasvals = imu_bias_values(productname, sensor)
        cmd = ssc_drva.set_ssc_drva_cmd(param_sets)
        ssc_drva.ssc_drva_run(cmd)
        post_biasvals = imu_bias_values(productname, sensor)
        total_count = 0
        diag_packets = quts_diag_service.getDataQueueItems(data_queue, 30000, 20)
        total_count += len(diag_packets)
        with pytest.assume:
            assert any([re.search(rf'Test level {factest}: PASS', diag_packet.summaryText) for diag_packet in diag_packets])
        if factest == 2:
            with pytest.assume:
                assert [pre+1 for pre in prev_biasvals] == list(post_biasvals)
