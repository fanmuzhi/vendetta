#!/usr/bin/env python
# encoding: utf-8
"""
# Description: adb operation module
"""
__filename__ = "adb"
__version__ = "init"
__author__ = "@henry.fan"

import logging
import os
import subprocess
import time
import json

class ADB:
    """
    adb class for adb operations, operated based on subprocess module
    """

    def __init__(self, device_id=None):
        self._device_id = device_id
        self.adb_proc = None
        self.adb_cmd_head = ['adb']
        if self._device_id:
            self.adb_cmd_head.extend(['-s', self._device_id])
        self.adb_root()

    @staticmethod
    def adb_devices():
        cmd_adb_devices = ['adb', 'devices']
        ret = subprocess.run(
            cmd_adb_devices,
            # shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            encoding="utf-8",
            timeout=20,
        )
        devices = ret.stdout.split()[4:]
        if not devices:
            raise RuntimeError('empty adb devices list')
        device_id = devices[0]
        return device_id

    def adb_shell_popen(self, cmd):
        assert cmd
        cmd = cmd.split() if isinstance(cmd, str) else cmd
        cmd = " ".join(self.adb_cmd_head + ['shell'] + cmd)
        self.adb_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        return self.adb_proc

    def adb_root(self):
        cmd = self.adb_cmd_head + ['root']
        ret = subprocess.run(cmd, check=True, timeout=60)
        self.adb_wait_for_device()
        return ret

    def adb_wait_for_device(self):
        cmd = self.adb_cmd_head + ['wait-for-device']
        i = 0
        dev_ready = False
        while not dev_ready:
            if i > 100:
                logging.error("ADB device connection lost, please check.")
                raise RuntimeError('Error in Waiting for adb devices')
            try:
                ret = subprocess.run(cmd, timeout=2)
                dev_ready = True if ret.returncode == 0 else False
            except subprocess.TimeoutExpired as e:
                i += 1

    def adb_remount(self):
        cmd = self.adb_cmd_head + ['remount']
        ret = subprocess.run(cmd, check=True, timeout=900)
        self.adb_wait_for_device()
        return ret

    def adb_push(self, local, remote):
        cmd = self.adb_cmd_head + ['push', local, remote]
        ret = subprocess.run(cmd, check=True, timeout=900)
        self.adb_wait_for_device()
        return ret

    def adb_pull(self, remote, local):
        cmd = self.adb_cmd_head + ['pull', remote, local]
        ret = subprocess.run(cmd, check=True, timeout=900)
        self.adb_wait_for_device()
        return ret

    def adb_reboot(self):
        cmd = self.adb_cmd_head + ['reboot']
        ret = subprocess.run(cmd, check=True, timeout=900)
        self.adb_wait_for_device()
        time.sleep(5)
        return ret

    def adb_proc_stop(self):
        if self.adb_proc:
            self.adb_proc.kill()
            self.adb_proc = None

    def adb_shell_run(self, cmd, **kwargs):
        assert cmd
        cmd = cmd.split() if isinstance(cmd, str) else cmd
        cmd = " ".join(self.adb_cmd_head + ['shell'] + cmd)
        ret = subprocess.run(cmd, **kwargs)
        self.adb_wait_for_device()
        return ret

    def adb_set_selinux(self, enable):
        cmd = ['setenforce', enable]
        ret = self.adb_shell_run(cmd, check=True, timeout=60)
        return ret

    def adb_sync(self):
        cmd = ['sync']
        ret = self.adb_shell_run(cmd, check=True, timeout=60)
        return ret

    def adb_chmod(self, value, target):
        cmd = ['chmod', value, target]
        ret = self.adb_shell_run(cmd, check=True, timeout=60)
        return ret

    def adb_rm_all_files_in(self, dir):
        cmd = ['rm', '-rf', os.path.join(dir, "*")]
        ret = self.adb_shell_run(cmd, check=True, timeout=60)
        return ret

    def adb_cat(self, file):
        cmd = ['cat', file]
        ret = self.adb_shell_run(cmd, stdout=subprocess.PIPE, check=True, timeout=60)
        return ret.stdout

    def adb_sensor_info(self):
        cmd = ['ssc_sensor_info']
        ret = self.adb_shell_run(cmd, stdout=subprocess.PIPE, encoding='utf-8', check=True, timeout=60)
        return ret.stdout

    def imu_bias_values(self, productname, sensor):
        if not sensor:
            return
        bias_folder = r'mnt/vendor/persist/sensors/registry/registry'
        biasfile = rf'{bias_folder}/{productname}_0_platform.{sensor}.fac_cal.bias'

        text = self.adb_cat(biasfile)
        json_buffer = json.loads(text.decode())
        root = list(json_buffer.keys())[0]
        return int(json_buffer[root]['x']['ver']), \
               int(json_buffer[root]['y']['ver']), \
               int(json_buffer[root]['z']['ver']),


if __name__ == '__main__':
    """
    debug code for adb.py module
    """
    dev_id = ADB.adb_devices()
    adb = ADB(device_id=dev_id)
    print(adb.adb_sensor_info())
