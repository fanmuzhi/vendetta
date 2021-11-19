#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "try"
__version__ = "init"
__author__ = "@henry.fan"

import itertools
from pprint import pp
n_hw = 1
hw_ids = list(range(n_hw))
sensor_list = ['accel', 'gyro']
streaming_odr_list = [-2, 50, 100, 200, -1, -3.0]
factorytest_list = [1, 2, 3]
single_sensor_stream_duration = 10
ssc_drva_delay = 2

stream_test_params_sensors = list(itertools.product(sensor_list, [None]))
stream_test_params_odrs = list(itertools.product(streaming_odr_list, [None]))
stream_test_params_factest = list(itertools.product(factorytest_list, [None]))
stream_test_params_duration = list(itertools.product([single_sensor_stream_duration], [None]))
stream_test_params_hw_ids = list(itertools.product(hw_ids, [None]))
single_sensor_stream_params_list = list(itertools.product(stream_test_params_sensors,
                                                          stream_test_params_odrs,
                                                          stream_test_params_duration,
                                                          stream_test_params_hw_ids))


internal_concurrent_stream_sensors = [tuple(itertools.repeat(sensor, 2)) for sensor in sensor_list]
internal_concurrent_stream_odrs = [(-1, -2), (-3.1, -3.2)]
internal_concurrent_stream_durations = [(30, 30)]
internal_concurrent_stream_hw_ids = [(0, 0)]
internal_concurrent_stream_delays = list(itertools.product([None], [ssc_drva_delay]))
internal_concurrent_stream_params_list = list(itertools.product(
    internal_concurrent_stream_sensors,
    internal_concurrent_stream_odrs,
    internal_concurrent_stream_durations,
    internal_concurrent_stream_hw_ids,
    internal_concurrent_stream_delays
))

intern_conc_stream_fac_odrs = list(itertools.product([-1], [None]))
intern_conc_stream_fac_factests = list(itertools.product([None], [1, 2]))
internal_concurrent_stream_fac_durations = [(30, 5)]




external_concurrent_stream_odrs = [(-1, -2), (-1, -3.1), (-2, -3.2), (-3.0, -3.1)]
external_concurrent_stream_sensors = list(itertools.permutations(sensor_list))
# print(list(itertools.product([None], [1, 2])))
if __name__ == "__main__":
    # print("single sensor test sensor list:")
    # print(stream_test_params_sensors)
    # print('single sensor test odr list:')
    # print(stream_test_params_odrs)
    # print('single sensor stream test params list')
    # pp(single_sensor_stream_params_list)

    print('internal cuncurrent test sensors list')
    print(internal_concurrent_stream_sensors)

    print('internal stream concurrent test params list')
    pp(internal_concurrent_stream_params_list)

    print('internal stream factest concurrent test params list')
    print(list(itertools.product(internal_concurrent_stream_sensors, intern_conc_stream_fac_odrs, intern_conc_stream_fac_factests)))

    print('external concurrent test sensor list:')
    print(external_concurrent_stream_sensors)

    print('external concurrent stream test params list')
    print(list(itertools.product(external_concurrent_stream_sensors, external_concurrent_stream_odrs)))


