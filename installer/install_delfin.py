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
import subprocess
from subprocess import CalledProcessError
import traceback as tb
from installer.helper import copy_files, create_dir, \
    logger, logfile, delfin_log_dir, create_file

delfin_source_path = ''
delfin_etc_dir = '/etc/delfin'
delfin_var_dir = '/var/lib/delfin'
conf_file = os.path.join(delfin_etc_dir, 'delfin.conf')
proj_name = 'delfin'
DEVNULL = '/dev/null'


def _activate():
    path_to_activate = os.path.join(delfin_source_path, 'installer',
                                    proj_name, 'bin/activate')
    command = '. ' + path_to_activate
    os.system(command)


# Initialize the settings first
def init():
    pass


def create_delfin_db():
    try:
        db_path = os.path.join(delfin_source_path, 'script', 'create_db.py')
        subprocess.check_call(['python3', db_path,
                               '--config-file', conf_file])
    except CalledProcessError as cpe:
        logger.error("Got CPE error [%s]:[%s]" % (cpe, tb.print_exc()))
        return
    logger.info('db created ')


def start_processes():
    # start api process
    proc_path = os.path.join(delfin_source_path, 'delfin', 'cmd', 'api.py')
    command = 'python3 ' + proc_path + ' --config-file ' +\
              conf_file + ' >' + DEVNULL + ' 2>&1 &'
    # >/dev/null 2>&1
    logger.info("Executing command [%s]", command)
    os.system(command)
    logger.info("API process_started")

    # Start task process
    proc_path = os.path.join(delfin_source_path, 'delfin', 'cmd', 'task.py')
    command = 'python3 ' + proc_path + ' --config-file ' +\
              conf_file + ' >' + DEVNULL + ' 2>&1 &'
    logger.info("Executing command [%s]", command)
    os.system(command)

    logger.info("TASK process_started")

    # Start alert process
    proc_path = os.path.join(delfin_source_path, 'delfin', 'cmd', 'alert.py')
    command = 'python3 ' + proc_path + ' --config-file ' +\
              conf_file + ' >' + DEVNULL + ' 2>&1 &'
    logger.info("Executing command [%s]", command)
    os.system(command)
    logger.info("ALERT process_started")

    # Start exporter server process
    proc_path = os.path.join(delfin_source_path, 'delfin', 'exporter',
                             'prometheus', 'exporter_server.py')
    command = 'python3 ' + proc_path + ' --config-file ' +\
              conf_file + ' >' + DEVNULL + ' 2>&1 &'
    logger.info("Executing command [%s]", command)
    os.system(command)
    logger.info("Exporter process_started")


def install_delfin():
    python_setup_comm = ['build', 'install']
    req_logs = os.path.join(delfin_log_dir, 'requirements.log')
    command = 'pip3 install -r requirements.txt >' + req_logs + ' 2>&1'
    logger.info("Executing [%s]", command)
    os.system(command)

    setup_file = os.path.join(delfin_source_path, 'setup.py')
    for command in python_setup_comm:
        try:
            command = 'python3 ' + setup_file + ' ' +\
                      command + ' >>' + logfile
            logger.info("Executing [%s]", command)
            os.system(command)
        except CalledProcessError as cpe:
            logger.error("Got CPE error [%s]:[%s]" % (cpe, tb.print_exc()))
            return


def main():
    global delfin_source_path
    cwd = os.getcwd()
    logger.info("Current dir is %s" % cwd)
    this_file_dir = os.path.dirname(os.path.realpath(__file__))
    delfin_source_path = os.path.join(this_file_dir, "../")

    logger.info("delfins [%s]" % delfin_source_path)
    os.chdir(delfin_source_path)
    logger.info(os.getcwd())

    # create required directories
    create_dir(delfin_etc_dir)
    create_dir(delfin_var_dir)

    # Create blank prometheus exporter file
    filename = delfin_var_dir + '/' + 'delfin_exporter.txt'
    create_file(filename)

    # Copy required files
    # Copy api-paste.ini
    ini_file_src = os.path.join(delfin_source_path, 'etc',
                                'delfin', 'api-paste.ini')
    ini_file_dest = os.path.join(delfin_etc_dir, 'api-paste.ini')
    copy_files(ini_file_src, ini_file_dest)

    # Copy the conf file
    conf_file_src = os.path.join(delfin_source_path, 'etc',
                                 'delfin', 'delfin.conf')
    copy_files(conf_file_src, conf_file)

    # install
    install_delfin()

    # create db
    create_delfin_db()

    # start
    start_processes()


if __name__ == "__main__":
    main()
