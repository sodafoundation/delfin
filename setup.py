# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages


setup(
    name="delfin",
    version="1.0.0",
    author="SODA Authors",
    author_email="Opensds-tech-discuss@lists.opensds.io",
    license="Apache 2.0",
    packages=find_packages(exclude=("tests", "tests.*")),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    entry_points={
        'delfin.alert.exporters': [
            'example = delfin.exporter.example:AlertExporterExample',
            'prometheus = delfin.exporter.prometheus.exporter'
            ':AlertExporterPrometheus',
        ],
        'delfin.performance.exporters': [
            'example = delfin.exporter.example:PerformanceExporterExample',
            'prometheus = delfin.exporter.prometheus.exporter'
            ':PerformanceExporterPrometheus',
            'kafka = delfin.exporter.kafka.exporter:PerformanceExporterKafka'
        ],
        'delfin.storage.drivers': [
            'fake_storage fake_driver = delfin.drivers.fake_storage:FakeStorageDriver',
            'fujitsu eternus = delfin.drivers.fujitsu.eternus.eternus_stor:EternusDriver',
            'dellemc unity = delfin.drivers.dell_emc.unity.unity:UnityStorDriver',
            'dellemc vmax = delfin.drivers.dell_emc.vmax.vmax:VMAXStorageDriver',
            'dellemc pmax = delfin.drivers.dell_emc.vmax.vmax:VMAXStorageDriver',
            'dellemc scaleio = delfin.drivers.dell_emc.scaleio.scaleio_stor:ScaleioStorageDriver',
            'dellemc vnx_block = delfin.drivers.dell_emc.vnx.vnx_block.vnx_block:VnxBlockStorDriver',
            'dellemc vplex = delfin.drivers.dell_emc.vplex.vplex_stor:VplexStorageDriver',
            'dellemc powerstore = delfin.drivers.dell_emc.power_store.power_store:PowerStoreDriver',
            'hitachi vsp = delfin.drivers.hitachi.vsp.vsp_stor:HitachiVspDriver',
            'hpe 3par = delfin.drivers.hpe.hpe_3par.hpe_3parstor:Hpe3parStorDriver',
            'hpe primera = delfin.drivers.hpe.hpe_3par.hpe_3parstor:Hpe3parStorDriver',
            'hpe msa = delfin.drivers.hpe.hpe_msa.hpe_msastor:HpeMsaStorDriver',
            'huawei oceanstor = delfin.drivers.huawei.oceanstor.oceanstor:OceanStorDriver',
            'ibm storwize_svc = delfin.drivers.ibm.storwize_svc.storwize_svc:StorwizeSVCDriver',
            'ibm ds8k = delfin.drivers.ibm.ds8k.ds8k:DS8KDriver',
            'netapp cmode = delfin.drivers.netapp.dataontap.cluster_mode:NetAppCmodeDriver',
            'hitachi hnas = delfin.drivers.hitachi.hnas.hds_nas:HitachiHNasDriver',
            'pure flasharray = delfin.drivers.pure.flasharray.pure_flasharray:PureFlashArrayDriver',
            'h3c unistor_cf = delfin.drivers.h3c.unistor_cf.unistor_cf:H3cUniStorCfDriver',
            'macrosan macrosan = delfin.drivers.macro_san.ms.ms_stor:MacroSanDriver',
            # AS5500/AS5300/AS2600/AS2200 use the same driver
            'inspur as5500 = delfin.drivers.inspur.as5500.as5500:As5500Driver'
        ]
    },
)
