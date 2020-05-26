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
    name="dolphin",
    version="1.0",
    author="SODA Authors",
    author_email="Opensds-tech-discuss@lists.opensds.io",
    license="Apache 2.0",
    packages=find_packages(exclude=("tests", "tests.*")),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    entry_points={
        'resource.exporter': [
            'example1 = dolphin.exporter.example_exporter:Example1Exporter',
            'example2 = dolphin.exporter.example_exporter:Example2Exporter'
        ],
        'dolphin.storage.drivers': [
            'fake_storage fake_driver = dolphin.drivers.fake_storage:FakeStorageDriver',
            'dellemc vmax = dolphin.drivers.dell_emc.vmax.vmax:VMAXStorageDriver'
        ]
    },
)
