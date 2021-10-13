from delfin.drivers import driver
from delfin.drivers.hpe.hpe_msa import ssh_handler


class HpeMsaStorDriver(driver.StorageDriver):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ssh_hanlder = ssh_handler.SSHHandler(**kwargs)

    def reset_connection(self, context, **kwargs):
        self.ssh_hanlder.login()

    def get_storage(self, context):
        return self.ssh_hanlder.get_storage(self.storage_id)

    def list_storage_pools(self, context):
        return self.ssh_hanlder.list_storage_pools(self.storage_id)

    def list_volumes(self, context):
        return self.ssh_hanlder.list_storage_volume(self.storage_id)

    def list_controllers(self, context):
        return self.ssh_hanlder.list_storage_controller(self.storage_id)

    def list_ports(self, context):
        return self.ssh_hanlder.list_storage_ports(self.storage_id)

    def list_disks(self, context):
        return self.ssh_hanlder.list_storage_disks(self.storage_id)

    def list_alerts(self, context, query_para=None):
        return self.ssh_hanlder.list_storage_error(query_para)

    def add_trap_config(self, context, trap_config):
        pass

    def remove_trap_config(self, context, trap_config):
        pass

    def clear_alert(self):
        pass
