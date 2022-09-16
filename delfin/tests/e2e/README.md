# Introduction
This folder contains end to end, automated, testing scripts for Delfin.

These tests are using [Robot Framework](https://robotframework.org/) for automation and report generation.

The end-to-end tests are run against a test driver provided in the path `delfin/tests/e2e/testdriver`.
This test driver uses, included storage details in file `delfin/tests/e2e/testdriver/storage.json` for storage simulation when testing.

# Supported OS version
Ubuntu 16.04, Ubuntu 18.04, Ubuntu 22.04

# Prerequisite
Prerequisite for [standalone installer](https://github.com/sodafoundation/delfin/blob/master/installer/README.md) is applicable here too.

Install python 3.6+ and pip.

Export PYTHONPATH as below

```bash
export PYTHONPATH=$(pwd)
```
# Run tests
The end-to-end tests can be run from command prompt as below

```bash
git clone https://github.com/sodafoundation/delfin.git && cd delfin
./delfin/tests/e2e/test_e2e.sh
```
The above script injects test driver into delfin, builds and installs delfin using delfin standalone installer.
It runs robot framework scripts against the running delfin application for verifying delfin APIs.

When the script finish execution, robot framework generates the test execution summary and log.
These are available in the delfin root directory, with names `report.html` and `log.html` respectively.