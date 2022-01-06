#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "csv_log_parser"
__version__ = "init"
__author__ = "@henry.fan"

import math
import os
import re

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

# result = {True: 'Pass', False: 'Fail', None: 'N/A'}
axises = ['x', 'y', 'z']
units = {'accel': 'm/s^2', 'gyro': 'rad/s', 'mag': 'µT'}

data_bases = {
    'accel': {'x': 0.0, 'y': 0.0, 'z': 9.8},
    'gyro': {'x': 0.0, 'y': 0.0, 'z': 0.0},
    'mag': {'x': 0.0, 'y': 0.0, 'z': 0.0},
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
        self.stats = self.data_df.describe()
        self.unit = units[self.sensor]

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

    def check_odr(self, ignore_min=False, ignore_max=False):
        col_name = 'interval'
        intv = calc_interval_ms(self.odr)
        l_limit = 0 * intv if not ignore_min else -float('inf')
        h_limit = 1.8 * intv if not ignore_max else float('inf')
        intv_min = self.stats[col_name]['min']
        intv_max = self.stats[col_name]['max']
        assert (
            l_limit
            <= self.stats[col_name]['min']
            < self.stats[col_name]['max']
            < h_limit
        ), f'{self.sensor} time interval [{intv_min}, {intv_max}] data out of range [{l_limit} {h_limit}] in <{self.csv_file}>'

    def check_data_range(self, col_name, axis):
        # col_name = f'{self.sensor.capitalize()} {axis.upper()} ({self.unit})'
        l_limit = data_bases[self.sensor][axis] - data_offsets[self.sensor][axis]
        h_limit = data_bases[self.sensor][axis] + data_offsets[self.sensor][axis]
        data_min, data_max = self.stats[col_name]['min'], self.stats[col_name]['max']
        assert (
            l_limit <= data_min <= data_max <= h_limit
        ), f"{col_name} data [{data_min}, {data_max}] out of range [{l_limit}, {h_limit}] in {self.csv_file}"

    def check_data_stddev(self, col_name, axis):
        stddev = self.stats[col_name]['std']
        l_limit = 0
        # h_limit = 0
        h_limit = stddev_limits[self.sensor][axis]
        assert (
            l_limit < stddev < h_limit
        ), f"{col_name} standard deviation {stddev} exceeds limit [{l_limit}, {h_limit}] in {self.csv_file}"


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    folder = r'C:\Users\FNH1SGH\Desktop\logs\dlf\20210830161604_Stream_ssr=mag_dur=30_sr=-1_hw=0\Data'
    # folder_parsing(folder, skip_data=1)
