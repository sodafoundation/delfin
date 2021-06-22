*** Settings ***
Documentation    Tests to verify that Delete of storage

Library                 RequestsLibrary
Library                 Collections
Library                 JSONLibrary

*** Variables ***
${delfin_url}           http://localhost:8190/v1

*** Test Cases ***

Delete Storage with valid storage_id
    [Tags]    DELFIN
    Sleep                   5s
    ${storage_id_test}=     Register Test Storage
    Create Session          delfin      ${delfin_url}
    ${resp_del}=            DELETE On Session    delfin     storages/${storage_id_test}
    Status Should Be        202         ${resp_del}

Delete Storage with in-valid storage_id
    [Tags]    DELFIN
    Create Session          delfin      ${delfin_url}
    ${resp_del2}=           DELETE On Session    delfin     storages/111  404
    ${error_code}=         Get Value From Json   ${resp_del2.json()}  $..error_code
    dictionary should contain value   ${resp_del2.json()}   StorageNotFound

*** Keywords ***
Register Test Storage
    ${test}=                 Load Json From File   ${CURDIR}/test.json
    ${access_info}=          Get Value From Json   ${test}   $.test_register_access_info

    Create Session          delfin      ${delfin_url}
    ${resp_register}=       POST On Session     delfin     storages    json=${access_info[0]}
    Status Should Be                            201    ${resp_register}
    Dictionary Should Contain Key               ${resp_register.json()}     id
    ${storage_id}=          Get Value From Json	     ${resp_register.json()} 	 $..id
    [Return]                ${storage_id[0]}
