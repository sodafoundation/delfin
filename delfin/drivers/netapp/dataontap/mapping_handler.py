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
from delfin.common import constants
from delfin.drivers.netapp.dataontap import constants as constant
from delfin.drivers.utils.tools import Tools


class MappingHandler(object):

    @staticmethod
    def format_initiators(init_list, initiator_info,
                          storage_id, protocol_type, is_default=False):
        initiator_map_list, initiator_list = [], []
        Tools.split_value_map_list(initiator_info,
                                   initiator_map_list,
                                   split=':')
        if not is_default and protocol_type == 'fc':
            initiator_list.extend(
                MappingHandler.get_fc_initiator
                (initiator_map_list, storage_id))
        elif not is_default and protocol_type == 'iscsi':
            initiator_list.extend(
                MappingHandler.get_iscsi_initiator
                (initiator_map_list, storage_id))
        if is_default:
            initiator_list.extend(
                MappingHandler.get_initiator_from_host
                (init_list, initiator_map_list, storage_id))
        return initiator_list

    @staticmethod
    def get_iscsi_initiator(initiator_map_list, storage_id):
        initiator_list = []
        for initiator_map in initiator_map_list:
            if 'IgroupName' in initiator_map:
                initiator_id = \
                    initiator_map.get('InitiatorName').replace(' ', '')
                initiator_model = {
                    'native_storage_host_initiator_id': initiator_id,
                    'native_storage_host_id':
                        initiator_map.get('IgroupName'),
                    'name': initiator_id,
                    'alias': initiator_map.get('InitiatorAlias'),
                    'type': constants.PortType.ISCSI,
                    'status': constants.InitiatorStatus.ONLINE,
                    'wwn': initiator_id,
                    'storage_id': storage_id,
                }
                initiator_list.append(initiator_model)
        return initiator_list

    @staticmethod
    def get_fc_initiator(initiator_map_list, storage_id):
        initiator_list = []
        for initiator_map in initiator_map_list:
            if 'IgroupName' in initiator_map:
                initiator_id = \
                    initiator_map.get('InitiatorWWPN').replace(' ', '')
                initiator_model = {
                    'native_storage_host_initiator_id': initiator_id,
                    'native_storage_host_id':
                        initiator_map.get('IgroupName'),
                    'name': initiator_id,
                    'alias': initiator_map.get('InitiatorWWPNAlias'),
                    'type': constants.PortType.FC,
                    'status': constants.InitiatorStatus.ONLINE,
                    'wwn': initiator_map.get('InitiatorWWPN'),
                    'storage_id': storage_id,
                }
                initiator_list.append(initiator_model)
        return initiator_list

    @staticmethod
    def get_initiator_type(protocol_type, initiator_name):
        if protocol_type != 'mixed':
            return constant.NETWORK_PORT_TYPE.get(protocol_type)
        else:
            if constant.IQN_PATTERN.search(initiator_name):
                return constants.PortType.ISCSI
            elif constant.WWN_PATTERN.search(initiator_name):
                return constants.PortType.FC
            return None

    @staticmethod
    def get_initiator_from_host(init_list, initiator_map_list, storage_id):
        initiator_list = []
        for initiator_map in initiator_map_list:
            if 'IgroupName' in initiator_map:
                initiator_id = \
                    initiator_map.get('Initiators').replace(' ', '')
                initiator_id = \
                    initiator_id.replace(constant.INITIATOR_KEY, '')
                protocol_type = \
                    MappingHandler.get_initiator_type(
                        initiator_map.get('Protocol'), initiator_id)
                initiator_model = {
                    'native_storage_host_initiator_id': initiator_id,
                    'native_storage_host_id':
                        initiator_map.get('IgroupName'),
                    'name': initiator_id,
                    'type': protocol_type,
                    'status': constants.InitiatorStatus.ONLINE,
                    'storage_id': storage_id,
                    'wwn': initiator_id
                }
                initiator_list.append(initiator_model)
                for key in initiator_map:
                    if constant.INITIATOR_KEY in key:
                        initiator_id = \
                            key.replace(constant.INITIATOR_KEY, '')
                        protocol_type = \
                            MappingHandler.get_initiator_type(
                                initiator_map.get('Protocol'), initiator_id)
                        initiator_model = {
                            'native_storage_host_initiator_id':
                                initiator_id,
                            'native_storage_host_id':
                                initiator_map.get('IgroupName'),
                            'name': initiator_id,
                            'type': protocol_type,
                            'status': constants.InitiatorStatus.ONLINE,
                            'storage_id': storage_id,
                            'wwn': initiator_id
                        }
                        initiator_list.append(initiator_model)
        for initiator in init_list:
            for initiator_model in initiator_list:
                if initiator['name'] == initiator_model['name']:
                    initiator_list.remove(initiator_model)
        return initiator_list

    @staticmethod
    def format_host(initiator_info, storage_id):
        initiator_map_list, initiator_list = [], []
        Tools.split_value_map_list(initiator_info,
                                   initiator_map_list,
                                   split=':')
        for initiator_map in initiator_map_list:
            if 'IgroupName' in initiator_map:
                initiator_model = {
                    'native_storage_host_id':
                        initiator_map.get('IgroupName'),
                    'name': initiator_map.get('IgroupName'),
                    'os_type':
                        constant.HOST_OS_TYPE_MAP.get(
                            initiator_map.get('OSType')),
                    'status': constants.HostStatus.NORMAL,
                    'storage_id': storage_id,
                }
                initiator_list.append(initiator_model)
        return initiator_list

    @staticmethod
    def format_port_group(port_set_info, lif_info, storage_id):
        port_map_list, port_group_list, lif_map_list = [], [], []
        Tools.split_value_map_list(port_set_info, port_map_list, split=':')
        Tools.split_value_map_list(lif_info, lif_map_list, split=':')
        for port_map in port_map_list:
            if 'PortsetName' in port_map:
                port_group_id = "%s-%s-%s" % \
                                (port_map.get('VserverName'),
                                 port_map.get('PortsetName'),
                                 port_map.get('Protocol'))
                ports = \
                    port_map.get('LIFOrTPGName').replace(' ', '').split(',')
                ports_str = ''
                for lif_map in lif_map_list:
                    if 'LogicalInterfaceName' in lif_map:
                        if lif_map.get('LogicalInterfaceName') in ports:
                            port_id = "%s_%s" % \
                                      (lif_map['CurrentNode'],
                                       lif_map['CurrentPort'])
                            if ports_str:
                                ports_str = \
                                    "{0},{1}".format(ports_str, port_id)
                            else:
                                ports_str = "{0}".format(port_id)

                port_group_model = {
                    'native_port_group_id': port_group_id,
                    'name': port_map.get('PortsetName'),
                    'ports': ports_str,
                    'storage_id': storage_id,
                }
                port_group_list.append(port_group_model)
        return port_group_list

    @staticmethod
    def format_mapping_view(mapping_info, volume_info, storage_id, host_list):
        mapping_map_list, mapping_view_list, volume_map_list = [], [], []
        Tools.split_value_map_list(mapping_info, mapping_map_list, split=":")
        Tools.split_value_map_list(volume_info, volume_map_list, split=":")
        for mapping_map in mapping_map_list:
            if 'LUNPath' in mapping_map:
                host_id = None
                for host in host_list:
                    if mapping_map.get('IgroupName') == host.get('name'):
                        host_id = host.get('native_storage_host_id')
                native_masking_view_id = \
                    '%s_%s_%s_%s' % (mapping_map.get('LUNNode'),
                                     mapping_map.get('VserverName'),
                                     mapping_map.get('IgroupName'),
                                     mapping_map.get('LUNName'))
                name = '%s_%s' % (mapping_map.get('IgroupName'),
                                  mapping_map.get('LUNName'))
                port_group_id = "%s-%s-%s" % \
                                (mapping_map.get('VserverName'),
                                 mapping_map.get('PortsetBindingIgroup'),
                                 mapping_map.get('IgroupProtocolType'))
                native_volume_id = None
                for volume_map in volume_map_list:
                    if 'LUNName' in volume_map:
                        if volume_map.get('LUNName') == \
                                mapping_map.get('LUNName') \
                                and volume_map.get('VserverName') == \
                                mapping_map.get('VserverName') \
                                and volume_map.get('LUNPath') == \
                                mapping_map.get('LUNPath'):
                            native_volume_id = volume_map['SerialNumber']
                mapping_view = {
                    'native_masking_view_id':
                        native_masking_view_id,
                    'name': name,
                    'native_port_group_id': port_group_id,
                    'native_storage_host_id': host_id,
                    'native_volume_id': native_volume_id,
                    'storage_id': storage_id,
                }
                mapping_view_list.append(mapping_view)
        return mapping_view_list
