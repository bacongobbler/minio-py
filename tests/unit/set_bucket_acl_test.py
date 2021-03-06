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

import mock

from nose.tools import raises
from unittest import TestCase

from minio import Minio
from minio.api import _DEFAULT_USER_AGENT
from minio.error import InvalidBucketError
from minio.bucket_acl import Acl

from .minio_mocks import MockResponse, MockConnection

class SetBucketAclTest(TestCase):
    @raises(TypeError)
    def test_bucket_is_string(self):
        client = Minio('localhost:9000')
        client.set_bucket_acl(1234, Acl.private())

    @raises(InvalidBucketError)
    def test_bucket_is_not_empty_string(self):
        client = Minio('localhost:9000')
        client.set_bucket_acl('  \t \n  ', Acl.private())

    @raises(InvalidBucketError)
    def test_set_bucket_acl_invalid_name(self):
        client = Minio('localhost:9000')
        client.set_bucket_acl('ABCD', Acl.private())

    @mock.patch('urllib3.PoolManager')
    def test_set_bucket_acl_works(self, mock_connection):
        mock_server = MockConnection()
        mock_connection.return_value = mock_server
        mock_server.mock_add_request(MockResponse('PUT',
                                                  'https://localhost:9000/hello/?acl',
                                                  {'x-amz-acl': 'private',
                                                   'User-Agent':  _DEFAULT_USER_AGENT}, 200))
        client = Minio('localhost:9000')
        client.set_bucket_acl('hello', Acl.private())
