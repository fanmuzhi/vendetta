# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import argparse
import os
import sys
import pytest
from lib import utils
report_dir = r"c:\temp\report"
os.makedirs(report_dir, exist_ok=True)
product = ''
default_args = [
        '-v',
        '--capture=sys',
        '--tb=native',
        # f'--html={utils.datetime_str()}_{product}_report.html',
        '-p',
        'no:faulthandler',
        '-W ignore::DeprecationWarning'
    ]


def main():

    pytest.main(
        args=argv,
    )


if __name__ == '__main__':
    argv = sys.argv[1:]
    if '--product' not in argv or '--product' == argv[-1]:
        print("argument --product not assigned")
        sys.exit(1)
    else:
        product = argv[argv.index('--product') + 1]
        if not utils.get_sensorlist(product):
            print('invalid product name')
            sys.exit(1)
        fhtmlreport = f'{utils.datetime_str()}_{product}_report.html'
        argv.append(f'--html={fhtmlreport}')

    for arg in default_args:
        if arg not in argv:
            argv.append(arg)
    main()
