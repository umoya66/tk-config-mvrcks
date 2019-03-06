﻿# Copyright (c) 2017 Shotgun Software Inc.
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
import tank as sgtk

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
        }

        # update the base settings with these settings
        collector_settings.update(maya_session_settings)

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

            # self.collect_playblasts(item, project_root)
            # self.collect_alembic_caches(item, project_root)
            self.collect_alembic_exports(item, project_root)
            # self.collect_alembic_cameras(item, project_root)
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

        # look at the render layers to find rendered images on disk
        # self.collect_rendered_images(item)
        # self._collect_meshes(item)

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

        self.logger.info('-----Start with collecting Alembics -----')

        # get sgtk engine
        eng = sgtk.platform.current_engine()

        # get context
        ctx = eng.context

        # get toolkit
        tk = ctx.sgtk

        # get necessary templates

        maya_file = ''
        abc_working_template_path = ''

        if ctx.entity['type'] == 'Asset':
            maya_file = tk.templates['maya_asset_work']
            abc_working_template_path = tk.templates["maya_asset_alembic"]
            abc_publish_template_path = tk.templates["maya_asset_pub_alembic"]
            cam_working_template_path = tk.templates["maya_asset_camera"]
            cam_publish_template_path = tk.templates["maya_asset_pub_camera"]

        elif ctx.entity['type'] == 'Shot':
            maya_file = tk.templates['maya_shot_work']
            abc_working_template_path = tk.templates["maya_shot_alembic"]
            abc_publish_template_path = tk.templates["maya_shot_pub_alembic"]
            cam_working_template_path = tk.templates["maya_shot_camera"]
            cam_publish_template_path = tk.templates["maya_shot_pub_camera"]

        else:
            pass

        # get current maya file path
        current_file_path = cmds.file(query=True, sn=True)

        # validate and get all the fields we need for writing out the working file
        path_fields = maya_file.validate_and_get_fields(current_file_path)

        if path_fields is not None:
            abc_output_path = abc_working_template_path.apply_fields(path_fields)
            abc_exports_dir = os.path.dirname(abc_output_path)
            cam_output_path = cam_working_template_path.apply_fields(path_fields)
            cam_exports_dir = os.path.dirname(cam_output_path)

        # self.logger.info("Output Path: %s" % (abc_output_path))
        # self.logger.info("maya file: %s" % (maya_file))
        self.logger.info("ABC working template path: %s" % (abc_working_template_path))
        self.logger.info("CAM working template path: %s" % (cam_working_template_path))

        self.logger.info(
            "Processing alembic exports folder: %s" % (abc_exports_dir,),
            extra={
                "action_show_folder": {
                    "path": abc_exports_dir
                }
            }
        )
        self.logger.info(
            "Processing camera exports folder: %s" % (cam_exports_dir,),
            extra={
                "action_show_folder": {
                    "path": cam_exports_dir
                }
            }
        )
        
        icon_path = os.path.join(
            self.disk_location,
            os.pardir,
            "icons",
            "mesh.png"
        )

        # look for alembic files in the cache folder
        for filename in os.listdir(abc_exports_dir):
            cache_path = os.path.join(abc_exports_dir, filename)

            # do some early pre-processing to ensure the file is of the right
            # type. use the base class item info method to see what the item
            # type would be.
            item_info = self._get_item_info(filename)
            if item_info["item_type"] != "file.alembic":
                continue

            self.logger.info('Adding Alembic Item: %s' % (filename))

            # allow the base class to collect and create the item. it knows how
            # to handle alembic files
            # super(MayaSessionCollector, self)._collect_file(parent_item, cache_path)

            mesh_item = parent_item.create_item(
                "file.alembic",
                "Mesh",
                filename
            )

            # set the icon for the item
            mesh_item.set_icon_from_path(icon_path)

            # finally, add information to the mesh item that can be used
            # by the publish plugin to identify and export it properly
            mesh_item.properties["object"] = 'geo'
            mesh_item.properties["path"] = cache_path
            mesh_item.properties["alembic_template"] = abc_working_template_path
            mesh_item.properties["publish_template"] = abc_publish_template_path


        # look for Camera alembics files in the cache folder
        for filename in os.listdir(cam_exports_dir):
            cache_path = os.path.join(cam_exports_dir, filename)

            # do some early pre-processing to ensure the file is of the right
            # type. use the base class item info method to see what the item
            # type would be.
            item_info = self._get_item_info(filename)
            if item_info["item_type"] != "file.alembic":
                continue

            self.logger.info('Adding Camera Item: %s' % (filename))

            # allow the base class to collect and create the item. it knows how
            # to handle alembic files
            # super(MayaSessionCollector, self)._collect_file(parent_item, cache_path)

            mesh_item = parent_item.create_item(
                "file.alembic",
                "Alembic",
                filename
            )

            # set the icon for the item
            mesh_item.set_icon_from_path(icon_path)

            # finally, add information to the mesh item that can be used
            # by the publish plugin to identify and export it properly
            mesh_item.properties["object"] = 'camera'
            mesh_item.properties["path"] = cache_path
            mesh_item.properties["alembic_template"] = cam_working_template_path
            mesh_item.properties["publish_template"] = cam_publish_template_path

        self.logger.info('-----Finished with collecting Alembics -----')

    def collect_alembic_caches(self, parent_item, project_root):
        """
        Creates items for alembic caches

        Looks for a 'project_root' property on the parent item, and if such
        exists, look for alembic caches in a 'cache/alembic' subfolder.

        :param parent_item: Parent Item instance
        :param str project_root: The maya project root to search for alembics
        """

        # ensure the alembic cache dir exists
        cache_dir = os.path.join(project_root, "cache", "alembic")
        if not os.path.exists(cache_dir):
            return

        self.logger.info(
            "Processing alembic cache folder: %s" % (cache_dir,),
            extra={
                "action_show_folder": {
                    "path": cache_dir
                }
            }
        )

        # look for alembic files in the cache folder
        for filename in os.listdir(cache_dir):
            cache_path = os.path.join(cache_dir, filename)

            # do some early pre-processing to ensure the file is of the right
            # type. use the base class item info method to see what the item
            # type would be.
            item_info = self._get_item_info(filename)
            if item_info["item_type"] != "file.alembic":
                continue

            # allow the base class to collect and create the item. it knows how
            # to handle alembic files
            super(MayaSessionCollector, self)._collect_file(
                parent_item,
                cache_path
            )

    def _collect_session_geometry(self, parent_item):
        """
        Creates items for session geometry to be exported.

        :param parent_item: Parent Item instance
        """

        geo_item = parent_item.create_item(
            "maya.session.geometry",
            "Geometry",
            "All Session Geometry"
        )

        # get the icon path to display for this item
        icon_path = os.path.join(
            self.disk_location,
            os.pardir,
            "icons",
            "geometry.png"
        )

        geo_item.set_icon_from_path(icon_path)

    def collect_playblasts(self, parent_item, project_root):
        """
        Creates items for quicktime playblasts.

        Looks for a 'project_root' property on the parent item, and if such
        exists, look for movie files in a 'movies' subfolder.

        :param parent_item: Parent Item instance
        :param str project_root: The maya project root to search for playblasts
        """

        movie_dir_name = None

        # try to query the file rule folder name for movies. This will give
        # us the directory name set for the project where movies will be
        # written
        if "movie" in cmds.workspace(fileRuleList=True):
            # this could return an empty string
            movie_dir_name = cmds.workspace(fileRuleEntry='movie')

        if not movie_dir_name:
            # fall back to the default
            movie_dir_name = "movies"

        # ensure the movies dir exists
        movies_dir = os.path.join(project_root, movie_dir_name)
        if not os.path.exists(movies_dir):
            return

        self.logger.info(
            "Processing movies folder: %s" % (movies_dir,),
            extra={
                "action_show_folder": {
                    "path": movies_dir
                }
            }
        )

        # look for movie files in the movies folder
        for filename in os.listdir(movies_dir):

            # do some early pre-processing to ensure the file is of the right
            # type. use the base class item info method to see what the item
            # type would be.
            item_info = self._get_item_info(filename)
            if item_info["item_type"] != "file.video":
                continue

            movie_path = os.path.join(movies_dir, filename)

            # allow the base class to collect and create the item. it knows how
            # to handle movie files
            item = super(MayaSessionCollector, self)._collect_file(
                parent_item,
                movie_path
            )

            # the item has been created. update the display name to include
            # the an indication of what it is and why it was collected
            item.name = "%s (%s)" % (item.name, "playblast")

    def collect_rendered_images(self, parent_item):
        """
        Creates items for any rendered images that can be identified by
        render layers in the file.

        :param parent_item: Parent Item instance
        :return:
        """

        # iterate over defined render layers and query the render settings for
        # information about a potential render
        for layer in cmds.ls(type="renderLayer"):

            self.logger.info("Processing render layer: %s" % (layer,))

            # use the render settings api to get a path where the frame number
            # spec is replaced with a '*' which we can use to glob
            (frame_glob,) = cmds.renderSettings(
                genericFrameImageName="*",
                fullPath=True,
                layer=layer
            )

            # see if there are any files on disk that match this pattern
            rendered_paths = glob.glob(frame_glob)

            if rendered_paths:
                # we only need one path to publish, so take the first one and
                # let the base class collector handle it
                item = super(MayaSessionCollector, self)._collect_file(
                    parent_item,
                    rendered_paths[0],
                    frame_sequence=True
                )

                # the item has been created. update the display name to include
                # the an indication of what it is and why it was collected
                item.name = "%s (Render Layer: %s)" % (item.name, layer)

    def _collect_meshes(self, parent_item):
        """
        Collect mesh definitions and create publish items for them.

        Added this function from
        https://support.shotgunsoftware.com/hc/en-us/articles/219039938-Pipeline-Tutorial#Create%20a%20shader%20publish%20plugin

        :param parent_item: The maya session parent item
        """

        # build a path for the icon to use for each item. the disk
        # location refers to the path of this hook file. this means that
        # the icon should live one level above the hook in an "icons"
        # folder.

        icon_path = os.path.join(
            self.disk_location,
            os.pardir,
            "icons",
            "mesh.png"
        )

        # iterate over all top-level transforms and create mesh items
        # for any mesh.

        for object in cmds.ls(assemblies=True):

            if not cmds.ls(object, dag=True, type="mesh"):
                # ignore non-meshes
                continue

            # create a new item parented to the supplied session item. We
            # define an item type (maya.session.mesh) that will be
            # used by an associated shader publish plugin as it searches for
            # items to act upon. We also give the item a display type and
            # display name (the group name). In the future, other publish
            # plugins might attach to these mesh items to publish other things

            mesh_item = parent_item.create_item(
                "maya.session.mesh",
                "Mesh",
                object
            )

            # set the icon for the item
            mesh_item.set_icon_from_path(icon_path)

            # finally, add information to the mesh item that can be used
            # by the publish plugin to identify and export it properly
            mesh_item.properties["object"] = object