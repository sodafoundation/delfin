*** Settings ***
Documentation    Tests to verify that registration of storage succeed
...              and fail correctly depending on the access_info
...              input provided.
...              Delfin needs to be installed and APIs are accessble.

Library                 RequestsLibrary
Library                 Collections
Library                 JSONLibrary
Library                 OperatingSystem

*** Variables ***
${delfin_url}           http://localhost:8190/v1

*** Test Cases ***
Register Storage with in-valid access_info Test
    [Tags]    DELFIN

    Create Session          delfin      ${delfin_url}

    ${ref_input}=           Load Json From File   ${CURDIR}/test.json
    ${ref_access_info}=     Get Value From Json   ${ref_input}   $.test_register_access_info

    # Invalid ip
    ${access_info}=         Copy Dictionary       ${ref_access_info[0]}   Deepcopy=True
    Set To Dictionary       ${access_info['rest']}       host=10.10.10.123

    ${resp_register}=       POST On Session     delfin     storages    json=${access_info}   expected_status=any
    Status Should Be        400    ${resp_register}
    dictionary should contain value   ${resp_register.json()}   InvalidIpOrPort

    # Invalid port
    ${access_info}=         Copy Dictionary       ${ref_access_info[0]}   Deepcopy=True
    Set To Dictionary       ${access_info['rest']}       port=${80}

    ${resp_register}=       POST On Session     delfin     storages    json=${access_info}   expected_status=any
    Status Should Be        400    ${resp_register}
    dictionary should contain value   ${resp_register.json()}   InvalidIpOrPort

    # Invalid username
    ${access_info}=         Copy Dictionary       ${ref_access_info[0]}   Deepcopy=True
    Set To Dictionary       ${access_info['rest']}       username=user

    ${resp_register}=       POST On Session     delfin     storages    json=${access_info}   expected_status=any
    Status Should Be        400    ${resp_register}
    dictionary should contain value   ${resp_register.json()}   InvalidUsernameOrPassword

    # Invalid Password
    ${access_info}=         Copy Dictionary       ${ref_access_info[0]}   Deepcopy=True
    Set To Dictionary       ${access_info['rest']}       password=pass

    ${resp_register}=       POST On Session     delfin     storages    json=${access_info}   expected_status=any
    Status Should Be        400    ${resp_register}
    dictionary should contain value   ${resp_register.json()}   InvalidUsernameOrPassword


Register Storage with valid access_info Test
    [Tags]    DELFIN
    # Read storage backend details from JSON file
    ${ref_storage}=         Load Json From File   ${CURDIR}/testdriver/storage.json
    ${ref_device}=          Get Value From Json   ${ref_storage}   $..storage

    ${storage_test}=        Register Test Storage
    Dictionary Should Contain Sub Dictionary        ${storage_test}     ${ref_device[0]}
    Delete Storage With ID  ${storage_test["id"]}

Register Storage with same access_info Test
    [Tags]    DELFIN
    Sleep                   1s
    ${storage_test}=        Register Test Storage

    ${test}=                Load Json From File   ${CURDIR}/test.json
    ${access_info}=         Get Value From Json   ${test}   $.test_register_access_info
    Create Session          delfin      ${delfin_url}
    ${resp_register}=       POST On Session     delfin     storages    json=${access_info[0]}   expected_status=any
    Status Should Be        400    ${resp_register}
    dictionary should contain value   ${resp_register.json()}   StorageAlreadyExists

    Delete Storage With ID      ${storage_test["id"]}

*** Keywords ***
Register Test Storage
    ${test}=                Load Json From File   ${CURDIR}/test.json
    ${access_info}=         Get Value From Json   ${test}   $.test_register_access_info

    Create Session          delfin      ${delfin_url}
    ${resp_register}=       POST On Session     delfin     storages    json=${access_info[0]}
    Status Should Be        201    ${resp_register}
    [Return]                ${resp_register.json()}

Delete Storage With ID
    [Arguments]             ${storage_id}
    Create Session          delfin      ${delfin_url}
    ${resp_del}=            DELETE On Session    delfin     storages/${storage_id}
    Status Should Be        202    ${resp_del}
