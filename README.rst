coursera_autograder
===================

This command-line tool is a software development toolkit to help instructional
teams author asynchronous graders for Coursera (typically programming
assignments). Coursera's asynchronous grading environment is based upon
`docker <https://www.docker.com/>`_. While use of this tool is by no means
required to develop the docker container images, we believe it is helpful in the
endeavour. See below for brief descriptions of this tool's capabilities.

Installation
------------

Use the following commands to install from source::

  git clone https://github.com/coursera/coursera_autograder.git
  cd coursera_autograder
  virtualenv -p python3 venv (Optional)
  source venv/bin/activate (Optional)
  python setup.py develop
  pip install -r test_requirements.txt
  pip install -e .  

You would need to install git, pip, and python3 to install and run correctly.

  `pip install coursera_autograder` is coming soon.


If you have used the `pip install` workflow previously to install `coursera_autograder`, we recommend using this flow to update your `coursera_autograder` version.

If you would like to separate your build environments, we recommend installing `coursera_autograder` within a virtual environment.

`pip <https://pip.pypa.io/en/latest/index.html>`_ is a python package manager.
If you do not have ``pip`` installed on your machine, please follow the
installation instructions for your platform found at:
https://pip.pypa.io/en/latest/installing.html#install-or-upgrade-pip

The tool includes its own usage information and documentation. Simply run::

    coursera_autograder -h

or::

    coursera_autograder --help

for a complete list of features, flags, and documentation.

Note: the tool requires ``docker`` to already be installed on your machine.
Please see the docker
`installation instructions <http://docs.docker.com/index.html>`_ for further
information.

Subcommands
-----------

grade local
^^^^^^^^^^^

This ``grade local`` subcommand loosely replicates the production grading environment on
your local machine. Note that because the GrID system has
adopted a defense-in-depth or layered defensive posture, not all layers of the
production environment can be faithfully replicated locally.

``grade local`` runs a local grader
container image on a sample submission on the local file system, provided as part of the command. This command is intended
to help instructional teams verify new versions of their graders correctly
handle problematic submissions.

Examples:
 - ``coursera_autograder grade local $MY_CONTAINER_IMAGE_TAG
   /path/to/sample/submission/ $ENV_VAR_JSON --dst-dir ~/Desktop``
   invokes the grader passing in the sample submission into the grader.
 - When the grade local is successful, you can verify that feedback.json is produced in dst-dir (in this case it is ~/Desktop).
 - $ENV_VAR_JSON is a json string like'{"partId": "Zb6wb"}',
 - ``coursera_autograder grade local --help`` displays the full list of
   flags and options available.
 - ``coursera_autograder grade local python_grader ./submission '{"partId": "5ShhY"}' --dst-dir ~/Desktop``
 - Please make sure there is only the correct solution file in the submission directory (./submission).
 
In contrast to this local tester, Coursera's production system will also set these environment variables for internal purposes. In local testing, it is possible to specify these as well with the environment variable JSON, although it's completely up to the grading Docker you create to use them or not. In typical usage, you would not set or read these variables.

- ``filename`` - The original filename of the file the student has chosen to submit, prior to being renamed on the server automatically. To avoid confusion, note that the `grade local` command takes a directory path, not a file path; the directory should contain a submission file with the same filename as the "suggested filename" you've configured for the assignment as published on Coursera's UI, and your autograder should also look for the file with the "suggested filename." The ``filename`` environment variable *does not* specify the "suggested filename". Also, autograders live in production will find the submitted file has already been renamed, so the ``filename`` env var does not have much usefulness inside the grader. One use case might be to display a warning to learners if the file they chose to submit does not have the correct file extension prior to being automatically renamed.
- ``userId`` - a unique string Coursera uses to disambiguate learners.

upload
^^^^^^

Allows an instructional team to upload their containers to Coursera without
using a web browser. It is designed to even work in an unattended fashion (i.e.
from a jenkins job). In order to make the upload command work from a Jenkins
automated build machine, simply copy the `~/.coursera` directory from a working
machine, and install it in the jenkins home folder. Beware that the oauth2_cache
file within that directory contains a refresh token for the user who authorized
themselves. This refresh token should be treated as if it were a password and
not shared or otherwise disclosed!

To find the course id, item id, and part id, first go to the web authoring
interface for your programming assignment. There, the URL will be of the form:
``/:courseSlug/author/outline/programming/:itemId/``. The part id will be
displayed in the authoring user interface for each part. To convert the
``courseSlug`` into a ``courseId``, you can take advantage of our `Course API` putting in the appropriate ``courseSlug``. For example, given a
course slug of ``developer-iot``, you can query the course id by making the
request: ``https://api.coursera.org/api/onDemandCourses.v1?q=slug&slug=developer-iot``.
The response will be a JSON object containing an ``id`` field with the value:
``iRl53_BWEeW4_wr--Yv6Aw``.

The uploaded grader can be linked to multiple (itemId, partId) pairs without making duplicate uploads by using the ``--additional_item_and_part`` flag.

This command can also be used to customize the resources that will be allocated
to your grader when it grades learner submissions. The CPU, memory limit and
timeout are all customizable.

 - ``--grader-cpu`` takes a value of 1, 2 or 4, representing the number of cores
   the grader will have access to when grading. The default is 1.
 - ``--grader-memory-limit`` takes a value between 4096 to 16384, increnment of 1024. representing the
   amount of memory in MB the grader will have access to when grading. The
   default is 4096 (4GB).
   
   Not all combinations of cpu and memory are supported. The supported combinations is listed here:
   
   - For 1024 (1 vCPU), Memory needs to be between 2048 (2GB) and 8192 (8GB) in increments of 1024 (1GB).
   
   - For 2048 (2 vCPU), Memory needs to be between 4096 (4GB) and 16384 (16GB) in increments of 1024 (1GB).
   
   - For 4096 (4 vCPU), Memory needs to be between 8192 (8GB) and 16384 (16GB) in increments of 1024 (1GB)


 - ``--grading-timeout`` takes a value between 300 and 1800, representing the
   amount of time the grader is allowed to run before it times out. Note this
   value is counted from the moment the grader starts execution and does not
   include the time it takes Coursera to schedule the grader. The default value
   is 1200.

Examples:
 - ``coursera_autograder upload $PATH_TO_IMAGE_ZIP_FILE $COURSE_OR_BRANCH_ID $ITEM_ID
   $PART_ID`` uploads the specified grader container image to Coursera, begins
   the post-upload processing, and associates the new grader with the
   specified item part in a new draft. Navigate to the course authoring UI
   or use the `publish` command to publish the draft to make it live.
 - ``coursera_autograder upload $PATH_TO_IMAGE_ZIP_FILE $COURSE_OR_BRANCH_ID $ITEM_ID $PART_ID
   --additional_item_and_part $ITEM_ID2 $PART_ID2 $ITEM_ID3 $PART_ID3`` uploads
   the specified graded container image to Coursera, begins the post-upload procesing,
   and associates the new grader with all the three item_id part_id pairs.
   Navigate to the course authoring UI for each item to publish the draft to make it live.
 - ``coursera_autograder upload --help`` displays all available options
   for the :code:`upload` subcommand.
 - ``zip -r PythonGrader.zip .`` (Make sure you are in the directory containing the Dockerfile. This must be the top level directory)
 - ``coursera_autograder upload ./PythonGrader.zip iRl53_BWEeW4_wr--Yv6Aw rLa7F Zb6wb``

get_resource_limits
^^^^^^^^^^^^^^^^^^^

Allows an instructional team to view the resource limits (vCPU's, MiB, timeout) allocated to the grader for a given programming assignment.
It requires the instructor to provide the course id, item id, and part id to identify the specific programming assignment. Instructions on 
how to find these values can be found in the previous section for the ``upload`` command.

Usage:
 - ``coursera_autograder get_resource_limits $COURSE_OR_BRANCH_ID $ITEM_ID $PART_ID``

update_resource_limits
^^^^^^^^^^^^^^^^^^^^^^

Allows an instructional team to update the resource limits (vCPU's, MiB, timeout) allocated to the grader for a given programming assignment.
It requires the instructor to provide the course id, item id, and part id to identify the specific programming assignment. Instructions on 
how to find these values can be found in the previous section for the ``upload`` command. In addition, the instructor must provide the values
they wish to update by using the parameter flags

 - ``--grader-cpu`` to update the allocated vCPU's
 - ``--grader-memory-limit`` to update the memory limit
 - ``--grader-timeout`` to update the timeout threshold

If a certain parameter is not provided, then we will simply use the previously existing value. Note that there are restrictions on which
combinations of CPU's and memory values are valid. These restrictions can be found in the ``upload`` section above.

Usage:
 - ``coursera_autograder update_resource_limits $COURSE_OR_BRANCH_ID $ITEM_ID $PART_ID`` --grader-cpu $CPU --grader-memory-limit $MEMORY --grader-timeout $TIMEOUT

configure
^^^^^^^^^

Makes sure that the instructor is able to communicate with the coursera.org API servers with the correct authentication.

Usage:
 - ``coursera_autograder config check-auth``
 - ``coursera_autograder config display-auth-cache``


Bugs / Issues / Feature Requests
--------------------------------

Please reach out to your partner support teams to file an enhancement request or report a bug. While we check in on the issues logged on this repository from time to time, reaching out to your partner support teams will likely provide you with a faster response. We appreciate your support and dedication to improving this tool for all Coursera partners!

Supported Platforms
^^^^^^^^^^^^^^^^^^^

Note: We do not have the bandwidth to officially support this tool on windows.
That said, patches to add / maintain windows support are welcome!

Developing / Contributing
-------------------------

We recommend developing ``coursera_autograder`` within a python
`virtualenv <https://pypi.python.org/pypi/virtualenv>`_.
To get your environment set up properly, do the following::

    virtualenv venv
    source venv/bin/activate
    python setup.py develop
    pip install -r test_requirements.txt

Tests
^^^^^

To run tests, simply run: ``nosetests``, or ``tox``.

Code Style
^^^^^^^^^^

Code should conform to pep8 style requirements. To check, simply run::

    pep8 coursera_autograder tests
