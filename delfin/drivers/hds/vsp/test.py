import time

from delfin import context
from delfin.drivers.hds.vsp.vspstor import HdsVspDriver
ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "hds",
    "model": "VSP G350",
    "rest": {
        "host": "10.143.133.207",
        "port": 443,
        "username": "maintenance",
        "password": "raid-maintenance"
    },
    "ssh": {
        "host": "110.143.132.231",
        "port": 22,
        "username": "user",
        "password": "pass"
    }
}

if __name__ == '__main__':
    kwargs = ACCESS_INFO
    sshclient = HdsVspDriver(**kwargs)
    # time.sleep(610)
    re = sshclient.list_storage_pools(context)
    print(len(re))
    print(re)