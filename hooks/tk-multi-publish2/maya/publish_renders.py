# Copyright (c) 2017 Shotgun Software Inc.

# CONFIDENTIAL AND PROPRIETARY

# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

# this was the original "upload_version.py" from tk-multi-publish2/hooks

import traceback
import os
import pprint
import sgtk
import tank as sgtk

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
                "Render Publish Template": {
                    "type": "template",
                    "default": None,
                    "description": "Template path for published work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
                               },
                "Render Work Template": {
                    "type": "template",
                    "default": None,
                    "description": "Template path for work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
                               }, 
                # "File Extensions": {
                #     "type": "str",
                #     "default": None,
                #     "description": "File Extensions of files to include" 
                #     }, 
                "Move Files": {
                    "type": "bool",
                    "default": False,
                    "description": "Move files instead of copying them" 
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

        # We need to check to see if we've labelled this as a rendered image in teh collecotr as
        # playblasts can get caught by this plugin
        if 'publish_type' in item.properties:
            if item.properties['publish_type'] != 'Rendered Image':
                self.logger.info('This is not a Rendered Image')
                return {
                    'accepted': False,
                    'checked': False,
                    'visible': False
                    }


        render_work_template = self.parent.get_template_by_name(settings['Render Work Template'].value)
        publish_template = self.parent.get_template_by_name(settings['Render Publish Template'].value)

        path_fields = render_work_template.validate_and_get_fields(item.properties['path'])

        # publish_template = item.properties['publish_template']
        self.publish_path = publish_template.apply_fields(path_fields)

        # check that file is of correct type
        file_path = item.properties["path"]

        if os.path.exists(self.publish_path):
            error_msg = 'Published File already exists: %s' % (self.publish_path)
            self.logger.error(error_msg)
            return {
                "accepted": True,
                "checked": False,
                'visible': True
                }
        else:
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


        # file_info = publisher.util.get_file_path_components(file_path)
        # self.logger.debug("file_info: %s ", file_info)
        # extension = file_info["extension"].lower()

        # self.logger.debug("File extensions: %s", settings['File Extensions'].value)

        # if extension in settings["File Extensions"].value:
        #     # log the accepted file and display a button to reveal it in the fs
        #     self.logger.info(
        #         "Version upload plugin accepted: %s" % (file_path,),
        #         extra={
        #             "action_show_folder": {
        #                 "path": file_path
        #             }
        #         }
        #     )

        #     # return the accepted info
        #     return {'accepted': True,
        #             'checked': True,
        #             'visible': True
        #            }
        # else:
        #     self.logger.debug(
        #         "%s is not in the valid extensions list for Version creation", extension
        #     )
        #     return {"accepted": False}

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

        self.thumb = item.get_thumbnail_as_path()
        print self.thumb


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

        work_path = item.properties["path"]

        self.logger.debug("Using path info hook to determine publish name.")

        # use the path's filename as the publish name
        path_components = publisher.util.get_file_path_components(work_path)
        publish_name = path_components["filename"]

        self.logger.debug("Publish name: %s", (publish_name,))

        # get the thumbnail that the user selected
        self.thumb = item.get_thumbnail_as_path()

        # set up for PublishedFile publish
        published_file = self.publishPublishedFiles(item)

        # move or copy the published files
        self.moveOrCopyFiles(settings, item)

        # set up for Version publish
        self.logger.info("Creating Version...")

        version_data = {
            "project": item.context.project,
            "code": publish_name,
            "description": item.description,
            "entity": self._get_version_entity(item),
            "sg_task": item.context.task,
            'published_files': [published_file],
            "sg_path_to_frames": self.publish_path,
        }

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

        self.logger.info("Version %s created!", publish_name)

        self.uploadThumbnail(self.thumb, version['id'], "Version")

        # stash the version info in the item just in case
        item.properties["sg_version_data"] = version

        self.logger.info("Render Layer Version publish complete!")


    def uploadThumbnail(self, path, entity_id, entity_type):
        """Uploads thumbnail to shotgunfor specified entity
        return: id of Attachment
        """
        if self.thumb is not None:
            if os.path.exists(path):

                try:
                    self.logger.info("Uploading thumbnail...")
                    thumbnail_id = self.parent.shotgun.upload_thumbnail(
                        entity_type,
                        entity_id,
                        path
                    )
                except sgtk.TankError:
                    self.logger.warn('Error uploading thumbnail to Shotgun: %s' % sgtk.TankError)

            else:
                self.logger.warn('Thumbnail path does not exist: %s' % path)
        else:
            self.logger.info('No thumbnail selected')


    def publishPublishedFiles(self, item):
        """publish all associated files and return a published file entity"""
        publisher = self.parent

        published_file_type = {'type': 'PublishedFileType', 'id': 2}
        published_file_path = {'type': 'Attachment',
                               'link_type': 'local',
                               'local_path': self.publish_path,
                              }

        published_file_data = {
            'project': item.context.project,
            'entity':  item.context.entity,
            'code': os.path.basename(self.publish_path),
            'name': os.path.basename(self.publish_path),
            'description': item.description,
            'path': published_file_path,
            'published_file_type': published_file_type,
            'version_number': item.properties['version'],
            }

        sg_published_file = publisher.shotgun.create("PublishedFile", published_file_data)

        self.uploadThumbnail(self.thumb, sg_published_file['id'], 'PublishedFile')

        return sg_published_file


    def moveOrCopyFiles(self, settings, item):
        """Move or copy folders depending on settings """

        work_folder = os.path.dirname(item.properties['path'])
        publish_folder = os.path.dirname(self.publish_path)

        # Move or copy the work folders to publish area
        if settings["Move Files"].value:
            self.logger.info("Moving Folder...")

            # move the directory
            try:
                sgtk.util.filesystem.ensure_folder_exists(publish_folder, permissions=0755)
                sgtk.util.filesystem.move_folder(work_folder, publish_folder, folder_permissions=0755)
            except Exception, e:
                raise Exception(
                    "Failed to move work folder from '%s' to '%s'.\n%s" %
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


    def finalize(self, settings, item):
        """
        Execute the finalization pass. This pass executes once all the publish
        tasks have completed, and can for example be used to version up files.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """


        version = item.properties["sg_version_data"]
        path = version['sg_path_to_frames']

        self.logger.info(
            "Version data: %s" % version,
            extra={
                "action_show_in_shotgun": {
                    "label": "Show Version",
                    "tooltip": "Reveal the version in Shotgun.",
                    "entity": version}
                }
            )
        self.logger.info(
            "Version path: %s" % (path,),
            extra={
                "action_show_folder": {
                    "label": "Show Folder",
                    "tooltip": "Reveal the version in filesystem.",
                    "path": path
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
