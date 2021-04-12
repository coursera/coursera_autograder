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

from coursera_autograder.commands import common
from coursera_autograder.commands import oauth2
import logging
import requests
import urllib.parse


def command_get_status(args):
    "Implements the get_status subcommand"

    oauth2_instance = oauth2.build_oauth2(args)
    auth = oauth2_instance.build_authorizer()

    s = requests.Session()
    s.auth = auth

    course_branch_id = (args.course.replace("~", "!~")
                        if "authoringBranch~" in args.course else args.course)
    course_grader_id = '%s~%s' % (course_branch_id, args.graderId)

    result = s.get('%s%s' % (args.getGraderStatus_endpoint, course_grader_id))
    if result.status_code == 404:
        logging.error(
            '\nUnable to find grader with id %s in course %s.\n'
            'Status Code: 404 \n'
            'URL: %s \n'
            'Response: %s\n',
            args.graderId,
            args.course,
            result.url,
            result.text)
        return 1
    elif result.status_code != 200:
        logging.error(
            '\nUnable to get grader status.\n'
            'CourseId: %s\n'
            'GraderId: %s\n'
            'Status Code: %d \n'
            'URL: %s \n'
            'Response: %s\n',
            args.course,
            args.graderId,
            result.status_code,
            result.url,
            result.text
        )
        return 1

    status = result.json()['elements'][0]['status']
    print('\nGrader status: %s\n' % (status))
    return 0


def setup_registration_parser(parser):
    'This is a helper function to coalesce all the common registration'
    'parameters for code reuse.'

    parser.add_argument(
        'course',
        help='The course id associated with the grader. The course id is a '
        'gibberish string UUID. Given a course slug such as `developer-iot`, '
        'you can retrieve the course id by querying the catalog API. e.g.: '
        'https://api.coursera.org/api/onDemandCourses.v1?q=slug&'
        'slug=developer-iot')

    parser.add_argument(
        'graderId',
        help='The id associated with the grader. If you just ran the upload '
        'command, a grader id should have been printed out.'
    )

    parser.add_argument(
        '--getGraderStatus-endpoint',
        default='https://www.coursera.org/api/gridExecutors.v1/',
        help='Override the endpoint used to retrieve grader status'
    )


def parser(subparsers):
    "Build an argparse argument parser to parse the command line."

    # create the parser for the get_status command
    parser_status = subparsers.add_parser(
        'get_status',
        help='Gets the status of an uploaded grader.')
    parser_status.set_defaults(func=command_get_status)

    setup_registration_parser(parser_status)

    return parser_status
