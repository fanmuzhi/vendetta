#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "utils"
__version__ = "init"
__author__ = "@henry.fan"


import ctypes, sys


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False