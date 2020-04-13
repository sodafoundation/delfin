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

from oslo_config import cfg
from oslo_db.sqlalchemy import models
from sqlalchemy import Column, Integer, String, schema
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm
from sqlalchemy import ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship, backref

from dolphin.common import constants

CONF = cfg.CONF
BASE = declarative_base()


class DolphinBase(models.ModelBase,
                 models.TimestampMixin,
                 models.SoftDeleteMixin):
    """Base class for Dolphin Models."""
    __table_args__ = {'mysql_engine': 'InnoDB'}
    metadata = None

    def to_dict(self):
        model_dict = {}
        for k, v in self.items():
            if not issubclass(type(v), DolphinBase):
                model_dict[k] = v
        return model_dict

    def soft_delete(self, session, update_status=False,
                    status_field_name='status'):
        """Mark this object as deleted."""
        if update_status:
            setattr(self, status_field_name, constants.STATUS_DELETED)

        return super(DolphinBase, self).soft_delete(session)

class ConnectionParams(BASE, DolphinBase):
    """Represent registration parameters required for storage object."""
    __tablename__ = "connection_params"
    storage_id = Column(String(36), primary_key=True)
    hostname = Column(String(36), default='False')
    username = Column(String(255))
    password = Column(String(255))

class Storage(BASE, DolphinBase):
    """Represents a storage object."""

    __tablename__ = 'storages'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    vendor = Column(String(255))
    description = Column(String(255))
    model = Column(String(255))
    status = Column(String(255))
    serial_number = Column(String(255))
    location = Column(String(255))
    connection_param = orm.relationship(
        ConnectionParams,
        backref="storages",
        foreign_keys=id,
        primaryjoin="and_("
                    "Storage.id=="
                    "ConnectionParams.storage_id)")

