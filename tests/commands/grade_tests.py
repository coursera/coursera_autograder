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
from coursera_autograder import main
from coursera_autograder.commands import grade
from mock import MagicMock
from mock import patch
from testfixtures import LogCapture
from os import path, remove
import json


def test_grade_local_parsing():
    # TODO: mock out `os.path.isdir` to make this test more portable.
    parser = main.build_parser()
    args = parser.parse_args(
        'grade local myContainerTag /tmp {"partId":"1a2b3"}'.split())
    assert args.func == grade.command_grade_local
    assert args.containerTag == 'myContainerTag'
    assert args.dir == '/tmp'
    assert args.envVar == '{"partId":"1a2b3"}'
    assert not args.no_rm
    assert args.mem_limit == 1024


def test_grade_local_parsing_no_rm():
    parser = main.build_parser()
    args = parser.parse_args(
        ('grade local --no-rm --mem-limit 2048 ' +
         'myContainerTag /tmp {"partId":"1a2b3"}').split())
    assert args.func == grade.command_grade_local
    assert args.containerTag == 'myContainerTag'
    assert args.dir == '/tmp'
    assert args.envVar == '{"partId":"1a2b3"}'
    assert args.no_rm
    assert args.mem_limit == 2048


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_output_bad_isCorrect(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        data = {}
        data['isCorrect'] = 'true-string-is-not-true'
        data['feedback'] = 'You win!'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'ERROR', "Field 'isCorrect' is not a boolean value."),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    grade.sys.exit.assert_called_with(1)
    remove(path.join(args.dst_dir, 'feedback.json'))


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_output_no_feedback(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        data = {}
        data['isCorrect'] = False
        data['not-feedback'] = 'garbage'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'ERROR', "Field 'feedback' not present in parsed output."),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    grade.sys.exit.assert_called_with(1)


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_output_fractional_score_boolean(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        data = {}
        data['fractionalScore'] = False
        data['feedback'] = 'wheeeee'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'ERROR', "Field 'fractionalScore' must be a decimal."),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    grade.sys.exit.assert_called_with(1)


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_output_fractional_score_string(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        data = {}
        data['fractionalScore'] = '0.3'
        data['feedback'] = 'wheeeee'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'ERROR', "Field 'fractionalScore' must be a decimal."),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    grade.sys.exit.assert_called_with(1)


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_output_fractional_score_too_high(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        data = {}
        data['fractionalScore'] = 1.1
        data['feedback'] = 'wheeeee'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'ERROR', "Field 'fractionalScore' must be <= 1."),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    grade.sys.exit.assert_called_with(1)


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_output_fractional_score_too_low(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        data = {}
        data['fractionalScore'] = -1.1
        data['feedback'] = 'wheeeee'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'ERROR', "Field 'fractionalScore' must be >= 0."),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    grade.sys.exit.assert_called_with(1)


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_output_missing_grade(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        data = {}
        data['feedback'] = 'wheeeee'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'ERROR', "Required field 'fractionalScore' is missing."),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    grade.sys.exit.assert_called_with(1)


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_output_malformed_output(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        outfile = open(path.join(args.dst_dir, 'feedback.json'), 'w')
        outfile.write('{"isCorrect":false, "not-feedback": "garbageeeeeeee')

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'ERROR', "The output was not a valid JSON document."),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    grade.sys.exit.assert_called_with(1)


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_output_bad_return_code(sys, get_feedback):
    with LogCapture():
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 1

        data = {}
        data['isCorrect'] = True
        data['feedback'] = 'You win!'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    grade.sys.exit.assert_called_with(1)


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_output_good_output_is_correct(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        data = {}
        data['isCorrect'] = False
        data['feedback'] = 'Helpful comment!'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    assert not grade.sys.exit.called, "sys.exit should not be called!"


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_output_good_output_fractional_score(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        data = {}
        data['fractionalScore'] = 0.2
        data['feedback'] = 'Helpful comment!'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    assert not grade.sys.exit.called, "sys.exit should not be called!"


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_output_good_output_fractional_score_one(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        data = {}
        data['fractionalScore'] = 1
        data['feedback'] = 'Helpful comment!'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    assert not grade.sys.exit.called, "sys.exit should not be called!"


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_good_output_fractional_score_one_point_oh(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        data = {}
        data['fractionalScore'] = 1.0
        data['feedback'] = 'Helpful comment!'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    assert not grade.sys.exit.called, "sys.exit should not be called!"


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_output_good_output_fractional_score_zero(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        data = {}
        data['fractionalScore'] = 0
        data['feedback'] = 'Helpful comment!'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    assert not grade.sys.exit.called, "sys.exit should not be called!"


@patch('coursera_autograder.commands.grade.sys')
@patch('coursera_autograder.commands.grade.get_feedback')
def test_check_good_output_fractional_score_zero_point_oh(sys, get_feedback):
    with LogCapture() as logs:
        docker_mock = MagicMock()
        container = {
            "Id": "myimageId"
        }
        args = argparse.Namespace()
        args.dst_dir = './'
        args.timeout = 300
        args.no_rm = False

        docker_mock.wait.return_value = 0

        data = {}
        data['fractionalScore'] = 0.0
        data['feedback'] = 'Helpful comment!'

        with open(path.join(args.dst_dir, 'feedback.json'), 'w') as outfile:
            json.dump(data, outfile)

        # Run the function under test
        grade.run_container(docker_mock, container, args)
    logs.check(
        ('root', 'INFO', 'Start of standard error:'),
        ('root', 'INFO', 'End of standard error'),
        ('root', 'DEBUG', "About to remove container: {'Id': 'myimageId'}")
    )
    assert not grade.sys.exit.called, "sys.exit should not be called!"


@patch('coursera_autograder.commands.grade.common')
@patch('coursera_autograder.commands.grade.utils')
@patch('coursera_autograder.commands.grade.run_container')
@patch('coursera_autograder.commands.grade.docker.utils')
def test_command_local_grade_simple(
        docker_utils,
        run_container,
        utils,
        common):
    args = argparse.Namespace()
    args.dir = '/tmp'
    args.containerTag = 'myimageId'
    args.envVar = '{"partId":"1a2b3"}'
    args.mem_limit = 1024

    common.mk_submission_volume_str.return_value = 'foo'
    docker_mock = MagicMock()
    docker_mock.create_container.return_value = {
        "Id": "myContainerInstanceId",
    }
    utils.docker_client.return_value = docker_mock

    h_config = {'foo': 'bar'}  # just some unique value
    docker_mock.create_host_config.return_value = h_config

    grade.command_grade_local(args)

    docker_mock.create_container.assert_called_with(
        image='myimageId',
        environment={'partId': '1a2b3'},
        host_config=h_config,
    )
    docker_mock.create_host_config.assert_called_with(
        binds=['foo', ],
        network_mode='none',
        mem_limit='1g',
        memswap_limit='1g',
    )
    run_container.assert_called_with(
        docker_mock,
        docker_mock.create_container.return_value,
        args)
