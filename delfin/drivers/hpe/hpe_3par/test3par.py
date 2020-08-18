from delfin.drivers.hpe.hpe_3par.hpe_3parstor import Hpe3parStorDriver
from delfin.drivers.utils.ssh_client import SSHClient
from delfin import context

kwargs = {
    "vendor": "hpe",
    "model": "threeparstor",
    "rest": {
        "host": "10.0.0.1",
        "port": 8443,
        "username": "user",
        "password": "pass"
    },
    "ssh": {
        "host": "10.143.132.232",
        "port": 22,
        "username": "root",
        "password": "Pbu4@123",
        "host_key": "10.143.132.232 ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBD1pNiVR96+F3ywv/yueGCI/v7mFzwcvB73gKirKwHyzHpxkzdCLjQw//k4ZyceSvLOjwkE3FECVX+CNV8TpL7A="
    }
}

def test1():
    sshcl = SSHClient(**kwargs)
    command_str = 'cd springcloudcmp;ls -l'
    re = sshcl.doexec(context, command_str)
    print('re====={}'.format(re))

alert = {
    'sysUpTime': '1399844806',
    'snmpTrapOID': 'alertNotify',
    'component': 'test_trap',
    'details': 'This is a test trap sent from InServ hp3parf200, Serial Number 1307327',
    'nodeID': '0',
    'severity': 'debug',
    'timeOccurred': '2020-08-12 12:58:36 CST',
    'id': '4294967295',
    'messageCode': '4294967295',
    'state': 'autofixed',
    'serialNumber': '1307327',
    'transport_address': '100.118.18.100',
    'storage_id': '1c094309-70f2-4da3-ac47-e87cc1492ad5'
}

def test2():
    hpe3pardriver = Hpe3parStorDriver(**kwargs)
    re = hpe3pardriver.parse_alert(context,alert)
    print('re====={}'.format(re))
test2()