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
from nose.tools import nottest
from testfixtures import LogCapture
from os import remove


def test_upload_parsing():
    parser = main.build_parser()

    zip_file_path = './test.zip'
    open(zip_file_path, 'w')

    args = parser.parse_args(
               'upload {} COURSE_ID ITEM_ID PART_ID'.format(zip_file_path).split())
    assert args.imageZipFile.endswith('test.zip')
    assert args.course == 'COURSE_ID'
    assert args.item == 'ITEM_ID'
    assert args.part == 'PART_ID'
    assert args.additional_item_and_part is None
    remove(zip_file_path)


def test_upload_parsing_with_additional_items():
    parser = main.build_parser()

    zip_file_path = './test.zip'
    open(zip_file_path, 'w')

    args = parser.parse_args('upload {} COURSE_ID ITEM_ID '
                             'PART_ID '
                             '--additional_item_and_part ITEM_2 PART_2 '
                             '--additional_item_and_part ITEM_3 PART_3'
                             .format(zip_file_path)
                             .split())
    assert args.additional_item_and_part == [['ITEM_2', 'PART_2'],
                                             ['ITEM_3', 'PART_3']]

    remove(zip_file_path)


def test_upload_parsing_with_resource_customization():
    parser = main.build_parser()

    zip_file_path = './test.zip'
    open(zip_file_path, 'w')

    args = parser.parse_args('upload {} COURSE_ID ITEM_ID '
                             'PART_ID '
                             '--grader-cpu 1 '
                             '--grader-memory-limit 4096 '
                             '--grading-timeout 300 '
                             .format(zip_file_path)
                             .split())
    assert args.grader_cpu == 1
    assert args.grader_memory_limit == 4096
    assert args.grading_timeout == 300

    remove(zip_file_path)

@nottest
def test_upload_parsing_invalid_cpu():
    parser = main.build_parser()
    try:
        parser.parse_args('upload CONTAINER_IMAGE_ID COURSE_ID ITEM_ID '
                          'PART_ID '
                          '--grader-cpu 3 '
                          '--grader-memory-limit 1024 '
                          '--grading-timeout 300 '
                          .split())
    except SystemExit:
        assert True
    else:
        assert False, 'parser should have thrown exception'


@nottest
def test_upload_parsing_invalid_memory():
    parser = main.build_parser()
    try:
        parser.parse_args('upload CONTAINER_IMAGE_ID COURSE_ID ITEM_ID '
                          'PART_ID '
                          '--grader-cpu 1 '
                          '--grader-memory-limit 3 '
                          '--grading-timeout 300 '
                          .split())
    except SystemExit:
        assert True
    else:
        assert False, 'parser should have thrown exception'


@nottest
def test_upload_parsing_timeout_too_low():
    parser = main.build_parser()
    try:
        parser.parse_args('upload CONTAINER_IMAGE_ID COURSE_ID ITEM_ID '
                          'PART_ID '
                          '--grader-cpu 1 '
                          '--grader-memory-limit 1024 '
                          '--grading-timeout 299 '
                          .split())
    except SystemExit:
        assert True
    else:
        assert False, 'parser should have thrown exception'


@nottest
def test_upload_parsing_timeout_too_high():
    parser = main.build_parser()
    try:
        parser.parse_args('upload CONTAINER_IMAGE_ID COURSE_ID ITEM_ID '
                          'PART_ID '
                          '--grader-cpu 1 '
                          '--grader-memory-limit 1024 '
                          '--grading-timeout 1801 '
                          .split())
    except SystemExit:
        assert True
    else:
        assert False, 'parser should have thrown exception'
