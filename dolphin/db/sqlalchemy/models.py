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
SQLAlchemy models for Dolphin  data.
"""
import json

from oslo_config import cfg
from oslo_db.sqlalchemy import models
from oslo_db.sqlalchemy.types import JsonEncodedDict
from sqlalchemy import Column, Integer, String, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base

CONF = cfg.CONF
BASE = declarative_base()


class DolphinBase(models.ModelBase,
                  models.TimestampMixin):
    """Base class for Dolphin Models."""
    __table_args__ = {'mysql_engine': 'InnoDB'}
    metadata = None

    def to_dict(self):
        model_dict = {}
        for k, v in self.items():
            if not issubclass(type(v), DolphinBase):
                model_dict[k] = v
        return model_dict


class AccessInfo(BASE, DolphinBase):
    """Represent access info required for storage accessing."""
    __tablename__ = "access_info"
    storage_id = Column(String(128), primary_key=True)
    hostname = Column(String(128))
    username = Column(String(128))
    password = Column(String(128))
    connect_protocol = Column(String(32))
    extra_attributes = Column(JsonEncodedDict)


class Storage(BASE, DolphinBase):
    """Represents a storage object."""

    __tablename__ = 'storages'
    id = Column(String(128), primary_key=True)
    name = Column(String(128))
    vendor = Column(String(128))
    description = Column(String(256))
    model = Column(String(128))
    status = Column(String(32))
    serial_number = Column(String(128))
    firmware_version = Column(String(128))
    location = Column(String(128))
    total_capacity = Column(Numeric)
    used_capacity = Column(Numeric)
    free_capacity = Column(Numeric)


class Volume(BASE, DolphinBase):
    """Represents a volume object."""
    __tablename__ = 'volumes'
    id = Column(String(128), primary_key=True)
    name = Column(String(128))
    storage_id = Column(String(128))
    pool_id = Column(String(128))
    description = Column(String(128))
    status = Column(String(32))
    original_id = Column(String(128))
    wwn = Column(String(128))
    provisioning_policy = Column(String(32))
    total_capacity = Column(Numeric)
    used_capacity = Column(Numeric)
    free_capacity = Column(Numeric)
    compressed = Column(Boolean)
    deduplicated = Column(Boolean)


class Pool(BASE, DolphinBase):
    """Represents a pool object."""
    __tablename__ = 'pools'
    id = Column(String(128), primary_key=True)
    name = Column(String(128))
    storage_id = Column(String(128))
    original_id = Column(String(128))
    description = Column(String(256))
    status = Column(String(32))
    storage_type = Column(String(32))
    total_capacity = Column(Numeric)
    used_capacity = Column(Numeric)
    free_capacity = Column(Numeric)


class Disk(BASE, DolphinBase):
    """Represents a disk object."""
    __tablename__ = 'disks'
    id = Column(String(128), primary_key=True)
    name = Column(String(128))
    status = Column(String(32))
    vendor = Column(String(128))
    original_id = Column(String(128))
    serial_number = Column(String(128))
    model = Column(String(128))
    media_type = Column(String(32))
    capacity = Column(Numeric)
