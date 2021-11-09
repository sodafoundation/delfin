from delfin.drivers import driver
from delfin.drivers.hpe.hpe_msa import ssh_handler
from delfin.drivers.hpe.hpe_msa.ssh_handler import SSHHandler


class HpeMsaStorDriver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ssh_handler = ssh_handler.SSHHandler(**kwargs)

    def reset_connection(self, context, **kwargs):
        self.ssh_handler.login()

    def get_storage(self, context):
        return self.ssh_handler.get_storage(self.storage_id)

    def list_storage_pools(self, context):
        return self.ssh_handler.list_storage_pools(self.storage_id)

    def list_volumes(self, context):
        return self.ssh_hanlder.list_storage_volume(self.storage_id)

    def list_controllers(self, context):
        return self.ssh_handler.\
            list_storage_controller(self.storage_id)

    def list_ports(self, context):
        return self.ssh_hanlder.list_storage_ports(self.storage_id)

    def list_disks(self, context):
        return self.ssh_handler.list_storage_disks(self.storage_id)

    def list_alerts(self, context, query_para=None):
        return self.ssh_handler.list_alerts(query_para)

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    @staticmethod
    def parse_alert(context, alert):
        return SSHHandler.parse_alert(alert)

    def clear_alert(self, context, alert):
        pass
