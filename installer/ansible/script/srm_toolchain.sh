#!/usr/bin/env bash

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


uninstall(){
    echo "Entered uninstall"
    if [ "docker" == "$1" ]
    then
        echo "Entered if condition"
        docker stop monitoring_prometheus
        docker rm monitoring_prometheus
        docker stop monitoring_alertmanager
        docker rm monitoring_alertmanager
        docker stop monitoring_grafana
        docker rm monitoring_grafana
        docker ps -a | grep prometheus
    fi
    
}