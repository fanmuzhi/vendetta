#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "utils"
__version__ = "init"
__author__ = "@henry.fan"

from datetime import datetime
import ctypes, sys

datetime_format = '%Y-%m-%d_%H-%M-%S'


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def datetime_str():
    return datetime.now().strftime(datetime_format)


def da_test_csv_files_in(path):
    # TODO: find valid da test csv files in the folder 'path'
    pass

if __name__ == "__main__":
    print(datetime_str())
