# Driver Development Guide


Delfin is an Infrastructure Management framework under SODA foundation projects for Heterogeneous storage backends (cloud-enabled, offline-storage, etc.) for management, status collection, telemetry and alerting.

## Goals

  - Enable third parties to integrate a new backend to SODA Delfin framework
  - Collect the steps needed to integrate a new backend to SODA Delfin framework
  - Details the interfaces that new backend driver needs to be implemented

## Motivation and background

Delfin is an Infrastructure Management framework developed in Python programming language. It provides a Python plugin interface for adding third party drivers thereby supporting third party backends. The third party driver needs to implement the interfaces defined in the Driver python class, for the framework to use the third party driver. Once drivers implement the interfaces with the details of backend storage, delfin can manage the backend.

## Non-Goals

  - Support backend specific implementation details 
  - Explain internal or higher level framework specific details

## Third party driver integration

SODA Delfin project already contains some [drivers](https://github.com/sodafoundation/delfin/tree/master/delfin/drivers), which can be used as reference by the new third party driver developers.

Existing Delfin Drivers for reference:
  - fake_driver - This is a dummy/sample driver used for testing purpose
  - Huawei - This driver implements Huawei's OeanStor backend
  - VMAX - This driver implements Dell EMC's VMAX storage backend

### Code changes needed

* Add driver plugin 'entry points' to the file 'setup.py'.

* Create driver source code folder under <delfin path>/delfin/drivers/

* Extend base class StorageDriver defined in <delfin path>/delfin/drivers/driver.py, to implement a new driver.

* Implement all the interfaces defined in <delfin path>/delfin/drivers/driver.py, in the new driver.

* Ensure create storages API call from Delfin, can load the driver successfully.

* Ensure APIs of list_*() and alert*() works as expected.

* Raise PR with test reports to Delfin repository.

### How it works

Third party drivers are located and loaded into Delfin, when the create storage API (POST request) is invoked for that backend.

Create Storages POST API contains a request body model namely access_info, which contains fields ‘vendor’ & ‘model’. These fields are used to match and identify the driver from the ‘entry_points’ registered by the driver. Delfin loads this matched driver and registers the driver for the created backend. Any further API calls on this backend will use this newly loaded driver.

Delfin class Driver Manager internally utilizes the Python module ‘stevedore’ for the loading of driver plugins.

## Conclusion

Pluggable design of Driver Manager makes it easy to add third party drivers expanding infrastructure management capabilities of SODA Delfin to multiple storage backends.


