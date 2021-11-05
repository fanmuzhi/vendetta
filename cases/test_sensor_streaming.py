#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "test_sensor_streaming"
__version__ = "init"
__author__ = "@henry.fan"
import pytest
from lib.data_process import std_sensor_event_log
sensor = 'accel'
sample_rate = 50

list_params = [
    (
        {
            'sensor': 'accel',
            'duration': 5,
            'factory_test': 2,
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

    @pytest.mark.parametrize('generate_ssc_drva_data_packet', list_params, indirect=True)
    def test_sensor_streaming(self, generate_ssc_drva_data_packet):
        # f = run_ssc_drva_test
        log_fp = r'C:\Users\FNH1SGH\Desktop\11111\Data\SensorAPI_ACCEL_S0_I0_D2_R1_[std_sensor_event].csv'
        log_obj = std_sensor_event_log.SeeDrvLog(log_fp, skip_data=1)
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


