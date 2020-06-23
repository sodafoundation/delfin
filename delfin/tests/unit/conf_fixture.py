# Copyright 2020 The SODA Authors.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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

import os

from oslo_service import wsgi

from delfin.common import config

CONF = config.CONF


def set_defaults(conf):
    _safe_set_of_opts(conf, 'verbose', True)
    _safe_set_of_opts(conf, 'state_path', os.path.abspath(
        os.path.join(os.path.dirname(__file__),
                     '..',
                     '..')))
    _safe_set_of_opts(conf, 'connection', "sqlite://", group='database')
    _safe_set_of_opts(conf, 'sqlite_synchronous', False)
    _API_PASTE_PATH = os.path.abspath(
        os.path.join(CONF.state_path,
                     'etc/delfin/api-paste.ini'))
    wsgi.register_opts(conf)
    _safe_set_of_opts(conf, 'api_paste_config', _API_PASTE_PATH)


def _safe_set_of_opts(conf, *args, **kwargs):
    try:
        conf.set_default(*args, **kwargs)
    except config.cfg.NoSuchOptError:
        # Assumed that opt is not imported and not used
        pass
