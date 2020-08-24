# Copyright 2020 The SODA Authors.
# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Piston Cloud Computing, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
SQLAlchemy models for Delfin  data.
"""

from oslo_config import cfg
from oslo_db.sqlalchemy import models
from oslo_db.sqlalchemy.types import JsonEncodedDict
from sqlalchemy import Column, Integer, String, Boolean, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base

from delfin.common import constants

CONF = cfg.CONF
BASE = declarative_base()


class DelfinBase(models.ModelBase,
                 models.TimestampMixin):
    """Base class for Delfin Models."""
    __table_args__ = {'mysql_engine': 'InnoDB'}
    metadata = None

    def to_dict(self):
        model_dict = {}
        for k, v in self.items():
            if not issubclass(type(v), DelfinBase):
                model_dict[k] = v
        return model_dict


class AccessInfo(BASE, DelfinBase):
    """Represent access info required for storage accessing."""
    __tablename__ = "access_info"
    storage_id = Column(String(36), primary_key=True)
    vendor = Column(String(255))
    model = Column(String(255))
    rest = Column(JsonEncodedDict)
    ssh = Column(JsonEncodedDict)
    extra_attributes = Column(JsonEncodedDict)


class Storage(BASE, DelfinBase):
    """Represents a storage object."""

    __tablename__ = 'storages'
    id = Column(String(36), primary_key=True)
    name = Column(String(255))
    vendor = Column(String(255))
    description = Column(String(255))
    model = Column(String(255))
    status = Column(String(255))
    serial_number = Column(String(255))
    firmware_version = Column(String(255))
    location = Column(String(255))
    total_capacity = Column(BigInteger)
    used_capacity = Column(BigInteger)
    free_capacity = Column(BigInteger)
    raw_capacity = Column(BigInteger)
    subscribed_capacity = Column(BigInteger)
    sync_status = Column(Integer, default=constants.SyncStatus.SYNCED)
    deleted_at = Column(DateTime)
    deleted = Column(Boolean, default=False)


class Volume(BASE, DelfinBase):
    """Represents a volume object."""
    __tablename__ = 'volumes'
    id = Column(String(36), primary_key=True)
    name = Column(String(255))
    storage_id = Column(String(36))
    native_storage_pool_id = Column(String(255))
    description = Column(String(255))
    status = Column(String(255))
    native_volume_id = Column(String(255))
    wwn = Column(String(255))
    type = Column(String(255))
    total_capacity = Column(BigInteger)
    used_capacity = Column(BigInteger)
    free_capacity = Column(BigInteger)
    compressed = Column(Boolean)
    deduplicated = Column(Boolean)


class StoragePool(BASE, DelfinBase):
    """Represents a storage_pool object."""
    __tablename__ = 'storage_pools'
    id = Column(String(36), primary_key=True)
    name = Column(String(255))
    storage_id = Column(String(36))
    native_storage_pool_id = Column(String(255))
    description = Column(String(255))
    status = Column(String(255))
    storage_type = Column(String(255))
    total_capacity = Column(BigInteger)
    used_capacity = Column(BigInteger)
    free_capacity = Column(BigInteger)
    subscribed_capacity = Column(BigInteger)


class Disk(BASE, DelfinBase):
    """Represents a disk object."""
    __tablename__ = 'disks'
    id = Column(String(36), primary_key=True)
    name = Column(String(255))
    status = Column(String(255))
    vendor = Column(String(255))
    native_disk_id = Column(String(255))
    serial_number = Column(String(255))
    model = Column(String(255))
    media_type = Column(String(255))
    capacity = Column(BigInteger)


class AlertSource(BASE, DelfinBase):
    """Represents an alert source configuration."""
    __tablename__ = 'alert_source'
    storage_id = Column(String(36), primary_key=True)
    host = Column(String(255))
    version = Column(String(255))
    community_string = Column(String(255))
    username = Column(String(255))
    security_level = Column(String(255))
    auth_key = Column(String(255))
    auth_protocol = Column(String(255))
    privacy_protocol = Column(String(255))
    privacy_key = Column(String(255))
    engine_id = Column(String(255))
    port = Column(Integer)
    context_name = Column(String(255))
    retry_num = Column(Integer)
    expiration = Column(Integer)
