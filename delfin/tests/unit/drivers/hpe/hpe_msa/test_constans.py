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

LIST_HOST_INITIATORS = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show host-groups">
<COMP G="2" P="3"/>
 <OBJECT basetype="initiator" name="initiator" oid="3" format="rows">
    <PROPERTY name="durable-id">I2</PROPERTY>
    <PROPERTY name="nickname">FC-port1</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped">No</PROPERTY>
    <PROPERTY name="profile">HP-UX</PROPERTY>
    <PROPERTY name="host-bus-type">FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" key="true">21000024ff3dfed1</PROPERTY>
    <PROPERTY name="host-id">NOHOST</PROPERTY>
    <PROPERTY name="host-key" >HU</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b">0</PROPERTY>
  </OBJECT>
<COMP G="5" P="6"/>
 <OBJECT basetype="initiator" name="initiator" oid="6" format="rows">
    <PROPERTY name="durable-id">I1</PROPERTY>
    <PROPERTY name="nickname">FC-port2</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped">Yes</PROPERTY>
    <PROPERTY name="profile">HP-UX</PROPERTY>
    <PROPERTY name="host-bus-type">FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" key="true">10000090fa13870e</PROPERTY>
    <PROPERTY name="host-id">00c0ff26c2360000e2399f6101010000</PROPERTY>
    <PROPERTY name="host-key" >H1</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b">0</PROPERTY>
  </OBJECT>
<COMP G="5" P="7"/>
<OBJECT basetype="initiator" name="initiator" oid="7" format="rows">
    <PROPERTY name="durable-id">I0</PROPERTY>
    <PROPERTY name="nickname">FC-port3</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped">Yes</PROPERTY>
    <PROPERTY name="profile">HP-UX</PROPERTY>
    <PROPERTY name="host-bus-type">FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" key="true">10000090fa13870f</PROPERTY>
    <PROPERTY name="host-id">00c0ff26c2360000e2399f6101010000</PROPERTY>
    <PROPERTY name="host-key" >H1</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b">0</PROPERTY>
  </OBJECT>
<COMP G="9" P="10"/>
<OBJECT basetype="initiator" name="initiator" oid="10" format="rows">
    <PROPERTY name="durable-id">I6</PROPERTY>
    <PROPERTY name="nickname">rac01_01</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped">Yes</PROPERTY>
    <PROPERTY name="profile">Standard</PROPERTY>
    <PROPERTY name="host-bus-type">FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" key="true">500143801875548e</PROPERTY>
    <PROPERTY name="host-id">00c0ff26c4ea0000057f245b01010000</PROPERTY>
    <PROPERTY name="host-key" >H4</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b">0</PROPERTY>
  </OBJECT>
<COMP G="9" P="11"/>
<OBJECT basetype="initiator" name="initiator" oid="11" format="rows">
    <PROPERTY name="durable-id">I5</PROPERTY>
    <PROPERTY name="nickname">rac01_02</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped">Yes</PROPERTY>
    <PROPERTY name="profile">Standard</PROPERTY>
    <PROPERTY name="host-bus-type">FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" key="true">5001438012097ed6</PROPERTY>
    <PROPERTY name="host-id">00c0ff26c4ea0000057f245b01010000</PROPERTY>
    <PROPERTY name="host-key" >H4</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b">0</PROPERTY>
  </OBJECT>
<COMP G="12" P="13"/>
<OBJECT basetype="initiator" name="initiator" oid="13" format="rows">
    <PROPERTY name="durable-id">I3</PROPERTY>
    <PROPERTY name="nickname">rac02_01</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped">Yes</PROPERTY>
    <PROPERTY name="profile">Standard</PROPERTY>
    <PROPERTY name="host-bus-type">FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" key="true">50014380029ceb58</PROPERTY>
    <PROPERTY name="host-id">00c0ff26c4ea0000f77f245b01010000</PROPERTY>
    <PROPERTY name="host-key" >H3</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b">0</PROPERTY>
  </OBJECT>
<COMP G="12" P="14"/>
 <OBJECT basetype="initiator" name="initiator" oid="14" format="rows">
    <PROPERTY name="durable-id">I4</PROPERTY>
    <PROPERTY name="nickname">rac02_02</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped">No</PROPERTY>
    <PROPERTY name="profile">Standard</PROPERTY>
    <PROPERTY name="host-bus-type">FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" key="true">500143801209031c</PROPERTY>
    <PROPERTY name="host-id">00c0ff26c4ea0000f77f245b01010000</PROPERTY>
    <PROPERTY name="host-key" >H3</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b">0</PROPERTY>
  </OBJECT>
<COMP G="15" P="16"/>
<OBJECT basetype="initiator" name="initiator" oid="16" format="rows">
    <PROPERTY name="durable-id">I2</PROPERTY>
    <PROPERTY name="nickname">FC-port1</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped">No</PROPERTY>
    <PROPERTY name="profile">HP-UX</PROPERTY>
    <PROPERTY name="host-bus-type">FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" key="true">21000024ff3dfed1</PROPERTY>
    <PROPERTY name="host-id">NOHOST</PROPERTY>
    <PROPERTY name="host-key" >HU</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b">0</PROPERTY>
  </OBJECT>
</RESPONSE>

"""

LIST_HOST_GROUPS = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show host-groups">
<COMP G="0" P="1"/>
 <OBJECT basetype="host-group" name="host-group" oid="1" format="rows">
    <PROPERTY name="durable-id" >HGU</PROPERTY>
    <PROPERTY name="name">-ungrouped-</PROPERTY>
    <PROPERTY name="serial-number" >UNGROUPEDHOSTS</PROPERTY>
    <PROPERTY name="member-count" >0</PROPERTY>
  </OBJECT>
<COMP G="1" P="2"/>  <OBJECT basetype="host" name="host" oid="2" format="rows">
    <PROPERTY name="durable-id">HU</PROPERTY>
    <PROPERTY name="name">-nohost-</PROPERTY>
    <PROPERTY name="serial-number">NOHOST</PROPERTY>
    <PROPERTY name="member-count" >0</PROPERTY>
    <PROPERTY name="host-group">UNGROUPEDHOSTS</PROPERTY>
    <PROPERTY name="group-key" >HGU</PROPERTY>
  </OBJECT>
<COMP G="2" P="3"/>
<OBJECT basetype="initiator" name="initiator" oid="3" format="rows">
    <PROPERTY name="durable-id" >I2</PROPERTY>
    <PROPERTY name="nickname" >FC-port1</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped" >No</PROPERTY>
    <PROPERTY name="profile" >HP-UX</PROPERTY>
    <PROPERTY name="host-bus-type" >FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" >21000024ff3dfed1</PROPERTY>
    <PROPERTY name="host-id" >NOHOST</PROPERTY>
    <PROPERTY name="host-key" >HU</PROPERTY>
    <PROPERTY name="host-port-bits-a" >0</PROPERTY>
    <PROPERTY name="host-port-bits-b" >0</PROPERTY>
  </OBJECT>
<COMP G="0" P="4"/>
<OBJECT basetype="host-group" name="host-group" oid="4" format="rows">
    <PROPERTY name="durable-id" >HG0</PROPERTY>
    <PROPERTY name="name">HostGroup1</PROPERTY>
    <PROPERTY name="serial-number" >00c0ff26c2360000223a9f6101010000</PROPERTY>
    <PROPERTY name="member-count">1</PROPERTY>
  </OBJECT>
<COMP G="4" P="5"/>  <OBJECT basetype="host" name="host" oid="5" format="rows">
    <PROPERTY name="durable-id" >H1</PROPERTY>
    <PROPERTY name="name">Host1</PROPERTY>
    <PROPERTY name="serial-number" >00c0ff26c2360000e2399f6101010000</PROPERTY>
    <PROPERTY name="member-count">2</PROPERTY>
    <PROPERTY name="host-group">00c0ff26c2360000223a9f6101010000</PROPERTY>
    <PROPERTY name="group-key">HG0</PROPERTY>
  </OBJECT>
<COMP G="5" P="6"/>
 <OBJECT basetype="initiator" name="initiator" oid="6" format="rows">
    <PROPERTY name="durable-id" >I1</PROPERTY>
    <PROPERTY name="nickname" >FC-port2</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped" >Yes</PROPERTY>
    <PROPERTY name="profile" >HP-UX</PROPERTY>
    <PROPERTY name="host-bus-type" >FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" >10000090fa13870e</PROPERTY>
    <PROPERTY name="host-id" >00c0ff26c2360000e2399f6101010000</PROPERTY>
    <PROPERTY name="host-key" >H1</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b" >0</PROPERTY>
  </OBJECT>
<COMP G="5" P="7"/>
<OBJECT basetype="initiator" name="initiator" oid="7" format="rows">
    <PROPERTY name="durable-id" >I0</PROPERTY>
    <PROPERTY name="nickname" >FC-port3</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped" >Yes</PROPERTY>
    <PROPERTY name="profile" >HP-UX</PROPERTY>
    <PROPERTY name="host-bus-type" >FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" >10000090fa13870f</PROPERTY>
    <PROPERTY name="host-id" >00c0ff26c2360000e2399f6101010000</PROPERTY>
    <PROPERTY name="host-key" >H1</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b" >0</PROPERTY>
  </OBJECT>
<COMP G="0" P="8"/>
<OBJECT basetype="host-group" name="host-group" oid="8" format="rows">
    <PROPERTY name="durable-id" >HG2</PROPERTY>
    <PROPERTY name="name" >rac</PROPERTY>
    <PROPERTY name="serial-number">00c0ff26c4ea00008c81245b01010000</PROPERTY>
    <PROPERTY name="member-count" >2</PROPERTY>
  </OBJECT>
<COMP G="8" P="9"/>  <OBJECT basetype="host" name="host" oid="9" format="rows">
    <PROPERTY name="durable-id" >H4</PROPERTY>
    <PROPERTY name="name" >rac01</PROPERTY>
    <PROPERTY name="serial-number">00c0ff26c4ea0000057f245b01010000</PROPERTY>
    <PROPERTY name="member-count" >2</PROPERTY>
    <PROPERTY name="host-group" >00c0ff26c4ea00008c81245b01010000</PROPERTY>
    <PROPERTY name="group-key">HG2</PROPERTY>
  </OBJECT>
<COMP G="9" P="10"/>
 <OBJECT basetype="initiator" name="initiator" oid="10" format="rows">
    <PROPERTY name="durable-id" >I6</PROPERTY>
    <PROPERTY name="nickname" >rac01_01</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped" >Yes</PROPERTY>
    <PROPERTY name="profile" >Standard</PROPERTY>
    <PROPERTY name="host-bus-type" >FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" >500143801875548e</PROPERTY>
    <PROPERTY name="host-id" >00c0ff26c4ea0000057f245b01010000</PROPERTY>
    <PROPERTY name="host-key" >H4</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b" >0</PROPERTY>
  </OBJECT>
<COMP G="9" P="11"/>
 <OBJECT basetype="initiator" name="initiator" oid="11" format="rows">
    <PROPERTY name="durable-id" >I5</PROPERTY>
    <PROPERTY name="nickname" >rac01_02</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped" >Yes</PROPERTY>
    <PROPERTY name="profile" >Standard</PROPERTY>
    <PROPERTY name="host-bus-type" >FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" >5001438012097ed6</PROPERTY>
    <PROPERTY name="host-id" >00c0ff26c4ea0000057f245b01010000</PROPERTY>
    <PROPERTY name="host-key" >H4</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b" >0</PROPERTY>
  </OBJECT>
<COMP G="8" P="12"/>
<OBJECT basetype="host" name="host" oid="12" format="rows">
    <PROPERTY name="durable-id" >H3</PROPERTY>
    <PROPERTY name="name" >rac02</PROPERTY>
    <PROPERTY name="serial-number">00c0ff26c4ea0000f77f245b01010000</PROPERTY>
    <PROPERTY name="member-count" >2</PROPERTY>
    <PROPERTY name="host-group">00c0ff26c4ea00008c81245b01010000</PROPERTY>
    <PROPERTY name="group-key">HG2</PROPERTY>
  </OBJECT>
<COMP G="12" P="13"/>
<OBJECT basetype="initiator" name="initiator" oid="13" format="rows">
    <PROPERTY name="durable-id" >I3</PROPERTY>
    <PROPERTY name="nickname" >rac02_01</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped" >Yes</PROPERTY>
    <PROPERTY name="profile" >Standard</PROPERTY>
    <PROPERTY name="host-bus-type" >FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" >50014380029ceb58</PROPERTY>
    <PROPERTY name="host-id" >00c0ff26c4ea0000f77f245b01010000</PROPERTY>
    <PROPERTY name="host-key" >H3</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b" >0</PROPERTY>
  </OBJECT>
<COMP G="12" P="14"/>
<OBJECT basetype="initiator" name="initiator" oid="14" format="rows">
    <PROPERTY name="durable-id" >I4</PROPERTY>
    <PROPERTY name="nickname" >rac02_02</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped" >No</PROPERTY>
    <PROPERTY name="profile" >Standard</PROPERTY>
    <PROPERTY name="host-bus-type" >FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" >500143801209031c</PROPERTY>
    <PROPERTY name="host-id" >00c0ff26c4ea0000f77f245b01010000</PROPERTY>
    <PROPERTY name="host-key" >H3</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b" >0</PROPERTY>
  </OBJECT>
<COMP G="0" P="15"/>
 <OBJECT basetype="host" name="host" oid="15" format="rows">
    <PROPERTY name="durable-id" >HU</PROPERTY>
    <PROPERTY name="name" >-nohost-</PROPERTY>
    <PROPERTY name="serial-number">NOHOST</PROPERTY>
    <PROPERTY name="member-count" >0</PROPERTY>
    <PROPERTY name="host-group" >UNGROUPEDHOSTS</PROPERTY>
    <PROPERTY name="group-key">HGU</PROPERTY>
  </OBJECT>
<COMP G="15" P="16"/>
<OBJECT basetype="initiator" name="initiator" oid="16" format="rows">
    <PROPERTY name="durable-id" >I2</PROPERTY>
    <PROPERTY name="nickname" >FC-port1</PROPERTY>
    <PROPERTY name="discovered">No</PROPERTY>
    <PROPERTY name="mapped" >No</PROPERTY>
    <PROPERTY name="profile" >HP-UX</PROPERTY>
    <PROPERTY name="host-bus-type" >FC</PROPERTY>
    <PROPERTY name="host-bus-type-numeric">6</PROPERTY>
    <PROPERTY name="id" >21000024ff3dfed1</PROPERTY>
    <PROPERTY name="host-id" >NOHOST</PROPERTY>
    <PROPERTY name="host-key" >HU</PROPERTY>
    <PROPERTY name="host-port-bits-a">0</PROPERTY>
    <PROPERTY name="host-port-bits-b" >0</PROPERTY>
  </OBJECT>
</RESPONSE>
"""
LIST_HOST = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show host-groups">
<COMP G="1" P="2"/>  <OBJECT basetype="host" name="host" oid="2" format="rows">
    <PROPERTY name="durable-id">HU</PROPERTY>
    <PROPERTY name="name">-nohost-</PROPERTY>
    <PROPERTY name="serial-number">NOHOST</PROPERTY>
    <PROPERTY name="member-count">0</PROPERTY>
    <PROPERTY name="host-group">UNGROUPEDHOSTS</PROPERTY>
    <PROPERTY name="group-key">HGU</PROPERTY>
  </OBJECT>
<COMP G="4" P="5"/>  <OBJECT basetype="host" name="host" oid="5" format="rows">
    <PROPERTY name="durable-id">H1</PROPERTY>
    <PROPERTY name="name">Host1</PROPERTY>
    <PROPERTY name="serial-number">00c0ff26c2360000e2399f6101010000</PROPERTY>
    <PROPERTY name="member-count">2</PROPERTY>
    <PROPERTY name="host-group">00c0ff26c2360000223a9f6101010000</PROPERTY>
    <PROPERTY name="group-key">HG0</PROPERTY>
  </OBJECT>
<COMP G="8" P="9"/>  <OBJECT basetype="host" name="host" oid="9" format="rows">
    <PROPERTY name="durable-id">H4</PROPERTY>
    <PROPERTY name="name">rac01</PROPERTY>
    <PROPERTY name="serial-number">00c0ff26c4ea0000057f245b01010000</PROPERTY>
    <PROPERTY name="member-count">2</PROPERTY>
    <PROPERTY name="host-group">00c0ff26c4ea00008c81245b01010000</PROPERTY>
    <PROPERTY name="group-key">HG2</PROPERTY>
  </OBJECT>
<COMP G="8" P="12"/>
<OBJECT basetype="host" name="host" oid="12" format="rows">
    <PROPERTY name="durable-id">H3</PROPERTY>
    <PROPERTY name="name">rac02</PROPERTY>
    <PROPERTY name="serial-number">00c0ff26c4ea0000f77f245b01010000</PROPERTY>
    <PROPERTY name="member-count">2</PROPERTY>
    <PROPERTY name="host-group">00c0ff26c4ea00008c81245b01010000</PROPERTY>
    <PROPERTY name="group-key">HG2</PROPERTY>
  </OBJECT>
<COMP G="0" P="15"/><OBJECT basetype="host" name="host" oid="15" format="rows">
    <PROPERTY name="durable-id">HU</PROPERTY>
    <PROPERTY name="name">-nohost-</PROPERTY>
    <PROPERTY name="serial-number">NOHOST</PROPERTY>
    <PROPERTY name="member-count">0</PROPERTY>
    <PROPERTY name="host-group">UNGROUPEDHOSTS</PROPERTY>
    <PROPERTY name="group-key">HGU</PROPERTY>
  </OBJECT>
</RESPONSE>
"""
LIST_VOLUME_GROUPS = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show volume-groups">
<COMP G="0" P="4"/>
<OBJECT basetype="volume-groups" name="volume-groups" oid="4" format="rows">
    <PROPERTY name="durable-id">VG6</PROPERTY>
    <PROPERTY name="group-name" >VGroup1</PROPERTY>
    <PROPERTY name="serial-number">00c0ff26c4ea0000ab2b9f6101000000</PROPERTY>
    <PROPERTY name="type" >Volume</PROPERTY>
    <PROPERTY name="type-numeric">3672</PROPERTY>
    <PROPERTY name="member-count">2</PROPERTY>
  </OBJECT>
<COMP G="4" P="5"/>
 <OBJECT basetype="volumes" name="volume" oid="5" format="rows">
    <PROPERTY name="durable-id">V0</PROPERTY>
    <PROPERTY name="virtual-disk-name" >A</PROPERTY>
    <PROPERTY name="storage-pool-name">A</PROPERTY>
    <PROPERTY name="volume-name">Vol0001</PROPERTY>
    <PROPERTY name="size" >100.9GB</PROPERTY>
    <PROPERTY name="size-numeric" >197255168</PROPERTY>
    <PROPERTY name="total-size">100.9GB</PROPERTY>
    <PROPERTY name="total-size-numeric" >197255168</PROPERTY>
    <PROPERTY name="allocated-size">0B</PROPERTY>
    <PROPERTY name="allocated-size-numeric">0</PROPERTY>
    <PROPERTY name="storage-type" >Virtual</PROPERTY>
    <PROPERTY name="storage-type-numeric" >1</PROPERTY>
    <PROPERTY name="preferred-owner">A</PROPERTY>
    <PROPERTY name="preferred-owner-numeric">1</PROPERTY>
    <PROPERTY name="owner" >A</PROPERTY>
    <PROPERTY name="owner-numeric">1</PROPERTY>
    <PROPERTY name="serial-number" >00c0ff26c4ea0000fa80546101000000</PROPERTY>
    <PROPERTY name="write-policy" >write-back</PROPERTY>
    <PROPERTY name="write-policy-numeric">1</PROPERTY>
    <PROPERTY name="cache-optimization" >standard</PROPERTY>
    <PROPERTY name="cache-optimization-numeric" >0</PROPERTY>
    <PROPERTY name="read-ahead-size" >Adaptive</PROPERTY>
    <PROPERTY name="read-ahead-size-numeric" >-1</PROPERTY>
    <PROPERTY name="volume-type" >base</PROPERTY>
    <PROPERTY name="volume-type-numeric">15</PROPERTY>
    <PROPERTY name="volume-class" >standard</PROPERTY>
    <PROPERTY name="volume-class-numeric" >0</PROPERTY>
    <PROPERTY name="profile-preference" >Standard</PROPERTY>
    <PROPERTY name="profile-preference-numeric">0</PROPERTY>
    <PROPERTY name="snapshot" >No</PROPERTY>
    <PROPERTY name="volume-qualifier">N/A</PROPERTY>
    <PROPERTY name="volume-qualifier-numeric" >0</PROPERTY>
    <PROPERTY name="blocks" >197255168</PROPERTY>
    <PROPERTY name="capabilities">dmse</PROPERTY>
    <PROPERTY name="volume-parent"></PROPERTY>
    <PROPERTY name="snap-pool"></PROPERTY>
    <PROPERTY name="replication-set" ></PROPERTY>
    <PROPERTY name="attributes" ></PROPERTY>
    <PROPERTY name="wwn" >600C0FF00026C4EAFA80546101000000</PROPERTY>
    <PROPERTY name="progress">0%</PROPERTY>
    <PROPERTY name="progress-numeric">0</PROPERTY>
    <PROPERTY name="container-name">A</PROPERTY>
    <PROPERTY name="allowed-storage-tiers-numeric" >7</PROPERTY>
    <PROPERTY name="threshold-percent-of-pool" >10.00 %</PROPERTY>
    <PROPERTY name="reserved-size-in-pages" >0</PROPERTY>
    <PROPERTY name="allocate-reserved-pages-first">Enabled</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
    <PROPERTY name="health-numeric">0</PROPERTY>
    <PROPERTY name="health-reason"></PROPERTY>
    <PROPERTY name="health-recommendation" ></PROPERTY>
    <PROPERTY name="volume-group">00c0ff26c4ea0000ab2b9f6101000000</PROPERTY>
    <PROPERTY name="group-key" >VG6</PROPERTY>
  </OBJECT>
<COMP G="4" P="6"/>
<OBJECT basetype="volumes" name="volume" oid="6" format="rows">
    <PROPERTY name="durable-id">V1</PROPERTY>
    <PROPERTY name="virtual-disk-name" >A</PROPERTY>
    <PROPERTY name="storage-pool-name">A</PROPERTY>
    <PROPERTY name="volume-name">Vol0002</PROPERTY>
    <PROPERTY name="size" >99.9GB</PROPERTY>
    <PROPERTY name="size-numeric" >195305472</PROPERTY>
    <PROPERTY name="total-size">99.9GB</PROPERTY>
    <PROPERTY name="total-size-numeric" >195305472</PROPERTY>
    <PROPERTY name="allocated-size">0B</PROPERTY>
    <PROPERTY name="allocated-size-numeric">0</PROPERTY>
    <PROPERTY name="storage-type" >Virtual</PROPERTY>
    <PROPERTY name="storage-type-numeric" >1</PROPERTY>
    <PROPERTY name="preferred-owner">A</PROPERTY>
    <PROPERTY name="preferred-owner-numeric">1</PROPERTY>
    <PROPERTY name="owner" >A</PROPERTY>
    <PROPERTY name="owner-numeric">1</PROPERTY>
    <PROPERTY name="serial-number" >00c0ff26c4ea00000a81546101000000</PROPERTY>
    <PROPERTY name="write-policy" >write-back</PROPERTY>
    <PROPERTY name="write-policy-numeric">1</PROPERTY>
    <PROPERTY name="cache-optimization" >standard</PROPERTY>
    <PROPERTY name="cache-optimization-numeric" >0</PROPERTY>
    <PROPERTY name="read-ahead-size" >Adaptive</PROPERTY>
    <PROPERTY name="read-ahead-size-numeric" >-1</PROPERTY>
    <PROPERTY name="volume-type" >base</PROPERTY>
    <PROPERTY name="volume-type-numeric">15</PROPERTY>
    <PROPERTY name="volume-class" >standard</PROPERTY>
    <PROPERTY name="volume-class-numeric" >0</PROPERTY>
    <PROPERTY name="profile-preference" >Standard</PROPERTY>
    <PROPERTY name="profile-preference-numeric">0</PROPERTY>
    <PROPERTY name="snapshot" >No</PROPERTY>
    <PROPERTY name="volume-qualifier">N/A</PROPERTY>
    <PROPERTY name="volume-qualifier-numeric" >0</PROPERTY>
    <PROPERTY name="blocks" >195305472</PROPERTY>
    <PROPERTY name="capabilities">dmse</PROPERTY>
    <PROPERTY name="volume-parent"></PROPERTY>
    <PROPERTY name="snap-pool"></PROPERTY>
    <PROPERTY name="replication-set" ></PROPERTY>
    <PROPERTY name="attributes" ></PROPERTY>
    <PROPERTY name="wwn" >600C0FF00026C4EA0A81546101000000</PROPERTY>
    <PROPERTY name="progress">0%</PROPERTY>
    <PROPERTY name="progress-numeric">0</PROPERTY>
    <PROPERTY name="container-name">A</PROPERTY>
    <PROPERTY name="allowed-storage-tiers-numeric" >7</PROPERTY>
    <PROPERTY name="threshold-percent-of-pool" >10.00 %</PROPERTY>
    <PROPERTY name="reserved-size-in-pages" >0</PROPERTY>
    <PROPERTY name="allocate-reserved-pages-first">Enabled</PROPERTY>
    <PROPERTY name="health">OK</PROPERTY>
    <PROPERTY name="health-numeric">0</PROPERTY>
    <PROPERTY name="health-reason"></PROPERTY>
    <PROPERTY name="health-recommendation" ></PROPERTY>
    <PROPERTY name="volume-group">00c0ff26c4ea0000ab2b9f6101000000</PROPERTY>
    <PROPERTY name="group-key" >VG6</PROPERTY>
  </OBJECT>
</RESPONSE>
"""

LIST_MAPS_ALL = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<RESPONSE VERSION="L100" REQUEST="show maps">
<COMP G="0" P="1"/>
 <OBJECT basetype="volume-group-view">
    <PROPERTY name="durable-id">VG5</PROPERTY>
    <PROPERTY name="serial-number">00c0ff26c4ea0000e22b9f6101000000</PROPERTY>
    <PROPERTY name="group-name">VGroup2.*</PROPERTY>
  </OBJECT>
<COMP G="1" P="2"/>
<OBJECT basetype="volume-group-view-mappings" >
    <PROPERTY name="durable-id" >VG5_I3</PROPERTY>
    <PROPERTY name="parent-id">VG5</PROPERTY>
    <PROPERTY name="mapped-id">I3</PROPERTY>
    <PROPERTY name="ports">1,2</PROPERTY>
    <PROPERTY name="access">read-write</PROPERTY>
    <PROPERTY name="access-numeric">3</PROPERTY>
    <PROPERTY name="initiator-id">50014380029ceb58</PROPERTY>
    <PROPERTY name="nickname">rac02_01</PROPERTY>
    <PROPERTY name="host-profile">Standard</PROPERTY>
  </OBJECT>
<COMP G="2" P="3"/>
<OBJECT basetype="volume-group-view-mappings-luns">
    <PROPERTY name="volume-name">Vol0003</PROPERTY>
    <PROPERTY name="volume-serial">00c0ff26c4ea000082537a6101000000</PROPERTY>
    <PROPERTY name="lun">0</PROPERTY>
  </OBJECT>
<COMP G="2" P="4"/>
<OBJECT basetype="volume-group-view-mappings-luns">
    <PROPERTY name="volume-name" >Vol0004</PROPERTY>
    <PROPERTY name="volume-serial" >00c0ff26c4ea000085537a6101000000</PROPERTY>
    <PROPERTY name="lun">2</PROPERTY>
  </OBJECT>
<COMP G="1" P="5"/>
 <OBJECT basetype="volume-view">
    <PROPERTY name="durable-id">V3</PROPERTY>
    <PROPERTY name="volume-serial" >00c0ff26c4ea000085537a6101000000</PROPERTY>
    <PROPERTY name="volume-name">Vol0004</PROPERTY>
  </OBJECT>
<COMP G="5" P="6"/>
 <OBJECT basetype="volume-view-mappings" >
    <PROPERTY name="durable-id" >V3_I0</PROPERTY>
    <PROPERTY name="parent-id">V3</PROPERTY>
    <PROPERTY name="mapped-id" >I0</PROPERTY>
    <PROPERTY name="ports">3,4</PROPERTY>
    <PROPERTY name="lun"  >0</PROPERTY>
    <PROPERTY name="access">read-write</PROPERTY>
    <PROPERTY name="access-numeric">3</PROPERTY>
    <PROPERTY name="identifier" >10000090fa13870f</PROPERTY>
    <PROPERTY name="nickname" >FC-port3</PROPERTY>
    <PROPERTY name="host-profile">HPUX</PROPERTY>
  </OBJECT>
<COMP G="0" P="7"/>
  <OBJECT basetype="volume-view">
    <PROPERTY name="durable-id">V0</PROPERTY>
    <PROPERTY name="volume-serial">00c0ff26c4ea0000fa80546101000000</PROPERTY>
    <PROPERTY name="volume-name" >Vol0001</PROPERTY>
  </OBJECT>
<COMP G="7" P="8"/>
<OBJECT basetype="volume-view-mappings">
    <PROPERTY name="durable-id" key="true">V0_I1</PROPERTY>
    <PROPERTY name="parent-id">V0</PROPERTY>
    <PROPERTY name="mapped-id">I1</PROPERTY>
    <PROPERTY name="ports">1,2</PROPERTY>
    <PROPERTY name="lun">0</PROPERTY>
    <PROPERTY name="access">read-write</PROPERTY>
    <PROPERTY name="access-numeric">3</PROPERTY>
    <PROPERTY name="identifier">10000090fa13870e</PROPERTY>
    <PROPERTY name="nickname">FC-port2</PROPERTY>
    <PROPERTY name="host-profile">HPUX</PROPERTY>
  </OBJECT>
<COMP G="0" P="9"/>
<OBJECT basetype="volume-view">
    <PROPERTY name="durable-id" >V1</PROPERTY>
    <PROPERTY name="volume-serial">00c0ff26c4ea00000a81546101000000</PROPERTY>
    <PROPERTY name="volume-name">Vol0002</PROPERTY>
  </OBJECT>
<COMP G="9" P="10"/>
<OBJECT basetype="volume-view-mappings">
    <PROPERTY name="durable-id">V1_H4</PROPERTY>
    <PROPERTY name="parent-id" >V1</PROPERTY>
    <PROPERTY name="mapped-id">H4</PROPERTY>
    <PROPERTY name="ports">1,2</PROPERTY>
    <PROPERTY name="lun">0</PROPERTY>
    <PROPERTY name="access">read-write</PROPERTY>
    <PROPERTY name="access-numeric">3</PROPERTY>
    <PROPERTY name="identifier">00c0ff26c4ea0000057f245b01010000</PROPERTY>
    <PROPERTY name="nickname">rac01.*</PROPERTY>
    <PROPERTY name="host-profile">Standard</PROPERTY>
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

list_storage_host_initiators = [
    {
        'name': 'FC-port1',
        'type': 'fc',
        'alias': 'I2',
        'storage_id': 'kkk',
        'native_storage_host_initiator_id': 'I2',
        'wwn': '21000024ff3dfed1',
        'status': 'online',
        'native_storage_host_id': 'NOHOST'
    },
    {
        'name': 'FC-port2',
        'type': 'fc',
        'alias': 'I1',
        'storage_id': 'kkk',
        'native_storage_host_initiator_id': 'I1',
        'wwn': '10000090fa13870e',
        'status': 'online',
        'native_storage_host_id': '00c0ff26c2360000e2399f6101010000'
    },
    {
        'name': 'FC-port3',
        'type': 'fc',
        'alias': 'I0',
        'storage_id': 'kkk',
        'native_storage_host_initiator_id': 'I0',
        'wwn': '10000090fa13870f',
        'status': 'online',
        'native_storage_host_id': '00c0ff26c2360000e2399f6101010000'
    },
    {
        'name': 'rac01_01',
        'type': 'fc',
        'alias': 'I6',
        'storage_id': 'kkk',
        'native_storage_host_initiator_id': 'I6',
        'wwn': '500143801875548e',
        'status': 'online',
        'native_storage_host_id': '00c0ff26c4ea0000057f245b01010000'
    },
    {
        'name': 'rac01_02',
        'type': 'fc',
        'alias': 'I5',
        'storage_id': 'kkk',
        'native_storage_host_initiator_id': 'I5',
        'wwn': '5001438012097ed6',
        'status': 'online',
        'native_storage_host_id': '00c0ff26c4ea0000057f245b01010000'
    },
    {
        'name': 'rac02_01',
        'type': 'fc',
        'alias': 'I3',
        'storage_id': 'kkk',
        'native_storage_host_initiator_id': 'I3',
        'wwn': '50014380029ceb58',
        'status': 'online',
        'native_storage_host_id': '00c0ff26c4ea0000f77f245b01010000'
    },
    {
        'name': 'rac02_02',
        'type': 'fc',
        'alias': 'I4',
        'storage_id': 'kkk',
        'native_storage_host_initiator_id': 'I4',
        'wwn': '500143801209031c',
        'status': 'online',
        'native_storage_host_id': '00c0ff26c4ea0000f77f245b01010000'
    },
    {
        'name': 'FC-port1',
        'type': 'fc',
        'alias': 'I2',
        'storage_id': 'kkk',
        'native_storage_host_initiator_id': 'I2',
        'wwn': '21000024ff3dfed1',
        'status': 'online',
        'native_storage_host_id': 'NOHOST'
    }
]

list_storage_hosts = [
    {
        'name': 'Host1',
        'description': 'H1',
        'storage_id': 'kkk',
        'native_storage_host_id': '00c0ff26c2360000e2399f6101010000',
        'os_type': 'HP-UX',
        'status': 'normal'
    },
    {
        'name': 'rac01',
        'description': 'H4',
        'storage_id': 'kkk',
        'native_storage_host_id': '00c0ff26c4ea0000057f245b01010000',
        'os_type': 'HP-UX',
        'status': 'normal'
    },
    {
        'name': 'rac02',
        'description': 'H3',
        'storage_id': 'kkk',
        'native_storage_host_id': '00c0ff26c4ea0000f77f245b01010000',
        'os_type': 'HP-UX',
        'status': 'normal'
    }
]


list_storage_host_groups = {
    'storage_host_groups': [
        {
            'name': 'HostGroup1',
            'description': 'HG0',
            'storage_id': 'kkk',
            'native_storage_host_group_id': '00c0ff26c2360000223a9f6101010000',
            'storage_hosts': '00c0ff26c2360000e2399f6101010000'
        }, {
            'name': 'rac',
            'description': 'HG2',
            'storage_id': 'kkk',
            'native_storage_host_group_id': '00c0ff26c4ea00008c81245b01010000',
            'storage_hosts': '00c0ff26c4ea0000057f245b01010000,'
                             '00c0ff26c4ea0000f77f245b01010000'
        }
    ],
    'storage_host_grp_host_rels': [
        {'storage_id': 'kkk',
         'native_storage_host_group_id': '00c0ff26c2360000223a9f6101010000',
         'native_storage_host_id': '00c0ff26c2360000e2399f6101010000'
         },
        {
            'storage_id': 'kkk',
            'native_storage_host_group_id': '00c0ff26c4ea00008c81245b01010000',
            'native_storage_host_id': '00c0ff26c4ea0000057f245b01010000'
        },
        {
            'storage_id': 'kkk',
            'native_storage_host_group_id': '00c0ff26c4ea00008c81245b01010000',
            'native_storage_host_id': '00c0ff26c4ea0000f77f245b01010000'
        }
    ]
}

list_volume_groups = {
    'volume_groups':
        [
            {
                'name': 'VGroup1',
                'description': 'VG6',
                'storage_id': 'kkk',
                'native_volume_group_id': 'VG6',
                'volumes': 'V0,V1'
            }
        ],
    'vol_grp_vol_rels':
        [
            {
                'storage_id': 'kkk',
                'native_volume_group_id': 'VG6',
                'native_volume_id': 'V0'
            },
            {
                'storage_id': 'kkk',
                'native_volume_group_id': 'VG6',
                'native_volume_id': 'V1'
            }
        ]
}

list_masking_views = [
    {
        'name': 'FC-port3',
        'description': 'FC-port3',
        'storage_id': 'kkk',
        'native_masking_view_id': 'V3_I0V3',
        'native_port_group_id': 'port_group_A3B3A4B4',
        'native_volume_id': 'V3',
        'native_storage_host_id': '00c0ff26c2360000e2399f6101010000'
    },
    {
        'name': 'FC-port2',
        'description': 'FC-port2',
        'storage_id': 'kkk',
        'native_masking_view_id': 'V0_I1V0',
        'native_port_group_id': 'port_group_A1B1A2B2',
        'native_volume_id': 'V0',
        'native_storage_host_id': '00c0ff26c2360000e2399f6101010000'
    },
    {
        'name': 'rac01.*',
        'description': 'rac01.*',
        'storage_id': 'kkk',
        'native_masking_view_id': 'V1_H4V1',
        'native_port_group_id': 'port_group_A1B1A2B2',
        'native_volume_id': 'V1',
        'native_storage_host_id': '00c0ff26c4ea0000057f245b01010000'
    },
    {
        'name': 'rac02_01',
        'description': 'rac02_01',
        'storage_id': 'kkk',
        'native_masking_view_id': 'VG5_I3VG5',
        'native_port_group_id': 'port_group_A1B1A2B2',
        'native_volume_group_id': 'VG5',
        'native_storage_host_id': '00c0ff26c4ea0000f77f245b01010000'
    }
]
