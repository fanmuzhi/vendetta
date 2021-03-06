#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "conftest.py"
__version__ = "init"
__author__ = "@henry.fan"

import pytest
import itertools
import subprocess
import xml.dom.minidom
import lib.seevt.seevt

from lib.ssc_drva.ssc_drva import SscDrvaTest
from lib.quts.quts import *
from lib.seevt.seevt import Qseevt
from lib.utils import *

productname = 'bmi3x0'
n_hw = 1
hwid = list(range(n_hw))
sensor_list = ['accel', 'gyro']
# sensor_list = ['accel']
streamtest_odr_list = [-2, 50, 100, 200, -1, -3.0]
# streamtest_odr_list = [-2, 50]
factest_type_list = [1, 2, 3]
sensor_streamtest_dur = 30
sensor_factest_dur = 5
ssc_drva_delay = 2
null_params = [None]


using_ssc_drva_keys = [
    'sensor',
    'duration',
    'sample_rate',
    'factory_test',
    'hw_id',
    'delay',
]


def extern_conc_streamtest_odr_to_dur(odr):
    if isinstance(odr, int):
        return 100
    else:
        return 10


def setup_param_sets(params_list):
    """
     :param params_list:
        eg:{
             'sensor': ('gyro', 'gyro'),
             'duration': (30, 5),
             'sample_rate': (-1, None),
             'factory_test': (None, 2),
             'hw_id': (0, 0),
             'delay': (None, 2)
         }
     # :return: param_sets
     """
    param_sets = [dict(), dict()]
    for k, v in params_list.items():
        if v is not None:
            for i in range(2):
                if v[i] is not None:
                    param_sets[i].update({k: v[i]})
    return param_sets


def test_case_id_str(pairs):
    id_word_list = []
    for i in range(2):
        if pairs['sensor'][i]:
            id_word_list.append(pairs['sensor'][i])
        if pairs['sample_rate'] and pairs['sample_rate'][i] is not None:
            id_word_list.append(cfg.Odr(pairs['sample_rate'][i]).name)
        if pairs['factory_test'] and pairs['factory_test'][i] is not None:
            id_word_list.append(cfg.FacTest(pairs['factory_test'][i]).name)
        if pairs['hw_id'] and pairs['hw_id'][i] is not None:
            id_word_list.append(f"hw{pairs['hw_id'][i]}")
    id = '-'.join(id_word_list)
    return id


def match_summary_text(diag_service, re_pattern, data_queue='data'):
    diag_packets = diag_service.getDataQueueItems(data_queue, 1, 20)
    while diag_packets:
        if re.search(re_pattern, diag_packets[0].summaryText):
            found = True
            break
        diag_packets = diag_service.getDataQueueItems(data_queue, 1, 20)
    else:
        found = False
    return found


def pytest_generate_tests(metafunc):
    fixturename = ''
    params_list = []
    if "factorytest" in metafunc.fixturenames:
        fixturename = 'factorytest'
        params_sensor = list(itertools.product(sensor_list, [None]))
        params_factest_type = list(itertools.product(factest_type_list, [None]))
        params_odr = null_params
        params_dur = list(itertools.product([sensor_factest_dur], [None]))
        params_hwid = list(itertools.product(hwid, [None]))
        params_delay = null_params

        params_list = list(
            itertools.product(
                params_sensor,
                params_dur,
                params_odr,
                params_factest_type,
                params_hwid,
                params_delay,
            )
        )

    if "streamtest" in metafunc.fixturenames:
        fixturename = 'streamtest'
        params_sensor = list(itertools.product(sensor_list, [None]))
        params_dur = list(itertools.product([sensor_streamtest_dur], [None]))
        if "change_registry_res_value" in metafunc.fixturenames:
            params_odr = list(
                itertools.product(
                    [cfg.Odr.odr_max.value, cfg.Odr.odr_min.value], [None]
                )
            )
        else:
            params_odr = list(itertools.product(streamtest_odr_list, [None]))

        if "dynarange" in metafunc.fixturenames:
            params_sensor = list(itertools.product(sensor_list, [None]))
        params_factest_type = null_params
        params_hwid = list(itertools.product(hwid, [None]))
        params_delay = null_params
        params_list = list(
            itertools.product(
                params_sensor,
                params_dur,
                params_odr,
                params_factest_type,
                params_hwid,
                params_delay,
            )
        )

    if "intern_conc_streamtest" in metafunc.fixturenames:
        fixturename = 'intern_conc_streamtest'
        params_sensor = [tuple(itertools.repeat(sensor, 2)) for sensor in sensor_list]
        params_dur = [(30, 30)]
        params_odr = [(-1, -2), (-3.1, -3.2)]
        params_factest_type = null_params
        params_hwid = [(0, 0)]
        params_delays = list(itertools.product([None], [ssc_drva_delay]))
        params_list = list(
            itertools.product(
                params_sensor,
                params_dur,
                params_odr,
                params_factest_type,
                params_hwid,
                params_delays,
            )
        )

    if "intern_conc_factest" in metafunc.fixturenames:
        fixturename = 'intern_conc_factest'
        params_sensor = [tuple(itertools.repeat(sensor, 2)) for sensor in sensor_list]
        params_odr = list(itertools.product([-1], [None]))
        params_factest_type = list(itertools.product([None], [1, 2]))
        params_dur = [(30, 5)]
        params_hwid = [(0, 0)]
        params_delays = list(itertools.product([None], [ssc_drva_delay]))
        params_list = list(
            itertools.product(
                params_sensor,
                params_dur,
                params_odr,
                params_factest_type,
                params_hwid,
                params_delays,
            )
        )

    if "extern_conc_streamtest" in metafunc.fixturenames:
        fixturename = 'extern_conc_streamtest'
        params_sensor = list(itertools.permutations(sensor_list, 2))
        params_dur = null_params
        params_odr = [(-1, -2), (-1, -3.1), (-2, -3.2), (-3.0, -3.1)]
        params_factest_type = null_params
        params_hwid = [(0, 0)]
        params_delays = list(itertools.product([None], [ssc_drva_delay]))
        params_list = []
        for odr in params_odr:
            params_list.extend(
                list(
                    itertools.product(
                        params_sensor,
                        [
                            (
                                extern_conc_streamtest_odr_to_dur(odr[0]),
                                extern_conc_streamtest_odr_to_dur(odr[1]),
                            )
                        ],
                        [odr],
                        params_factest_type,
                        params_hwid,
                        params_delays,
                    )
                )
            )
    params_sets_list = [
        setup_param_sets(dict(zip(using_ssc_drva_keys, param))) for param in params_list
    ]
    ids = [test_case_id_str(dict(zip(using_ssc_drva_keys, param))) for param in params_list]

    metafunc.parametrize(fixturename, params_sets_list, ids=ids)


@pytest.fixture(scope='session', autouse=True)
def isadmin():
    if is_admin():
        return True
    else:
        pytest.exit("Please run this app as adminisitrator")


# adb fixtures
@pytest.fixture(scope="session", autouse=True)
def adb():
    if not ADB.adb_devices():
        pytest.exit("No ADB devices found")
        # pytest.exit(ADB.adb_devices())
    adb = ADB()
    adb.adb_root()
    yield adb
    del adb


# ssc_drva fixtures
@pytest.fixture(scope="package")
def ssc_drva(adb):
    ssc_drva = SscDrvaTest(adb)
    yield ssc_drva
    del ssc_drva

#
# @pytest.fixture(scope='package')
# def run_ssc_drva_test(ssc_drva, request):
#     param_sets = request.param
#     ssc_drva_cmd = ssc_drva.set_ssc_drva_cmd(param_sets=param_sets)
#     ssc_drva.ssc_drva_run(ssc_drva_cmd)
#     return None


# quts fixtures
@pytest.fixture(scope='session', autouse=True)
def add_quts_sys_path():
    if sys.platform.startswith("linux"):
        sys.path.append('/opt/qcom/QUTS/Support/python')
    elif sys.platform.startswith("win"):
        sys.path.append('C:\Program Files (x86)\Qualcomm\QUTS\Support\python')
    elif sys.platform.startswith("darwin"):
        sys.path.append('/Applications/Qualcomm/QUTS/QUTS.app/Contents/Support/python')


@pytest.fixture(scope="package")
def quts_client():
    client = QutsClient.QutsClient("BST MEMS Sensor Driver Test")
    yield client
    client.stop()
    del client


@pytest.fixture(scope='package')
def quts_set_all_callbacks(quts_client):
    set_all_callbacks(quts_client)


@pytest.fixture(scope='function')
def data_queue(quts_diag_service):
    queuename = 'data'
    error_code = create_data_queue_for_monitoring(
        quts_diag_service, queue_name=queuename
    )
    if error_code != 0:
        pytest.exit("Error  creating data queue error code: {error_code}")
    # else:
    #     print("Data queue Created")
    yield queuename
    quts_diag_service.removeDataQueue(queuename)
    # del items


@pytest.fixture(scope="package", autouse=True)
def quts_dev_mgr(quts_client):
    dev_mgr = quts_client.getDeviceManager()
    return dev_mgr


@pytest.fixture(scope="package", autouse=True)
def quts_list_devices(quts_dev_mgr):
    device_list = quts_dev_mgr.getDeviceList()
    if not device_list:
        pytest.exit("No device found")


@pytest.fixture(scope="function", autouse=True)
def quts_list_services(quts_dev_mgr):
    services_list = quts_dev_mgr.getServicesList()
    if not services_list:
        pytest.exit("No service found")


@pytest.fixture(scope="package", autouse=True)
def quts_device_handle(quts_dev_mgr):
    device_handle = get_device_handle(quts_dev_mgr)
    if not device_handle:
        pytest.exit("No Qualcomm USB Composite Device Found")
    yield device_handle
    del device_handle


@pytest.fixture(scope="package", autouse=True)
def quts_list_protocals(quts_dev_mgr, quts_device_handle):
    protocol_handle = None
    if not get_diag_protocal_handle(quts_dev_mgr, quts_device_handle):
        pytest.exit("No Qualcomm USB Composite Protocal Found")
    yield protocol_handle
    del protocol_handle


@pytest.fixture(scope="package", autouse=True)
def quts_device_service(quts_client, quts_device_handle):
    dev_service = DeviceConfigService.DeviceConfigService.Client(
        quts_client.createService(
            DeviceConfigService.constants.DEVICE_CONFIG_SERVICE_NAME,
            quts_device_handle,
        )
    )
    if not dev_service:
        pytest.exit("No Qualcomm USB Composite Device Found")
    dev_service.initializeService()

    yield dev_service

    dev_service.destroyService()
    del dev_service


@pytest.fixture(scope="package")
def quts_diag_service(quts_client, quts_device_handle):
    diag_service = DiagService.DiagService.Client(
        quts_client.createService(
            DiagService.constants.DIAG_SERVICE_NAME, quts_device_handle
        )
    )
    diag_service.initializeService()

    yield diag_service

    diag_service.destroyService()
    del diag_service


@pytest.fixture(scope="package", autouse=True)
def quts_load_config(quts_diag_service):
    with open(r'C:\Users\FNH1SGH\Desktop\mydmc.dmc', 'rb') as f:
        quts_diag_service.setLoggingMask(f.read(), 2)  # 2 for dmc file
    if 0 != quts_diag_service:
        quts_diag_service.getLastError()


@pytest.fixture(scope='package')
def qseevt():
    seevt = Qseevt(lib.seevt.seevt.seevt_exe)
    seevt.run()
    seevt.enter_log_analysis_window()
    seevt.minimize()
    yield seevt

    seevt.close()
    del seevt


@pytest.fixture(scope='package', autouse=True)
def check_protos():
    if not os.path.exists(cfg.seevt_protos_dir):
        pytest.exit(
            'No Protos imported for QSEEVT tool, please import .protos in QSEEVT first'
        )
    if not os.path.exists(r'C:\ProgramData\Qualcomm\Qualcomm_SEEVT\Protos.config'):
        pytest.exit(
            'No Protos imported for QSEEVT tool, please import .protos in QSEEVT first'
        )
    tree = xml.dom.minidom.parse(cfg.proto_config_file)
    configuration = tree.documentElement
    current_protos = configuration.getElementsByTagName("CurrentProtos")
    if not current_protos or not current_protos[0].firstChild.data:
        pytest.exit(
            'No Protos imported for QSEEVT tool, please import .protos in QSEEVT first'
        )


@pytest.fixture(scope='package', autouse=True)
def sensor_info_txt(adb):
    text = adb.adb_sensor_info()
    if text:
        filename = os.path.join(os.path.dirname(__file__), 'sensorinfo.txt')
        with open(filename, 'w') as f:
            f.write(text)
        yield filename
        os.remove(filename)
    else:
        pytest.exit('Cannot get ssc_sensor_info text')


@pytest.fixture(scope='package', autouse=True)
def sensor_registry(adb):
    text = adb.adb_cat(
        rf'/vendor/etc/sensors/config/{cfg.platform_code["hdk8350"]}_hdk_{productname}_0.json'
    )
    registry_dict = json.loads(text)
    if not registry_dict:
        pytest.exit('cannot load the registry file from the system')
    yield registry_dict
    del registry_dict


@pytest.fixture(scope='package')
def reset_origin_registry(adb, sensor_registry, hw_id=0):
    yield
    new_regi = sensor_registry.copy()
    reg_file_name = rf'./{cfg.platform_code["hdk8350"]}_hdk_{productname}_{hw_id}.json'
    with open(reg_file_name, 'w') as f:
        json.dump(new_regi, f)
    adb.update_registry_file(reg_file_name)
    os.remove(reg_file_name)
    print('origin registry reset')


@pytest.fixture(scope='class')
def change_registry_res_value(adb, sensor_registry, request, hw_id=0):
    """
    [
        {'accel': 1, 'gyro': 2,},
        {'accel': 2, 'gyro': 3,},
    ]
    :return:
    """
    new_regi = sensor_registry.copy()
    for sensor, res_val in request.param.items():
        new_regi[f'{productname}_{hw_id}'][f'.{sensor}']['.config']['res_idx'][
            'data'
        ] = str(res_val)
    reg_file_name = rf'./{cfg.platform_code["hdk8350"]}_hdk_{productname}_{hw_id}.json'
    with open(reg_file_name, 'w') as f:
        json.dump(new_regi, f)
    adb.update_registry_file(reg_file_name)
    os.remove(reg_file_name)


@pytest.fixture(scope='function')
def test_case_info():
    pass
