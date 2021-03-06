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

def command_update_resource_limits(args):
    "Implements the update_resource_limits subcommand"

    oauth2_instance = oauth2.build_oauth2(args)
    auth = oauth2_instance.build_authorizer()

    s = requests.Session()
    s.auth = auth

    course_branch_id = args.course.replace("~", "!~") if "authoringBranch" in args.course else args.course
    course_branch_item = '%s~%s' % (course_branch_id, args.item)

    params = 'id=%s&partId=%s' % (course_branch_item, args.part)

    if args.grader_cpu != None and args.grader_cpu not in {'1', '2', '4'}:
        logging.error('Invalid CPU value. Please choose a value of 1, 2, or 4')
        return 1

    body = {
        "reservedCpu": int(args.grader_cpu) * 1024 if args.grader_cpu != None else None, 
        "reservedMemory": int(args.grader_memory_limit) if args.grader_memory_limit != None else None, 
        "wallClockTimeout": int(args.grader_timeout) if args.grader_timeout != None else None
        }
    result = s.post(args.updateGraderResourceLimits_endpoint, params = params, json = body)
    if result.status_code == 404:
        logging.error(
            '\nUnable to find the part or grader with part id %s in item %s in course %s.\n'
            'Status Code: 404 \n'
            'URL: %s \n'
            'Response: %s\n',
            args.part, 
            args.item, 
            args.course,
            result.url,
            result.text)
        return 1
    elif result.status_code != 200:
        logging.error(
            '\nUnable to update grader resources.\n'
            'CourseId: %s\n'
            'ItemId: %s\n'
            'PartId: %s\n'
            'Status Code: %d \n'
            'URL: %s \n'
            'Response: %s\n',
            args.course,
            args.item,
            args.part,
            result.status_code,
            result.url,
            result.text
        )
        return 1
    print(
        '\nUpdated resource Limits for grader with part id %s in item %s in course %s:\n'
        'New Reserved CPU (vCPUs): %s\n'
        'New Reserved Memory (MiB): %s\n'
        'New Wall Clock Timeout (s): %s\n' %
        (args.part,
         args.item,
         args.course,
         int(result.json()['reservedCpu'])/1024 if 'reservedCpu' in result.json() 
            else 'Cpu limit not set - default is 1 vCPU',
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
        help = 'The course id associated with the grader. The course id is a '
        'gibberish string UUID. Given a course slug such as `developer-iot`, '
        'you can retrieve the course id by querying the catalog API. e.g.: '
        'https://api.coursera.org/api/onDemandCourses.v1?q=slug&'
        'slug=developer-iot')

    parser.add_argument(
        'item',
        help = 'The id of the item associated with the grader. The easiest way '
        'to find the item id is by looking at the URL in the authoring web '
        'interface. It is the last part of the URL, and is a short UUID.')

    parser.add_argument(
        'part',
        help = 'The id of the part associated with the grader.')

    parser.add_argument(
        '--updateGraderResourceLimits-endpoint',
        default = 'https://api.coursera.org/api/authoringProgrammingAssignments.v3/?action=updateGraderResourceLimits',
        help = 'Override the endpoint used to retrieve information about a certain grader'
    )

    parser.add_argument(
        '--grader-cpu',
        default = None,
        help = 'New CPU limit'
    )

    parser.add_argument(
        '--grader-memory-limit',
        default = None,
        help = 'New memory limit'
    )

    parser.add_argument(
        '--grader-timeout',
        default = None,
        help = 'New timeout'
    )



def parser(subparsers):
    "Build an argparse argument parser to parse the command line."

    # create the parser for the resources command
    parser_resources = subparsers.add_parser(
        'update_resource_limits',
        help='Validates and updates the resource limits of a programming assignment part (autograder).')
    parser_resources.set_defaults(func=command_update_resource_limits)

    setup_registration_parser(parser_resources)

    return parser_resources