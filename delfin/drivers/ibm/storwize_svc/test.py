import sys
import time
from unittest import mock
import xlrd
from dateutil import tz
from dateutil.tz import tzlocal
from datetime import datetime

from pytz import all_timezones
sys.modules['delfin.cryptor'] = mock.Mock()
from delfin import context
# from delfin.drivers.dell_emc.unity.unity import UNITYStorDriver
import re

from delfin.drivers.ibm.storwize_svc.storwize_svc import StorwizeSVCDriver

ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "ibm emc",
    "model": "unity",
    "rest": {
        "host": "118.122.119.73",
        "port": 58040,
        "username": "admin",
        "password": "password1"
    },
    "ssh": {
        "host": "10.143.133.119",
        "port": 22,
        "username": "root",
        "password": "Pbu4@123"
    }
    # "verify": "F:\soda\ds8000\ds8000.cer"
}

TIME_PATTERN = "%Y-%m-%dT%H:%M:%S-%f"

def get_time_stamp(time_str):
    """ Time stamp to time conversion
    """
    time_stamp = ''
    try:
        if time_str is not None:
            tz_name = datetime.now(tzlocal()).tzname()
            to_zone = tz.gettz(tz_name)
            time_d = re.findall(r"\d+", time_str)
            print(time_d)
            tt = datetime(int(time_d[0]), int(time_d[1]), int(time_d[2]),
                          int(time_d[3]), int(time_d[4]), int(time_d[5]),
                          tzinfo=to_zone)
            time_stamp = int(time.mktime(tt.timetuple())) * 1000
            # time_array = time.strptime(time_str, TIME_PATTERN)
            # # Convert to timestamps to milliseconds
            # time_stamp = int(time.mktime(time_array) * 1000)
    except Exception as e:
        # LOG.error(e)
        raise e


    return time_stamp

if __name__ == '__main__':
    kwargs = ACCESS_INFO
    # timet = '2020-12-20T13:00:23-0700'
    # print(int(time.mktime(time.strptime(
    #                 timet,
    #                 TIME_PATTERN))))
    # workbook = xlrd.open_workbook('F:\soda\文档\checklist\checklist_ds8000.xls')
    # sheet = workbook.sheet_by_index(0)
    # for index in range(1, sheet.nrows):
    #     row_value = sheet.row_values(index)
    #     print(row_value)
    # test =[]
    # if test:
    #     print(test)
    # for system in test:
    #     print(system)
    unityclient = StorwizeSVCDriver(**kwargs)
    # sshhanlder = SSHHandler(**kwargs)
    # sshhanlder.set_storage_id('0')
    # testtime = '2020-09-23 04:15:13 CST'
    # re = get_time_stamp(testtime)
    # re = unityclient.get_storage(context)
    # re = unityclient.list_storage_pools(context)
    # re = unityclient.list_volumes(context)
    # re = unityclient.list_ports(context)
    file_map = {'Nv_stats_169800': {1625735504000: 'Nv_stats_169800_210708_171044',
                                    1625735624000: 'Nv_stats_169800_210708_171144',
                                    1625735824000: 'Nv_stats_169800_210708_171244'}
                }
    metrics = []
    file_list = '1 Nv_stats_169800_210708_171344\n' \
                '2 Nm_stats_169800_210708_171044\n' \
                '3 Nn_stats_169800_210708_171044\n' \
                '4 Nv_stats_169800_210708_171144'
    re = unityclient.ssh_hanlder.get_stats_file_data(
                    file_map,
                    'volume',
                    metrics,
                    '1234')
    # re = unityclient.list_alerts(context, query_para=None)
    print(re)
    print(len(re))