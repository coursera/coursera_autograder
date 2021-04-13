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


def command_list_graders(args):
    "Implements the list subcommand"

    oauth2_instance = oauth2.build_oauth2(args)
    auth = oauth2_instance.build_authorizer()

    s = requests.Session()
    s.auth = auth

    result = s.get('%s%s' % (args.listGrader_endpoint, args.course))
    if result.status_code == 404:
        logging.error(
            '\nUnable to locate course with id %s.\n'
            'Status Code: 404 \n'
            'URL: %s \n'
            'Response: %s\n',
            args.course,
            result.url,
            result.text)
        return 1
    elif result.status_code != 200:
        logging.error(
            '\nUnable to list graders.\n'
            'CourseId: %s\n'
            'Status Code: %d \n'
            'URL: %s \n'
            'Response: %s\n',
            args.course,
            result.status_code,
            result.url,
            result.text
        )
        return 1

    elements = result.json()['elements']
    print('Graders associated with course id %s:\n' % args.course)
    for element in elements:
        course_grader_id = element['id']
        grader = course_grader_id.split('~')[-1]
        filename = element['filename']
        print('Filename: %s\nGraderId: %s\n' % (filename, grader))

    return 0


def setup_registration_parser(parser):
    'This is a helper function to coalesce all the common registration'
    'parameters for code reuse.'

    parser.add_argument(
        'course',
        help='The course id to look up. The course id is a '
        'gibberish string UUID. Given a course slug such as `developer-iot`, '
        'you can retrieve the course id by querying the catalog API. e.g.: '
        'https://api.coursera.org/api/onDemandCourses.v1?q=slug&'
        'slug=developer-iot')

    parser.add_argument(
        '--listGrader-endpoint',
        default='https://www.coursera.org/api/gridExecutors.v1/' +
        '?q=listByBranch&branchId=',
        help='Override the endpoint used to list graders associated ' +
        'with the given course'
    )


def parser(subparsers):
    "Build an argparse argument parser to parse the command line."

    # create the parser for the resources command
    parser_list_graders = subparsers.add_parser(
        'list_graders',
        help='Lists all graders associated with a given course.')
    parser_list_graders.set_defaults(func=command_list_graders)

    setup_registration_parser(parser_list_graders)

    return parser_list_graders
