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


class SscDrvaTest(object):
    """
    SscDrvaTest class to wrap ssc_drva_test
    """

    def __init__(self, adb: ADB):
        self._adb = adb
        self.proc = None

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
        if debug:
            cmd_list.append('-debug')
        return cmd_list

    def ssc_drva_run(self, cmd_list, stdout_en=False):
        out = sys.stdout if stdout_en else PIPE
        logging.info(f'\nexecute {" ".join(cmd_list)}')
        timeout = 600  # 10 minutes timeout

        try:
            self._adb.adb_shell_run(cmd_list, stdout=out, timeout=timeout)

        except TimeoutExpired:
            print(
                f"{' '.join(cmd_list)} command execution reached timeout={timeout}s, process killed"
            )


if __name__ == '__main__':
    """
    debug code of ssc_drva.py module
    """
    try:
        dev_id = ADB.adb_devices()
    except AttributeError as e:
        dev_id = None
