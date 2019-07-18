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
import traceback
import sgtk
import traceback
import maya.cmds as cmds

HookBaseClass = sgtk.get_hook_baseclass()


class UploadVersionPlugin(HookBaseClass):
    """
    Plugin for sending quicktimes and images to shotgun for review.
    """

    @property
    def icon(self):
        """
        Path to an png icon on disk
        """

        # look for icon one level up from this hook's folder in "icons" folder
        return os.path.join(
            self.disk_location,
            "icons",
            "review.png"
        )

    @property
    def name(self):
        """
        One line display name describing the plugin
        """
        return "Upload for review"

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting.
        """

        publisher = self.parent

        shotgun_url = publisher.sgtk.shotgun_url

        media_page_url = "%s/page/media_center" % (shotgun_url,)
        review_url = "https://www.shotgunsoftware.com/features/#review"

        return """
        Upload a Maya Playblast to Shotgun for review.<br><br>

        A <b>Version</b> entry will be created in Shotgun and a transcoded
        copy of the file will be attached to it. The file can then be reviewed
        via the project's <a href='%s'>Media</a> page, <a href='%s'>RV</a>, or
        the <a href='%s'>Shotgun Review</a> mobile app.
        """ % (media_page_url, review_url, review_url)

        # TODO: when settings editable, describe upload vs. link

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
        return {
            "Upload": {
                "type": "bool",
                "default": True,
                "description": "Upload content to Shotgun?"
            },
            "Playblast Publish Template": {
                "type": "template",
                "default": None,
                "description": "Template path for published work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
            },
            "Playblast Work Template": {
                "type": "template",
                "default": None,
                "description": "Template path for work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
            },
            "Move Files": {
                "type": "bool",
                "default": False,
                "description": "Move files instead of copying them" 
            }, 
}

    @property
    def item_filters(self):
        """
        List of item types that this plugin is interested in.

        Only items matching entries in this list will be presented to the
        accept() method. Strings can contain glob patters such as *, for example
        ["maya.*", "file.maya"]
        """

        # we use "video" since that's the mimetype category.
        return ["file.video"]

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

        if 'publish_type' in item.properties:
            if item.properties['publish_type'] != 'Playblast':
                self.logger.info('This is not a playblast')
                return {
                    'accepted': False,
                    'checked': False,
                    'visible': False
                    }

        self.logger.debug('---Items---')
        for prop, value in item.properties.iteritems():
            self.logger.debug('\t%s: %s' % (prop, value))

        self.logger.debug('---Settings---')
        for setting, value in settings.iteritems():
            self.logger.debug('\t%s: %s' % (setting, value.value))

        playblast_work_template = self.parent.get_template_by_name(settings['Playblast Work Template'].value)
        publish_template = self.parent.get_template_by_name(settings['Playblast Publish Template'].value)

        path_fields = playblast_work_template.validate_and_get_fields(item.properties['path'])

        # publish_path = publish_template.apply_fields(path_fields)
        self.publish_path = publish_template.apply_fields(path_fields)

        file_path = item.properties["path"]

        if os.path.exists(self.publish_path):
            error_msg = 'Published File already exists: %s' % (self.publish_path)
            self.logger.error(error_msg)
            return {
                "accepted": False,
                "checked": False,
                'visible': False
                }
        else:
            # log the accepted file and display a button to reveal it in the fs
            self.logger.info(
                "Version upload plugin accepted: %s" % (path,),
                extra={
                    "action_show_folder": {
                        "path": path
                    }
                }
            )

            # return the accepted info
            return {'accepted': True,
                    'checked': True,
                    'visible': True
                   }


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
        self.logger.debug('---Items---')
        for prop, value in item.properties.iteritems():
            self.logger.debug('\t%s: %s' % (prop, value))

        self.logger.debug('---Settings---')
        self.logger.debug(settings)
        for setting, value in settings.iteritems():
            self.logger.debug('\t%s: %s' % (setting, value.value))

        # TODO: Check that the file hasnt already been copied to the publish dir
        # TODO: Check that the directory is writeable in this context

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
        path = item.properties["path"]
        publish_path = item.properties['publish_path']
        publish_name = item.properties.get("publish_name")

        # allow the publish name to be supplied via the item properties. this is
        # useful for collectors that have access to templates and can determine
        # publish information about the item that doesn't require further, fuzzy
        # logic to be used here (the zero config way)

        self.logger.debug("Using path info hook to determine publish name.")

        # use the path's filename as the publish name
        path_components = publisher.util.get_file_path_components(path)
        publish_name = path_components["filename"]


        self.logger.info("Creating Version...")
        version_data = {
            "project": item.context.project,
            "code": publish_name,
            "description": item.description,
            "entity": self._get_version_entity(item),
            "sg_task": item.context.task,
            'sg_path_to_movie': path
        }

        # if "sg_publish_data" in item.properties:
        #     publish_data = item.properties["sg_publish_data"]
        #     version_data["published_files"] = [publish_data]

        # version_data["sg_path_to_movie"] = path

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
        item.properties["sg_publish_data"] = version

        thumb = item.get_thumbnail_as_path()

        if settings["Upload"].value:
            self.logger.info("Uploading content...")

            # on windows, ensure the path is utf-8 encoded to avoid issues with
            # the shotgun api
            if sys.platform.startswith("win"):
                upload_path = path.decode("utf-8")
            else:
                upload_path = path

            self.parent.shotgun.upload(
                "Version",
                version["id"],
                upload_path,
                "sg_uploaded_movie"
            )
        elif thumb:
            # only upload thumb if we are not uploading the content. with
            # uploaded content, the thumb is automatically extracted.
            self.logger.info("Uploading thumbnail...")
            self.parent.shotgun.upload_thumbnail(
                "Version",
                version["id"],
                thumb
            )

        self.moveOrCopyFile(settings, item)

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
        version = item.properties["sg_publish_data"]

        self.logger.info('-------SG_PUBLISH_DATA-------------')
        data = {
            'sg_path_to_movie': '/mav/stor/prod/SandBox/sequences/Seq001/Shot001/comp/publish/maya/movies/Shot001_comp_cone_v032_playblast.mov',
            'code': 'Shot001_comp_cone_v032_playblast.mov', 'description': None,
            'entity': {'type': 'Shot', 'id': 10559, 'name': 'Shot001'},
            'project': {'type': 'Project', 'id': 321, 'name': 'SandBox'}, 'type': 'Version', 'id': 59704,
            'sg_task': {'type': 'Task', 'id': 125080, 'name': '2hrcomp'}}

        self.logger.info(version)

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


    def moveOrCopyFile(self, settings, item):
        """Move or copy folders depending on settings """

        work_folder = os.path.dirname(item.properties['path'])
        work_file = item.properties['path']
        publish_folder = os.path.dirname(self.publish_path)

        # Move or copy the work folders to publish area
        if settings["Move Files"].value:
            self.logger.info("Moving Folder...")

            # move the directory
            try:
                sgtk.util.filesystem.ensure_folder_exists(publish_folder, permissions=0755)
                sgtk.util.filesystem.copy_file(work_file, publish_folder, permissions=0755)
                sgtk.util.filesystem.safe_delete_file(work_file)
            except Exception, e:
                raise Exception(
                    "Failed to move work file from '%s' to '%s'.\n%s" %
                    (work_file, publish_folder, traceback.format_exc())
                )
        else:
            self.logger.info("Copying Folder...")

            # copy the directory
            # util leaves the source directory empty
            try:
                sgtk.util.filesystem.ensure_folder_exists(publish_folder, permissions=0755)
                sgtk.util.filesystem.copy_file(work_file, publish_folder, permissions=0755)
            except Exception, e:
                raise Exception(
                    "Failed to copy work folder from '%s' to '%s'.\n%s" %
                    (work_folder, publish_folder, traceback.format_exc())
                )

