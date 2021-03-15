#!/usr/bin/env python

# Copyright 2021 Coursera
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

import argparse
import docker
import requests
from coursera_autograder import main
from coursera_autograder.commands import get_resource_limits
from mock import MagicMock
from mock import patch
from nose.tools import nottest
from testfixtures import LogCapture
from os import remove
import json


def test_get_resource_limits_parsing():
    parser = main.build_parser()

    args = parser.parse_args(
               'get_resource_limits COURSE_ID ITEM_ID PART_ID'.split())
    assert args.func == get_resource_limits.command_get_resource_limits
    assert args.course == 'COURSE_ID'
    assert args.item == 'ITEM_ID'
    assert args.part == 'PART_ID'

class MockResponse:

    def __init__(self, status_code, url, text, jsonObj = {}):
        self.status_code = status_code
        self.url = url
        self.text = text
        self.content = "Mock content"
        self.jsonObj = jsonObj

    def json(self):
        return self.jsonObj

@patch('coursera_autograder.commands.get_resource_limits.oauth2')
@patch.object(requests.Session, 'post', return_value=MockResponse(404, 'endpoint', 'not found!'))
def test_get_resource_limits_error_not_found(mock_oauth, mock_post):
    with LogCapture() as logs: 
        args = argparse.Namespace()
        args.course = 'COURSE_ID'
        args.item = 'ITEM_ID'
        args.part = 'PART_ID'
        args.getGraderResourceLimits_endpoint = 'endpoint'
    
        exit_val = get_resource_limits.command_get_resource_limits(args)

    logs.check(
        ('root',
         'ERROR',
         '\n'
         'Unable to find the part or grader with part id PART_ID in item ITEM_ID in '
         'course COURSE_ID.\n'
         'Status Code: 404 \n'
         'URL: endpoint \n'
         'Response: not found!\n')
    )

    assert exit_val == 1

@patch('coursera_autograder.commands.get_resource_limits.oauth2')
@patch.object(requests.Session, 'post', return_value=MockResponse(403, 'endpoint', 'not authorized!'))
def test_get_resource_limits_error_general(mock_oauth, mock_post):
    with LogCapture() as logs: 
        args = argparse.Namespace()
        args.course = 'COURSE_ID'
        args.item = 'ITEM_ID'
        args.part = 'PART_ID'
        args.getGraderResourceLimits_endpoint = 'endpoint'
    
        exit_val = get_resource_limits.command_get_resource_limits(args)

    logs.check(
        ('root',
         'ERROR',
         '\n'
         'Unable to get grader resources.\n'
         'CourseId: COURSE_ID\n'
         'ItemId: ITEM_ID\n'
         'PartId: PART_ID\n'
         'Status Code: 403 \n'
         'URL: endpoint \n'
         'Response: not authorized!\n')
    )

    assert exit_val == 1

data = {}
data['reservedCpu'] = 1024
data['reservedMemory'] = 4096
data['wallClockTimeout'] = 1200

@patch('coursera_autograder.commands.get_resource_limits.oauth2')
@patch.object(requests.Session, 'post', return_value = MockResponse(200, 'endpoint', 'OK', data))
def test_get_resource_limits_ok(mock_oauth, mock_post):
    with LogCapture() as logs: 
        args = argparse.Namespace()
        args.course = 'COURSE_ID'
        args.item = 'ITEM_ID'
        args.part = 'PART_ID'
        args.getGraderResourceLimits_endpoint = 'endpoint'
    
        exit_val = get_resource_limits.command_get_resource_limits(args)

    assert exit_val == 0

defaultData = {}
defaultData['reservedCpu'] = 4096
defaultData['reservedMemory'] = 8192

@patch('coursera_autograder.commands.get_resource_limits.oauth2')
@patch.object(requests.Session, 'post', return_value = MockResponse(200, 'endpoint', 'OK', data))
def test_get_resource_limits_ok_default_values(mock_oauth, mock_post):
    with LogCapture() as logs: 
        args = argparse.Namespace()
        args.course = 'COURSE_ID'
        args.item = 'ITEM_ID'
        args.part = 'PART_ID'
        args.getGraderResourceLimits_endpoint = 'endpoint'
    
        exit_val = get_resource_limits.command_get_resource_limits(args)

    assert exit_val == 0