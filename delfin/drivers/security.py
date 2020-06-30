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

from OpenSSL.crypto import load_certificate, FILETYPE_PEM
from oslo_config import cfg
from oslo_log import log

from delfin import exception

LOG = log.getLogger(__name__)
CONF = cfg.CONF


class RootRestClient(object):
    def __init__(self):
        """
        Checking the southbound security config validation.
        As required by requests, ca_path must be a directory prepared using
        the c_rehash tool included with OpenSSL.
        Once new certificate added, this function can be called for update.
        If there is a CA certificate chain, all CA certificates should be
        included in a single file.
        """
        self.enable_ssl = CONF.southbound_security.enable_ssl
        self.ca_path = CONF.southbound_security.ca_path

        if self.enable_ssl:
            if not os.path.exists(self.ca_path):
                LOG.error("Directory {0} could not be found.".format(
                    self.ca_path))
                raise exception.InvalidSouthboundCAPath(self.ca_path)

            suffixes = ['.pem', '.cer', '.crt', '.crl']
            files = os.listdir(self.ca_path)
            for file in files:
                if not os.path.isdir(file):
                    suf = os.path.splitext(file)[1]
                    if suf in suffixes:
                        fpath = self.ca_path + file
                        cert_content = open(fpath, "rb").read()
                        cert = load_certificate(FILETYPE_PEM, cert_content)
                        hash_val = cert.subject_name_hash()
                        hash_hex = hex(hash_val).strip('0x') + ".0"
                        linkfile = self.ca_path + hash_hex
                        if os.path.exists(linkfile):
                            LOG.debug("Link for {0} already exist.".format(
                                file))
                        else:
                            LOG.info("Create link file {0} for {1}.".format(
                                linkfile, fpath))
                            os.symlink(fpath, linkfile)
