# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook that gets executed every time an engine has been fully initialized.
"""

from tank import Hook
import os


class EngineInit(Hook):

    def execute(self, engine, **kwargs):
        """
        Executed when a Toolkit engine has been fully initialized.

        At this point, all apps and frameworks have been loaded,
        and the engine is fully operational.

        The default implementation does nothing.

        :param engine: Engine that has been initialized.
        :type engine: :class:`~sgtk.platform.Engine`
        """

        os.environ['NUKE_CACHE'] = "/tmp/Nuke_Cache"
        os.environ['NUKE_CACHE_FROM'] = "/array/X/"
        os.environ['NUKE_DISK_CACHE'] = "/var/tmp"
        os.environ['NUKE_FONT_PATH'] = ":/array/X/Library/fonts"
        os.environ['NUKE_PATH'] = "/array/X/Library/NukeScripts/:/array/X/Library/NukeScripts/plugins/:/array/X/Library/NukeScripts/gizmos:/array/X/Library/NukeScripts/python:/usr/OFX/Plugins"
        os.environ['NUKE_TEMP_DIR'] = "/var/tmp"

