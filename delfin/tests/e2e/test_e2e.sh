#!/bin/bash
# Copyright 2021 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

TOP_DIR=$(cd $(dirname "$0") && pwd)
DELFIN_DIR=$(cd $TOP_DIR/../../.. && pwd)

cd $DELFIN_DIR

ps -ef | grep 'cmd/api.py' | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep 'cmd/task.py' | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep 'cmd/alert.py' | grep -v grep | awk '{print $2}' | xargs kill -9
ps -ef | grep 'exporter_server.py' | grep -v grep | awk '{print $2}' | xargs kill -9

# Update setup.py to inject test driver
cp setup.py setup.py.orig

str="\ \ \ \ \ \ \ \ \ \ \ \ 'test_vendor test_model = delfin.tests.e2e.testdriver:TestDriver',"
sed -i "/FakeStorageDriver',/ a $str" $DELFIN_DIR/setup.py

installer/install

source installer/delfin/bin/activate
pip install robotframework
pip install robotframework-requests
pip install robotframework-jsonlibrary

ORIG_PATH='"storage.json"'
FILE_PATH="${TOP_DIR}/testdriver/storage.json"
sed -i "s|${ORIG_PATH}|\"${FILE_PATH}\"|g" $TOP_DIR/test.json

sleep 10

robot delfin/tests/e2e

deactivate

mv setup.py.orig  setup.py
echo "Test completed successfully ..."
