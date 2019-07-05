                    # Copyright (c) 2017 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

# Copied from tk-maya/hooks/tk-multi-publish2/basic/publish_session_geometry.py

import os
import traceback
import maya.cmds as cmds
import maya.mel as mel
import sgtk
# import tank as sgtk for debugging
import tank as sgtk
import pprint

HookBaseClass = sgtk.get_hook_baseclass()


class MayaAlembicGeometryPublishPlugin(HookBaseClass):
    """
    Plugin for publishing an open maya session.

    This hook relies on functionality found in the base file publisher hook in
    the publish2 app and should inherit from it in the configuration. The hook
    setting for this plugin should look something like this::

        hook: "{self}/publish_file.py:{engine}/tk-multi-publish2/basic/publish_session.py"

    """

    # NOTE: The plugin icon and name are defined by the base file plugin.

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting.
        """

        return """
        <p>This plugin publishes previously exported Alembic Geometry and Cameras for the current session. Please use 
        the Mavericks Alembic Shotgun export tool.
        </p>
        """

    @property
    def settings(self):
        """
        Dictionary defining the settings that this plugin expects to receive
        through the settings parameter in the accept, validate, publish and
        finalize methods.

        A dictionary on the following form::

            {
                "Settings Name": {
                    "type": "settings_type",
                    "default": "default_value",
                    "description": "One line description of the setting"
            }

        The type string should be one of the data types that toolkit accepts as
        part of its environment configuration.
        """
        # inherit the settings from the base publish plugin
        base_settings = super(MayaAlembicGeometryPublishPlugin, self).settings or {}

        # settings specific to this class
        maya_publish_settings = {
            "Camera Publish Template": {
                "type": "template",
                "default": None,
                "description": "Template path for published work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
            },
            "Camera Working Template": {
                "type": "template",
                "default": None,
                "description": "Template path for published work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
            },
            "Alembic Publish Template": {
                "type": "template",
                "default": None,
                "description": "Template path for work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
            },
            "Alembic Working Template": {
                "type": "template",
                "default": None,
                "description": "Template path for work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
            }
        }

        # update the base settings
        base_settings.update(maya_publish_settings)

        return base_settings

    @property
    def item_filters(self):
        """
        List of item types that this plugin is interested in.

        Only items matching entries in this list will be presented to the
        accept() method. Strings can contain glob patters such as *, for example
        ["maya.*", "file.maya"]
        """
        # return ["maya.session.geometry"]
        return ["file.alembic.camera", "file.alembic.geo"]

    def accept(self, settings, item):
        """
        Method called by the publisher to determine if an item is of any
        interest to this plugin. Only items matching the filters defined via the
        item_filters property will be presented to this method.

        A publish task will be generated for each item accepted here. Returns a
        dictionary with the following booleans:

            - accepted: Indicates if the plugin is interested in this value at
                all. Required.
            - enabled: If True, the plugin will be enabled in the UI, otherwise
                it will be disabled. Optional, True by default.
            - visible: If True, the plugin will be visible in the UI, otherwise
                it will be hidden. Optional, True by default.
            - checked: If True, the plugin will be checked in the UI, otherwise
                it will be unchecked. Optional, True by default.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process

        :returns: dictionary with boolean keys accepted, required and enabled
        """

        publish_type = self.get_publish_type(settings, item)

        if publish_type == 'Alembic Geo' or publish_type == 'Alembic Camera':
            return {
                "accepted": True,
                "checked": True,
                'visible': True
            }

        else:
            self.logger.info('No viable items')
            return {
                "accepted": False,
                "checked": False,
                'visible': False
            }

    def validate(self, settings, item):
        """
        Validates the given item to check that it is ok to publish. Returns a
        boolean to indicate validity.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        :returns: True if item is valid, False otherwise.
        """

        publish_type = self.get_publish_type(settings, item)
        self.logger.debug('Validate Publish Type: %s' % publish_type)

        # Get path of current maya file
        path = _session_path()

        alembic_path = item.properties["path"]

        # Ensure the session has been saved
        if not path:
            # the session still requires saving. provide a save button.
            # validation fails.
            error_msg = "The Maya session has not been saved."
            self.logger.error(
                error_msg,
                extra=_get_save_as_action()
            )
            raise Exception(error_msg)

        # get the normalized paths
        path = sgtk.util.ShotgunPath.normalize(path)
        alembic_path = sgtk.util.ShotgunPath.normalize(alembic_path)

        # get the configured work file template
        work_template = item.properties.get("alembic_template")
        publish_template = item.properties.get("publish_template")

        # get the current scene path and extract fields from it using the work template:
        work_fields = work_template.get_fields(alembic_path)

        # ensure the fields work for the publish template
        missing_keys = publish_template.missing_keys(work_fields)
        if missing_keys:
            error_msg = "Work file '%s' missing keys required for the " \
                        "publish template: %s" % (path, missing_keys)
            self.logger.error(error_msg)
            raise Exception(error_msg)

        # create the publish path by applying the fields. store it in the item's
        # properties. This is the path we'll create and then publish in the base
        # publish plugin. Also set the publish_path to be explicit.
        publish_path = publish_template.apply_fields(work_fields)
        item.properties["publish_path"] = publish_path

        # Check if published files exist
        if os.path.exists(publish_path):
            error_msg = 'Published File already exists: %s' % (publish_path)
            self.logger.error(error_msg)
            raise Exception(error_msg)

        self.logger.debug("Work Path: %s" % (alembic_path))
        self.logger.debug("Publish Path: %s" % (publish_path))

        self.logger.debug("working template path: %s" % (work_template))
        self.logger.debug("publish template path: %s" % (publish_template))

        return True

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """

        alembic_path = item.properties["path"]
        publish_path = item.properties["publish_path"]

        # copy the file
        try:
            publish_folder = os.path.dirname(publish_path)
            sgtk.util.filesystem.ensure_folder_exists(publish_folder)
            sgtk.util.filesystem.copy_file(alembic_path, publish_path)
        except Exception, e:
            raise Exception(
                "Failed to copy work file from '%s' to '%s'.\n%s" %
                (alembic_path, publish_path, traceback.format_exc())
            )

        self.logger.debug(
            "Copied work file '%s' to publish file '%s'." %
            (alembic_path, publish_path)
        )

        # Now that the path has been generated, hand it off to the
        super(MayaAlembicGeometryPublishPlugin, self).publish(settings, item)


def _find_scene_animation_range():
    """
    Find the animation range from the current scene.
    """
    # look for any animation in the scene:
    animation_curves = cmds.ls(typ="animCurve")

    # if there aren't any animation curves then just return
    # a single frame:
    if not animation_curves:
        return 1, 1

    # something in the scene is animated so return the
    # current timeline.  This could be extended if needed
    # to calculate the frame range of the animated curves.
    start = int(cmds.playbackOptions(q=True, min=True))
    end = int(cmds.playbackOptions(q=True, max=True))

    return start, end


def _session_path():
    """
    Return the path to the current session
    :return:
    """
    path = cmds.file(query=True, sn=True)

    if isinstance(path, unicode):
        path = path.encode("utf-8")

    return path


def _get_save_as_action():
    """
    Simple helper for returning a log action dict for saving the session
    """

    engine = sgtk.platform.current_engine()

    # default save callback
    callback = cmds.SaveScene

    # if workfiles2 is configured, use that for file save
    if "tk-multi-workfiles2" in engine.apps:
        app = engine.apps["tk-multi-workfiles2"]
        if hasattr(app, "show_file_save_dlg"):
            callback = app.show_file_save_dlg

    return {
        "action_button": {
            "label": "Save As...",
            "tooltip": "Save the current session",
            "callback": callback
        }
    }
