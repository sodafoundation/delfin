# Copyright 2020 The SODA Authors.
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

FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev && \
    apt-get install -y sqlite3 && \
    apt-get install -y libffi-dev

ADD . /SIM
WORKDIR /SIM

RUN mkdir -p /var/log/SIM
RUN mkdir -p /var/lib/dolphin/

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY etc/dolphin/api-paste.ini /etc/dolphin/api-paste.ini
COPY etc/dolphin/dolphin.conf /etc/dolphin/dolphin.conf

COPY script/start.sh start.sh

CMD ./start.sh
