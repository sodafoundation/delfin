LIST_CONTROLLERS = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show controllers">
<COMP G="0" P="1"/>
<OBJECT basetype="controllers" name="controllers">
    <PROPERTY name="durable-id" >controller_a</PROPERTY>
    <PROPERTY name="controller-id">A</PROPERTY>
    <PROPERTY name="serial-number">7CE539M591</PROPERTY>
    <PROPERTY name="cache-memory-size">4096</PROPERTY>
    <PROPERTY name="system-memory-size">6144</PROPERTY>
    <PROPERTY name="sc-fw">GLS210R04-01</PROPERTY>
    <PROPERTY name="sc-cpu-type">Gladden</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
    <PROPERTY name="position">Top</PROPERTY>
    </OBJECT>
<COMP G="0" P="13"/>
<OBJECT basetype="controllers" name="controllers">
    <PROPERTY name="durable-id">controller_b</PROPERTY>
    <PROPERTY name="controller-id">B</PROPERTY>
    <PROPERTY name="serial-number">7CE539M591</PROPERTY>
    <PROPERTY name="cache-memory-size">4096</PROPERTY>
    <PROPERTY name="system-memory-size">6144</PROPERTY>
    <PROPERTY name="sc-fw">GLS210R04-01</PROPERTY>
    <PROPERTY name="sc-cpu-type">Gladden</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
    <PROPERTY name="position">Bottom</PROPERTY>
    </OBJECT>
</RESPONSE>
"""

LIST_SYSTEM = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show system">
<COMP G="0" P="1"/>
<OBJECT basetype="system" >
    <PROPERTY name="system-name">msa2040</PROPERTY>
    <PROPERTY name="midplane-serial-number">00C0FF26DCB0</PROPERTY>
    <PROPERTY name="system-location">Uninitialized Location</PROPERTY>
    <PROPERTY name="vendor-name">HP</PROPERTY>
    <PROPERTY name="product-id">MSA 2040 SAN</PROPERTY>
    <PROPERTY name="product-brand" >MSA Storage</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
    </OBJECT>
</RESPONSE>
"""

LIST_VISION = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show version">
<COMP G="0" P="1"/>
<OBJECT basetype="versions">
    <PROPERTY name="bundle-version">GL210R004</PROPERTY>
</OBJECT>
</RESPONSE>
"""

LIST_PORTS = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show ports">
<COMP G="0" P="1"/>
 <OBJECT basetype="port" name="ports" oid="1" format="rows">
    <PROPERTY name="durable-id">hostport_A1</PROPERTY>
    <PROPERTY name="port">A1</PROPERTY>
     <PROPERTY name="configured-speed">8Gb</PROPERTY>
    <PROPERTY name="port-type">FC</PROPERTY>
    <PROPERTY name="target-id">207000c0ff26dcb0</PROPERTY>
    <PROPERTY name="health">N/A</PROPERTY>
  </OBJECT>
<COMP G="1" P="2"/>
<OBJECT basetype="fc-port" name="port-details" oid="2" format="rows">
    <PROPERTY name="sfp-supported-speeds">4G,8G</PROPERTY>
  </OBJECT>
<COMP G="0" P="3"/>
 <OBJECT basetype="port" name="ports" oid="3" format="rows">
    <PROPERTY name="durable-id">hostport_A2</PROPERTY>
    <PROPERTY name="port">A2</PROPERTY>
    <PROPERTY name="target-id">217000c0ff26dcb0</PROPERTY>
    <PROPERTY name="port-type">FC</PROPERTY>
     <PROPERTY name="configured-speed">8Gb</PROPERTY>
    <PROPERTY name="health">N/A</PROPERTY>
  </OBJECT>
<COMP G="3" P="4"/>
<OBJECT basetype="fc-port" name="port-details" oid="4" format="rows">
    <PROPERTY name="sfp-supported-speeds">4G,8G</PROPERTY>
</OBJECT>
<COMP G="0" P="5"/>
 <OBJECT basetype="port" name="ports" oid="5" format="rows">
    <PROPERTY name="durable-id">hostport_A3</PROPERTY>
    <PROPERTY name="port">A3</PROPERTY>
    <PROPERTY name="port-type">iSCSI</PROPERTY>
    <PROPERTY name="health">N/A</PROPERTY>
</OBJECT>
<COMP G="5" P="6"/>
<OBJECT basetype="iscsi-port" name="port-details" oid="6" format="pairs">
    <PROPERTY name="ip-address">0.0.0.0</PROPERTY>
    <PROPERTY name="mac-address">00:C0:FF:35:BD:64</PROPERTY>
  </OBJECT>
<COMP G="0" P="7"/>
 <OBJECT basetype="port" name="ports" oid="7" format="rows">
    <PROPERTY name="durable-id" >hostport_A4</PROPERTY>
    <PROPERTY name="port">A4</PROPERTY>
    <PROPERTY name="port-type">iSCSI</PROPERTY>
    <PROPERTY name="configured-speed">Auto</PROPERTY>
    <PROPERTY name="health">N/A</PROPERTY>
  </OBJECT>
<COMP G="7" P="8"/>
<OBJECT basetype="iscsi-port" name="port-details" oid="8" format="pairs">
    <PROPERTY name="ip-address">0.0.0.0</PROPERTY>
    <PROPERTY name="mac-address">00:C0:FF:35:BD:65</PROPERTY>
  </OBJECT>
<COMP G="0" P="9"/>
<OBJECT basetype="port" name="ports" oid="9" format="rows">
    <PROPERTY name="durable-id">hostport_B1</PROPERTY>
    <PROPERTY name="port">B1</PROPERTY>
    <PROPERTY name="target-id">247000c0ff26dcb0</PROPERTY>
    <PROPERTY name="port-type">FC</PROPERTY>
    <PROPERTY name="configured-speed">8Gb</PROPERTY>
    <PROPERTY name="health">N/A</PROPERTY>
  </OBJECT>
<COMP G="9" P="10"/>
<OBJECT basetype="fc-port" name="port-details" oid="10" format="rows">
    <PROPERTY name="sfp-supported-speeds">4G,8G</PROPERTY>
  </OBJECT>
<COMP G="0" P="11"/>
<OBJECT basetype="port" name="ports" oid="11" format="rows">
    <PROPERTY name="durable-id">hostport_B2</PROPERTY>
    <PROPERTY name="port">B2</PROPERTY>
    <PROPERTY name="port-type">FC</PROPERTY>
    <PROPERTY name="target-id">257000c0ff26dcb0</PROPERTY>
    <PROPERTY name="configured-speed">8Gb</PROPERTY>
    <PROPERTY name="health">N/A</PROPERTY>
  </OBJECT>
<COMP G="11" P="12"/>
 <OBJECT basetype="fc-port" name="port-details" oid="12" format="rows">
    <PROPERTY name="sfp-supported-speeds">4G,8G</PROPERTY>
  </OBJECT>
<COMP G="0" P="13"/>
<OBJECT basetype="port" name="ports" oid="13" format="rows">
    <PROPERTY name="durable-id">hostport_B3</PROPERTY>
    <PROPERTY name="port">B3</PROPERTY>
    <PROPERTY name="port-type">iSCSI</PROPERTY>
    <PROPERTY name="configured-speed">Auto</PROPERTY>
    <PROPERTY name="health">N/A</PROPERTY>
  </OBJECT>
<COMP G="13" P="14"/>
<OBJECT basetype="iscsi-port" name="port-details" oid="14" format="pairs">
    <PROPERTY name="ip-address">0.0.0.0</PROPERTY>
    <PROPERTY name="mac-address">00:C0:FF:35:BA:BC</PROPERTY>
  </OBJECT>
<COMP G="0" P="15"/>
 <OBJECT basetype="port" name="ports" oid="15" format="rows">
    <PROPERTY name="durable-id">hostport_B4</PROPERTY>
    <PROPERTY name="port">B4</PROPERTY>
    <PROPERTY name="port-type">iSCSI</PROPERTY>
    <PROPERTY name="configured-speed">Auto</PROPERTY>
    <PROPERTY name="health">N/A</PROPERTY>
  </OBJECT>
<COMP G="15" P="16"/>
<OBJECT basetype="iscsi-port" name="port-details" oid="16" format="pairs">
    <PROPERTY name="ip-address">0.0.0.0</PROPERTY>
    <PROPERTY name="mac-address">00:C0:FF:35:BA:BD</PROPERTY>
  </OBJECT>
</RESPONSE>
"""

LIST_POOLS = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show pools">
<COMP G="0" P="1"/>
 <OBJECT basetype="pools" name="pools" oid="1" format="rows">
    <PROPERTY name="name">A</PROPERTY>
    <PROPERTY name="serial-number">00c0ff26c4ea0000d980546101000000</PROPERTY>
    <PROPERTY name="total-size">1196.8GB</PROPERTY>
    <PROPERTY name="total-avail">1196.8GB</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
  </OBJECT>
</RESPONSE>
"""

LIST_VOLUMES = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show volumes">
<COMP G="0" P="1"/>
<OBJECT basetype="volumes" name="volume"  format="rows">
    <PROPERTY name="durable-id">V1</PROPERTY>
    <PROPERTY name="volume-name">Vol0001</PROPERTY>
    <PROPERTY name="size">99.9GB</PROPERTY>
    <PROPERTY name="allocated-size">0B</PROPERTY>
    <PROPERTY name="total-size">99.9GB</PROPERTY>
    <PROPERTY name="blocks">195305472</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
    <PROPERTY name="wwn">600C0FF00026C4EAFA80546101000000</PROPERTY>
    <PROPERTY name="volume-type">base</PROPERTY>
  </OBJECT>
<COMP G="0" P="2"/>
 <OBJECT basetype="volumes" name="volume"  format="rows">
    <PROPERTY name="durable-id">V2</PROPERTY>
    <PROPERTY name="volume-name">Vol0002</PROPERTY>
    <PROPERTY name="allocated-size">0B</PROPERTY>
    <PROPERTY name="total-size">99.9GB</PROPERTY>
    <PROPERTY name="blocks">195305472</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
    <PROPERTY name="wwn">600C0FF00026C4EA0A81546101000000</PROPERTY>
    <PROPERTY name="volume-type">base</PROPERTY>
  </OBJECT>
</RESPONSE>
"""

LIST_DISKS = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show disks">
<COMP G="0" P="1"/>
<OBJECT basetype="drives" name="drive" oid="1" format="rows">
    <PROPERTY name="durable-id">disk_01.01</PROPERTY>
    <PROPERTY name="location" >1.1</PROPERTY>
    <PROPERTY name="port">0</PROPERTY>
    <PROPERTY name="serial-number">6SL9CD560000N51404EF</PROPERTY>
    <PROPERTY name="vendor">SEAGATE</PROPERTY>
    <PROPERTY name="model">ST3600057SS</PROPERTY>
    <PROPERTY name="description">SAS</PROPERTY>
    <PROPERTY name="type">SAS</PROPERTY>
    <PROPERTY name="rpm" >15</PROPERTY>
    <PROPERTY name="size">600.1GB</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
    <PROPERTY name="disk-group">dgA01</PROPERTY>
  </OBJECT>
<COMP G="0" P="2"/>
 <OBJECT basetype="drives" name="drive" oid="2" format="rows">
    <PROPERTY name="durable-id">disk_01.02</PROPERTY>
    <PROPERTY name="location">1.2</PROPERTY>
    <PROPERTY name="serial-number">6SL7X4RE0000B42601SF</PROPERTY>
    <PROPERTY name="vendor">SEAGATE</PROPERTY>
    <PROPERTY name="model">ST3600057SS</PROPERTY>
    <PROPERTY name="description">SAS</PROPERTY>
    <PROPERTY name="type">SAS</PROPERTY>
    <PROPERTY name="rpm">15</PROPERTY>
    <PROPERTY name="size">600.1GB</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
    <PROPERTY name="disk-group">dgA01</PROPERTY>
  </OBJECT>
<COMP G="0" P="3"/>
 <OBJECT basetype="drives" name="drive" oid="3" format="rows">
    <PROPERTY name="durable-id">disk_01.03</PROPERTY>
    <PROPERTY name="location">1.3</PROPERTY>
    <PROPERTY name="serial-number">6SL9QR5T0000N52120SK</PROPERTY>
    <PROPERTY name="vendor">SEAGATE</PROPERTY>
     <PROPERTY name="description">SAS</PROPERTY>
    <PROPERTY name="model">ST3600057SS</PROPERTY>
    <PROPERTY name="rpm">15</PROPERTY>
    <PROPERTY name="size">600.1GB</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
    <PROPERTY name="disk-group">dgA01</PROPERTY>
  </OBJECT>
<COMP G="0" P="4"/>
<OBJECT basetype="drives" name="drive" oid="4" format="rows">
    <PROPERTY name="durable-id">disk_01.04</PROPERTY>
    <PROPERTY name="port">0</PROPERTY>
    <PROPERTY name="location">1.4</PROPERTY>
     <PROPERTY name="description">SAS</PROPERTY>
    <PROPERTY name="serial-number">3SL0WT7G00009051YBTF</PROPERTY>
    <PROPERTY name="vendor">SEAGATE</PROPERTY>
    <PROPERTY name="model">ST3600057SS</PROPERTY>
    <PROPERTY name="rpm" >15</PROPERTY>
    <PROPERTY name="size">600.1GB</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
    <PROPERTY name="disk-group">dgA01</PROPERTY>
  </OBJECT>
</RESPONSE>
"""
LIST_ERROR = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show events error">
<COMP G="0" P="13"/>
 <OBJECT basetype="events" name="event" oid="1" format="packed">
    <PROPERTY name="time-stamp">2021-11-12 08:16:20</PROPERTY>
    <PROPERTY name="time-stamp-numeric" >1636704980</PROPERTY>
    <PROPERTY name="event-code">557</PROPERTY>
    <PROPERTY name="event-id" >A891</PROPERTY>
    <PROPERTY name="model">MSA 2040 SAN</PROPERTY>
    <PROPERTY name="serial-number">00C0FF26C236</PROPERTY>
    <PROPERTY name="controller" >A</PROPERTY>
    <PROPERTY name="controller-numeric">1</PROPERTY>
    <PROPERTY name="severity">ERROR</PROPERTY>
    <PROPERTY name="severity-numeric">2</PROPERTY>
    <PROPERTY name="message" >An Enclosure Management Processor(EMP)</PROPERTY>
     <PROPERTY name="additional-information">Management</PROPERTY>
     <PROPERTY name="recommended-action">Management</PROPERTY>
  </OBJECT>
</RESPONSE>
"""

error_result = [
    {
        'alert_id': 'A891',
        'alert_name': '557',
        'category': 'Fault',
        'description': 'Management',
        'location': 'An Enclosure Management Processor(EMP)',
        'match_key': 'd0317252aed04fd8b68e79d7eab08277',
        'occur_time': 1636704980000,
        'resource_type': '557',
        'sequence_number': 'A891',
        'severity': 'ERROR',
        'time': '2021-11-12 08:16:20',
        'type': 'EquipmentAlarm'
    }
]

volume_result = [
    {
        'name': 'Vol0001',
        'storage_id': 'kkk',
        'description': 'Vol0001',
        'status': 'normal',
        'native_volume_id': 'V1',
        'native_storage_pool_id': '00c0ff26c4ea0000d980546101000000',
        'wwn': '600C0FF00026C4EAFA80546101000000',
        'type': 'base',
        'total_capacity': 107266808217,
        'free_capacit': 107266808217,
        'used_capacity': 0,
        'blocks': 195305472,
        'compressed': True,
        'deduplicated': True
    }, {
        'name': 'Vol0002',
        'storage_id': 'kkk',
        'description': 'Vol0002',
        'status': 'normal',
        'native_volume_id': 'V2',
        'native_storage_pool_id': '00c0ff26c4ea0000d980546101000000',
        'wwn': '600C0FF00026C4EA0A81546101000000',
        'type': 'base',
        'total_capacity': 107266808217,
        'free_capacit': 107266808217,
        'used_capacity': 0,
        'blocks': 195305472,
        'compressed': True,
        'deduplicated': True
    }
]

pools_result = [
    {
        'name': 'A',
        'storage_id': 'kkk',
        'native_storage_pool_id': '00c0ff26c4ea0000d980546101000000',
        'status': 'normal',
        'storage_type': 'block',
        'total_capacity': 1285054214963,
        'subscribed_capacity': 390610944,
        'used_capacity': 214533616434,
        'free_capacity': 1070520598529
    }
]

ports_result = [
    {
        'native_port_id': 'hostport_A1',
        'name': 'A1', 'type': 'fc',
        'connection_status': 'disconnected',
        'health_status': 'abnormal',
        'location': 'A1_FC',
        'storage_id': 'kkk',
        'speed': 8589934592.0,
        'max_speed': 8589934592.0,
        'mac_address': None,
        'ipv4': None,
        'wwn': '207000c0ff26dcb0'
    }, {
        'native_port_id': 'hostport_A2',
        'name': 'A2',
        'type': 'fc',
        'connection_status': 'disconnected',
        'health_status': 'abnormal',
        'location': 'A2_FC',
        'storage_id': 'kkk',
        'speed': 8589934592.0,
        'max_speed': 8589934592.0,
        'mac_address': None,
        'ipv4': None,
        'wwn': '217000c0ff26dcb0'
    }, {
        'native_port_id': 'hostport_A3',
        'name': 'A3',
        'type': 'eth',
        'connection_status': 'disconnected',
        'health_status': 'abnormal',
        'location': 'A3_ISCSI',
        'storage_id': 'kkk',
        'speed': 0,
        'max_speed': 0,
        'mac_address': '00:C0:FF:35:BD:64',
        'ipv4': '0.0.0.0',
        'wwn': None
    }, {
        'native_port_id': 'hostport_A4',
        'name': 'A4',
        'type': 'eth',
        'connection_status': 'disconnected',
        'health_status': 'abnormal',
        'location': 'A4_ISCSI',
        'storage_id': 'kkk',
        'speed': 0,
        'max_speed': 0,
        'mac_address': '00:C0:FF:35:BD:65',
        'ipv4': '0.0.0.0',
        'wwn': None
    }, {
        'native_port_id': 'hostport_B1',
        'name': 'B1',
        'type': 'fc',
        'connection_status': 'disconnected',
        'health_status': 'abnormal',
        'location': 'B1_FC',
        'storage_id': 'kkk',
        'speed': 8589934592.0,
        'max_speed': 8589934592.0,
        'mac_address': None,
        'ipv4': None,
        'wwn': '247000c0ff26dcb0'
    }, {
        'native_port_id': 'hostport_B2',
        'name': 'B2',
        'type': 'fc',
        'connection_status': 'disconnected',
        'health_status': 'abnormal',
        'location': 'B2_FC',
        'storage_id': 'kkk',
        'speed': 8589934592.0,
        'max_speed': 8589934592.0,
        'mac_address': None,
        'ipv4': None,
        'wwn': '257000c0ff26dcb0'
    }, {
        'native_port_id': 'hostport_B3',
        'name': 'B3',
        'type': 'eth',
        'connection_status': 'disconnected',
        'health_status': 'abnormal',
        'location': 'B3_ISCSI', 'storage_id': 'kkk',
        'speed': 0,
        'max_speed': 0,
        'mac_address': '00:C0:FF:35:BA:BC',
        'ipv4': '0.0.0.0',
        'wwn': None
    }, {
        'native_port_id': 'hostport_B4',
        'name': 'B4',
        'type': 'eth',
        'connection_status': 'disconnected',
        'health_status': 'abnormal',
        'location': 'B4_ISCSI',
        'storage_id': 'kkk',
        'speed': 0,
        'max_speed': 0,
        'mac_address': '00:C0:FF:35:BA:BD',
        'ipv4': '0.0.0.0',
        'wwn': None
    }]

disks_result = [
    {
        'native_disk_id': '1.1',
        'name': '1.1',
        'physical_type': 'sas',
        'status': 'normal',
        'storage_id': 'kkk',
        'native_disk_group_id': 'dgA01',
        'serial_number': '6SL9CD560000N51404EF',
        'manufacturer': 'SEAGATE',
        'model': 'ST3600057SS',
        'speed': 15000,
        'capacity': 644352468582,
        'health_score': 'normal'
    }, {
        'native_disk_id': '1.2',
        'name': '1.2',
        'physical_type': 'sas',
        'status': 'normal',
        'storage_id': 'kkk',
        'native_disk_group_id': 'dgA01',
        'serial_number': '6SL7X4RE0000B42601SF',
        'manufacturer': 'SEAGATE',
        'model': 'ST3600057SS',
        'speed': 15000,
        'capacity': 644352468582,
        'health_score': 'normal'
    }, {
        'native_disk_id': '1.3',
        'name': '1.3',
        'physical_type': 'sas',
        'status': 'normal',
        'storage_id': 'kkk',
        'native_disk_group_id': 'dgA01',
        'serial_number': '6SL9QR5T0000N52120SK',
        'manufacturer': 'SEAGATE',
        'model': 'ST3600057SS',
        'speed': 15000, 'capacity': 644352468582,
        'health_score': 'normal'
    }, {
        'native_disk_id': '1.4',
        'name': '1.4',
        'physical_type': 'sas',
        'status': 'normal',
        'storage_id': 'kkk',
        'native_disk_group_id': 'dgA01',
        'serial_number': '3SL0WT7G00009051YBTF',
        'manufacturer': 'SEAGATE',
        'model': 'ST3600057SS',
        'speed': 15000,
        'capacity': 644352468582,
        'health_score': 'normal'
    }
]

system_info = {
    'name': 'msa2040',
    'vendor': 'HPE',
    'model': 'MSA 2040 SAN',
    'status': 'normal',
    'serial_number': '00C0FF26DCB0',
    'firmware_version': 'GL210R004',
    'location': 'Uninitialized Location',
    'raw_capacity': 2577409874328,
    'total_capacity': 1285054214963,
    'used_capacity': 214533616434,
    'free_capacity': 1070520598529
}

controller_result = [
    {
        'native_controller_id': 'A',
        'name': 'controller_a',
        'storage_id': 'kkk',
        'status': 'normal',
        'location': 'Top',
        'soft_version': 'GLS210R04-01',
        'cpu_info': 'Gladden',
        'memory_size': 6442450944
    },
    {
        'native_controller_id': 'B',
        'name': 'controller_b',
        'storage_id': 'kkk',
        'status': 'normal',
        'location': 'Bottom',
        'soft_version': 'GLS210R04-01',
        'cpu_info': 'Gladden',
        'memory_size': 6442450944
    }
]
