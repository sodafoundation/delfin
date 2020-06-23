# Copyright 2020 The SODA Authors.
# Copyright (C) 2017 NTT DATA
# All Rights Reserved.
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

"""
Request Body validating middleware.

"""

import functools

from delfin.api.validation import validators


def schema(request_body_schema):
    """Register a schema to validate request body.

    Registered schema will be used for validating request body just before
    API method executing.

    :param dict request_body_schema: a schema to validate request body.

    """

    def add_validator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            schema_validator = validators._SchemaValidator(request_body_schema)
            schema_validator.validate(kwargs['body'])
            return func(*args, **kwargs)
        return wrapper

    return add_validator
