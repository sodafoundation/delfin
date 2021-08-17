# Copyright 2021 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import six
from oslo_log import log

from delfin import db
from delfin.db.sqlalchemy.models import StorageHostGrpStorageHostRelation as \
    StorageHostGrpRelation
from delfin.db.sqlalchemy.models import VolumeGrpVolumeRelation, \
    PortGrpPortRelation
from delfin.i18n import _

LOG = log.getLogger(__name__)


class HostMappingTask(object):

    def __init__(self):
        pass

    def _build_storgage_host_grp_relations(self, ctx, storage_id):
        """ Builds storage host grp to host relations."""
        storage_host_grps = db.storage_host_groups_get_all(
            ctx, filters={"storage_id": storage_id})

        storage_host_grp_relation_list = []
        for storage_host_grp in storage_host_grps:
            storage_hosts = storage_host_grp['storage_hosts']
            storage_hosts = storage_hosts.split(',')
            if not storage_hosts:
                continue

            for storage_host in storage_hosts:
                storage_host_grp_relation = {
                    StorageHostGrpRelation.storage_id.name: storage_id,
                    StorageHostGrpRelation.native_storage_host_group_id.name:
                        storage_host_grp['native_storage_host_group_id'],
                    StorageHostGrpRelation.native_storage_host_id.name:
                        storage_host}
                storage_host_grp_relation_list \
                    .append(storage_host_grp_relation)

        db.storage_host_grp_host_relations_create(
            ctx, storage_host_grp_relation_list)

    def _build_volume_grp_relations(self, ctx, storage_id):
        """ Builds volume grp to volume relations."""
        volume_grps = db.volume_groups_get_all(
            ctx, filters={"storage_id": storage_id})

        volume_grp_relation_list = []
        for volume_grp in volume_grps:
            volumes = volume_grp['volumes']
            volumes = volumes.split(',')
            if not volumes:
                continue

            for volume in volumes:
                volume_grp_relation = {
                    VolumeGrpVolumeRelation.storage_id.name: storage_id,
                    VolumeGrpVolumeRelation.native_volume_group_id
                    .name: volume_grp['native_volume_group_id'],
                    VolumeGrpVolumeRelation.native_volume_id.name: volume}
                volume_grp_relation_list.append(volume_grp_relation)

        db.volume_grp_volume_relations_create(ctx, volume_grp_relation_list)

    def _build_port_grp_relations(self, ctx, storage_id):
        """ Builds port grp to port relations."""
        port_grps = db.port_groups_get_all(
            ctx, filters={"storage_id": storage_id})

        port_grp_relation_list = []
        for port_grp in port_grps:
            ports = port_grp['ports']
            ports = ports.split(',')
            if not ports:
                continue

            for port in ports:
                port_grp_relation = {
                    PortGrpPortRelation.storage_id.name: storage_id,
                    PortGrpPortRelation.native_port_group_id
                    .name: port_grp['native_port_group_id'],
                    PortGrpPortRelation.native_port_id.name: port}
                port_grp_relation_list.append(port_grp_relation)

        db.port_grp_port_relations_create(ctx, port_grp_relation_list)

    def build_host_mapping_relations(self, ctx, storage_id):
        """ Builds relations from host mapping attributes"""

        LOG.info('Building host mapping relations for storage id:{0}'
                 .format(storage_id))

        try:
            # Delete all existing group relation entries before building new
            db.storage_host_grp_host_relations_delete_by_storage(ctx,
                                                                 storage_id)
            db.volume_grp_volume_relations_delete_by_storage(ctx, storage_id)
            db.port_grp_port_relations_delete_by_storage(ctx, storage_id)

            # Get all storage host groups and add host grp, host relation
            # for each of the entries
            # Do similar steps for volume grp and port grp as well
            self._build_storgage_host_grp_relations(ctx, storage_id)
            self._build_volume_grp_relations(ctx, storage_id)
            self._build_port_grp_relations(ctx, storage_id)

            LOG.info('Building host mapping group relations successful for '
                     'storage id:{0}'.format(storage_id))
        except Exception as e:
            msg = _('Failed to build group relations for storage device: {0}'
                    .format(six.text_type(e)))
            LOG.error(msg)
