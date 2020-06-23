#!/usr/bin/env python

# Copyright 2020 The SODA Authors.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Starter script for delfin task service."""

import eventlet
eventlet.monkey_patch()

import sys

from oslo_config import cfg
from oslo_log import log

from delfin.common import config  # noqa
from delfin import service
from delfin import utils
from delfin import version

CONF = cfg.CONF


def main():
    log.register_options(CONF)
    CONF(sys.argv[1:], project='delfin',
         version=version.version_string())
    log.setup(CONF, "delfin")
    utils.monkey_patch()

    task_server = service.Service.create(binary='delfin-task',
                                         coordination=True)
    service.serve(task_server)
    service.wait()


if __name__ == '__main__':
    main()
