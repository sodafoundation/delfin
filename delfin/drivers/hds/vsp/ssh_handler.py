# Copyright 2020 The SODA Authors.
# Copyright (c) 2016 Huawei Technologies Co., Ltd.
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

from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class SSHHandler(object):

    test_command = 'showwsapi'

    def __init__(self, sshclient):
        self.sshclient = sshclient

    def login(self, context):
        """Test SSH connection """
        version = ''
        try:
            self.sshclient.doexec(context, SSHHandler.test_command)
        except Exception as e:
            LOG.error('login error:{}'.format(e))
            raise e
        return version
