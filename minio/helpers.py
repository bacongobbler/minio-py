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
Helper functions
"""

import collections
import binascii
import hashlib
import re

from .compat import urlsplit, basestring, urlencode
from .error import InvalidBucketError, InvalidEndpointError

class PartMetadata(object):
    """
    Parts manager split parts metadata :class:`PartMetadata <PartMetadata>`.

    :param data: Part writer object backed by temporary file.
    :param md5digest: Md5sum digest of the part.
    :param sha256digest: Sha256sum digest of the part.
    :param size: Size of the part.
    """
    def __init__(self, data, md5digest, sha256digest, size):
        self.data = data
        self.md5digest = md5digest
        self.sha256digest = sha256digest
        self.size = size

def parts_manager(data, part_size=5*1024*1024):
    """
    Reads data and provides temporary files of a given size.

    :param data: Input reader object which needs to be saved.
    :param part_size: Individual part number defaults to 5MB.
    :return: Returns :class:`PartMetadata <PartMetadata>`
    """
    tmpdata = tempfile.NamedTemporaryFile(delete=True)
    md5hasher = hashlib.md5()
    sha256hasher = hashlib.sha256()
    total_read = 0
    while total_read < part_size:
        current_data = data.read(1024)
        if not current_data or len(current_data) == 0:
            break
        tmpdata.write(current_data)
        md5hasher.update(current_data)
        sha256hasher.update(current_data)
        total_read = total_read + len(current_data)

    return PartMetadata(tmpdata, md5hasher.digest(), sha256hasher.digest(), total_read)

def get_target_url(endpoint, bucket_name=None, object_name=None, query=None):
    """
    Construct final target url.

    :param endpoint: Target endpoint url where request is served to.
    :param bucket_name: Bucket component for the target url.
    :param object_name: Object component for the target url.
    :param query: Query parameters as a *dict* for the target url.
    :return: Returns final target url as *str*.
    """
    parsed_url = urlsplit(endpoint)
    url = None
    if bucket_name is None:
        url = parsed_url.scheme + '://' + parsed_url.netloc
    else:
        if 'amazonaws.com' in parsed_url.netloc:
            url = parsed_url.scheme + '://' + bucket_name + '.' + parsed_url.netloc
        else:
            url = parsed_url.scheme + '://' + parsed_url.netloc + '/' + bucket_name

    url_components = [url]
    url_components.append('/')

    if object_name is not None:
        object_name = encode_object_name(object_name)
    if object_name is not None:
        url_components.append(object_name)

    if query is not None:
        ordered_query = collections.OrderedDict(sorted(query.items()))
        query_components = []
        for component_key in ordered_query:
            single_component = [component_key]
            if ordered_query[component_key] is not None:
                single_component.append('=')
                single_component.append(
                    urlencode(str(ordered_query[component_key])).replace('/', '%2F'))
            query_components.append(''.join(single_component))

        query_string = '&'.join(query_components)
        if query_string:
            url_components.append('?')
            url_components.append(query_string)

    return ''.join(url_components)

def is_valid_endpoint(endpoint):
    """
    Verify if endpoint is valid.

    :type endpoint: string
    :param endpoint: An endpoint. Must have at least a scheme and a hostname.
    :return: True if the endpoint is valid. Raises *InvalidEndpointError* otherwise.
    """
    if not isinstance(endpoint, basestring):
        raise TypeError('endpoint')

    parts = urlsplit(endpoint)
    hostname = parts.hostname
    if hostname is None:
        raise InvalidEndpointError('endpoint')

    if len(hostname) > 255:
        raise InvalidEndpointError('endpoint')

    if hostname[-1] == '.':
        hostname = hostname[:-1]
    allowed = re.compile(
        "^((?!-)[A-Z\\d-]{1,63}(?<!-)\\.)*((?!-)[A-Z\\d-]{1,63}(?<!-))$",
        re.IGNORECASE)
    if not allowed.match(hostname):
        raise InvalidEndpointError('endpoint')

    if hostname.endswith('amazonaws.com') and (hostname != 's3.amazonaws.com'):
        raise InvalidEndpointError('endpoint')

    return True

def is_valid_bucket_name(bucket_name):
    """
    Check to see if the ``bucket_name`` complies with the
    restricted DNS naming conventions necessary to allow
    access via virtual-hosting style.

    Even though '.' characters are perfectly valid in this DNS
    naming scheme, we are going to punt on any name containing a
    '.' character because these will cause SSL cert validation
    problems if we try to use virtual-hosting style addressing.

    :param bucket_name: Bucket name in *str*.
    :return: True if the bucket is valid. Raises *InvalidBucketError* otherwise.
    """
    validbucket = re.compile('^[a-zA-Z][a-zA-Z0-9\\-]+[a-zA-Z0-9]$')
    if '.' in bucket_name:
        raise InvalidBucketError('bucket')

    if len(bucket_name) < 3 or len(bucket_name) > 63:
        # Wrong length
        raise InvalidBucketError('bucket')

    match = validbucket.match(bucket_name)
    if match is None or match.end() != len(bucket_name):
        raise InvalidBucketError('bucket')

    return True

def is_non_empty_string(input_string):
    """
    Validate if non empty string

    :param input_string: Input is a *str*.
    :return: True if input is string. Raises *err* otherwise.
    """
    if not isinstance(input_string, basestring):
        raise TypeError()
    if not input_string.strip():
        raise ValueError()

    return True

def encode_object_name(object_name):
    """
    URL encode input object name.

    :param object_name: Un-encoded object name.
    :return: URL encoded input object name.
    """
    is_non_empty_string(object_name)
    return urlencode(object_name)

def get_sha256(content):
    """
    Calculate sha256 digest of input byte array.

    :param content: Input byte array.
    :return: sha256 digest of input byte array.
    """
    if len(content) == 0:
        content = b''
    hasher = hashlib.sha256()
    hasher.update(content)
    return hasher.digest()

def get_md5(content):
    """
    Calculate md5 digest of input byte array.

    :param content: Input byte array.
    :return: md5 digest of input byte array.
    """
    if len(content) == 0:
        content = b''
    hasher = hashlib.md5()
    hasher.update(content)
    return hasher.digest()

def encode_to_base64(content):
    """
    Calculate base64 of input byte array.

    :param content: Input byte array.
    :return: base64 encoding of input byte array.
    """
    return binascii.b2a_base64(content).strip().decode('utf-8')

def encode_to_hex(content):
    """
    Calculate hex for input byte array.

    :param content: Input byte array.
    :return: hexlified input byte array.
    """
    return binascii.hexlify(content)

def calculate_part_size(length):
    """
    Calculate optimal part size for multipart uploads.

    :param length: Input length to calculate part size of.
    :return: Optimal part size.
    """
    minimum_part_size = 1024 * 1024 * 5
    maximum_part_size = 1024 * 1024 * 1024 * 5
    if length == -1:
        return maximum_part_size
    proposed_part_size = length / 9999 ## make sure last part has enough buffer
    if proposed_part_size > maximum_part_size:
        return maximum_part_size
    return max(minimum_part_size, proposed_part_size)
