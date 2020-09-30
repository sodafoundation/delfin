# Introduction
This is a standalone/non-containerized installer for SODA Infrastructure Manager (delfin) project.
It contains a script and options to check the environment feasible for installing delfin. Installs required dependent software/binaries.

# Prerequisite
Python3 and Pip3 should be installed on the system.
Ensure the logged-in user has root privileges.

Note: If you don't have python3 in your system, you may follow below steps to setup python3 virtual environment.

##### How to setup python3 virtual environment and delfin project

1. Install python-virtual environment package

  ```sh
  apt-get install python-virtualenv
  ```
2. Clone delfin repo

  ```sh
  git clone https://github.com/sodafoundation/delfin.git

  # Example
  root@root1:~/delfin-demo$ git clone https://github.com/sodafoundation/delfin.git

  root@root1:~/delfin-demo$ cd delfin
  ```

3. Create a project, using python3
  ```sh
  virtualenv -p /usr/bin/python3.6 project_delfin

  # Example
  root@root1:~/delfin-demo/delfin$ virtualenv -p /usr/bin/python3.6 project_delfin
  ```
4. Activate your project

  ```sh
  source project_delfin/bin/activate

  # Example
  root@root1:~/delfin-demo/delfin$ source project_delfin/bin/activate
  # (project_delfin) root@root1:~/delfin-demo/delfin$
  ```
5. Install all requirements using Pip

  ```sh
  pip install -r requirements.txt

  # Example
  (project_delfin) root@root1:~/delfin-demo/delfin$ pip install -r requirements.txt
  ```
6. set PYTHONPATH to working directory

  ```sh
  export PYTHONPATH=$(pwd)
  ```
  

#### How to setup prometheus to monitor performance metric

  Follow the below steps to setup delfin with prometheus. Once your setup is ready, you can register the storage devices for performance monitoring. Later, the performance metrics can be viewed on prometheus server. This example also guides you to configure and update the targets and interval for scraping the metrics.

  Alternatively, you can also watch this [video]((https://drive.google.com/file/d/1WMmLXQeNlToZd0DP5hCFtDZ1IbNJpO6B/view?usp=drivesdk) for more detail.


  step1: Install and start prometheus server

  1. [Download the latest binaries from here](https://prometheus.io/download/) and run the below steps.


    1. tar xvfz prometheus-*.tar.gz

    2. cd prometheus-*

    3. ./prometheus

  Example:
  ```sh
  root@root:/prometheus/prometheus-2.20.0.linux-amd64$ ./prometheus
  ```

  2. Edit the prometheus.yml and set the appropriate target, interval and metrics_api path. Below is sample example of prometheus.yml

   ###### prometheus.yml

    global:
      scrape_interval: 900s
    scrape_configs:
     - job_name: delfin-prometheus
     metrics_path: /metrics
     static_configs:
      - targets:
              - localhost:8195

# Supported OS
Ubuntu 16.04, Ubuntu 18.04

# Logs
All the installer logs are stored in the /var/log/sodafoundation directory.
The logs can be uniquely identified based upon the timestamp.

# Structure of the installer
This installer comes with options of pre-check, install and uninstall
pre-check: This script checks for the components required by delfin to function. If they are not present, precheck will install them.
Install: Installs and starts the delfin process
Uninstall: Uninstalls the delfin. Doesn't uninstall the required components. You may need to uninstall it explicitly using the native approach.

# How to install
To get help, execute 'install -h'. It will show help information

Install script can be executed with three different switches to:
- either do a pre-check [./install -p]
- only run the installer without doing pre-check (if pre-check has been executed explicitly) [./install -s]
- execute pre-check as well the install [./install]

## For the available options for install, you can execute 'install -h'
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

## For Pre-check, run below command
  ```sh
  installer/install -p

  # Example

  root@root1:~/delfin-demo/delfin$ installer/install -p
                              OR
  root@root1:~/delfin-demo/delfin/installer$ ./install --precheck
  ```

## Install without pre-check
```sh
installer/install -s

# Example

root@root1:~/delfin-demo/delfin$ installer/install -s
```

## Execute both pre-check as well as install
```sh
installer/install

# Example
root@root1:~/delfin-demo/delfin$ installer/install
```

# Uninstall
Running the uninstall script will stop all delfin processes and do cleanup
    
    installer/uninstall
    
    # Example
    root@root1:~/delfin-demo/delfin$ installer/uninstall


# Test the running delfin setup
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
        "vendor": "fake_storage",
        "model": "fake_driver",
        "rest": {
        "host": "127.0.0.1",
        "port": 8088,
        "username": "admin",
        "password": "pass"
        },
        "extra_attributes": {
            "array_id": "12345"
        }
       }

    ```
3. Run the GET API to get the registered storages. 
    
    GET http://localhost:8190/v1/storages
    
    use storage_id for registering storage for performance collection or alert monitoring

4. Register storage for performance collection

   PUT http://localhost:8190/v1/storages/<storage_id>/metrics-config

   body :
      ```
      {
    "array_polling": {
    "perf_collection": true,
    "interval": 900,
    "is_historic": true
    }
    }
      ```
5. Monitor the performance metrics on prometheus server at default location

   http://localhost:9090/graph
