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

*** Test Cases ***
Update with invalid access_info Test
    [Tags]    DELFIN
    @{storages}=            Get All Storages
    ${storage_id}=          Get Value From Json	    ${storages[0]} 	        $..id

    # Invalid access_info vendor and model
    ${access_info_rest}=    Create dictionary  host=10.10.10.10  port=${8080}   username=user_1  password=pass_1
    ${access_info}=         Create dictionary  vendor=test_vendor  model=test_model  rest=${access_info_rest}
    ${resp}=                Update Access Info      ${storage_id[0]}   ${access_info}
    Status Should Be        400         ${resp}
    dictionary should contain value     ${resp.json()}   InvalidInput

    # Invalid access_info, ip address
    ${access_info_rest}=    Create dictionary  host=100.10.10.10  port=${8080}   username=user_1  password=pass_1
    ${access_info}=         Create dictionary  rest=${access_info_rest}
    ${resp}=                Update Access Info      ${storage_id[0]}   ${access_info}
    Status Should Be        400         ${resp}
    dictionary should contain value     ${resp.json()}   InvalidIpOrPort

    # Invalid access_info, port
    ${access_info_rest}=    Create dictionary  host=10.10.10.10  port=${80}   username=user_1  password=pass_1
    ${access_info}=         Create dictionary  rest=${access_info_rest}
    ${resp}=                Update Access Info      ${storage_id[0]}   ${access_info}
    Status Should Be        400         ${resp}
    dictionary should contain value     ${resp.json()}   InvalidIpOrPort

    # Invalid access_info, username
    ${access_info_rest}=    Create dictionary  host=10.10.10.10  port=${8080}   username=user  password=pass_1
    ${access_info}=         Create dictionary  rest=${access_info_rest}
    ${resp}=                Update Access Info      ${storage_id[0]}   ${access_info}
    Status Should Be        400         ${resp}
    dictionary should contain value     ${resp.json()}   InvalidUsernameOrPassword

    # Invalid access_info, password
    ${access_info_rest}=    Create dictionary  host=10.10.10.10  port=${8080}   username=user_1  password=pass
    ${access_info}=         Create dictionary  rest=${access_info_rest}
    ${resp}=                Update Access Info      ${storage_id[0]}   ${access_info}
    Status Should Be        400         ${resp}
    dictionary should contain value     ${resp.json()}   InvalidUsernameOrPassword

    # Invalid storage_id
    ${access_info_rest}=    Create dictionary  host=10.10.10.10  port=${8080}   username=user_1  password=pass_1
    ${access_info}=         Create dictionary  rest=${access_info_rest}
    ${resp}=                Update Access Info      123   ${access_info}
    Status Should Be        404         ${resp}
    dictionary should contain value     ${resp.json()}   AccessInfoNotFound

Update with valid access_info Test
    [Tags]    DELFIN
    @{storages}=            Get All Storages
    ${storage_id}=          Get Value From Json	    ${storages[0]} 	        $..id

    # Valid access info and  storage_id
    ${access_info_rest}=    Create dictionary  host=10.10.10.10  port=${8080}   username=user_1  password=pass_1
    ${access_info}=         Create dictionary  rest=${access_info_rest}
    ${resp}=                Update Access Info      ${storage_id[0]}   ${access_info}
    Status Should Be        200         ${resp}
    dictionary should contain value     ${resp.json()}   test_vendor
    dictionary should contain value     ${resp.json()}   test_model
    dictionary should contain value     ${resp.json()}   ${storage_id[0]}

*** Keywords ***
Update Access Info
    [Arguments]             ${storage_id}   ${access_info}
    Create Session          delfin      ${delfin_url}
    ${resp_update}=         PUT On Session     delfin     storages/${storage_id}/access-info    json=${access_info}   expected_status=any
    [Return]                ${resp_update}

Register Test Storage
    ${test}=                 Load Json From File   ${CURDIR}/test.json
    ${access_info}=          Get Value From Json   ${test}   $.test_register_access_info

    Create Session          delfin      ${delfin_url}
    ${resp_register}=       POST On Session     delfin     storages    json=${access_info[0]}
    Status Should Be                            201    ${resp_register}
    Dictionary Should Contain Key               ${resp_register.json()}     id
    ${storage_id}=          Get Value From Json	     ${resp_register.json()} 	 $..id
    [Return]                ${storage_id[0]}

Delete Storage With ID
    [Arguments]             ${storage_id}
    Create Session          delfin      ${delfin_url}
    ${resp_del}=            DELETE On Session    delfin     storages/${storage_id}
    Status Should Be        202    ${resp_del}
    Sleep       5s


Get All Storages
    Create Session          delfin      ${delfin_url}
    ${resp_get}=            GET On Session    delfin    storages
    Status Should Be        200    ${resp_get}
    ${resp_get_storage}=    Get Value From Json	        ${resp_get.json()}      $..storages
    [Return]                ${resp_get_storage[0]}

Close Application
    @{storages}=            Get All Storages
    FOR     ${storage}      IN                      @{storages}
            ${storage_id}=  Get Value From Json	    ${storage} 	        $..id
            Delete Storage With ID                  ${storage_id[0]}
    END
    Sleep       5s

Open Application
    ${array_id}=            Register Test Storage
    Sleep       5s

