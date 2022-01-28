#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import pytest

# import logging

from libs import utils

from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
from pycallgraph import Config
from pycallgraph import GlobbingFilter

test_result_root_dir = r'c:\SeeTests'
product = ''
defualt_testpath = r'testcases/QualcommSeeDriverTests/test_imu_driver.py'

default_args = [
    # '--lf',
    '-sv',
    '--capture=sys',
    '--tb=native',
    '-p',
    'no:faulthandler',
    '-W ignore::DeprecationWarning',
]


def main():
    argv = sys.argv[1:]

    if not argv[0].replace("\\", "/").startswith(defualt_testpath):
        argv = [defualt_testpath] + argv

    if '--product' not in argv or '--product' == argv[-1]:
        print("argument --product not assigned")
        sys.exit(1)
    else:
        product = argv[argv.index('--product') + 1]

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
    pytest.main(args=argv,)


if __name__ == '__main__':
    config = Config()
    # 关系图中包括(include)哪些函数名。
    #如果是某一类的函数，例如类gobang，则可以直接写'gobang.*'，表示以gobang.开头的所有函数。（利用正则表达式）。
    config.trace_filter = GlobbingFilter(
            include=[
                'main',
                'libs.adb.adb.*',
                'libs.data_process.std_sensor_event_log.*',
                'libs.sensor_file.sensor_file.*',
                'libs.ssc_drva.ssc_drva.*',
                'libs.config.*',
                'libs.qseevt.*',
                'libs.quts.*',
                'libs.utils.*',
                # 'testcases.*',
            ]
    )
    # 该段作用是关系图中不包括(exclude)哪些函数。(正则表达式规则)
    # config.trace_filter = GlobbingFilter(exclude=[
    #     'pycallgraph.*',
    #     '*.secret_function',
    #     'FileFinder.*',
    #     'ModuleLockManager.*',
    #     'SourceFilLoader.*'
    # ])
    graphviz = GraphvizOutput()
    # graphviz.output_file = 'graph.svg'
    graphviz.output_file = 'graph.png'
    with PyCallGraph(output=graphviz, config=config):
        main()
    # main()
