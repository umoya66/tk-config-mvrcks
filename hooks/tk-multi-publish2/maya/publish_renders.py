# Copyright (c) 2017 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

# this was the original "upload_version.py" from tk-multi-publish2/hooks

import os
import pprint
import sys
import sgtk
import tank as sgtk
import traceback

HookBaseClass = sgtk.get_hook_baseclass()


class RenderPublish(HookBaseClass):
    """
    Plugin for sending quicktimes and images to shotgun for review.
    """
    # NOTE: The plugin icon and name are defined by the base file plugin.


    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting.
        """

        return """
        <p>This plugin publishes previously rendered Images for the current session. Please 
        render your layers to the correct shotgun template in order for them to be published 
        </p>
        """

    @property
    def settings(self):
        """
        Dictionary defining the settings that this plugin expects to recieve
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
        maya_publish_settings = { 
                "Publish Template": { 
                    "type": "template", 
                    "default": None,
                    "description": "Template path for published work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.", 
                               }, 
                "Work Template": { 
                    "type": "template",
                    "default": None,
                    "description": "Template path for work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
                               }, 
                "File Extensions": {
                    "type": "str",
                    "default": None,
                    "description": "File Extensions of files to include" 
                    }, 
                "Move Files": {
                    "type": "bool",
                    "default": False,
                    "description": "Move files instead of copying them" 
                    }, 
                "Link Local File": {
                    "type": "bool",
                    "default": True,
                    "description": "Should the local file be referenced by Shotgun" 
                    },
                }

        return maya_publish_settings


    @property
    def item_filters(self):
        """
        List of item types that this plugin is interested in.

        Only items matching entries in this list will be presented to the
        accept() method. Strings can contain glob patters such as *, for example
        ["maya.*", "file.maya"]
        """

        # we use "image" since that's the mimetype category.
        return ["file.image"]

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

        publisher = self.parent
        
        # self.logger.debug(dir(item))

        publish_path = item.properties['publish_path']
        publish_template = item.properties['publish_template']

        if os.path.exists(publish_path):
            error_msg = 'Published File already exists: %s' % (publish_path)
            self.logger.error(error_msg)
            return {
                "accepted": False,
                "checked": False,
                'visible': False
                }

        # check that file is of correct type
        file_path = item.properties["path"]

        file_info = publisher.util.get_file_path_components(file_path)
        self.logger.debug("file_info: %s " % file_info)
        extension = file_info["extension"].lower()

        self.logger.debug("File extensions: %s" % settings['File Extensions'].value)

        if extension in settings["File Extensions"].value:
            # log the accepted file and display a button to reveal it in the fs
            self.logger.info(
                "Version upload plugin accepted: %s" % (file_path,),
                extra={
                    "action_show_folder": {
                        "path": file_path
                    }
                }
            )

            # return the accepted info
            return {'accepted': True,
                    'checked': True,
                    'visible': True
                    }
        else:
            self.logger.debug(
                "%s is not in the valid extensions list for Version creation" %
                (extension,)
            )
            return {"accepted": False}

    def validate(self, settings, item):
        """
        Validates the given item to check that it is ok to publish.

        Returns a boolean to indicate validity.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process

        :returns: True if item is valid, False otherwise.
        """

        return True

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """

        publisher = self.parent

        # allow the publish name to be supplied via the item properties. this is
        # useful for collectors that have access to templates and can determine
        # publish information about the item that doesn't require further, fuzzy
        # logic to be used here (the zero config way)

        publish_name = item.properties.get("publish_name")

        work_path = item.properties["path"]
        publish_path = item.properties["publish_path"]

        if not publish_name:

            self.logger.debug("Using path info hook to determine publish name.")

            # use the path's filename as the publish name
            path_components = publisher.util.get_file_path_components(work_path)
            publish_name = path_components["filename"]

        self.logger.debug("Publish name: %s" % (publish_name,))

        self.logger.info("Creating Version...")

        version_data = {
            "project": item.context.project,
            "code": publish_name,
            "description": item.description,
            "entity": self._get_version_entity(item),
            "sg_task": item.context.task
        }

        # if "sg_publish_data" in item.properties:
        # publish_data = item.properties["publish_path"]

        # TODO: Need to add full enity hash for "published_files"

        version_data["published_files"] = [item.properties["publish_path"]]

        if settings["Link Local File"].value:
            version_data["sg_path_to_frames"] = publish_path

        # log the version data for debugging
        self.logger.debug(
            "Populated Version data...",
            extra={
                "action_show_more_info": {
                    "label": "Version Data",
                    "tooltip": "Show the complete Version data dictionary",
                    "text": "<pre>%s</pre>" % (pprint.pformat(version_data),)
                }
            }
        )

        # Create the version
        version = publisher.shotgun.create("Version", version_data)
        self.logger.info("Version created!")

        # stash the version info in the item just in case
        item.properties["sg_version_data"] = version

        thumb = item.get_thumbnail_as_path()
        publish_folder = os.path.dirname(publish_path)
        work_folder = os.path.dirname(work_path)

        #####################
        # Move or copy the work folders to publish area
        if settings["Move Files"].value:
            self.logger.info("Moving Folder...")

            # move the directory
            try:
                sgtk.util.filesystem.ensure_folder_exists(publish_folder, permissions=0755)
                sgtk.util.filesystem.move_folder(work_folder, publish_folder, folder_permissions=0755)
            except Exception, e:
                raise Exception(
                    "Failed to move work ffolder from '%s' to '%s'.\n%s" %
                    (work_folder, publish_folder, traceback.format_exc())
                )
        else:
            self.logger.info("Copying Folder...")

            # copy the directory
            # util leaves the source directory empty
            try:
                sgtk.util.filesystem.ensure_folder_exists(publish_folder, permissions=0755)
                sgtk.util.filesystem.copy_folder(work_folder, publish_folder, folder_permissions=0755)
            except Exception, e:
                raise Exception(
                    "Failed to copy work folder from '%s' to '%s'.\n%s" %
                    (work_folder, publish_folder, traceback.format_exc())
                )
                
        #####################
        # Upload thumbnail if there is one created
        if thumb:
            # only upload thumb if we are not uploading the content. with
            # uploaded content, the thumb is automatically extracted.
            self.logger.info("Uploading thumbnail...")
            self.parent.shotgun.upload_thumbnail(
                "Version",
                version["id"],
                thumb
            )

        self.logger.info("Upload complete!")

    def finalize(self, settings, item):
        """
        Execute the finalization pass. This pass executes once all the publish
        tasks have completed, and can for example be used to version up files.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """

        path = item.properties["path"]
        version = item.properties["sg_version_data"]

        self.logger.info(
            "Version uploaded for file: %s" % (path,),
            extra={
                "action_show_in_shotgun": {
                    "label": "Show Version",
                    "tooltip": "Reveal the version in Shotgun.",
                    "entity": version
                }
            }
        )

    def _get_version_entity(self, item):
        """
        Returns the best entity to link the version to.
        """

        if item.context.entity:
            return item.context.entity
        elif item.context.project:
            return item.context.project
        else:
            return None
