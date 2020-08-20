# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import ssl
import json
import requests
from OpenSSL.crypto import load_certificate, FILETYPE_PEM
from oslo_config import cfg
from oslo_log import log
from urllib3 import PoolManager

from delfin import exception

LOG = log.getLogger(__name__)
CONF = cfg.CONF
FILE = 'configs.json'


class SecurityUtils(object):
    def reload_certificate(self, enable_verify, ca_path):
        """
        Checking the southbound security config validation.
        As required by requests, ca_path must be a directory prepared using
        the c_rehash tool included with OpenSSL.
        Once new certificate added, this function can be called for update.
        If there is a CA certificate chain, all CA certificates along this
        chain should be included in a single file.
        """
        if enable_verify:
            if not os.path.exists(ca_path):
                LOG.error("Directory {0} could not be found.".format(
                    ca_path))
                raise exception.InvalidSouthboundCAPath(ca_path)

            suffixes = ['.pem', '.cer', '.crt', '.crl']
            files = os.listdir(ca_path)
            for file in files:
                if not os.path.isdir(file):
                    suf = os.path.splitext(file)[1]
                    if suf in suffixes:
                        fpath = ca_path + file
                        cert_content = open(fpath, "rb").read()
                        cert = load_certificate(FILETYPE_PEM, cert_content)
                        hash_val = cert.subject_name_hash()
                        hash_hex = hex(hash_val).strip('0x') + ".0"
                        linkfile = ca_path + hash_hex
                        if os.path.exists(linkfile):
                            LOG.debug("Link for {0} already exist.".format(
                                file))
                        else:
                            LOG.info("Create link file {0} for {1}.".format(
                                linkfile, fpath))
                            os.symlink(fpath, linkfile)

    def get_configs(self):
        return CONF.southbound_security.reload_cert,\
            CONF.southbound_security.enable_verify,\
            CONF.southbound_security.ca_path,\
            CONF.southbound_security.assert_hostname

    def get_configs_from_file(self, filename=FILE):
        """ For testing security configs from file, create file configs.json
            with contents as below:
            ---
            {
                "reload_cert": true,
                "enable_verify": true,
                "ca_path": "<path to certificates>",
                "assert_hostname": false
            }
            ---
        """
        with open(filename, 'r') as f:
            configs = json.load(f)
            enable_verify = configs.get('enable_verify', False)
            ca_path = configs.get('ca_path', '')
            assert_hostname = configs.get('assert_hostname', False)
            reload_cert = configs.get('reload_cert', False)
            return reload_cert, enable_verify, ca_path, assert_hostname


class HostNameIgnoreAdapter(requests.adapters.HTTPAdapter):
    def cert_verify(self, conn, url, verify, cert):
        conn.assert_hostname = False
        return super(HostNameIgnoreAdapter, self).cert_verify(
            conn, url, verify, cert)

    def init_poolmanager(self, connections, maxsize, block=False,
                         **pool_kwargs):
        self._pool_connections = connections
        self._pool_maxsize = maxsize
        self._pool_block = block
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize,
                                       block=block, strict=True,
                                       ssl_version=ssl.PROTOCOL_TLSv1_2,
                                       **pool_kwargs)
