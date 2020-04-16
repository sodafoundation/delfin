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
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base

CONF = cfg.CONF
BASE = declarative_base()


class DolphinBase(models.ModelBase,
                  models.TimestampMixin):
    """Base class for Dolphin Models."""
    __table_args__ = {'mysql_engine': 'InnoDB'}
    metadata = None


class RegistryContext(BASE, DolphinBase):
    """Represent registration parameters required for storage object."""
    __tablename__ = "registry_contexts"
    storage_id = Column(String(36), primary_key=True)
    hostname = Column(String(36), default='False')
    username = Column(String(255))
    password = Column(String(255))
    vendor = Column(String(255))
    model = Column(String(255))
    extra_attributes = Column(JsonEncodedDict)


class Storage(BASE, DolphinBase):
    """Represents a storage object."""

    __tablename__ = 'storages'
    id = Column(String(36), primary_key=True)
    name = Column(String(255))
    vendor = Column(String(255))
    description = Column(String(255))
    model = Column(String(255))
    status = Column(String(255))
    serial_number = Column(String(255))
    location = Column(String(255))
    total_capacity = Column(Numeric)
    used_capacity = Column(Numeric)
    free_capacity = Column(Numeric)



class Volume(BASE, DolphinBase):
    """Represents a volume object."""
    __tablename__ = 'volumes'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    storage_id = Column(String(255))
    pool_id = Column(String(255))
    description = Column(String(255))
    status = Column(String(255))
    total_capacity = Column(Numeric)
    used_capacity = Column(Numeric)
    free_capacity = Column(Numeric)


class Pool(BASE, DolphinBase):
    """Represents a pool object."""
    __tablename__ = 'pools'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    storage_id = Column(String(255))
    description = Column(String(255))
    status = Column(String(255))
    total_capacity = Column(Numeric)
    used_capacity = Column(Numeric)
    free_capacity = Column(Numeric)
