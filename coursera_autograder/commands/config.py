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

"""
Coursera's asynchronous grader command line SDK.

You may install it from source, or via pip.
"""

from coursera_autograder.commands import oauth2
import time
import sys


def display_auth_cache(args):
    '''
    Writes to the screen the state of the authentication cache. (For debugging
    authentication issues.) BEWARE: DO NOT email the output of this command!!!
    You must keep the tokens secure. Treat them as passwords.
    '''
    oauth2_instance = oauth2.build_oauth2(args)
    if not args.quiet or args.quiet == 0:
        token = oauth2_instance.token_cache['token']
        if not args.no_truncate and token is not None:
            token = token[:10] + '...'
        print("Auth token: %s" % token)

        expires_time = oauth2_instance.token_cache['expires']
        expires_in = int((expires_time - time.time()) * 10) / 10.0
        print("Auth token expires in: %s seconds." % expires_in)

        if 'refresh' in oauth2_instance.token_cache:
            refresh = oauth2_instance.token_cache['refresh']
            if not args.no_truncate and refresh is not None:
                refresh = refresh[:10] + '...'
            print("Refresh token: %s" % refresh)
        else:
            print("No refresh token found.")


def parser(subparsers):
    "Build an argparse argument parser to parse the command line."
    # create the parser for the configure subcommand. (authentication / etc.)
    parser_config = subparsers.add_parser(
        'configure',
        help='Configure %(prog)s for operation!')
    config_subparsers = parser_config.add_subparsers()

    parser_local_cache = config_subparsers.add_parser(
        'display-auth-cache',
        help=display_auth_cache.__doc__)
    parser_local_cache.set_defaults(func=display_auth_cache)
    parser_local_cache.add_argument(
        '--no-truncate',
        action='store_true',
        help='Do not truncate the keys [DANGER!!]')

    if len(sys.argv) == 2 and sys.argv[1] == 'configure':
        parser_config.print_help(sys.stderr)
        sys.exit(1)

    return parser_config
