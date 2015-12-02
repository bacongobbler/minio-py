# -*- coding: utf-8 -*-
# Minio Python Library for Amazon S3 Compatible Cloud Storage, (C) 2015 Minio, Inc.
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
minio.error
~~~~~~~~~~~~~~~~~~~

This module provides custom exception classes for Minio library and API specific errors.
"""

class InvalidEndpointError(Exception):
    """
    InvalidEndpointError is raised when input endpoint URL is invalid.
    """
    def __init__(self, message, **kwargs):
        self.message = message
        super(InvalidEndpointError, self).__init__(**kwargs)

    def __str__(self):
        string_format = 'InvalidEndpointError: message: {0}'
        return string_format.format(self.message)

class InvalidBucketError(Exception):
    """
    InvalidBucketError is raised when input bucket name is invalid.

    NOTE: Bucket names are validated based on Amazon S3 requirements.
    """
    def __init__(self, message, **kwargs):
        self.message = message
        super(InvalidBucketError, self).__init__(**kwargs)

    def __str__(self):
        string_format = 'InvalidBucketError: message: {0}'
        return string_format.format(self.message)

class InvalidArgumentError(Exception):
    """
    InvalidArgumentError is raised when an unexpected
    argument is received by the callee.
    """
    def __init__(self, message, **kwargs):
        self.message = message
        super(InvalidArgumentError, self).__init__(**kwargs)

    def __str__(self):
        string_format = 'InvalidArgumentError: message: {0}'
        return string_format.format(self.message)

class ResponseError(Exception):
    """
    ResponseError is raised when an API call doesn't succeed.
    To indicate a successful status each API verifies 2xx, 3xx
    and raises :class:`ResponseError <ResponseError>` accordingly.

    :param code: Response code usually a string and Amazon S3 API specific.
    :param message: Human readable message explanation of the Response code.
    :param request_id: X-Amz-Request-Id value sent by the S3 server.
    :param host_id: X-Amz-Host-Id value sent by the S3 server.
    :param resource: Server resource on which the error was generated for.
    """
    def __init__(self, code, message, request_id, host_id, resource, xml=None,
                 **kwargs):
        super(ResponseError, self).__init__(**kwargs)
        self.code = code
        self.message = message
        self.request_id = request_id
        self.host_id = host_id
        self.resource = resource
        self.xml = xml

    def __str__(self):
        return 'ResponseError: code: {0}, message: {1}, request_id: {2},' \
            'host_id: {3}, resource: {4}, xml: {5}'.format(self.code,
                                                           self.message,
                                                           self.request_id,
                                                           self.host_id,
                                                           self.resource,
                                                           self.xml)
