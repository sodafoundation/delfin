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

import sys, os, shutil, subprocess
from subprocess import CalledProcessError
import traceback as tb
import logging
from logging.handlers import RotatingFileHandler

sim_source_path = ''
sim_etc_dir = '/etc/dolphin'
sim_var_dir = '/var/lib/dolphin'
sim_log_dir = '/var/log/sodafoundation/'
conf_file = os.path.join(sim_etc_dir, 'dolphin.conf')
log_filename = 'sim_installer.log'
LOGGING_FORMAT = "[%(asctime)s] [%(levelname)s] [%(filename)s] " \
    "[%(funcName)s():%(lineno)s] [PID:%(process)d TID:%(thread)d] %(message)s"
LOGGING_LEVEL = "INFO"
logger = None
logfile=''
proj_name = 'SIM'

def _activate():
    path_to_activate = os.getcwd() + '/' + proj_name + '/bin/activate'
    print(path_to_activate)
    command = '. ' +  path_to_activate    
    os.system(command) 
    sys.exit()

def init():
    #_activate()
    global logfile
    global logger
    
    try:
        os.mkdir(sim_log_dir)
    except OSError as ose:
        pass
    logfile = sim_log_dir + log_filename
    server_log_file = RotatingFileHandler(
                                            logfile,
                                            maxBytes=10000,
                                            backupCount=5
                                        )
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(LOGGING_FORMAT)
    server_log_file.setFormatter(formatter)
    logger.addHandler(server_log_file)
    
    
def create_dirs():
    try:
        os.mkdir(sim_etc_dir)
    except OSError as ose:
        logger.warning("Directory [%s] already exists [%s]" \
            % (sim_etc_dir, ose))
        pass
    except Exception as e:
        logger.error("Error in creating Directory [%s] [%s]" \
            % (sim_etc_dir, e))
        return
    
    try:
        os.mkdir(sim_var_dir)
    except OSError as ose:
        logger.warning("Directory [%s] already exists [%s]" % (sim_var_dir, ose))
        pass
    except Exception as e:
        logger.error("Error in creating Directory [%s] [%s]" % (sim_var_dir, e))
        return
    
def copy_req_files():
    ini_file_src = os.path.join(sim_source_path, 'etc', 'dolphin', 'api-paste.ini')
    ini_file_dest = os.path.join(sim_etc_dir, 'api-paste.ini')
    logger.info("Copying [%s] to [%s]" % (ini_file_src, ini_file_dest))

    shutil.copy(ini_file_src, ini_file_dest)

    conf_file_src = os.path.join(sim_source_path, 'etc', 'dolphin', 'dolphin.conf')
    logger.info("Copying [%s] to [%s]" % (conf_file_src, conf_file))

    shutil.copy(conf_file_src, conf_file)


def create_sim_db():
    try:
        db_path = os.path.join(sim_source_path, 'install', 'create_db.py')
        subprocess.check_call(['python3', db_path, '--config-file', conf_file])
    except CalledProcessError as cpe:
        logger.error("Got CPE error [%s]:[%s]" % (cpe, tb.print_exc()))
        return
    logger.info('db created ')
        
def start_api():
    api_path = os.path.join(sim_source_path, 'dolphin', 'cmd', 'api.py')
    command = 'python3 ' + api_path + ' --config-file ' + conf_file  + ' &'
    os.system(command)
    #subprocess.call(['python3', api_path, '--config-file', conf_file], shell=True)
    logger.info("process_started")
    
    
def install_sim():
    python_setup_comm = ['build', 'install'] 
    req_logs = os.path.join(sim_log_dir, 'requirements.log')
    command='pip3 install -r requirements.txt >' + req_logs+ ' 2>&1'
    os.system(command)
    
    setup_file=os.path.join(sim_source_path, 'setup.py')
    for command in python_setup_comm:
        try:
            command = 'python3 ' + setup_file + ' ' + command + ' >>' + logfile
            os.system(command)
        except CalledProcessError as cpe:
            logger.error("Got CPE error [%s]:[%s]" % (cpe, tb.print_exc()))
            return

def main():
    init()
    global sim_source_path
    cwd = os.getcwd()
    logger.info("Current dir is %s" % (cwd))
    sim_source_path = os.path.join(cwd, ".." )
    logger.info("sims [%s]" % (sim_source_path))
    os.chdir(sim_source_path)
    logger.info(os.getcwd())

    # create required directories
    create_dirs()

    # Copy required files
    copy_req_files()

    # install
    install_sim()

    # create db
    create_sim_db()

    # start
    start_api()
if __name__ == "__main__":
    main()
