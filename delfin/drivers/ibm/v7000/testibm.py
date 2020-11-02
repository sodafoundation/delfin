from delfin import context
from delfin.drivers.ibm.v7000.ssh_handler import SSHHandler
from delfin.drivers.utils.ssh_client import SSHClient
ACCESS_INFO = {
    "storage_id": "12345",
    "vendor": "hpe",
    "model": "3par",
    "rest": {
        "host": "10.0.0.1",
        "port": 8443,
        "username": "user",
        "password": "pass"
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
    sshclient = SSHClient(**kwargs)
    sshhanlder = SSHHandler(sshclient)
    sshhanlder.list_alerts(context)