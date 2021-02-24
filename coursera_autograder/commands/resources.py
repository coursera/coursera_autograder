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

"""
Coursera's asynchronous grader command line SDK.

You may install it from source, or via pip.
"""

from coursera_autograder.commands import common
from coursera_autograder.commands import oauth2
import logging
import requests
import urllib.parse

"""
target fields:
  reservedCpu: int?
  reservedMemory: int?
  wallClockTimeout: int?
"""

def command_resources(args):
    "Implements the resources subcommand"

    oauth2_instance = oauth2.build_oauth2(args)
    auth = oauth2_instance.build_authorizer()

    s = requests.Session()
    s.auth = auth

    course_branch_id = args.course.replace("~", "!~") if "authoringBranch" in args.course else args.course
    course_branch_item = '%s~%s' % (course_branch_id, args.item)

    params = 'id=%s&partId=%s' % (course_branch_item, args.part)
    result = s.post(args.getGraderResourceLimits_endpoint, params=params)
    if result.status_code == 404:
        logging.error(
            '\nUnable to find executor with part id %s in item %s in course %s.\n'
            'Status Code: 404 \nURL: %s \nResponse: %s\n',
            args.part, 
            args.item, 
            args.course,
            result.url,
            result.text)
        return 1
    elif result.status_code != 200:
        logging.error(
            '\nUnable to get executor resources.\n'
            'CourseId: %s\n'
            'ItemId: %s\n'
            'PartId: %s\n'
            'Status Code: %d \nURL: %s \nResponse: %s\n',
            args.course,
            args.item,
            args.part,
            result.status_code,
            result.url,
            result.text
        )
        return 1
    print(
        '\nResource Limits for executor with part id %s in item %s in course %s:\n'
        'Reserved CPU (AWS units -- 1024 units = 1 vCPU): %s (%s vCPUs)\n'
        'Reserved Memory (MiB): %s\n'
        'Wall Clock Timeout (s): %s\n' %
        (args.part,
         args.item,
         args.course,
         result.json()['reservedCpu'] if 'reservedCpu' in result.json() 
            else 'Cpu limit not set - default is 1024 AWS units',
         int(result.json()['reservedCpu'])/1024 if 'reservedCpu' in result.json() 
            else '1 vCPU',
         result.json()['reservedMemory'] if 'reservedMemory' in result.json() 
            else 'Memory limit not set - default is 4096 MiB',
         result.json()['wallClockTimeout'] if 'wallClockTimeout' in result.json() 
            else 'Timeout not set - default is 1200 seconds'))
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
        'item',
        help='The id of the item associated with the grader. The easiest way '
        'to find the item id is by looking at the URL in the authoring web '
        'interface. It is the last part of the URL, and is a short UUID.')

    parser.add_argument(
        'part',
        help='The id of the part associated with the grader.')

    parser.add_argument(
        '--getGraderResourceLimits-endpoint',
        default='https://api.coursera.org/api/authoringProgrammingAssignments.v3/?action=getGraderResourceLimits',
        help='Override the endpoint used to retrieve information about a certain executor'
    )



def parser(subparsers):
    "Build an argparse argument parser to parse the command line."

    # create the parser for the resources command
    parser_resources = subparsers.add_parser(
        'get_resource_limits',
        help='Gets the current resource limits of a programming assignment \
            part (autograder).')
    parser_resources.set_defaults(func=command_resources)

    setup_registration_parser(parser_resources)

    return parser_resources