# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pytest


def main():
    pytest.main([
        'testcases/QualcommSeeDriverTests/test_imu_driver.py::TestFactoryTest::test_factory_test',
        '-vs',
        # '-s',
        '--capture=sys',
        '--tb=line',
        '--html=report.html',
        '-p',
        'no:faulthandler',
        '-W ignore::DeprecationWarning'
    ])


if __name__ == '__main__':
    main()