#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import pytest
# import logging

from libs import utils

test_result_root_dir = r'c:\SeeTests'


#  start prior init
def app_prior_init():
    if sys.platform.startswith("linux"):
        sys.path.append('/opt/qcom/QUTS/Support/python')
    elif sys.platform.startswith("win"):
        sys.path.append('C:\Program Files (x86)\Qualcomm\QUTS\Support\python')
    elif sys.platform.startswith("darwin"):
        sys.path.append('/Applications/Qualcomm/QUTS/QUTS.app/Contents/Support/python')
    else:
        sys.exit("unrecognized system platform")
#  end prior init


product = ''
defualt_testpath = r'testcases\QualcommSeeDriverTests\test_imu_driver.py'

default_args = [
    # '--lf',
    '-sv',
    '--capture=sys',
    '--tb=native',
    '-p',
    'no:faulthandler',
    '-W ignore::DeprecationWarning',
]

if __name__ == '__main__':
    app_prior_init()
    argv = sys.argv[1:]

    if '--product' not in argv or '--product' == argv[-1]:
        print("argument --product not assigned")
        sys.exit(1)
    else:
        product = argv[argv.index('--product') + 1]

    if not argv[0].startswith(defualt_testpath):
        argv = [defualt_testpath] + argv

    if not product or not utils.get_sensorlist(product):
        print('invalid product name')
        sys.exit(1)

    for arg in default_args:
        if arg not in argv:
            argv.append(arg)

    if not any(['--co' in argv, '--collect-only' in argv]):
        test_info = f'{product}_{utils.datetime_str()}'
        test_folder = os.path.join(test_result_root_dir, test_info)
        log_dir = os.path.join(test_result_root_dir, test_info, 'log')
        os.makedirs(log_dir, exist_ok=True)

        f_html = f'report_{test_info}.html'
        if any(['--lf' in argv, '--last-fail' in argv]):
            f_html = f'FAILEDCASES-RETEST-{f_html}'
        argv.append(f'--html={os.path.join(test_folder, f_html)}')
        argv.append('--self-contained-html')
        # argv.append(f'--log_dir={log_dir}')

    # print(f'pytest {" ".join(argv)}')
    pytest.main(
        args=argv,
    )
