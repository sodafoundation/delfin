# Delfin Installation Guide

The SODA Delfin supports two types of installation
* Installation using Ansible
* Installation using Bash scripts

## Installation using Ansible

* Supported OS: **Ubuntu 20.04, Ubuntu 18.04**
* Prerequisite: **Python 3.6 or above** should be installed

### Install steps

Ensure no ansible & docker installed, OR Lastest ansible and docker tools are installed with versions listed below or later. If ansible & docker is not installed in the OS, script `install_dependencies.sh` will install it.

```bash
sudo apt-get update && sudo apt-get install -y git
git clone https://github.com/sodafoundation/delfin.git
# git checkout <delfin-release-version v1.6.1+>
cd delfin/installer
chmod +x install_dependencies.sh && source install_dependencies.sh
cd ansible
export PATH=$PATH:/home/$USER/.local/bin
sudo -E env "PATH=$PATH" ansible-playbook site.yml -i local.hosts -v
```

**NOTE:** *Tools version used for verification of Delfin under Ubuntu 20.04*
* ansible version: 5.10.0
* docker version: 20.10.21
* docker compose version: 2.12.2

### Uninstall
```bash
sudo -E env "PATH=$PATH" ansible-playbook clean.yml -i local.hosts -v
```


### Logs
Delfin processes execution logs can be found in /tmp/ folder
* /tmp/api.log
* /tmp/alert.log
* /tmp/task.log
* /tmp/exporter.log
* /tmp/create_db.log

### How to use Delfin
Delfin can be used either through dashboard or REST APIs.

Please refer [user guides](https://docs.sodafoundation.io/guides/user-guides/delfin/dashboard/)



## Installation using Bash Scripts
This is a standalone/non-containerized installer for SODA Infrastructure Manager (delfin) project.
It contains a script and options to check the environment feasible for installing delfin. Installs required dependent software/binaries.

* Supported OS: **Ubuntu 20.04, Ubuntu 18.04**
* Prerequisite:
  * **Python 3.6 or above** should be installed
  * Ensure the logged-in user has **root privileges**.

#### Installation steps
```bash
sudo -i
apt-get install python3 python3-pip
git clone https://github.com/sodafoundation/delfin.git && git checkout <delfin-release-version>
cd delfin
export PYTHONPATH=$(pwd)
./installer/install
```
Refer below for installer options

#### Uninstall
```bash
./installer/uninstall
```

- #### [Optional] Setup Prometheus (for monitor performance metric through prometheus)

  Follow the below steps to setup delfin with prometheus. Once your setup is ready, you can register the storage devices for performance monitoring. Later, the performance metrics can be viewed on prometheus server. This example also guides you to configure and update the targets and interval for scraping the metrics.

  Alternatively, you can also watch this [video](https://drive.google.com/file/d/1WMmLXQeNlToZd0DP5hCFtDZ1IbNJpO6B/view?usp=drivesdk) for more detail.

  [Download the latest binaries from here](https://prometheus.io/download/) and run the below steps.

     1. tar xvfz prometheus-*.tar.gz

     2. cd prometheus-*
     3. Edit the prometheus.yml and set the appropriate target, interval and metrics_api path. 
        Below is sample example of prometheus.yml
        ###### prometheus.yml
        ```
        global:
          scrape_interval: 10s
        scrape_configs:
          - job_name: delfin-prometheus
            metrics_path: /metrics
            static_configs:
              - targets:
                  - 'localhost:8195'
        ```
     4. ./prometheus
        
        Example:
        ```sh
         root@root:/prometheus/prometheus-2.20.0.linux-amd64$ ./prometheus
        ```
### Structure of the installer
This installer comes with options of pre-check, install and uninstall
pre-check: This script checks for the components required by delfin to function. If they are not present, precheck will install them.
Install: Installs and starts the delfin process
Uninstall: Uninstalls the delfin. Doesn't uninstall the required components. You may need to uninstall it explicitly using the native approach.

### How to install
To get help, execute 'install -h'. It will show help information

Install script can be executed with three different switches to:
- either do a pre-check [./install -p]
- only run the installer without doing pre-check (if pre-check has been executed explicitly) [./install -s]
- execute pre-check as well the install [./install]

#### For the available options for install, you can execute 'install -h'
```sh
 installer/install -h

 # Example
 root@root1:~/delfin-demo/delfin$ installer/install -h

 Usage install [--help|--precheck|--skip_precheck]
 Usage:
     install [-h|--help]
     install [-p|--precheck]
     install [-s|--skip_precheck]
 Flags:
     -h, --help Print the usage of install
     -p, --precheck Only perform system software requirements for installation
     -s, --skip_precheck If precheck is not required and directly install
```

#### For Pre-check, run below command
```sh
installer/install -p

# Example

root@root1:~/delfin-demo/delfin$ installer/install -p
                            OR
root@root1:~/delfin-demo/delfin/installer$ ./install --precheck
```

#### Install without pre-check
```sh
installer/install -s

# Example

root@root1:~/delfin-demo/delfin$ installer/install -s
```

#### Execute install with precheck
```sh
installer/install

# Example
root@root1:~/delfin-demo/delfin$ installer/install
```

#### Execute postcheck

#### Configure multiple instances of delfin components
Respective environment variable required to set for running multiple instances 
of delfin component before executing install command

```sh
$ export DELFIN_<<delfin component name>>_INSTANCES=<<number of instances>>
$ installer/install

# Example: Deploy delfin with 3 task and 2 alert instances 
  $ export DELFIN_TASK_INSTANCES=3
  $ export DELFIN_ALERT_INSTANCES=2
  $ installer/install
```

Note: Multiple instances of exporter and api is not allowed currently.

### Logs
All the installer logs are stored in the /var/log/soda directory.
The logs can be uniquely identified based upon the timestamp.


## Test the running delfin setup/process
  1. Make sure all delfin process are up and running
     ```
     ps -ef|grep delfin

     # Example
       root@root1:~/delfin-demo/delfin# ps -ef |grep delfin
       root       25856    3570  0 00:21 pts/0    00:00:04 python3 /root/delfin-demo/delfin/installer/../delfin/cmd/api.py --config-file /etc/delfin/delfin.conf
       root       25858    3570  0 00:21 pts/0    00:00:09 python3 /root/delfin-demo/delfin/installer/../delfin/cmd/task.py --config-file /etc/delfin/delfin.conf
       root       25860    3570  0 00:21 pts/0    00:00:06 python3 /root/delfin-demo/delfin/installer/../delfin/cmd/alert.py --config-file /etc/delfin/delfin.conf
       root       25862    3570  0 00:21 pts/0    00:00:00 python3 /root/delfin-demo/delfin/installer/../delfin/exporter/exporter_server.py --config-file /etc/delfin/delfin.conf

     ```

  2. Register storages

     POST http://localhost:8190/v1/storages

     body :
     ```
     {
        "vendor":"fake_storage",
        "model":"fake_driver",
        "rest":{
           "host":"127.0.0.1",
           "port":8088,
           "username":"admin",
           "password":"pass"
        },
        "extra_attributes":{
           "array_id":"12345"
        }
     }
     ```
  3. Run the GET API to get the registered storages. 
    
     GET http://localhost:8190/v1/storages
    
     use storage_id for registering storage for performance collection or alert monitoring

    
  4. [Optional] If prometheus is configured, monitor the performance metrics on prometheus server at default location

     http://localhost:9090/graph

## Limitation
Local installation, unlike Ansible installer, does not support SODA Dashboard integration.
