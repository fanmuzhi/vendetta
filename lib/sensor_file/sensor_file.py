#!/usr/bin/env python
# encoding: utf-8
"""
# Description: SEE platform *.JSON registry file module
"""
__filename__ = "registry"
__version__ = "init"
__author__ = "@henry.fan"

import os
import json
from lib.adb.adb import ADB
# import config as cfg


class ConfigJson:
    """json config files class for config: eg: registry(local) and bias(in system)"""

    def __init__(self, json_file):
        self._json_file = json_file
        self._json_buffer = {}
        # self.load_local_json()

    def load_local_json(self):
        with open(self._json_file) as registry:
            self._json_buffer = json.load(registry)

    def load_remote_json(self, dev_id=None):
        cat = ADB(dev_id).adb_cat(self._json_file)
        self._json_buffer = json.loads(cat.decode())

    def dump_json(self, dump_file):
        assert self._json_buffer
        json.dump(self._json_buffer, dump_file, indent=4, ensure_ascii=False)

    def get_json(self):
        return self._json_buffer


class Registry(ConfigJson):
    """
    Registry class for driver *.JSON registry file
    """

    def __init__(self, regfile, product):
        super(Registry, self).__init__(regfile)
        assert os.path.exists(regfile)
        assert product
        self._product = product
        self.load_local_json()

    def _change_res_value(self, sensor, res, hw_id=0):
        assert self._json_buffer[f'{self._product}_{hw_id}'][f'.{sensor}']['.config'][
            'res_idx'
        ]['data']
        self._json_buffer[f'{self._product}_{hw_id}'][f'.{sensor}']['.config'][
            'res_idx'
        ]['data'] = str(res)

    def change_reg_res(
        self,
        hw_id=0,
        # acc_res=None,
        # gyr_res=None,
        **kwargs,
    ):
        assert os.path.exists(self._json_file)
        reg_path, reg_name = os.path.split(self._json_file)
        for k, v in kwargs.items():
            self._change_res_value(k, v, hw_id=hw_id)
            # if gyr_res is not None:
            #     self._change_res_value(cfg.Sensor.gyr.value, gyr_res)
        temp_file_name = os.path.join(reg_path, f'temp_{reg_name}')
        with open(temp_file_name, 'w') as f_temp:
            self.dump_json(f_temp)
        dest = os.path.join(cfg.QcmBoard.conf_dest_dir, reg_name)
        self.switch_reg_file(temp_file_name, dest)
        os.remove(temp_file_name)

    def reset_orig_reg(self):
        reg_path, reg_name = os.path.split(self._json_file)
        dest = os.path.join(cfg.QcmBoard.conf_dest_dir, reg_name)
        self.switch_reg_file(self._json_file, dest)

    @staticmethod
    def switch_reg_file(reg, dest, adb_id=None):
        adb = ADB(adb_id)
        adb.adb_root()
        adb.adb_remount()
        adb.adb_rm_all_files_in(cfg.QcmBoard.registry_dir)
        adb.adb_push(reg, dest)

    @staticmethod
    def sync_reg(adb_id=None):
        adb = ADB(adb_id)
        adb.adb_sync()
        adb.adb_reboot()
        adb.adb_root()


class FacCalBias(ConfigJson):
    def __init__(self, bias_file, dev_id=None):
        # assert product
        super(FacCalBias, self).__init__(bias_file)
        self.load_remote_json(dev_id)

    def read_imu_bias_values(self, sensor):
        if not sensor:
            return
        bias_dict = self._json_buffer
        root = list(bias_dict.keys())[0]
        return (
            int(bias_dict[root]['x']['ver']),
            int(bias_dict[root]['y']['ver']),
            int(bias_dict[root]['z']['ver']),
        )


if __name__ == '__main__':
    regfile = r'C:\workspace\BPDD\SEE\8250_androidQ\config\kona_hdk_bmi26x_0.json'
    prod = cfg.Product.bmi26x
    reg = Registry(regfile, prod)
    reg.reset_orig_reg()
