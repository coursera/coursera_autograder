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
import requests
from coursera_autograder import main
from coursera_autograder.commands import list_graders
from mock import patch
from mock import MagicMock
from testfixtures import LogCapture
import json


def test_list_graders_parsing():
    parser = main.build_parser()

    args = parser.parse_args('list_graders COURSE_ID'.split())
    assert args.func == list_graders.command_list_graders
    assert args.course == 'COURSE_ID'


class MockResponse:

    def __init__(self, status_code, url, text, jsonObj={}):
        self.status_code = status_code
        self.url = url
        self.text = text
        self.content = "Mock content"
        self.jsonObj = jsonObj

    def json(self):
        return self.jsonObj


@patch('coursera_autograder.commands.list_graders.oauth2')
@patch.object(requests.Session, 'get',
              return_value=MockResponse(404, 'endpoint', 'not found!'))
def test_list_graders_error_not_found(mock_oauth, mock_get):
    with LogCapture() as logs:
        args = argparse.Namespace()
        args.course = 'COURSE_ID'
        args.listGrader_endpoint = 'endpoint'

        exit_val = list_graders.command_list_graders(args)

    logs.check(
        ('root',
         'ERROR',
         '\n'
         'Unable to locate course with id COURSE_ID.\n'
         'Status Code: 404 \n'
         'URL: endpoint \n'
         'Response: not found!\n')
    )

    assert exit_val == 1


@patch('coursera_autograder.commands.list_graders.oauth2')
@patch.object(requests.Session, 'get',
              return_value=MockResponse(403, 'endpoint', 'not authorized!'))
def test_list_graders_error_general(mock_oauth, mock_get):
    with LogCapture() as logs:
        args = argparse.Namespace()
        args.course = 'COURSE_ID'
        args.listGrader_endpoint = 'endpoint'

        exit_val = list_graders.command_list_graders(args)

    logs.check(
        ('root',
         'ERROR',
         '\n'
         'Unable to list graders.\n'
         'CourseId: COURSE_ID\n'
         'Status Code: 403 \n'
         'URL: endpoint \n'
         'Response: not authorized!\n')
    )

    assert exit_val == 1

data = {}
elements = []
data['elements'] = elements


@patch('coursera_autograder.commands.list_graders.oauth2')
@patch.object(requests.Session, 'get',
              return_value=MockResponse(200, 'endpoint', 'OK', data))
def test_list_graders_ok(mock_oauth, mock_get):
    with LogCapture() as logs:
        args = argparse.Namespace()
        args.course = 'COURSE_ID'
        args.listGrader_endpoint = 'endpoint'

        exit_val = list_graders.command_list_graders(args)

    assert exit_val == 0
