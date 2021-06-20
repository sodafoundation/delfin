*** Settings ***
Documentation    Tests to verify that GET of resources

Library                 RequestsLibrary
Library                 Collections
Library                 JSONLibrary
Library                 OperatingSystem

Suite Setup             Open Application
Suite Teardown          Close Application

*** Variables ***
${delfin_url}           http://localhost:8190/v1
${storage_pools}        storage-pools
@{res_urls}             storage-pools  volumes  controllers  disks  ports  quotas  qtrees  filesystems  shares
@{res_indx}             storage_pools  volumes  controllers  disks  ports  quotas  qtrees  filesystems  shares

*** Test Cases ***
GET Resources when test storage is registered
    [Tags]    DELFIN

    FOR     ${res_url}   ${res_ind}   IN ZIP    ${res_urls}   ${res_indx}
            ${ret_json}=            Get All Resource Of     ${res_url}
            ${res_s}=               Get Value From Json	    ${ret_json}         $..${res_ind}
            Should Not Be Empty     ${res_s[0]}
    END

GET Resources with ID
    [Tags]    DELFIN

    FOR     ${res_url}   ${res_ind}   IN ZIP    ${res_urls}   ${res_indx}
            ${ret_json}=            Get All Resource Of     ${res_url}
            ${res_s}=               Get Value From Json	    ${ret_json}         $..${res_ind}
            Should Not Be Empty     ${res_s[0]}
            ${resource_ids}         Get Value From Json	    ${ret_json}         $..id
            ${ret_json}=            Get All Resource with ID    ${res_url}     ${resource_ids[0]}
            Should Not Be Empty     ${res_s[0]}
    END

GET Resources with Filter
    [Tags]    DELFIN

    log to console          \n
    ${storages}=            Get All Storages
    ${storages_id}=         Get Value From Json	    ${storages[0]}         $..id

    FOR     ${res_url}   ${res_ind}   IN ZIP    ${res_urls}   ${res_indx}
            ${ret_json}=            Get All Resource with Filter     ${res_url}   storage_id=${storages_id[0]}
            ${res_s}=               Get Value From Json	    ${ret_json}         $..${res_ind}
            Should Not Be Empty     ${res_s[0]}
            ${ret_json}=            Get All Resource with Filter     ${res_url}   storage_id=123
            ${res_s}=               Get Value From Json	    ${ret_json}         $..${res_ind}
            Should Be Empty     ${res_s[0]}

    END

GET Resources when no storages are registered
    [Tags]    DELFIN
    Close Application
    FOR     ${res_url}   ${res_ind}   IN ZIP    ${res_urls}   ${res_indx}
            ${ret_json}=            Get All Resource Of     ${res_url}
            ${res_s}=               Get Value From Json	    ${ret_json}         $..${res_ind}
            Should Be Empty         ${res_s[0]}
    END
    Open Application

*** Keywords ***
Get All Resource Of
    [Arguments]             ${resource}
    Create Session          delfin          ${delfin_url}
    ${resp_get}=            GET On Session  delfin    ${resource}
    Status Should Be        200    ${resp_get}
    [Return]                ${resp_get.json()}

Get All Resource with ID
    [Arguments]             ${resource}     ${resource_id}
    Create Session          delfin          ${delfin_url}
    ${resp_get}=            GET On Session  delfin    ${resource}/${resource_id}
    Status Should Be        200    ${resp_get}
    [Return]                ${resp_get.json()}

Get All Resource with Filter
    [Arguments]             ${resource}     ${filter}
    Create Session          delfin          ${delfin_url}
    ${resp_get}=            GET On Session  delfin    ${resource}?${filter}
    Status Should Be        200    ${resp_get}
    [Return]                ${resp_get.json()}

Delete Storage With ID
    [Arguments]             ${storage_id}
    Create Session          delfin      ${delfin_url}
    ${resp_del}=            DELETE On Session    delfin     storages/${storage_id}
    Status Should Be        202    ${resp_del}

Register Test Storage
    ${test}=                 Load Json From File   ${CURDIR}/test.json
    ${access_info}=          Get Value From Json   ${test}   $.test_register_access_info

    Create Session          delfin      ${delfin_url}
    ${resp_register}=       POST On Session     delfin     storages    json=${access_info[0]}
    Status Should Be                            201    ${resp_register}
    Dictionary Should Contain Key               ${resp_register.json()}     id
    ${storage_id}=          Get Value From Json	     ${resp_register.json()} 	 $..id
    [Return]                ${storage_id[0]}

Get All Storages
    Create Session          delfin      ${delfin_url}
    ${resp_get}=            GET On Session    delfin    storages
    Status Should Be        200    ${resp_get}
    ${resp_get_storage}=    Get Value From Json	        ${resp_get.json()}      $..storages
    [Return]                ${resp_get_storage[0]}

Open Application
    ${array_id}=            Register Test Storage
    Sleep       1s

Close Application
    @{storages}=            Get All Storages
    FOR     ${storage}      IN                      @{storages}
            ${storage_id}=  Get Value From Json	    ${storage} 	        $..id
            Delete Storage With ID                  ${storage_id[0]}
    END
    Sleep       1s
