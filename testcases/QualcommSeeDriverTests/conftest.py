#!/usr/bin/env python
# encoding: utf-8
"""
# Description:
"""
__filename__ = "conftest.py"
__version__ = "init"
__author__ = "@henry.fan"
import csv
import itertools
import json
import os

import pytest

import libs.config as cfg
from libs import utils
from libs import qseevt
import libs.quts as quts

from libs.adb.adb import ADB
from libs.ssc_drva.ssc_drva import SscDrvaTest

sensor_info_list = utils.sensor_info_list()

fdmc = os.path.join(os.path.dirname(__file__), 'mydmc.dmc')
extra_odrs = [-3.0, -3.1, -3.2]
streamtest_odr_list = [-2, 50, 100, 200, -1, -3.0]
factest_type_list = [1, 2, 3]
sensor_streamtest_dur = 30
sensor_factest_dur = 5
ssc_drva_delay = 2
null_params = [None]
test_result_root_dir = r'c:\SeeTests'


def pytest_addoption(parser):
    parser.addoption(
        "--product",
        action="store",
        default="",
        help="Product name in registry file, eg: 'bmi3x0'",
    )
    parser.addoption(
        "--platform",
        action="store",
        default="hdk8350",
        help="qualcomm dev board, default=hdk8350",
    )


def resvalue_id_str(registry_dict):
    words = []
    for k, v in registry_dict.items():
        words.append(f'{k}.{cfg.res_values.get(k, {}).get(v, "unknown")}')
        # words.append(cfg.res_values.get(k, {}).get(v, "unknown"))
    return f"{'-'.join(words)}"


def pytest_generate_tests(metafunc):

    if 'test_data_streaming' == metafunc.definition.name:
        params = []
        for sensor_info in sensor_info_list:
            sensor = sensor_info['TYPE']
            odrs = sensor_info['RATES'] + extra_odrs
            hw_id = sensor_info['HW_ID']
            params.extend(list(itertools.product([sensor], odrs, [hw_id])))

        if all(fix in metafunc.fixturenames for fix in ['sensor', 'odr', 'hw_id']):
            ids = [
                f'{param[0]}-{cfg.Odr(param[1]).name}-hw_{param[2]}' for param in params
            ]
            metafunc.parametrize('sensor, odr, hw_id', params, ids=ids)

    if "test_factory_test" == metafunc.definition.name:
        params = []
        for sensor_info in sensor_info_list:
            sensor = sensor_info['TYPE']
            factests = sensor_info['PHYSICAL_SENSOR_TESTS']
            hw_id = sensor_info['HW_ID']
            params.extend(list(itertools.product([sensor], factests, [hw_id])))

        if all(fix in metafunc.fixturenames for fix in ['sensor', 'factest', 'hw_id']):
            ids = [
                f'{param[0]}-{cfg.FacTest(param[1]).name}-hw_{param[2]}'
                for param in params
            ]
            metafunc.parametrize('sensor, factest, hw_id', params, ids=ids)

    if "test_internal_concurrency_stream" == metafunc.definition.name:
        params = []
        for sensor_info in sensor_info_list:
            sensor = sensor_info['TYPE']
            hw_id = sensor_info['HW_ID']
            params.extend([(sensor, -1, -2, hw_id)])
            params.extend([(sensor, -3.0, -3.1, hw_id)])

        if all(
            fix in metafunc.fixturenames for fix in ['sensor', 'odr0', 'odr1', 'hw_id']
        ):
            ids = [
                f'{param[0]}-{cfg.Odr(param[1]).name}-{cfg.Odr(param[2]).name}-hw_{param[3]}'
                for param in params
            ]
            metafunc.parametrize('sensor, odr0, odr1, hw_id', params, ids=ids)

    if "test_internal_concurrency_factest" == metafunc.definition.name:
        params = []
        for sensor_info in sensor_info_list:
            sensor = sensor_info['TYPE']
            factests = sensor_info['PHYSICAL_SENSOR_TESTS']

            hw_id = sensor_info['HW_ID']
            params.extend(
                list(
                    itertools.product(
                        [sensor], [cfg.Odr.odr_max.value], factests, [hw_id]
                    )
                )
            )

        if all(
            fix in metafunc.fixturenames
            for fix in ['sensor', 'odr', 'factest', 'hw_id']
        ):
            ids = [
                f'{param[0]}-{cfg.Odr(param[1]).name}-{cfg.FacTest(param[2]).name}-hw_{param[3]}'
                for param in params
            ]
            metafunc.parametrize('sensor, odr, factest, hw_id', params, ids=ids)

    if "test_external_concurrency" == metafunc.definition.name:
        params = []
        external_sensor_info = [
            sensor_info
            for sensor_info in itertools.permutations(sensor_info_list, 2)
            if sensor_info[0]['HW_ID'] == sensor_info[1]['HW_ID']
        ]
        for extern_info in external_sensor_info:
            sensor0, sensor1 = extern_info[0]['TYPE'], extern_info[1]['TYPE']
            odrs = [(-1, -2), (-1, -3.1), (-2, -3.2), (-3.0, -3.1)]
            hw_id = extern_info[0]['HW_ID']
            params.extend(list(itertools.product([(sensor0, sensor1)], odrs, [hw_id])))
        if all(
            fix in metafunc.fixturenames
            for fix in ['sensor0', 'odr0', 'sensor1', 'odr1', 'hw_id']
        ):
            ids = [
                f'{param[0][0]}-{cfg.Odr(param[1][0]).name}-{param[0][1]}-{cfg.Odr(param[1][1]).name}-hw_{param[2]}'
                for param in params
            ]
            metafunc.parametrize(
                'sensor0, odr0, sensor1, odr1, hw_id',
                [
                    (param[0][0], param[1][0], param[0][1], param[1][1], param[2])
                    for param in params
                ],
                ids=ids,
            )

    if "test_dual_hw" == metafunc.definition.name:
        params = []
        dualhw_sensor_info = [
            sensor_info
            for sensor_info in itertools.permutations(sensor_info_list, 2)
            if (sensor_info[0]['HW_ID'], sensor_info[1]['HW_ID']) == (0, 1)
        ]
        for extern_info in dualhw_sensor_info:
            sensor0, sensor1 = extern_info[0]['TYPE'], extern_info[1]['TYPE']
            if sensor0 == sensor1:
                odrs = [(-1, -2), (-3.0, -3.1)]
            else:
                odrs = [(-3.2, -3.2), (-2, -1)]
            # odrs = [(-1, -2), (-1, -3.1), (-2, -3.2), (-3.0, -3.1)]
            hw_id0, hw_id1 = extern_info[0]['HW_ID'], extern_info[1]['HW_ID']
            params.extend(
                list(itertools.product([(sensor0, sensor1)], odrs, [(hw_id0, hw_id1)]))
            )
        if all(
            fix in metafunc.fixturenames
            for fix in ['sensor0', 'odr0', 'hw_id0', 'sensor1', 'odr1', 'hw_id1']
        ):
            ids = [
                f'{param[0][0]}-{cfg.Odr(param[1][0]).name}-hw_{param[2][0]}-{param[0][1]}-{cfg.Odr(param[1][1]).name}-hw_{param[2][1]}'
                for param in params
            ]
            metafunc.parametrize(
                'sensor0, odr0, hw_id0, sensor1, odr1, hw_id1',
                [
                    (
                        param[0][0],
                        param[1][0],
                        param[2][0],
                        param[0][1],
                        param[1][1],
                        param[2][1],
                    )
                    for param in params
                ],
                ids=ids,
            )

    if "change_registry_res_value" in metafunc.fixturenames:
        sensors = set()
        for sensor_info in sensor_info_list:
            sensors.add(sensor_info['TYPE'])
        sensors = list(sensors)
        ranges = []
        for sensor in sensors:
            if sensor == 'accel':
                ranges.append([0, 1, 2, 3])
            if sensor == 'gyro':
                ranges.append([1, 2, 3, 4])
            if sensor == 'mag':
                ranges.append([0] * 4)
        rvs = list(zip(*ranges))
        range_vals = [dict(zip(sensors, t)) for t in rvs]
        metafunc.parametrize(
            'change_registry_res_value',
            range_vals,
            ids=[resvalue_id_str(r) for r in range_vals],
            scope='class',
            indirect=True,
        )


@pytest.fixture(scope='session', autouse=True)
def productname(request):
    productname = request.config.getoption("--product")
    if productname:
        yield productname
    else:
        pytest.exit('Invalid product name')


@pytest.fixture(scope='session', autouse=True)
def isadmin():
    if utils.is_admin():
        return True
    else:
        pytest.exit("Please run this app as adminisitrator")


@pytest.fixture(scope='session', autouse=True)
def test_dir(productname, request):

    if request.config.getoption("--html"):
        fhtml = request.config.getoption("--html")
        test_dir = os.path.dirname(os.path.abspath(fhtml))
        # test_dir = os.path.join(test_dir, f'test_{productname}_{utils.datetime_str()}')
    else:
        test_path_root = r'C:\SeeTests'
        test_dir = os.path.join(
            test_path_root, f'test_{productname}_{utils.datetime_str()}'
        )
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


@pytest.fixture(scope='package', autouse=True)
def log_path(test_dir):
    log_path = os.path.join(test_dir, 'logs')
    os.makedirs(log_path, exist_ok=True)
    yield log_path


@pytest.fixture(autouse=True)
def log_file_name(log_path, request):
    file_name = f"{request.node.name}"
    if request.cls:
        file_name = f'{request.cls.__name__}-{file_name}'
    yield file_name


# adb fixtures
@pytest.fixture(scope="session", autouse=True)
def adb():
    if not ADB.adb_devices():
        pytest.exit("No ADB devices found")
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


@pytest.fixture(scope="package")
def quts_client():
    client = quts.quts_client("BST MEMS Sensor Driver Autotest")
    yield client
    client.stop()
    del client


# @pytest.fixture(scope='package')
# def quts_set_all_callbacks(quts_client):
#     quts.set_all_callbacks(quts_client)


# @pytest.fixture(scope='function')
# def data_queue(quts_diag_service):
#     queuename = 'data'
#     error_code = quts.create_data_queue_for_monitoring(
#         quts_diag_service, queue_name=queuename
#     )
#     if error_code != 0:
#         pytest.exit("Error  creating data queue error code: {error_code}")
#     yield queuename
#     quts_diag_service.removeDataQueue(queuename)


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
    device_handle = quts.get_device_handle(quts_dev_mgr)
    if not device_handle:
        pytest.exit("No Qualcomm USB Composite Device Found")
    yield device_handle
    del device_handle


@pytest.fixture(scope="package", autouse=True)
def quts_list_protocals(quts_dev_mgr, quts_device_handle):
    protocol_handle = None
    if not quts.get_diag_protocal_handle(quts_dev_mgr, quts_device_handle):
        pytest.exit("No Qualcomm USB Composite Protocal Found")
    yield protocol_handle
    del protocol_handle


@pytest.fixture(scope="package", autouse=True)
def quts_device_service(quts_client, quts_device_handle):
    dev_service = quts.device_service(quts_client, quts_device_handle)
    if not dev_service:
        pytest.exit("No Qualcomm USB Composite Device Found")
    dev_service.initializeService()

    yield dev_service

    dev_service.destroyService()
    del dev_service


@pytest.fixture(scope="package")
def quts_diag_service(quts_client, quts_device_handle):
    diag_service = quts.diagservice_client(quts_client, quts_device_handle)
    diag_service.initializeService()

    yield diag_service

    diag_service.destroyService()
    del diag_service


@pytest.fixture()
def diag_packets_list(quts_diag_service):
    queuename = 'data'
    error_code = quts.create_data_queue_for_monitoring(
        quts_diag_service, queue_name=queuename
    )
    if error_code != 0:
        pytest.exit(f"Error  creating data queue error code: {error_code}")
    diag_packets_list = list()
    yield diag_packets_list
    quts_diag_service.removeDataQueue(queuename)
    del diag_packets_list


@pytest.fixture(autouse=True)
def save_drv_msglog(log_path, log_file_name, diag_packets_list):
    yield
    driver_msg_log_headers = ['Timestamp', 'Name', 'Message']
    drv_log_file = os.path.join(log_path, f'{log_file_name}.csv')
    with open(drv_log_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=driver_msg_log_headers)
        writer.writeheader()
        for i, diag_packet in enumerate(diag_packets_list):
            writer.writerow(
                dict(
                    zip(
                        driver_msg_log_headers,
                        [
                            diag_packet.receiveTimeString,
                            diag_packet.packetName,
                            diag_packet.summaryText,
                        ],
                    )
                )
            )


@pytest.fixture(scope="package", autouse=True)
def quts_load_config(quts_diag_service):
    with open(fdmc, 'rb') as f:
        quts_diag_service.setLoggingMask(f.read(), 2)  # 2 for dmc file
    if 0 != quts_diag_service:
        quts_diag_service.getLastError()


@pytest.fixture(scope='package')
def qseevt_app(check_protos, sensor_info_file):
    if not check_protos:
        pytest.exit(
            'No Protos imported for QSEEVT tool, please import .protos in QSEEVT'
        )
    seevt = qseevt.Qseevt(cfg.seevt_exe)
    seevt.run()
    seevt.enter_log_analysis_window()
    seevt.minimize()
    seevt.set_sensor_info_file_text(info_file=sensor_info_file)
    yield seevt

    seevt.close()
    del seevt


@pytest.fixture(scope='package')
def check_protos():
    if not os.path.exists(cfg.seevt_protos_dir) or not os.listdir(cfg.seevt_protos_dir):
        return False
    if not os.path.exists(r'C:\ProgramData\Qualcomm\Qualcomm_SEEVT\Protos.config'):
        return False
    return True


@pytest.fixture(scope='package', autouse=True)
def sensor_info_text(adb):
    text = adb.adb_sensor_info()
    if text:
        yield text
    else:
        pytest.exit('Cannot get ssc_sensor_info text')


@pytest.fixture(scope='package', autouse=True)
def sensor_info_file(sensor_info_text):
    filename = os.path.join(os.path.dirname(__file__), 'sensorinfo.txt')
    with open(filename, 'w') as f:
        f.write(sensor_info_text)
    yield filename
    os.remove(filename)


@pytest.fixture(scope='package', autouse=True)
def filter_sensorinfo_dict(sensor_info_text):
    def produce_var(string):
        try:
            var = eval(string)
        except (NameError, SyntaxError):
            var = string
        return var

    sensor_collections = ('accel', 'gyro', 'mag')
    sensor_info_list = list()
    sensor_info = dict()
    for line in sensor_info_text.splitlines():
        if line.startswith('SUID') and sensor_info:
            sensor_info_list.append(sensor_info)
            sensor_info = dict()
        try:
            k, v = [s.strip() for s in line.split('=') if line.count('=') == 1]
            sensor_info.update({produce_var(k): produce_var(v)})

        except ValueError:
            continue
    # hw_ids = [sensor_info['HW_ID'] for sensor_info in sensor_info_list if sensor_info.get('HW_ID', None) is not None]
    sensor_info_list = [
        sensor_info
        for sensor_info in sensor_info_list
        if sensor_info.get('VENDOR', '').lower() == 'bosch'
    ]
    sensor_info_list = [
        sensor_info
        for sensor_info in sensor_info_list
        if sensor_info.get('TYPE', '').lower() in sensor_collections
    ]
    yield sensor_info_list
    del sensor_info_list


@pytest.fixture(scope='package', autouse=True)
def sensor_registry(adb, request):
    productname = request.config.getoption("--product")
    platform = request.config.getoption("--platform")
    hw_ids = set()
    for sensor_info in sensor_info_list:
        hw_ids.add(sensor_info['HW_ID'])
    hw_ids = sorted(list(hw_ids))
    registries = {}
    for ihw in hw_ids:
        text = adb.adb_cat(
            rf'/vendor/etc/sensors/config/{cfg.platform_code[platform]}_hdk_{productname}_{ihw}.json'
        )
        ihw_reg = json.loads(text)
        if not ihw_reg:
            pytest.exit('cannot load the registry file from the system')
        registries.update({ihw: ihw_reg})
    yield registries
    del registries, ihw_reg


@pytest.fixture(scope='package')
def reset_origin_registry(adb, sensor_registry, request):
    yield
    platform = request.config.getoption("--platform")
    productname = request.config.getoption("--product")
    for ihw, registry in sensor_registry.items():
        reg_file_name = rf'./{cfg.platform_code[platform]}_hdk_{productname}_{ihw}.json'
        with open(reg_file_name, 'w') as f:
            json.dump(registry, f)
        adb.push_registry_file(reg_file_name)
        os.remove(reg_file_name)
    adb.adb_sync()
    adb.adb_reboot()
    adb.adb_root()
    print('origin registry reset')


@pytest.fixture()
def change_registry_res_value(adb, sensor_registry, request):
    """
    [
        {'accel': 1, 'gyro': 2,},
        {'accel': 2, 'gyro': 3,},
    ]
    :return:
    """
    platform = request.config.getoption("--platform")
    productname = request.config.getoption("--product")
    for ihw, registry in sensor_registry.items():
        new_regi = registry.copy()
        for sensor, res_val in request.param.items():
            if f'.{sensor}' in new_regi[f'{productname}_{ihw}']:
                new_regi[f'{productname}_{ihw}'][f'.{sensor}']['.config']['res_idx'][
                    'data'
                ] = str(res_val)
        reg_file_name = rf'./{cfg.platform_code[platform]}_hdk_{productname}_{ihw}.json'
        with open(reg_file_name, 'w') as f:
            json.dump(new_regi, f)
        adb.push_registry_file(reg_file_name)
        os.remove(reg_file_name)
    adb.adb_sync()
    adb.adb_reboot()
    adb.adb_root()
    yield
