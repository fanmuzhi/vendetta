#!/usr/bin/env python
# encoding: utf-8
"""
# Description: ssc_drva.py module of ssc_drva_test class
"""
__filename__ = "ssc_drva"
__version__ = "init"
__author__ = "@henry.fan"

import logging
import sys
from subprocess import PIPE, TimeoutExpired
from lib.adb.adb import ADB
# from log import logger


class SscDrvaParams:
    valid_keys_and_sort = {
        'sensor': 'ssr',
        'duration': 'dur',
        'sample_rate': 'sr',
        'batch_period': 'bp',
        'fifo': 'fifo',
        'batch_count': 'bc',
        'stop_n_go': 'sng',
        'delay': 'dly',
        'flush_fill': 'ff',
        'seed': 'seed',
        'iterations': 'iter',
        'num_samples': 'ns',
        'dri': 'dri',
        'factory_test': 'fac',
        'verbose': 'vb',
        'sensor_name': 'ssn',
        'hw_id': 'hw',
    }

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.valid_keys_and_sort and v is not None:
                exec(f'self.{k} = v')


class SscDrvaTest:
    """
    SscDrvaTest class to wrap ssc_drva_test
    """

    def __init__(self, adb: ADB):
        # self._cmd_list = ['ssc_drva_test']
        self._adb = adb
        self.proc = None

    # def get_test_cmd(self):
    #     return self._cmd_list

    # def single_sensor_test_cmd(self, p_sets):
    #     cmd_list = ['ssc_drva_test']
    #     assert all((p_sets[0].__dict__.get('sensor', None), p_sets[0].__dict__.get('duration', None)))
    #     for param, value in p_sets[0].__dict__.items():
    #         if value is None:
    #             continue
    #         cmd_list += (f'-{param}={value}')
    #     return cmd_list
    #
    # def extend_concsensor_test_cmd(self, p_sets):
    #     if len(p_sets) < 2:
    #         return
    #     assert all((p_sets[1].__dict__.get('sensor', None), p_sets[1].__dict__.get('duration', None)))
    #     self._cmd_list[0] = '"' + self._cmd_list[0]
    #     self._cmd_list.extend(['&"', '"ssc_drva_test'])
    #     for param, value in p_sets[1].__dict__.items():
    #         if value is None:
    #             continue
    #         self._cmd_list.append(f'-{param}={value}')

    #     self._cmd_list[-1] += '"'
    @staticmethod
    def set_ssc_drva_cmd(param_sets, debug=False):
        cmd_list = ['ssc_drva_test']
        assert 0 < len(param_sets) < 3

        p_sets = [SscDrvaParams(**p) for p in param_sets if p]
        for param, value in p_sets[0].__dict__.items():
            if value is None:
                continue
            cmd_list.append(f'-{param}={value}')
        if len(p_sets) >= 2:
            cmd_list[0] = '"' + cmd_list[0]
            cmd_list.extend(['&"', '"ssc_drva_test'])
            for param, value in p_sets[1].__dict__.items():
                if value is None:
                    continue
                cmd_list.append(f'-{param}={value}')
            cmd_list[-1] += '"'
        # self.single_sensor_test_cmd(p_sets)
        # self.extend_concsensor_test_cmd(p_sets)
        if debug:
            cmd_list.append('-debug')
        return cmd_list

    def ssc_drva_run(self, cmd_list, stdout_en=False):
        # print(cmd_list)
        # sscdrva_timeout = False
        out = sys.stdout if stdout_en else PIPE
        # self.set_ssc_drva_cmd(param_sets, debug=debug)
        logging.info(f'\nexecute {" ".join(cmd_list)}')
        timeout = 600  # 10 minutes timeout
        # for param in param_sets:
        #     if param:
        #         duration = param.get('duration')
        #         iterations = param.get('iterations', 1)
        #         delay = param.get('delay', 0)
        #         timeout += duration * iterations + delay
        # print(f'timeout: {timeout}s')
        try:
            self._adb.adb_shell_run(cmd_list, stdout=out, timeout=timeout)
            # self._adb.adb_shell_run(self._cmd_list, stdout=out, timeout=timeout)

        except TimeoutExpired:
            print(
                f"{' '.join(cmd_list)} command execution reached timeout={timeout}s, process killed"
            )
        # proc = self._adb.adb_shell_popen(self._cmd_list, stdout=out)
        # while proc.poll() is None and not sscdrva_timeout:
        # while proc.poll() is None:
        #     line = self._adb.adb_proc.stdout.readline()
        #     if stdout_en:
        #         sys.stdout.write(line.decode())
        # if 'received event: RECALC_TIMEOUT' in line.decode():
        #     sscdrva_timeout = True
        # proc.terminate()

    # def exec_test_popen(self, param_sets, debug=False):
    #     self.set_ssc_drva_cmd(param_sets, debug=debug)
    #     self.proc = self._adb.adb_shell_popen(self._cmd_list)
    #     return self.proc


if __name__ == '__main__':
    """
    debug code of ssc_drva.py module
    """
    try:
        dev_id = ADB.adb_devices()
    except AttributeError as e:
        dev_id = None
    # adb_obj = ADB(device_id=dev_id)
    # sdt = SscDrvaTest(adb=adb_obj)
    # prime_params = ssc_drva_params.copy()
    # conc_params = ssc_drva_params.copy()
    # prime_params.update({
    #     'sensor':      'accel',
    #     'duration':    20,
    #     'sample_rate': 5,
    # })
    # conc_params.update({
    #     'sensor':      'gyro',
    #     'duration':    10,
    #     'sample_rate': 7,
    # })
    # ssc_drva_params = (
    #     prime_params,
    #     conc_params,
    # )
    # sdt.set_ssc_drva_cmd(ssc_drva_params, debug=False)
    # print(" ".join(sdt.get_test_cmd()))
