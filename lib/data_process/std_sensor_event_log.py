#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "csv_log_parser"
__version__ = "init"
__author__ = "@henry.fan"

import os
import re
import math
import pandas as pd
# import matplotlib.pyplot as plt
# from log import logger

ODR_SUPPORTED_MIN, ODR_SUPPORTED_MAX = 25.0, 400.0
TICKS_KHZ = 19200.0  # KHz Ticks
GVALUE = 9.8  # acceleration of natural gravity
ACCDATA_OFFSET = 1.5  # 1.5m/s2
# GYRDATA_OFFSET = math.radians(2)  # 2 degrees transformed into radians
GYRDATA_OFFSET = 0.8  # 2 degrees transformed into radians
MAGDATA_OFFSET = 100.0  # 100uT in XY axis
MAGDATA_OFFSET_Z = 200.0  # 200uT in Z axis
ACC_STDDEV_LIMIT = 0.156960  # m/s2
GYR_STDDEV_LIMIT = 0.009774  # rad/s
MAG_STDDEV_LIMIT = 1.0  # 1uT in XY axis
MAG_STDDEV_LIMIT_Z = 1.4  # 1.4uT in XY axis
INTERVAL_COEFF_L, INTERVAL_COEFF_H = 0.0, 1.8

result = {True: 'Pass', False: 'Fail', None: 'N/A'}
axises = ['x', 'y', 'z']
unit = {'accel': 'm/s^2', 'gyro': 'rad/s', 'mag': 'µT'}

data_bases = {
    'accel': {
        'x': 0.0, 'y': 0.0, 'z': 9.8
    },
    'gyro': {
        'x': 0.0, 'y': 0.0, 'z': 0.0
    },
    'mag': {
        'x': 0.0, 'y': 0.0, 'z': 0.0
    },
}

data_offsets = {
    'accel': {'x': ACCDATA_OFFSET, 'y': ACCDATA_OFFSET, 'z': ACCDATA_OFFSET},
    'gyro': {'x': GYRDATA_OFFSET, 'y': GYRDATA_OFFSET, 'z': GYRDATA_OFFSET},
    'mag': {'x': MAGDATA_OFFSET, 'y': MAGDATA_OFFSET, 'z': MAGDATA_OFFSET_Z},
}

stddev_limits = {
    'accel': {'x': ACC_STDDEV_LIMIT, 'y': ACC_STDDEV_LIMIT, 'z': ACC_STDDEV_LIMIT},
    'gyro': {'x': GYR_STDDEV_LIMIT, 'y': GYR_STDDEV_LIMIT, 'z': GYR_STDDEV_LIMIT},
    'mag': {'x': MAG_STDDEV_LIMIT, 'y': MAG_STDDEV_LIMIT, 'z': MAG_STDDEV_LIMIT_Z},
}


# more options can be specified also
def print_df(dataframe):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(dataframe)


def calc_actual_odr(request_odr):
    if request_odr >= ODR_SUPPORTED_MAX:
        return ODR_SUPPORTED_MAX
    elif request_odr <= ODR_SUPPORTED_MIN:
        return ODR_SUPPORTED_MIN
    else:
        return ODR_SUPPORTED_MIN * (
            2 ** (math.ceil(math.log(request_odr / ODR_SUPPORTED_MIN, 2)))
        )


def calc_interval_ms(odr):
    return 1000 / odr


def fac_during_streaming(testcase):

    if testcase is not None and 'ssc_drva_tags' in testcase:
        keys = []
        for tag in testcase['ssc_drva_tags']:
            if isinstance(tag, dict):
                keys += list(tag.keys())
        if 'sample_rate' in keys and 'factory_test' in keys:
            return True
        else:
            return False
    else:
        return False


class SeeDrvLog:
    def __init__(self, csv_file, skip_data=0, testcase=None):
        self.testcase = testcase
        self.enough_data_exists = False
        self.csv_file = csv_file
        self.dataheader_row = self.get_dataheader_row()
        self.info_df = self.get_info_df()
        self.sensor = self.get_sensor()
        self.odr = self.get_info_odr()
        self.dest_sensor = self.get_info_dest_sensor()
        self.data_df = self.get_data_df(skip_data)

        if len(self.data_df) > 2:
            self.enough_data_exists = True
        self.statistics = self.data_stats()
        # print_df(self.data_df.head())

    def get_dataheader_row(self):
        with open(self.csv_file, 'r') as f:
            for row, line in enumerate(f.readlines()):
                if line.startswith('#'):
                    continue
                else:
                    return row - 1
            else:
                raise RuntimeError(f'no data header row found in {self.csv_file}')

    def get_sensor(self):
        return self.info_df.loc['#Sensor'].iat[0]

    def get_info_df(self):
        return pd.read_csv(
            self.csv_file, nrows=self.dataheader_row - 1, header=None, index_col=0
        )

    def get_info_odr(self):
        odr_text_pattern = r'{ sample_rate : (\d+\.\d+) }'
        match = re.search(odr_text_pattern, self.info_df.loc['#Request'].iat[0])
        if match:
            return calc_actual_odr(float(match.groups()[0]))
        else:
            return None
        # logger.warning(f'No {e} found in {self.csv_file}')
        # return None

    def get_info_dest_sensor(self):
        return self.info_df.loc['#Destination.Sensor'].iat[0]

    def get_data_df(self, skip_data=0):
        df = pd.read_csv(
            self.csv_file,
            header=self.dataheader_row,
            # index_col=0,
        )

        df.drop(columns='Status', inplace=True, errors='ignore')
        # df['log_time'] = self.time_data(df['Log Timestamp (19.2MHz Ticks)'])
        # df['time'] = self.time_data(df['Timestamp (19.2MHz Ticks)'])
        if skip_data > 0:
            df = df.drop(list(range(skip_data)))
        df = df.assign(
            log_time=self.time_data(df['Log Timestamp (19.2MHz Ticks)']),
            time=self.time_data(df['Timestamp (19.2MHz Ticks)']),
        )
        df = df.assign(
            log_interval=df.log_time.diff().dropna(), interval=df.time.diff().dropna()
        )

        return df

    # def extend_interval_series_cols(self):
    #     self.data_df = self.data_df.assign(
    #         log_time=self.time_data(self.data_df['Log Timestamp (19.2MHz Ticks)']),
    #         time=self.time_data(self.data_df['Timestamp (19.2MHz Ticks)']),
    #     )
    #     self.data_df = self.data_df.assign(
    #         log_interval=self.data_df.log_time.diff(), interval=self.data_df.time.diff()
    #     )

    def get_mean(self, column_name) -> float:
        value = self.data_df[column_name].mean()
        return value

    def get_max(self, column_name) -> float:
        value = self.data_df[column_name].max()
        return value

    def get_min(self, column_name) -> float:
        value = self.data_df[column_name].min()
        return value

    def get_std(self, column_name) -> float:
        value = self.data_df[column_name].std()
        return value

    def get_sum(self, column_name) -> float:
        value = self.data_df[column_name].sum()
        return value

    def data_stats(self):
        return self.data_df.describe()

    @staticmethod
    def time_data(time_stamp):
        return (time_stamp - time_stamp.iloc[0]) / TICKS_KHZ

    def get_col_stats(self, col_name):
        return self.data_df[col_name].describe()
        # interval_min = self.get_min(col_name)
        # interval_max = self.get_max(col_name)
        # limit_l = interval * coeff_l if not fac_during_streaming(self.testcase) else 0
        # limit_h = interval * coeff_h if not fac_during_streaming(self.testcase) else 600
        # rslt = result[limit_l <= interval_min <= interval_max <= limit_h]
        # return {
        #     f'time_interval(ms) [{limit_l} <= {interval_min} <= {interval_max} <= {limit_h}]': rslt
        # }

    def get_range_result(self, axis):
        sensorbase = data_bases.get(self.sensor).get(axis)
        sensoroffset = data_offsets.get(self.sensor).get(axis)
        min_val = self.get_min(
            f'{self.sensor.capitalize()} {axis.upper()} ({unit.get(self.sensor)})'
        )
        max_val = self.get_max(
            f'{self.sensor.capitalize()} {axis.upper()} ({unit.get(self.sensor)})'
        )
        rslt = result[
            sensorbase - sensoroffset <= min_val <= max_val <= sensorbase + sensoroffset
        ]
        return {
            f'AXIS_{axis}_min_max [{sensorbase - sensoroffset} <= {min_val} <= {max_val} <= {sensorbase + sensoroffset}]': rslt
        }

    def get_stddev_result(self, axis):
        stddev_limit = stddev_limits.get(self.sensor).get(axis)
        stddev = self.get_std(
            f'{self.sensor.capitalize()} {axis.upper()} ({unit.get(self.sensor)})'
        )
        rslt = result[0 <= stddev <= stddev_limit]
        return {f'AXIS_{axis}_std_dev [0 <= {stddev} <= {stddev_limit}]': rslt}

    def get_log_result(self):
        ret = {'file': os.path.basename(self.csv_file)}
        ret.update(self.get_time_interval_result())
        for axis in axises:
            ret.update(self.get_range_result(axis.lower()))
        for axis in axises:
            ret.update(self.get_stddev_result(axis.lower()))
        return ret

    # def plot_sensor_data(self, axis=('X', 'Y', 'Z')):
    #     cols = [
    #         f'{self.sensor.capitalize()} {ax} ({unit.get(self.sensor)})' for ax in axis
    #     ]
    #     cols.append('time')
    #     self.data_df[cols].plot(x='time')
    #     plt.show()

    @staticmethod
    def valid_csv_name(csv_name):
        if os.path.splitext(csv_name)[1] != '.csv':
            return False
        elif (
            'resampler' in csv_name.lower()
            or '[std_sensor_event]' not in csv_name.lower()
        ):
            return False
        else:
            pattern = (
                r'^SensorAPI_([A-Z|a-z]+)_S\d+_I\d+_D\d+_R\d+_\[std_sensor_event\].csv'
            )
            m = re.match(pattern, csv_name)
            return True if m else False


# def folder_parsing(folder, skip_data=0, testcase=None):
#     rslt = []
#     for par, dirs, files in os.walk(folder):
#         for data_log in [
#             os.path.join(par, f) for f in files if SeeDrvLog.valid_csv_name(f)
#         ]:
#             try:
#                 see_log = SeeDrvLog(data_log, skip_data=skip_data, testcase=testcase)
#                 if not see_log.dest_sensor == 'da_test':
#                     continue
#                 if not see_log.enough_data_exists:
#                     logger.warning(f'No enough data length exists, skipped')
#                     continue
#                 if not see_log.odr:
#                     logger.warning(f'ODR information not found, skipped')
#                     continue
#                 logger.info(f'analyzing csv: {os.path.join(par, data_log)}')
#                 rslt.append(see_log.get_log_result())
#             except IndexError as e:
#                 logger.warning(e.args)
#                 continue
#             except KeyError as e:
#                 logger.warning(f'{e.args[0]} not found, skipped')
#                 continue
#     return rslt


# def screen_failures(d):
#     if isinstance(d, dict):
#         for k, v in d.items():
#             screen_failures(v)
#     elif isinstance(d, list):
#         for x in d:
#             screen_failures(x)
#     elif isinstance(d, bool):
#         pass
#     elif isinstance(d, str):
#         pass


if __name__ == '__main__':
    # import json
    # from pprint import pp

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    folder = (
        r'C:\Users\FNH1SGH\Desktop\logs\dlf\20210830161604_Stream_ssr=mag_dur=30_sr=-1_hw=0\Data'
    )
    # folder_parsing(folder, skip_data=1)
