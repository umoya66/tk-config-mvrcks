                # Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

# Copied from tk-maya/hooks/tk-multi-publish2/basic/collector.py

import glob
import os
import maya.cmds as cmds
import maya.mel as mel
import sgtk
# Importing tank for debugging
# import tank as sgtk
# import pprint

HookBaseClass = sgtk.get_hook_baseclass()


class MayaSessionCollector(HookBaseClass):
    """
    Collector that operates on the maya session. Should inherit from the basic
    collector hook.
    """

    @property
    def settings(self):
        """
        Dictionary defining the settings that this collector expects to receive
        through the settings parameter in the process_current_session and
        process_file methods.

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

        # grab any base class settings
        collector_settings = super(MayaSessionCollector, self).settings or {}

        # settings specific to this collector
        maya_session_settings = {
            # This is required for the Maya file publish as we have taken over the original publish
            "Work Template": {
                "type": "template",
                "default": None,
                "description": "Template path for artist Maya work files. Should "
                               "correspond to a template defined in "
                               "templates.yml. If configured, is made available"
                               "to publish plugins via the collected item's "
                               "properties. ",
            },
            "Alembic Template": {
                "type": "template",
                "default": None,
                "description": "Template path for artist Alembic export work files. Should "
                               "correspond to a template defined in "
                               "templates.yml. If configured, is made available"
                               "to publish plugins via the collected item's "
                               "properties. ",
            },
            "Publish Template": {
                "type": "template",
                "default": None,
                "description": "Template path for published Alembic files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
            },
            "File Types": {
                "type": "list",
                "default": [
                    ["Alembic Cache", "abc"],
                    ["Alembic Camera", "abc"],
                    ["Alembic Geo", "abc"],
                    ["Maya Scene", "ma", "mb"],
                    ["Rendered Image", "dpx", "exr"],
                    ["Texture", "tiff", "tx", "tga", "dds"],
                    ["Image", "jpeg", "jpg", "png"],
                    ["Movie", "mov", "mp4"],
                ],
                "description": (
                    "List of file types to include. Each entry in the list "
                    "is a list in which the first entry is the Shotgun "
                    "published file type and subsequent entries are file "
                    "extensions that should be associated."
                )
            },
        }

        # update the base settings with these settings
        collector_settings.update(maya_session_settings)

        icon_path = os.path.join( self.disk_location, os.pardir, "icons", "alembic.png")

        self.common_file_info['Alembic Geo'] = {'item_type': 'file.alembic.geo',
                                                'extensions': ['abc'],
                                                'icon': icon_path}
        self.common_file_info['Alembic Camera'] = {'item_type': 'file.alembic.camera',
                                                   'extensions': ['abc'],
                                                   'icon': icon_path}

        return collector_settings

    def process_current_session(self, settings, parent_item):
        """
        Analyzes the current session open in Maya and parents a subtree of
        items under the parent_item passed in.

        :param dict settings: Configured settings for this collector
        :param parent_item: Root item instance

        """

        # create an item representing the current maya session
        item = self.collect_current_maya_session(settings, parent_item)
        project_root = item.properties["project_root"]

        # if we can determine a project root, collect other files to publish
        if project_root:

            self.logger.info(
                "Current Maya project is: %s." % (project_root,),
                extra={
                    "action_button": {
                        "label": "Change Project",
                        "tooltip": "Change to a different Maya project",
                        "callback": lambda: mel.eval('setProject ""')
                    }
                }
            )

            self.collect_playblasts(item, project_root)
            self.collect_alembic_exports(item, project_root)

        else:

            self.logger.info(
                "Could not determine the current Maya project.",
                extra={
                    "action_button": {
                        "label": "Set Project",
                        "tooltip": "Set the Maya project",
                        "callback": lambda: mel.eval('setProject ""')
                    }
                }
            )

    def collect_current_maya_session(self, settings, parent_item):
        """
        Creates an item that represents the current maya session.

        :param dict settings: Configured settings for this collector
        :param parent_item: Parent Item instance

        :returns: Item of type maya.session
        """

        publisher = self.parent

        # get the path to the current file
        path = cmds.file(query=True, sn=True)

        # determine the display name for the item
        if path:
            file_info = publisher.util.get_file_path_components(path)
            display_name = file_info["filename"]
        else:
            display_name = "Current Maya Session"

        # create the session item for the publish hierarchy
        session_item = parent_item.create_item(
            "maya.session",
            "Maya Session",
            display_name
        )

        # get the icon path to display for this item
        icon_path = os.path.join(
            self.disk_location,
            os.pardir,
            "icons",
            "maya.png"
        )
        session_item.set_icon_from_path(icon_path)

        # discover the project root which helps in discovery of other
        # publishable items
        project_root = cmds.workspace(q=True, rootDirectory=True)
        session_item.properties["project_root"] = project_root

        # if a work template is defined, add it to the item properties so
        # that it can be used by attached publish plugins
        work_template_setting = settings.get("Work Template")
        if work_template_setting:

            work_template = publisher.engine.get_template_by_name(
                work_template_setting.value)

            # store the template on the item for use by publish plugins. we
            # can't evaluate the fields here because there's no guarantee the
            # current session path won't change once the item has been created.
            # the attached publish plugins will need to resolve the fields at
            # execution time.
            session_item.properties["work_template"] = work_template
            self.logger.debug("Work template defined for Maya collection.")

        self.logger.info("Collected current Maya scene")

        return session_item

    def collect_alembic_exports(self, parent_item, project_root):
        """
        Creates items for alembic exports using the Mavericks Export Alembic which
        exports alembics to the directory specified in the template

        Looks for a 'project_root' property on the parent item, and if such
        exists, look for alembic exports in the specified template

        :param parent_item: Parent Item instance
        :param str project_root: The maya project root to search for alembics
        """

        self.logger.info('----- Start collecting Alembics -----')

        # self.logger.debug('self.parent: %s' % dir(self.parent))
        # parent = ['_Application__engine', '_Application__instance_name', '_TankBundle__cache_location',
        #                      '_TankBundle__context', '_TankBundle__descriptor', '_TankBundle__environment',
        #                      '_TankBundle__frameworks', '_TankBundle__log', '_TankBundle__module_uid',
        #                      '_TankBundle__resolve_hook_expression', '_TankBundle__resolve_hook_path',
        #                      '_TankBundle__resolve_setting_value', '_TankBundle__settings', '_TankBundle__sg',
        #                      '_TankBundle__tk', '__class__', '__delattr__', '__dict__', '__doc__', '__format__',
        #                      '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__',
        #                      '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__',
        #                      '__weakref__', '_base_hooks', '_destroy_frameworks', '_get_engine_name',
        #                      '_get_instance_name', '_manager_class', '_set_context', '_set_instance_name',
        #                      '_set_settings', '_util',
        #           'base_hooks', 'cache_location', 'change_context', 'context',
        #                      'context_change_allowed', 'create_hook_instance', 'create_publish_manager', 'description',
        #                      'descriptor', 'destroy_app', 'disk_location', 'display_name', 'documentation_url',
        #                      'engine', 'ensure_folder_exists', 'event_engine', 'event_file_close', 'event_file_open',
        #                      'execute_hook', 'execute_hook_by_name', 'execute_hook_expression', 'execute_hook_method',
        #                      'frameworks', 'get_metrics_properties', 'get_project_cache_location', 'get_setting',
        #                      'get_setting_from', 'get_template', 'get_template_by_name', 'get_template_from',
        #                      'icon_256', 'import_module', 'init_app', 'instance_name', 'log_debug', 'log_error',
        #                      'log_exception', 'log_info', 'log_metric', 'log_warning', 'logger', 'name',
        #                      'post_context_change', 'post_engine_init', 'pre_context_change', 'settings', 'sgtk',
        #                      'shotgun', 'site_cache_location', 'style_constants', 'support_url', 'tank', 'util',
        #                      'version']

        ###################
        # useful functions
        # self.parent.get_template_by_name('template name')  # get template object
        # self.parent.engine  # current engine
        # self.parent.context  # current context
        # self.parent.ensure_folder_exists('path')
        # self.parent.settings()  # returns teh plugin settings from tk-multi-publish2.yml

        # self.logger.debug('settings: %s' % (self.parent.settings))
        # settings = {
        #         'collector_settings': {'Work Template': 'maya_shot_work'}, 
        #         'publish_plugins': [ 
        #             
        #             
        #             {'hook': '{engine}/tk-multi-publish2/basic/start_version_control.py', 
        #             'name': 'Begin file versioning', 
        #             'settings': {}}, 

        #             {'hook': '{self}/publish_file.py:{engine}/tk-multi-publish2/basic/publish_session.py', 
        #                 'name': 'Publish Session to Shotgun', 
        #                 'settings': {'Publish Template': 'maya_shot_publish'}}, 

        #             {'hook': '{config}/tk-multi-publish2/maya/upload_playblast_version.py', 
        #                 'name': 'Publish Playblast', 
        #                 'settings': {}}, 

        #             {'hook': '{self}/publish_file.py:{config}/tk-multi-publish2/maya/publish_exported_alembics.py', 
        #                 'name': 'Publish Exported Alembics', 'settings': {}}
        #             ], 
        #         'collector': '{self}/collector.py:{config}/tk-multi-publish2/maya/collector.py', 
        #         'help_url': 'https://support.shotgunsoftware.com/hc/en-us/articles/115000068574-Integrations-User-Guide#The%20Publisher'}


        # get entity type being published - Shot/Asset/...
        entity_type = self.parent.context.entity['type'].lower()

        # get current maya file path
        current_file_path = cmds.file(query=True, sn=True)

        # get maya file template
        maya_template_path = self.parent.get_template_by_name('maya_' + entity_type + '_work')

        # validate and get all the fields we need for writing out the working file
        path_fields = maya_template_path.validate_and_get_fields(current_file_path)

        output_types = {'alembic': 'geo', 'camera': 'camera'}

        for otype, name in output_types.iteritems():

            # get necessary templates
            working_template_path = self.parent.get_template_by_name('maya_' + entity_type + '_' + otype)
            publish_template_path = self.parent.get_template_by_name('maya_' + entity_type + '_pub_' + otype)

            output_path = working_template_path.apply_fields(path_fields)
            exports_dir = os.path.dirname(output_path)

            alembic_publish_path = publish_template_path.apply_fields(path_fields)

            # check for dir
            if os.path.exists(exports_dir):

                # look for alembic files in the cache folder
                for filename in os.listdir(exports_dir):
                    cache_path = os.path.join(exports_dir, filename)

                    self.logger.info('Adding %s Item: %s' % (otype, filename))

                    mesh_item = parent_item.create_item(
                        "file.alembic." + name,
                        "Alembic " + name.capitalize(),
                        filename
                    )

                    icon_path = os.path.join(
                        self.disk_location,
                        os.pardir,
                        "icons",
                        "abc_" + name + ".png"
                    )

                    # set the icon for the item
                    mesh_item.set_icon_from_path(icon_path)

                    # finally, add information to the mesh item that can be used
                    # by the publish plugin to identify and export it properly
                    mesh_item.properties["object"] = name
                    mesh_item.properties["path"] = cache_path
                    mesh_item.properties["alembic_template"] = working_template_path
                    mesh_item.properties["publish_template"] = publish_template_path
                    mesh_item.properties["publish_type"] = 'Alembic ' + name.capitalize()

                    mesh_item.properties["publish_path"] = alembic_publish_path


                self.logger.info(
                    "Processing alembic exports folder: %s" % (exports_dir,),
                    extra={
                        "action_show_folder": {
                            "path": exports_dir
                        }
                    }
                )


        self.logger.debug('----- Finished with collecting Alembics -----')

    def collect_playblasts(self, parent_item, project_root):
        """
        Creates items for quicktime playblasts.

        Looks for a 'project_root' property on the parent item, and if such
        exists, look for movie files in a 'movies' subfolder.

        :param parent_item: Parent Item instance
        :param str project_root: The maya project root to search for playblasts
        """

        self.logger.debug('-----Start collecting Playblast -----')

        # get entity type
        entity_type = self.parent.context.entity['type'].lower()

        # get necessary templates
        maya_template_path = self.parent.get_template_by_name('maya_' + entity_type + '_work')
        playblast_working_template_path = self.parent.get_template_by_name('maya_' + entity_type + '_playblast')
        playblast_publish_template_path = self.parent.get_template_by_name('maya_' + entity_type + '_pub_playblast')

        # get current maya file path
        current_file_path = cmds.file(query=True, sn=True)

        # validate and get all the fields we need for writing out the working file
        path_fields = maya_template_path.validate_and_get_fields(current_file_path)

        playblast_output_path = playblast_working_template_path.apply_fields(path_fields)
        playblast_exports_dir = os.path.dirname(playblast_output_path)
        playblast_publish_path = playblast_publish_template_path.apply_fields(path_fields)

        self.logger.info(
            "Processing Playblasts exports folder: %s" % (playblast_exports_dir,),
            extra={
                "action_show_folder": {
                    "path": playblast_exports_dir
                }
            }
        )

        if os.path.exists(playblast_output_path):
            # item_info = self._get_item_info(os.path.basename(playblast_output_path))

            # self.logger.debug(item_info)

            # allow the base class to collect and create the item. it knows how
            # to handle movie files
            # item = super(MayaSessionCollector, self)._collect_file(
            #     parent_item,
            #     playblast_output_path
            # )
            item = parent_item.create_item("file.video", "Playblast", os.path.basename(playblast_output_path))

            # the item has been created. update the display name to include
            # the an indication of what it is and why it was collected
            self.logger.debug('Movie Name: %s' % item.name)
            item.name = "%s (%s)" % (item.name, "playblast")

            item.properties["publish_template"] = playblast_publish_template_path
            item.properties["publish_path"] = playblast_publish_path
            item.properties["path"] = playblast_output_path

        self.logger.debug('-----End collecting Playblast -----')

