*** Settings ***
Documentation    Tests to verify that GET of storages

Library                 RequestsLibrary
Library                 Collections
Library                 JSONLibrary
Library                 OperatingSystem

*** Variables ***
${delfin_url}           http://localhost:8190/v1

*** Test Cases ***
GET all Storages when no storages are registered
    [Tags]    DELFIN

    ${storages}=            Get All Storages
    Should Be Empty         ${storages}

GET all Storages when two storages are registered
    [Tags]    DELFIN

    ${storage_id_test}=          Register Test Storage
    ${storage_id_fake}=          Register Fake Storage

    # GET all storages
    ${storages}=            Get All Storages
    ${id_list}=    create list       ${storages[0]['id']}      ${storages[1]['id']}
    List should contain value  ${id_list}   ${storage_id_test}
    List should contain value  ${id_list}   ${storage_id_fake}

    Delete Storage With ID      ${storage_id_test}
    Delete Storage With ID      ${storage_id_fake}

GET Storage with a valid Storage ID
    [Tags]    DELFIN
    ${storage_id_test}=          Register Test Storage

    # GET all storages
    ${storage}=            Get Storage With ID     ${storage_id_test}
    ${id_list}=    create list       ${storage['id']}
    List should contain value  ${id_list}   ${storage_id_test}

    Delete Storage With ID      ${storage_id_test}

*** Keywords ***
Get All Storages
    Create Session          delfin      ${delfin_url}
    ${resp_get}=            GET On Session    delfin    storages
    Status Should Be        200         ${resp_get}
    ${resp_get_storage}=    Get Value From Json	        ${resp_get.json()}      $..storages
    [Return]                ${resp_get_storage[0]}

Get Storage With ID
    [Arguments]             ${storage_id}
    Create Session          delfin      ${delfin_url}
    ${resp_get}=            GET On Session    delfin    storages/${storage_id}
    Status Should Be        200    ${resp_get}
    [Return]                ${resp_get.json()}

Delete Storage With ID
    [Arguments]             ${storage_id}
    Create Session          delfin      ${delfin_url}
    ${resp_del}=            DELETE On Session    delfin     storages/${storage_id}
    Status Should Be        202    ${resp_del}
    Sleep                   5s

Register Test Storage
    ${test}=                 Load Json From File   ${CURDIR}/test.json
    ${access_info}=          Get Value From Json   ${test}   $.test_register_access_info

    Create Session          delfin      ${delfin_url}
    ${resp_register}=       POST On Session     delfin     storages    json=${access_info[0]}
    Status Should Be                            201    ${resp_register}
    Dictionary Should Contain Key               ${resp_register.json()}     id
    ${storage_id}=          Get Value From Json	     ${resp_register.json()} 	 $..id
    [Return]                ${storage_id[0]}

Register Fake Storage
    ${fake_rest}=            Create dictionary  host=10.10.10.100  port=${8080}   username=admin  password=password
    ${access_info}=          Create dictionary  vendor=fake_storage  model=fake_driver  rest=${fake_rest}
    ${fake_device}=          Create dictionary  vendor=fake_vendor  model=fake_model

    Create Session           delfin      ${delfin_url}
    ${resp_register}=        POST On Session     delfin     storages    json=${access_info}
    ${storage_id}=           Get Value From Json	     ${resp_register.json()} 	 $..id
    Dictionary Should Contain Sub Dictionary             ${resp_register.json()}     ${fake_device}
    [Return]                ${storage_id[0]}
