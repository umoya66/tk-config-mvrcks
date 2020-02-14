# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
The after_project_create file is executed as part of creating a new project.
If your starter config needs to create any data in shotgun or do any other
special configuration, you can add it to this file.

The create() method will be executed as part of the setup and is passed
the following keyword arguments:

* sg -         A shotgun connection
* project_id - The shotgun project id that is being setup
* log -        A logger instance to which progress can be reported via
               standard logger methods (info, warning, error etc)

Mavericks workaround in a python console run the fllowing...
----
from shotgun_api3 import Shotgun
import sgtk

SERVER_PATH = 'https://mavericks.shotgunstudio.com'  # make sure to change this to https if your studio uses it.
SCRIPT_NAME = 'CleanVersions'
SCRIPT_KEY = 'ebff505b5bbd4f973b407ca69aa8392418c323b4df336e061fea6c72100e12a0'

sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

logger = sgtk.platform.get_logger(__name__)

# run this  file
after_project_create

create(sg, {PROJECT ID}, logger)

----


"""


def create(sg, project_id, log, **kwargs):
    """
    Insert post-project code here
    """
    pass
