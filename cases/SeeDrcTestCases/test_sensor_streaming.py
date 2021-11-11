#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "test_sensor_streaming"
__version__ = "init"
__author__ = "@henry.fan"

import os.path

import pytest
from lib.data_process import std_sensor_event_log
from lib.utils import *
sensor = 'accel'
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
    # (
    #     {
    #         'sensor': 'gyro',
    #         'duration': 5,
    #         'sample_rate': 50,
    #     },
    #     {
    #         'sensor': 'accel',
    #         'duration': 5,
    #         'sample_rate': 50,
    #         'delay': 3
    #     }
    # )
]


class TestSensorStreaming(object):

    @pytest.mark.parametrize(
        'collect_stream_data_files',
        list_params,
        indirect=True,
    )
    def test_sensor_streaming(self, collect_stream_data_files):
        # f = run_ssc_drva_test
        # csv_log_fp = r'C:\Users\FNH1SGH\Desktop\11111\Data\SensorAPI_ACCEL_S0_I0_D2_R1_[std_sensor_event].csv'
        parseddir = collect_stream_data_files
        print(parseddir)
        for csv_log_fp in da_test_csv_files_in(parseddir):
            log_obj = std_sensor_event_log.SeeDrvLog(csv_log_fp, skip_data=1)
            unit = std_sensor_event_log.unit[sensor]
            stats = log_obj.data_df.describe()
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
