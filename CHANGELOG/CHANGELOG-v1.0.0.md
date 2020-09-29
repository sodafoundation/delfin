# Changelog

## [v1.0.0](https://github.com/sodafoundation/delfin/tree/v1.0.0) (2020-09-29)

[Full Changelog](https://github.com/sodafoundation/delfin/compare/v0.8.0...v1.0.0)

**Merged pull requests:**

- Fixing config path to sync with ansible installer [\#346](https://github.com/sodafoundation/delfin/pull/346) ([PravinRanjan10](https://github.com/PravinRanjan10))
- Syncing dev branch to master [\#345](https://github.com/sodafoundation/delfin/pull/345) ([PravinRanjan10](https://github.com/PravinRanjan10))
- Standalone Installer script for delfin [\#342](https://github.com/sodafoundation/delfin/pull/342) ([PravinRanjan10](https://github.com/PravinRanjan10))
- Sync master to performance collection  dev branch [\#339](https://github.com/sodafoundation/delfin/pull/339) ([NajmudheenCT](https://github.com/NajmudheenCT))
- Updating Fake driver to sync with vmax model [\#338](https://github.com/sodafoundation/delfin/pull/338) ([PravinRanjan10](https://github.com/PravinRanjan10))

## [v0.8.0](https://github.com/sodafoundation/delfin/tree/v0.8.0) (2020-09-28)

[Full Changelog](https://github.com/sodafoundation/delfin/compare/v0.6.0...v0.8.0)

**Merged pull requests:**

-  Modifying some exception in VMAX and schema validation of ssh acces info [\#343](https://github.com/sodafoundation/delfin/pull/343) ([NajmudheenCT](https://github.com/NajmudheenCT))

## [v0.6.0](https://github.com/sodafoundation/delfin/tree/v0.6.0) (2020-09-21)

[Full Changelog](https://github.com/sodafoundation/delfin/compare/v0.6.1...v0.6.0)

**Merged pull requests:**

- Code improvements [\#335](https://github.com/sodafoundation/delfin/pull/335) ([sushanthakumar](https://github.com/sushanthakumar))
- Fix static code check tools function depth defect [\#331](https://github.com/sodafoundation/delfin/pull/331) ([joseph-v](https://github.com/joseph-v))
- Fix static code check tool defects [\#330](https://github.com/sodafoundation/delfin/pull/330) ([joseph-v](https://github.com/joseph-v))
- Fix VMAX establish rest session [\#324](https://github.com/sodafoundation/delfin/pull/324) ([joseph-v](https://github.com/joseph-v))
- Fix volume name in VMAX driver [\#323](https://github.com/sodafoundation/delfin/pull/323) ([joseph-v](https://github.com/joseph-v))
- Remove plain text password caching in drivers [\#322](https://github.com/sodafoundation/delfin/pull/322) ([joseph-v](https://github.com/joseph-v))
- Correct input argument of StorageBackendException in oceanstor [\#317](https://github.com/sodafoundation/delfin/pull/317) ([joseph-v](https://github.com/joseph-v))

## [v0.6.1](https://github.com/sodafoundation/delfin/tree/v0.6.1) (2020-09-21)

[Full Changelog](https://github.com/sodafoundation/delfin/compare/v0.4.0...v0.6.1)

**Fixed bugs:**

- sync\_status is always 'synced' in the reponse of a registration [\#241](https://github.com/sodafoundation/delfin/issues/241)
- \[task manager\] Sync call stuck when rabbit-mq server is not running [\#129](https://github.com/sodafoundation/delfin/issues/129)

**Closed issues:**

- Dell EMC VMAX volume name is different from Unisphere dashboard [\#332](https://github.com/sodafoundation/delfin/issues/332)
- Encrypt password before caching in drivers [\#329](https://github.com/sodafoundation/delfin/issues/329)

**Merged pull requests:**

- Performance metric-config-update API for delfin [\#333](https://github.com/sodafoundation/delfin/pull/333) ([PravinRanjan10](https://github.com/PravinRanjan10))
-  VMAX driver Performance collection: Initial framework and  array level for metrics collection    [\#326](https://github.com/sodafoundation/delfin/pull/326) ([NajmudheenCT](https://github.com/NajmudheenCT))
- Performance-collection framework for delfin [\#325](https://github.com/sodafoundation/delfin/pull/325) ([PravinRanjan10](https://github.com/PravinRanjan10))
- Query para driver changes for list alert api [\#319](https://github.com/sodafoundation/delfin/pull/319) ([sushanthakumar](https://github.com/sushanthakumar))
- Exception handling for delete snmp trap config [\#318](https://github.com/sodafoundation/delfin/pull/318) ([sushanthakumar](https://github.com/sushanthakumar))
- Alert sync api changes [\#316](https://github.com/sodafoundation/delfin/pull/316) ([sushanthakumar](https://github.com/sushanthakumar))
- Fix static code check defects [\#315](https://github.com/sodafoundation/delfin/pull/315) ([joseph-v](https://github.com/joseph-v))
- Fix warnings from static analyze tool [\#314](https://github.com/sodafoundation/delfin/pull/314) ([joseph-v](https://github.com/joseph-v))
- Query para update for list alert api [\#312](https://github.com/sodafoundation/delfin/pull/312) ([sushanthakumar](https://github.com/sushanthakumar))

## [v0.4.0](https://github.com/sodafoundation/delfin/tree/v0.4.0) (2020-08-28)

[Full Changelog](https://github.com/sodafoundation/delfin/compare/v0.2.0...v0.4.0)

**Implemented enhancements:**

- Need a mechanism to support SSL certificate verify for HTTPS request from driver to storage device. [\#227](https://github.com/sodafoundation/delfin/issues/227)

**Fixed bugs:**

- \[Driver\] Create extended exceptions for StorageBackendException [\#184](https://github.com/sodafoundation/delfin/issues/184)
- \[Alert Manager\] Irrelevant fields are shown as null in GET alert source  [\#172](https://github.com/sodafoundation/delfin/issues/172)
- \[VMAX driver\] Firmware version is missing [\#147](https://github.com/sodafoundation/delfin/issues/147)
- VMAX volume details for volumes without Storage Group [\#74](https://github.com/sodafoundation/delfin/issues/74)
- In api.py: Change function name discover\_storage to update\_storage\_driver [\#69](https://github.com/sodafoundation/delfin/issues/69)

**Closed issues:**

- \[Alert Manager\] Clear alert implementation for EMC Vmax [\#261](https://github.com/sodafoundation/delfin/issues/261)
- \[Alert Manager\] Clear alert implementation for Huawei Oceanstor [\#260](https://github.com/sodafoundation/delfin/issues/260)
- \[Alert Manager\] Clear alert analysis for storage backends  [\#259](https://github.com/sodafoundation/delfin/issues/259)
- \[Alert Manager\] Get alert analysis for storage backends [\#258](https://github.com/sodafoundation/delfin/issues/258)
- \[Alert Manager\] Alert specification check for other storage backends [\#249](https://github.com/sodafoundation/delfin/issues/249)
- \[Alert Manager\]Improve readability for alert model fields [\#239](https://github.com/sodafoundation/delfin/issues/239)
- Update Project ReadMe [\#231](https://github.com/sodafoundation/delfin/issues/231)
- Exporting alert model to export manager [\#126](https://github.com/sodafoundation/delfin/issues/126)
- \[Alert manager\] Load all custom mibs from configured path [\#114](https://github.com/sodafoundation/delfin/issues/114)
- \[Alert Manager\] Clear alert at backend [\#99](https://github.com/sodafoundation/delfin/issues/99)
- \[task manager\] Push resource data to Exporter [\#93](https://github.com/sodafoundation/delfin/issues/93)
- Handle the optimization issues in pool update [\#55](https://github.com/sodafoundation/delfin/issues/55)
- Handle multi node use cases in Driver Manager [\#50](https://github.com/sodafoundation/delfin/issues/50)
- Not correct behaviour of log info message [\#46](https://github.com/sodafoundation/delfin/issues/46)

**Merged pull requests:**

- Clear alert fix in hpe 3par driver [\#309](https://github.com/sodafoundation/delfin/pull/309) ([sushanthakumar](https://github.com/sushanthakumar))
- Alert source configuration range changes [\#308](https://github.com/sodafoundation/delfin/pull/308) ([sushanthakumar](https://github.com/sushanthakumar))
- Hpe3par: update SSL certificate verification method [\#307](https://github.com/sodafoundation/delfin/pull/307) ([jiangyutan](https://github.com/jiangyutan))
- Send clear event when snmp validation succeed [\#305](https://github.com/sodafoundation/delfin/pull/305) ([wisererik](https://github.com/wisererik))
- update next release version in setup.py [\#304](https://github.com/sodafoundation/delfin/pull/304) ([NajmudheenCT](https://github.com/NajmudheenCT))
- Adding Configurable VMAX expiration time [\#303](https://github.com/sodafoundation/delfin/pull/303) ([PravinRanjan10](https://github.com/PravinRanjan10))
- Hpe3par:separate the common parts of rest and SSH interfaces [\#302](https://github.com/sodafoundation/delfin/pull/302) ([jiangyutan](https://github.com/jiangyutan))
- Updated delfin changes [\#299](https://github.com/sodafoundation/delfin/pull/299) ([sushanthakumar](https://github.com/sushanthakumar))
- List and clear alert changes for unisphere alerts [\#298](https://github.com/sodafoundation/delfin/pull/298) ([sushanthakumar](https://github.com/sushanthakumar))
- Optimizing vmax driver exception related code. [\#297](https://github.com/sodafoundation/delfin/pull/297) ([PravinRanjan10](https://github.com/PravinRanjan10))
-  Fetching Default SRP for volumes which are not associated with storage group [\#296](https://github.com/sodafoundation/delfin/pull/296) ([NajmudheenCT](https://github.com/NajmudheenCT))
- Hpe3par:modify traps;modify checkhealth's components [\#295](https://github.com/sodafoundation/delfin/pull/295) ([jiangyutan](https://github.com/jiangyutan))
- Add Secure backend driver and dynamic certificate reload [\#290](https://github.com/sodafoundation/delfin/pull/290) ([joseph-v](https://github.com/joseph-v))
- Remove debug infomation and Fix some grammar problems [\#289](https://github.com/sodafoundation/delfin/pull/289) ([jiangyutan](https://github.com/jiangyutan))
- Oceanstor driver return fix for clear alert [\#283](https://github.com/sodafoundation/delfin/pull/283) ([sushanthakumar](https://github.com/sushanthakumar))
- Handle invalid input while getting array details for VMAX driver [\#282](https://github.com/sodafoundation/delfin/pull/282) ([joseph-v](https://github.com/joseph-v))
-  Adding name and firmware version for VMAX [\#277](https://github.com/sodafoundation/delfin/pull/277) ([NajmudheenCT](https://github.com/NajmudheenCT))
- Fix oceanstor driver issue [\#276](https://github.com/sodafoundation/delfin/pull/276) ([wisererik](https://github.com/wisererik))
- hpe-3par driver support [\#274](https://github.com/sodafoundation/delfin/pull/274) ([jiangyutan](https://github.com/jiangyutan))

## [v0.2.0](https://github.com/sodafoundation/delfin/tree/v0.2.0) (2020-08-11)

[Full Changelog](https://github.com/sodafoundation/delfin/compare/v0.1.0...v0.2.0)

**Implemented enhancements:**

- Remove example code because it will not be used [\#86](https://github.com/sodafoundation/delfin/issues/86)

**Closed issues:**

- Need to support SSH connection between delfin and devices. [\#245](https://github.com/sodafoundation/delfin/issues/245)
- \[Alert Manager\] Alert model filling for Huawei OceanStor [\#195](https://github.com/sodafoundation/delfin/issues/195)

**Merged pull requests:**

- Update event type for alert model [\#273](https://github.com/sodafoundation/delfin/pull/273) ([wisererik](https://github.com/wisererik))
- Custom mib path enhancement [\#271](https://github.com/sodafoundation/delfin/pull/271) ([sushanthakumar](https://github.com/sushanthakumar))
- Alert source update with snmp validation [\#270](https://github.com/sodafoundation/delfin/pull/270) ([sushanthakumar](https://github.com/sushanthakumar))
- Update VMax driver to remove PyU4V lib [\#268](https://github.com/sodafoundation/delfin/pull/268) ([joseph-v](https://github.com/joseph-v))
- Adding raw\_capacity and subscribed capacity in  VMAX driver [\#267](https://github.com/sodafoundation/delfin/pull/267) ([NajmudheenCT](https://github.com/NajmudheenCT))
- Add configuration for exporter framework [\#266](https://github.com/sodafoundation/delfin/pull/266) ([wisererik](https://github.com/wisererik))
- Clear alert support [\#265](https://github.com/sodafoundation/delfin/pull/265) ([sushanthakumar](https://github.com/sushanthakumar))
- Alert model refine changes [\#264](https://github.com/sodafoundation/delfin/pull/264) ([sushanthakumar](https://github.com/sushanthakumar))
- Add raw capacity to database model [\#263](https://github.com/sodafoundation/delfin/pull/263) ([ThisIsClark](https://github.com/ThisIsClark))
- Modify the constant type of sync status [\#255](https://github.com/sodafoundation/delfin/pull/255) ([ThisIsClark](https://github.com/ThisIsClark))
-  swagger correction in mutiple APIS [\#253](https://github.com/sodafoundation/delfin/pull/253) ([NajmudheenCT](https://github.com/NajmudheenCT))
- Update access\_info model to support both REST and SSH. [\#246](https://github.com/sodafoundation/delfin/pull/246) ([sfzeng](https://github.com/sfzeng))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
