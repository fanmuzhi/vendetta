#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "try"
__version__ = "init"
__author__ = "@henry.fan"
import os
import itertools
from pprint import pp
from libs import config as cfg

print(os.path.dirname(__file__))
n_hw = 1
hwid = list(range(n_hw))
sensor_list = ['accel', 'gyro']
streamtest_odr_list = [-2, 50, 100, 200, -1, -3.0]
factest_type_list = [1, 2, 3]
sensor_streamtest_dur = 10
sensor_factest_dur = 5
ssc_drva_delay = 2
null_params = [None]

used_drva_keys = [
    'sensor',
    'duration',
    'sample_rate',
    'factory_test',
    'hw_id',
    'delay',
]
#
# streamtest_params_sensor = list(itertools.product(sensor_list, [None]))
# # print("single sensor test sensor list:")
# # print(streamtest_params_sensor)
#
# streamtest_params_odr = list(itertools.product(streamtest_odr_list, [None]))
# # print('single sensor test odr list:')
# # print(streamtest_params_odr)
#
# streamtest_params_dur = list(itertools.product([sensor_streamtest_dur], [None]))
# streamtest_params_hwid = list(itertools.product(hwid, [None]))
# streamtest_params_list = list(
#     itertools.product(
#         streamtest_params_sensor,
#         streamtest_params_dur,
#         streamtest_params_odr,
#         null_params,
#         streamtest_params_hwid,
#         null_params,
#     )
# )
# print('single sensor stream test params list')
# # pp(streamtest_params_list)
#
# for param in streamtest_params_list:
#     pp(dict(zip(used_drva_keys, param)))
#
#
# factest_params_sensor = list(itertools.product(sensor_list, [None]))
# factest_params_factest_type = list(itertools.product(factest_type_list, [None]))
# # print('single sensor factory test type list')
# # pp(factest_params_factest_type)
# factest_params_dur = list(itertools.product([sensor_factest_dur], [None]))
# factest_params_hwid = list(itertools.product(hwid, [None]))
#
# factest_params_list = list(
#     itertools.product(
#         factest_params_sensor,
#         factest_params_dur,
#         null_params,
#         factest_params_factest_type,
#         factest_params_hwid,
#         null_params,
#     )
# )
# print('single sensor factory test params list')
# # pp(factest_params_list)
# for param in factest_params_list:
#     pp(dict(zip(used_drva_keys, param)))
#
# intern_conc_stream_sensor = [
#     tuple(itertools.repeat(sensor, 2)) for sensor in sensor_list
# ]
# intern_conc_stream_odr = [(-1, -2), (-3.1, -3.2)]
# intern_conc_stream_dur = [(30, 30)]
# intern_conc_stream_hwid = [(0, 0)]
# intern_conc_stream_delays = list(itertools.product([None], [ssc_drva_delay]))
# intern_conc_stream_params_list = list(
#     itertools.product(
#         intern_conc_stream_sensor,
#         intern_conc_stream_dur,
#         intern_conc_stream_odr,
#         null_params,
#         intern_conc_stream_hwid,
#         intern_conc_stream_delays,
#     )
# )
# # print('intern cuncurrent stream test sensor list')
# # print(intern_conc_stream_sensor)
# for param in intern_conc_stream_sensor:
#     pp(dict(zip(used_drva_keys, param)))
#
# print('intern conc stream test params list')
# pp(intern_conc_stream_params_list)
# intern_conc_factest_sensor = [
#     tuple(itertools.repeat(sensor, 2)) for sensor in sensor_list
# ]
# intern_conc_factest_odr = list(itertools.product([-1], [None]))
# intern_conc_factest_type = list(itertools.product([None], [1, 2]))
# intern_conc_factest_dur = [(30, 5)]
# intern_conc_factest_hwid = [(0, 0)]
# intern_conc_factest_delays = list(itertools.product([None], [ssc_drva_delay]))
# intern_conc_factest_params_list = list(
#     itertools.product(
#         intern_conc_factest_sensor,
#         intern_conc_factest_dur,
#         intern_conc_factest_odr,
#         intern_conc_factest_type,
#         intern_conc_factest_hwid,
#         intern_conc_factest_delays,
#     )
# )
# print('intern conc factory test test params list')
# pp(intern_conc_factest_params_list)
# for param in intern_conc_factest_params_list:
#     pp(dict(zip(used_drva_keys, param)))
#
#
# def extern_conc_streamtest_odr_to_dur(odr):
#     if isinstance(odr, int):
#         return 100
#     else:
#         return 10
#
#
# extern_conc_stream_sensor = list(itertools.permutations(sensor_list))
# extern_conc_stream_odr = [(-1, -2), (-1, -3.1), (-2, -3.2), (-3.0, -3.1)]
# # extern_conc_stream_dur = [(30, 30)]
# extern_conc_stream_hwid = [(0, 0)]
# extern_conc_stream_delays = list(itertools.product([None], [ssc_drva_delay]))
# extern_conc_stream_params_list = []
# for odr in extern_conc_stream_odr:
#     extern_conc_stream_params_list.extend(
#         list(
#             itertools.product(
#                 extern_conc_stream_sensor,
#                 # [(extern_conc_streamtest_odr_to_dur(odr[0]), extern_conc_streamtest_odr_to_dur(odr[1])) for odr in
#                 #  extern_conc_stream_odr],
#                 [
#                     (
#                         extern_conc_streamtest_odr_to_dur(odr[0]),
#                         extern_conc_streamtest_odr_to_dur(odr[1]),
#                     )
#                 ],
#                 [odr],
#                 null_params,
#                 extern_conc_stream_hwid,
#                 extern_conc_stream_delays,
#             )
#         )
#     )
#
# print('extern conc stream test params list')
# # pp(extern_conc_stream_params_list)
# for param in extern_conc_stream_params_list:
#     pp(dict(zip(used_drva_keys, param)))
#


def setup_param_sets(params_list):
    """
     :param params_list:
        eg:{
             'sensor': ('gyro', 'gyro'),
             'duration': (30, 5),
             'sample_rate': (-1, None),
             'factory_test': (None, 2),
             'hw_id': (0, 0),
             'delay': (None, 2)
         }
     # :return: param_sets
     """
    param_sets = [dict(), dict()]
    for k, v in params_list.items():
        if v:
            for i in range(2):
                if v[i]:
                    param_sets[i].update({k: v[i]})
    return param_sets


if __name__ == "__main__":

    def setup_param_sets(pairs_dict):
        params_set = [dict(), dict()]
        for k, (v0, v1) in pairs_dict.items():
            print(k, v0, v1)
            if v0 is not None:
                params_set[0].update({k: v0})
            if v1 is not None:
                params_set[1].update({k: v1})
        return params_set

    pairs_dict = {
        'sensor': ('gyro', 'gyro'),
        'duration': (30, 5),
        'sample_rate': (-1, None),
        'factory_test': (None, 2),
        'hw_id': (0, 0),
        'delay': (None, 2),
    }

    def id_str(pairs):
        id_word_list = []
        for i in range(2):
            if pairs['sensor'][i]:
                id_word_list.append(pairs['sensor'][i])
            if pairs['sample_rate'][i] is not None:
                id_word_list.append(cfg.Odr(pairs['sample_rate'][i]).name)
            if pairs['factory_test'][i] is not None:
                id_word_list.append(cfg.FacTest(pairs['factory_test'][i]).name)
            if pairs['hw_id'][i] is not None:
                id_word_list.append(f"hw_{pairs['hw_id'][i]}")

        print('-'.join(id_word_list))

    print(setup_param_sets(pairs_dict))
    # params_set = {'sensor': 'gyro', 'duration': 30, 'sample_rate': -1, 'hw_id': 0}, {'sensor': 'gyro', 'duration': 5,
    #                                                                     'factory_test': 2, 'hw_id': 0, 'delay': 2}

    # print("#" * 60)
    # for paramlist in [
    #     # streamtest_params_list,
    #     # factest_params_list,
    #     # intern_conc_stream_params_list,
    #     # intern_conc_factest_params_list,
    #     extern_conc_stream_params_list
    # ]:
    #     for param in paramlist:
    #         print(setup_param_sets(dict(zip(used_drva_keys, param))))
    import yaml

    # import json
    # from collections import OrderedDict
    #
    # test_data = OrderedDict()
    # test_data.update({
    #     'sensors': sensor_list.copy(),
    #     'factest_duration': sensor_factest_dur,
    #     'streamtest_duration': sensor_streamtest_dur,
    #     'factorytest_type': factest_type_list.copy(),
    #     'streamtest_odr': streamtest_odr_list.copy(),
    #     'internal_concurrency_streamtest_sensor': sensor_list.copy(),
    #     'internal_concurrency_streamtest_duration': intern_conc_stream_dur.copy(),
    #     'internal_concurrency_streamtest_odr': [(-1, -2), (-3.1, -3.2)].copy(),
    #     'internal_concurrency_streamtest_hwid': 0,
    #     'internal_concurrency_factest_sensor': sensor_list.copy(),
    #     'internal_concurrency_factest_duration': intern_conc_factest_dur.copy(),
    #     'internal_concurrency_factest_type': [1, 2],
    #     'internal_concurrency_factest_hwid': 0,
    #     'external_concurrency_streamtest_sensor': sensor_list.copy(),
    #     'external_concurrency_streamtest_odr': [(-1, -2), (-1, -3.1), (-2, -3.2), (-3.0, -3.1)].copy(),
    #     'external_concurrency_streamtest_hwid': 0,
    #     'delay': ssc_drva_delay
    # })
    #
    # with open(r'.\test_data_bmi3x0.json', 'w') as f:
    # # with open(r'.\test_data_bmi3x0.yaml', 'w') as f:
    #     json.dump(dict(test_data), f, allow_nan=True, indent=4)
    #     # yaml.safe_dump(dict(test_data), f)
