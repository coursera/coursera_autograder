#!/usr/bin/env python

# Copyright 2015 Coursera
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
from coursera_autograder import main
from coursera_autograder.commands import ls
from mock import MagicMock
from mock import patch


def test_ls_parsing_simple():
    parser = main.build_parser()
    args = parser.parse_args('ls a1b2c3 /'.split())
    assert args.func == ls.command_ls, "func: %s" % args.func
    assert args.dir == '/', "Dir is: %s" % args.dir
    assert args.imageId == 'a1b2c3', "Container id: %s" % args.imageId


def test_ls_parsing_flags():
    parser = main.build_parser()
    args = parser.parse_args('ls -al --human my-container /foo/bar'.split())
    assert args.func == ls.command_ls
    assert args.dir == '/foo/bar', args.dir
    assert args.imageId == 'my-container', args.imageId
    assert args.a
    assert args.l
    assert args.human


@patch('coursera_autograder.commands.ls.utils')
def test_ls_run(utils):

    docker_mock = MagicMock(spec=docker.APIClient)
    docker_mock.create_container.return_value = {
        'Id': 'really-long-container-id-hash',
        'Warnings': None
    }
    docker_mock.wait.return_value = 0
    docker_mock.logs.return_value = "grader.sh\ntestcases.txt\n"
    utils.docker_client.return_value = docker_mock

    # Set up args
    args = argparse.Namespace()
    args.imageId = 'testImageId'
    args.dir = '/grader'
    args.l = False
    args.human = False
    args.a = False
    args.no_rm = False

    with patch('coursera_autograder.commands.ls.sys.stdout') as stdout:
        # Run the command
        ls.command_ls(args)

    # Verify correct command output
    stdout.write.assert_called_with(docker_mock.logs.return_value)

    docker_mock.create_container.assert_called_with(
        image='testImageId',
        entrypoint='/bin/ls',
        command=['/grader'])
    docker_mock.start.assert_called_with(
        docker_mock.create_container.return_value)
    docker_mock.logs.assert_called_with(
        docker_mock.create_container.return_value)
