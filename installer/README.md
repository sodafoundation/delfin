# Introduction
This is a standalone/non-containerized installer for SODA Infrastructure Management (SIM) project.
It contains script and options to check the environment feasible for installing SIM. Installs required dependent software/binaries.

# Pre-requisite
Python3 and Pip3 should be installed on the system.
Ensure the logged-in user has root privileges

# Supported OS
Ubuntu 16.04, Ubuntu 18.04

# Logs
All the installer logs are stored in /var/log/sodafoundation directory.
The logs can be uniquely identified based upon the timestamp.

# Strucute of the installer
This installer comes with options of pre-check, install and uninstall
pre-check: This script checks for the components required by SIM to function. If they are not present, precheck will install them.
Install: Installs and starts the SIM process
Uninstall: Uninstalls the SIM. Doesn't uninstalls the required components. You may need to uninstall it explicitly using the native approach.

# How to install
To get help, execute 'install -h'. It will show help information

Install script can be executed with three different switches to:
- either do a pre-check [./install -p]
- only run the installer without doing pre-check (if pre-check has been executed explicitly) [./install -s]
- execute pre-check as well the install [./install]

## For the available options for install, you can execute 'install -h'
```
<path to installer/instatll script>/install -h
$ pwd
/root/gopath/src/github.com/sodafoundation/SIM
$ installer/install -h
age install [--help|--precheck|--skip_precheck]
Usage:
    install [-h|--help]
    install [-p|--precheck]
    install [-s|--skip_precheck]
Flags:
    -h, --help Print the usage of install
    -p, --precheck Only perform system software requirements for installation
    -s, --skip_precheck If precheck is not required and directly install
```

## Pre-check
```
<path to installer/install script>/install -p
Ex:
$ pwd
/root/gopath/src/github.com/sodafoundation/SIM
$ installer/install -p

OR

$ pwd
/root/gopath/src/github.com/sodafoundation/SIM/installer
$ ./install -p

```

## Install without pre-check
```
<path to installer/install script>/install -s
Ex:
$ pwd
/root/gopath/src/github.com/sodafoundation/SIM
$ installer/install -s

OR

$ pwd
/root/gopath/src/github.com/sodafoundation/SIM/installer
$ ./install -s

```

## Execute both pre-check as well as install
```
<path to installer/install script>/install
Ex:
$ pwd
/root/gopath/src/github.com/sodafoundation/SIM
$ installer/install

OR

$ pwd
/root/gopath/src/github.com/sodafoundation/SIM/installer
$ ./install

```

# Uninstall
Running the uninstall script will stop all SIM processes and do cleanup
```
<path to installer/install script>/uninstall.sh
Ex:
$ pwd
/root/gopath/src/github.com/sodafoundation/SIM
$ installer/uninstall

