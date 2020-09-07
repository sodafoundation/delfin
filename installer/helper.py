#!/usr/bin/python3

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
import shutil
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

log_filename = 'delfin_installer.log' +\
               datetime.now().strftime("%d_%m_%Y_%H_%M_%s")
LOGGING_FORMAT = "[%(asctime)s] [%(levelname)s] [%(filename)s] " \
    "[%(funcName)s():%(lineno)s] [PID:%(process)d TID:%(thread)d] %(message)s"
LOGGING_LEVEL = "INFO"
logger = None
logfile = ''
delfin_log_dir = '/var/log/sodafoundation/'


def init_logging():
    global logfile
    global logger

    try:
        os.mkdir(delfin_log_dir)
    except OSError:
        pass
    logfile = delfin_log_dir + log_filename
    server_log_file = RotatingFileHandler(logfile, maxBytes=10000,
                                          backupCount=5)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(LOGGING_FORMAT)
    server_log_file.setFormatter(formatter)
    logger.addHandler(server_log_file)


def create_dir(dirname=None):
    try:
        os.mkdir(dirname)
    except OSError as ose:
        logger.warning("Directory [%s] already exists: [%s]" % (dirname, ose))
        pass
    except Exception as e:
        logger.error("Error in creating Directory [%s] [%s]" % (dirname, e))
        return


def copy_files(src=None, dest=None):
    logger.info("Copying [%s] to [%s]" % (src, dest))
    shutil.copy(src, dest)


init_logging()
