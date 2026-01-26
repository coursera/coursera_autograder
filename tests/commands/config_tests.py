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

from coursera_autograder import main
from coursera_autograder.commands import config
from testfixtures import LogCapture
import sys
from mock import patch


def test_config_parsing_display_auth_cache():
    parser = main.build_parser()
    args = parser.parse_args('configure display-auth-cache'.split())
    assert args.func == config.display_auth_cache


@patch('coursera_autograder.commands.config.sys.exit')
def test_config_help_message(exit):
    testargs = ['placeholder', 'configure']
    with LogCapture() as logs:
        with patch.object(sys, 'argv', testargs):
            parser = main.build_parser()

    config.sys.exit.assert_called_with(1)
