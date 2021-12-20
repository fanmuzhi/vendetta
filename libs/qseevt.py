# =================================================================
# Module:   qaatControl
# Function: Provide the interfaces to operate qaat
# Date:     June 12th 2018
# =================================================================
import logging
from pywinauto import application

# from pywinauto.findbestmatch import find_best_match
# from pywinauto.findwindows import find_window
# import pywinauto.findwindows as findwindows
from pywinauto.handleprops import children, dumpwindow

# classname, clientrect, contexthelpid, \
# controlid, exstyle, font, has_exstyle, has_style, is64bitprocess, \
# is_toplevel_window, isenabled, isunicode, isvisible, iswindow, parent, processid, \
# rectangle, style, text, userdata
import os

# import win32gui
# import re
import time

# from log import logger
import ctypes, sys
from libs.utils import *

# logger = logging.getLogger(__name__)

qseevt_luanch_window_name = "Qualcomm Sensor Execution Environment Validation Tool"
btn_run_analysis_on_existing_log_file = "Run Analysis on Existing Log File"

log_analysis_window_name = (
    "Qualcomm Sensor Execution Environment Validation Tool:  Log Analysis"
)
btn_run_log_analysis = 'Run Log Analysis'
choose_log_file_window_name = "Choose the log file to parse!"
status_strip = 'StatusStrip'


Finish_flag = "Log analysis completed!"
wait_for_ready = 'ready'
space_keystrokes = '{SPACE}'
# windows_task_mgt_name = "taskmgr.exe"
# task_mgr_window_name = "Windows Task Manager"
# end_Process = "End Process"

# ClassID would be different in each Win Env
# Log_Analysis_win_class = "WindowsForms10.Window.8.app.0.1a0e24_r9_ad1"

# ClassID would be different in each Win Env
# RichEdit_class_name = "WindowsForms10.RichEdit20W.app.0.141b42a_r9_ad1"

# Finish_flag = "Validation Tool completed!"


# class WindowMgr:
#     """Encapsulates some calls to the winapi for window management"""
#
#     def __init__(self):
#         """Constructor"""
#         self._handle = None
#
#     def find_window(self, class_name, window_name=None):
#         """find a window by its class_name"""
#         self._handle = win32gui.FindWindow(class_name, window_name)
#         # print(self._handle)
#
#     def _window_enum_callback(self, h_wnd, wildcard):
#         """Pass to win32gui.EnumWindows() to check all the opened windows"""
#         if re.match(wildcard, str(win32gui.GetWindowText(h_wnd))) is not None:
#             self._handle = h_wnd
#
#     def find_window_wildcard(self, wildcard):
#         """find a window whose title matches the wildcard regex"""
#         self._handle = None
#         win32gui.EnumWindows(self._window_enum_callback, wildcard)
#
#     def set_foreground(self):
#         """put the window in the foreground"""
#         win32gui.SetForegroundWindow(self._handle)
#
#     @staticmethod
#     def show_window_attr(hwnd):
#
#         if not hwnd:
#             return
#         title = win32gui.GetWindowText(hwnd)
#         clsname = win32gui.GetClassName(hwnd)
#
#         return title, clsname
#
#     def show_windows(self, hwnd_list):
#         for h in hwnd_list:
#             self.show_window_attr(h)
#
#     def demo_top_windows(self):
#
#         hwnd_list = []
#         win32gui.EnumWindows(lambda hwnd, param: param.append(hwnd), hwnd_list)
#         self.show_windows(hwnd_list)
#
#         return hwnd_list
#
#     def demo_child_windows(self):
#         parent = self._handle
#
#         if not parent:
#             return
#
#         h_wnd_child_list = []
#         win32gui.EnumChildWindows(parent, lambda h_wnd, param: param.append(h_wnd), h_wnd_child_list)
#         self.show_windows(h_wnd_child_list)
#         return h_wnd_child_list


class Qseevt(object):
    def __init__(self, app_name):
        """
        Init an application
        """

        self.app = application.Application()
        # self.window = WindowMgr()
        self.app_name = app_name

    def run(self):
        self.app.start(self.app_name)
        self.app[qseevt_luanch_window_name].wait(wait_for_ready)

    def enter_log_analysis_window(self):
        self.app[qseevt_luanch_window_name].wait(wait_for_ready)
        self.app[qseevt_luanch_window_name][
            btn_run_analysis_on_existing_log_file
        ].send_keystrokes(space_keystrokes)
        self.app[log_analysis_window_name].wait(wait_for_ready)
        # for i, child in enumerate(self.app[log_analysis_window_name].children()):
        #     print(i, ":", child)

    def set_hdffile_text(self, hdf_file):
        self.app[log_analysis_window_name].wait(wait_for_ready)
        self.app[log_analysis_window_name].children()[7].set_text(hdf_file)
        self.app[log_analysis_window_name].wait(wait_for_ready)

    def set_sensor_info_file_text(self, info_file):
        self.app[log_analysis_window_name].wait(wait_for_ready)
        self.app[log_analysis_window_name].children()[10].set_text(info_file)
        self.app[log_analysis_window_name].wait(wait_for_ready)

    def run_log_analysis(self):
        self.app[log_analysis_window_name].wait(wait_for_ready)
        self.app[log_analysis_window_name][btn_run_log_analysis].send_keystrokes(
            space_keystrokes
        )
        self.app[log_analysis_window_name].wait(wait_for_ready)

    def get_status_text(self):
        self.app[log_analysis_window_name].wait(wait_for_ready)
        status_text = self.app[log_analysis_window_name][status_strip].GetPartText()
        self.app[log_analysis_window_name].wait(wait_for_ready)
        return status_text

    def wait(self, window_name, wait_for):
        self.app[window_name].wait(wait_for)

    # def connect(self, window_name):
    #     self.app.connect(title=window_name)
    #     time.sleep(1)

    def close(self):
        self.app[log_analysis_window_name].close()
        # print(f'close {self.app.is_process_running()}')

    def minimize(self):
        self.app[log_analysis_window_name].minimize()

    def click(self, window_name, controller):
        self.app[window_name][controller].click()

    def set_focus(self, window_name, controller):
        self.app[window_name][controller].set_focus()

    def send_keystrokes(self, window_name, controller, keystrokes):
        self.app[window_name][controller].send_keystrokes(keystrokes)

    def input(self, window_name, controller, content):
        self.app[window_name][controller].set_edit_text(content)

    # def set_window_foreground(self, window_name):
    #     self.window.find_window_wildcard(window_name)
    #     self.window.set_foreground()
    #     time.sleep(1)

    def get_last_info_text(self):
        # w_handle = findwindows.find_windows(class_name=Log_Analysis_win_class)
        texts = self.app[log_analysis_window_name].children()[15].texts()
        return texts

    def get_test_proc_info_richedit(self):

        w_handle = self.app[log_analysis_window_name]
        edit = w_handle.children()[0].children()[0].children()[0]
        richedit_content = dumpwindow(edit)['text']
        return richedit_content

    def analyze_complete(self):
        text_list = self.get_last_info_text()
        if isinstance(text_list, list) and 'Log analysis completed!' in text_list:
            return True
        else:
            return False

        # hwd = w_handle[0]
        # winlist = children(hwd)
        #
        # richedit_content = dumpwindow(winlist[2])['text']
        # return richedit_content

    def parse_hdf_to_csv(self, hdflogfile, sensor_info_txt):
        self.set_hdffile_text(hdflogfile)
        self.set_sensor_info_file_text(info_file=sensor_info_txt)
        self.run_log_analysis()
        while not self.analyze_complete():
            time.sleep(0.1)
        parsed_folder = os.path.splitext(hdflogfile)[0]
        csv_data_logs = []
        for par, dirs, files in os.walk(parsed_folder):
            # csv_data_logs += [os.path.join(par, f) for f in files if valid_csv_name(f)]
            for f in files:
                if valid_csv_name(f):
                    csv_data_logs.append(os.path.join(par, f))
        return csv_data_logs


def analyze_hdf_file(hdf_file, seevt_exe, out=False):
    ret_val = False
    wait_until = 'ready'
    p_qawa = Qseevt(seevt_exe)
    logging.info("Start qaat to analyze logs")
    try:
        logging.info("Open Log Analysis dialog window")
        p_qawa.run()
        p_qawa.wait(qseevt_luanch_window_name, wait_until)
        # p_qawa.minimize(main_window_name)
        p_qawa.send_keystrokes(
            qseevt_luanch_window_name, btn_run_analysis_on_existing_log_file, '{SPACE}'
        )

        logging.info("Browse log file .hdf log file")
        p_qawa.wait(log_analysis_window_name, wait_until)
        # for i, child in enumerate(p_qawa.app[log_analysis_window_name].children()):
        #     print("---", i, child)
        p_qawa.app[log_analysis_window_name].children()[7].set_text(r"c:\r.hdf")
        time.sleep(1)
        p_qawa.app[log_analysis_window_name].children()[10].set_text(r"c:\bmi320.txt")

        time.sleep(100)

        # p_qawa.minimize(log_analysis_window_name)
        p_qawa.wait(log_analysis_window_name, wait_until)
    except application.AppStartError as e:
        logging.error(e)
    name, ext = os.path.splitext(hdf_file)
    try:
        assert os.path.exists(hdf_file)
    except AssertionError:
        logging.error("dlf file is not existed, please confirm.")
        return ret_val

    # p_qawa.minimize(log_analysis_window_name)
    p_qawa.wait(log_analysis_window_name, wait_until)

    # time.sleep(10)
    # p_qawa.send_keystrokes(log_analysis_window_name, "...", '{SPACE}')

    logging.info("Input log file name!")
    p_qawa.wait(choose_log_file_window_name, wait_until)
    # p_qawa.minimize(choose_log_file_window_name)
    p_qawa.input(choose_log_file_window_name, "Edit", hdf_file)
    p_qawa.wait(choose_log_file_window_name, wait_until)
    p_qawa.send_keystrokes(choose_log_file_window_name, r"&Open", '{SPACE}')

    logging.info("Run Analysis")
    p_qawa.wait(log_analysis_window_name, wait_until)
    # p_qawa.minimize(log_analysis_window_name)
    p_qawa.wait(log_analysis_window_name, wait_until)
    p_qawa.send_keystrokes(log_analysis_window_name, "Run Log Analysis", '{SPACE}')

    analysis_running = True
    printed_msg = ''
    logging.info(f"analysing {hdf_file}...")
    while analysis_running:
        current_proc_msg = p_qawa.get_test_proc_info_richedit()
        if len(current_proc_msg) > len(printed_msg):
            if out:
                logging.debug(current_proc_msg[len(printed_msg) :])
            printed_msg = current_proc_msg
        if Finish_flag in current_proc_msg:
            logging.info("Analysis is done!")
            analysis_running = False
            ret_val = True
        time.sleep(0.5)

        # time.sleep(1)
    logging.info("Close QaatCtrl window")
    p_qawa.close(log_analysis_window_name)
    return ret_val


if __name__ == "__main__":
    hdf = r'C:\Users\FNH1SGH\Desktop\hdfs\11-08.15-27-30-425.hdf'
    ret_val = False
    wait_until = 'ready'

    print(is_admin())

    if is_admin():
        print(is_admin())
        # analyze_hdf_file(hdf, seevt_exe)
        pq = Qseevt(cfg.seevt_exe)
        pq.run()

        pq.enter_log_analysis_window()
        pq.set_hdffile_text(r"C:\Users\FNH1SGH\Desktop\hdfs\11-08.15-27-30-425.hdf")
        pq.set_sensor_info_file_text(r"C:\Users\FNH1SGH\Desktop\bmi320_sensor_info.txt")
        pq.run_log_analysis()
        while 'Log analysis completed!' not in pq.get_last_info_text():
            print(pq.get_last_info_text())
            time.sleep(1)
        time.sleep(51)
        pq.close()
        #
        # pq.wait(qseevt_luanch_window_name, wait_until)
        # pq.app[m]
        #
        # time.sleep(5)
    else:
        print(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
