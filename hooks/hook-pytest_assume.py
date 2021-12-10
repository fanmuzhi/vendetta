#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "hook-pytest_assume.py"
__version__ = "init"
__author__ = "@henry.fan"
from PyInstaller.utils.hooks import copy_metadata

datas = copy_metadata('pytest_assume')