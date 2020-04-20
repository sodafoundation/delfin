import shlex
import subprocess
from oslo_log import log
from oslo_utils import uuidutils

LOG = log.getLogger(__name__)

DEVICE_INFO = {
    'storage_id': uuidutils.generate_uuid(),
    'hostname': 'string',
    'username': 'string',
    'password': 'string',
    'description': 'string',
    'status': 'string',
    'total_capacity': 'double',
    'used_capacity': 'double',
    'free_capacity': 'double',
    'manufacturer': 'string',
    'model': 'string',
    'firmwareVersion': 'string',
    'serial_number': 'string',
    'location': 'string',
    'created_at': 'string',
    'updated_at': 'string'
}


class Driver:
    def __init__(self):
        self.stderr = None
        self.stdout = None

    def run_command(self, command):
        args = shlex.split(command)
        process = subprocess.Popen(args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr != '':
            raise Exception(stderr)
        else:
            LOG.info("Stdout: {0}".format(stdout))
        return stdout, stderr

    def list_volumes(self, context, device_name):
        LOG.info("Listing Volumes for {0}".format(device_name))
        self.run_command("osdsctl volume list")

    def list_pools(self, context, device_name):
        LOG.info("Listing Pools for {0}".format(device_name))
        self.run_command("osdsctl pool list")

    def register(self, context):

        # the real implementation

        return DEVICE_INFO
