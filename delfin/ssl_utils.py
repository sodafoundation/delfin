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
import requests
from oslo_config import cfg
from oslo_log import log
from urllib3 import PoolManager
from OpenSSL.crypto import load_certificate, FILETYPE_PEM

from delfin import exception

LOG = log.getLogger(__name__)
CONF = cfg.CONF
FILE = 'configs.json'


def get_storage_ca_path():
    return CONF.storage_driver.ca_path


def verify_ca_path(ca_path):
    """
    Checking the ca_path exists
    """
    if not os.path.exists(ca_path):
        LOG.error("Directory {0} could not be found.".format(ca_path))
        raise exception.InvalidCAPath(ca_path)


def reload_certificate(ca_path):
    """
    Checking the driver security config validation.
    As required by requests, ca_path must be a directory prepared using
    the c_rehash tool included with OpenSSL.
    Once new certificate added, this function can be called for update.
    If there is a CA certificate chain, all CA certificates along this
    chain should be included in a single file.
    """

    suffixes = ['.pem', '.cer', '.crt', '.crl']
    files = os.listdir(ca_path)
    for file in files:
        if not os.path.isdir(file):
            suf = os.path.splitext(file)[1]
            if suf in suffixes:
                fpath = ca_path + file
                with open(fpath, "rb") as f:
                    cert_content = f.read()
                    cert = load_certificate(FILETYPE_PEM,
                                            cert_content)
                    hash_val = cert.subject_name_hash()
                    hash_hex = hex(hash_val).strip('0x') + ".0"
                    linkfile = ca_path + hash_hex
                    if os.path.exists(linkfile):
                        LOG.debug("Link for {0} already exist.".
                                  format(file))
                    else:
                        LOG.info("Create link file {0} for {1}.".
                                 format(linkfile, fpath))
                        os.symlink(fpath, linkfile)


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
