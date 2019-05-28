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
            "File Extensions": {
                "type": "str",
                "default": "jpeg, jpg, png, mov, mp4",
                "description": "File Extensions of files to include"
            },
            "Upload": {
                "type": "bool",
                "default": True,
                "description": "Upload content to Shotgun?"
            },
            "Link Local File": {
                "type": "bool",
                "default": True,
                "description": "Should the local file be referenced by Shotgun"
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
        return ["file.image", "file.video"]

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
        # self.logger.debug(publisher)
        # self.logger.debug(dir(publisher))
        # publisher = ['_Application__engine', '_Application__instance_name', '_TankBundle__cache_location',
        #               '_TankBundle__context', '_TankBundle__descriptor', '_TankBundle__environment',
        #               '_TankBundle__frameworks', '_TankBundle__log', '_TankBundle__module_uid',
        #               '_TankBundle__resolve_hook_expression', '_TankBundle__resolve_hook_path', '_TankBundle__resolve_setting_value',
        #               '_TankBundle__settings', '_TankBundle__sg', '_TankBundle__tk', '__class__', '__delattr__',
        #               '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__',
        #               '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__',
        #               '__subclasshook__', '__weakref__', '_base_hooks', '_destroy_frameworks', '_get_engine_name',
        #               '_get_instance_name', '_manager_class', '_set_context', '_set_instance_name',
        #               '_set_settings', '_util',
        #               'base_hooks',
        #               'cache_location',
        #               'change_context',
        #               'context',
        #               'context_change_allowed',
        #               'create_hook_instance',
        #               'create_publish_manager',
        #               'description',
        #               'descriptor',
        #               'destroy_app',
        #               'disk_location',
        #               'display_name',
        #               'documentation_url',
        #               'engine',
        #               'ensure_folder_exists',
        #               'event_engine',
        #               'event_file_close',
        #               'event_file_open',
        #               'execute_hook',
        #               'execute_hook_by_name',
        #               'execute_hook_expression',
        #               'execute_hook_method',
        #               'frameworks',
        #               'get_metrics_properties',
        #               'get_project_cache_location',
        #               'get_setting',
        #               'get_setting_from',
        #               'get_template',
        #               'get_template_by_name',
        #               'get_template_from',
        #               'icon_256',
        #               'import_module',
        #               'init_app',
        #               'instance_name',
        #               'log_debug',
        #               'log_error',
        #               'log_exception',
        #               'log_info',
        #               'log_metric',
        #               'log_warning',
        #               'logger',
        #               'name',
        #               'post_context_change',
        #               'post_engine_init',
        #               'pre_context_change',
        #               'settings',
        #               'sgtk',
        #               'shotgun',
        #               'site_cache_location',
        #               'style_constants',
        #               'support_url',
        #               'tank',
        #               'util',
        #               'version']

        # self.logger.debug('base_hooks: %s' % publisher.base_hooks )
        # self.logger.debug('cache_location: %s' % publisher.cache_location )
        # self.logger.debug('change_context: %s' % publisher.change_context )
        # self.logger.debug('context: %s' % publisher.context )
        # self.logger.debug('context_change_allowed: %s' % publisher.context_change_allowed )
        # self.logger.debug('create_hook_instance: %s' % publisher.create_hook_instance )
        # self.logger.debug('create_publish_manager: %s' % publisher.create_publish_manager )
        # self.logger.debug('description: %s' % publisher.description)
        # self.logger.debug('descriptor: %s' % publisher.descriptor)
        # self.logger.debug('destroy_app: %s' % publisher.destroy_app )
        # self.logger.debug('disk_location: %s' % publisher.disk_location )
        # self.logger.debug('display_name: %s' % publisher.display_name )
        # self.logger.debug('documentation_url: %s' % publisher.documentation_url)
        # self.logger.debug('engine: %s' % publisher.engine)
        # self.logger.debug('ensure_folder_exists: %s' % publisher.ensure_folder_exists)
        # self.logger.debug('event_engine: %s' % publisher.event_engine)
        # self.logger.debug('event_file_close: %s' % publisher.event_file_close)
        # self.logger.debug('event_file_open: %s' % publisher.event_file_open)
        # self.logger.debug('execute_hook: %s' % publisher.execute_hook)
        # self.logger.debug('execute_hook_by_name: %s' % publisher.execute_hook_by_name)
        # self.logger.debug('execute_hook_expression: %s' % publisher.execute_hook_expression)
        # self.logger.debug('execute_hook_method: %s' % publisher.execute_hook_method)
        # self.logger.debug('frameworks: %s' % publisher.frameworks)
        # self.logger.debug('get_metrics_properties: %s' % publisher.get_metrics_properties)
        # self.logger.debug('get_project_cache_location: %s' % publisher.get_project_cache_location)
        # self.logger.debug('get_setting: %s' % publisher.get_setting)
        # self.logger.debug('get_setting_from: %s' % publisher.get_setting_from)
        # self.logger.debug('get_template: %s' % publisher.get_template)
        # self.logger.debug('get_template_by_name: %s' % publisher.get_template_by_name)
        # self.logger.debug('get_template_from: %s' % publisher.get_template_from)
        # self.logger.debug('icon_256: %s' % publisher.icon_256)
        # self.logger.debug('import_module: %s' % publisher.import_module)
        # self.logger.debug('init_app: %s' % publisher.init_app)
        # self.logger.debug('instance_name: %s' % publisher.instance_name)
        # self.logger.debug('log_debug: %s' % publisher.log_debug)
        # self.logger.debug('log_error: %s' % publisher.log_error)
        # self.logger.debug('log_exception: %s' % publisher.log_exception)
        # self.logger.debug('log_info: %s' % publisher.log_info)
        # self.logger.debug('log_metric: %s' % publisher.log_metric)
        # self.logger.debug('log_warning: %s' % publisher.log_warning)
        # self.logger.debug('logger: %s' % publisher.logger)
        # self.logger.debug('name: %s' % publisher.name)
        # self.logger.debug('post_context_change: %s' % publisher.post_context_change)
        # self.logger.debug('post_engine_init: %s' % publisher.post_engine_init)
        # self.logger.debug('pre_context_change: %s' % publisher.pre_context_change)

        # self.logger.debug('settings: %s' % publisher.settings)
        # settings = {'collector_settings': {'Work Template': 'maya_shot_work'},

        #             'publish_plugins': [{'hook': '{engine}/tk-multi-publish2/basic/start_version_control.py',
        #                                  'name': 'Begin file versioning',
        #                                  'settings': {}},

        #                                 {'hook': '{self}/publish_file.py:{engine}/tk-multi-publish2/basic/publish_session.py',
        #                                  'name': 'Publish Session to Shotgun',
        #                                  'settings': {'Publish Template': 'maya_shot_publish'}},

        #                                 {'hook': '{config}/tk-multi-publish2/maya/upload_playblast_version.py',
        #                                  'name': 'Publish Playblast',
        #                                  'settings': {}},

        #                                 {'hook': '{self}/publish_file.py:{config}/tk-multi-publish2/maya/publish_exported_alembics.py',
        #                                  'name': 'Publish Exported Alembics',
        #                                  'settings': {}}],

        #             'collector': '{self}/collector.py:{config}/tk-multi-publish2/maya/collector.py',
        #             'help_url': 'https://support.shotgunsoftware.com/hc/en-us/articles/115000068574-Integrations-User-Guide#The%20Publisher'}

        # self.logger.debug('get_setting_from: %s' % publisher.get_setting_from)
        # self.logger.debug('get_template: %s' % ((publisher.get_template('maya_shot_playblast'))))
        # self.logger.debug('get_template_by_name: %s' % publisher.get_template_by_name('maya_shot_playblast'))
        # self.logger.debug('get_template_from: %s' % publisher.get_template_from)

        # self.logger.debug('sgtk: %s' % publisher.sgtk)
        # self.logger.debug('shotgun: %s' % publisher.shotgun)
        # self.logger.debug('site_cache_location: %s' % publisher.site_cache_location)
        # self.logger.debug('style_constants: %s' % publisher.style_constants)
        # self.logger.debug('support_url: %s' % publisher.support_url)
        # self.logger.debug('tank: %s' % publisher.tank)
        # self.logger.debug('util: %s' % publisher.util)
        # self.logger.debug('version: %s' % publisher.version)

        # Check that this file has not been published already

        item_list = pprint.pformat(dir(item))

        self.logger.debug(dir(item))

        # item = ['__class__', '__del__', '__delattr__', '__doc__', '__format__', '__getattribute__', '__hash__',
        #         '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__',
        #         '__sizeof__', '__slots__', '__str__', '__subclasshook__', '_active', '_allows_context_change',
        #         '_children', '_context', '_created_temp_files', '_current_temp_file_path', '_description', '_enabled',
        #         '_expanded', '_get_image', '_get_local_properties', '_get_type', '_global_properties', '_icon_path',
        #         '_icon_pixmap', '_local_properties', '_name', '_parent', '_persistent', '_set_type', '_tasks',
        #         '_thumbnail_enabled', '_thumbnail_explicit', '_thumbnail_path', '_thumbnail_pixmap', '_traverse_item',
        #         '_type_display', '_type_spec', '_validate_image', '_visit_recursive',
        #         'active', 'add_task', 'checked',
        #         'children', 'clear_tasks', 'context', 'context_change_allowed', 'create_item', 'descendants',
        #         'description', 'display_type', 'enabled', 'expanded', 'from_dict', 'get_property',
        #         'get_thumbnail_as_path', 'icon', 'is_root', 'local_properties', 'name', 'parent', 'persistent',
        #         'properties', 'remove_item', 'set_icon_from_path', 'set_thumbnail_from_path', 'tasks', 'thumbnail',
        #         'thumbnail_enabled', 'thumbnail_explicit', 'to_dict', 'type', 'type_display', 'type_spec']

        self.logger.debug('item properties: %s' % item.properties)

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
        extension = file_info["extension"].lower()

        valid_extensions = []

        for ext in settings["File Extensions"].value.split(","):
            ext = ext.strip().lstrip(".")
            valid_extensions.append(ext)

        self.logger.debug("Valid extensions: %s" % valid_extensions)

        if extension in valid_extensions:
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
        path = item.properties["path"]

        # allow the publish name to be supplied via the item properties. this is
        # useful for collectors that have access to templates and can determine
        # publish information about the item that doesn't require further, fuzzy
        # logic to be used here (the zero config way)
        publish_name = item.properties.get("publish_name")
        if not publish_name:

            self.logger.debug("Using path info hook to determine publish name.")

            # use the path's filename as the publish name
            path_components = publisher.util.get_file_path_components(path)
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

        if "sg_publish_data" in item.properties:
            publish_data = item.properties["sg_publish_data"]
            version_data["published_files"] = [publish_data]

        if settings["Link Local File"].value:
            version_data["sg_path_to_movie"] = path

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
