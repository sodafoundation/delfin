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
set -e

case "$1" in
  api)
    # Register database schema..
    python3 script/create_db.py --config-file /etc/delfin/delfin.conf
    # Run API Server
    exec python3 delfin/cmd/api.py --config-file /etc/delfin/delfin.conf
    ;;
  task)
    exec python3 delfin/cmd/task.py --config-file /etc/delfin/delfin.conf
    ;;
  alert)
    exec python3 delfin/cmd/alert.py --config-file /etc/delfin/delfin.conf
    ;;
  exporter)
    exec python3 delfin/exporter/prometheus/exporter_server.py --config-file /etc/delfin/delfin.conf
    ;;
  *)
    echo "Usage: $0 {api|task|alert|exporter}" >&2
    exit 1
    ;;
esac
