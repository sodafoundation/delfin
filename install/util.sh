#!/bin/bash
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

# Script to hold the utilities required

PROJECT_NAME='SIM'
LOG_DIR=/var/log/sodafoundation
LOGFILE=${LOGFILE:-/var/log/sodafoundation/sim_installer.log}

if [ ! -d ${LOGDIR} ]; then
    mkdir -p $LOG_DIR
fi

# Log function
sim::log(){
    DATE=`date "+%Y-%m-%d %H:%M:%S"`
    USER=$(whoami)
    echo "${DATE} ${USER} execute $0 [INFO] $@ 2>&1" >> $LOGFILE
}

