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
import tank as sgtk
import pprint

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
            "Camera Work Template": {
                "type": "template",
                "default": None,
                "description": "Template path for artist Alembic export work files. Should "
                               "correspond to a template defined in "
                               "templates.yml. If configured, is made available"
                               "to publish plugins via the collected item's "
                               "properties. ",
            },
            "Alembic Work Template": {
                "type": "template",
                "default": None,
                "description": "Template path for artist Alembic export work files. Should "
                               "correspond to a template defined in "
                               "templates.yml. If configured, is made available"
                               "to publish plugins via the collected item's "
                               "properties. ",
            },
            "Render Work Template": {
                "type": "template",
                "default": None,
                "description": "Template path for artist Alembic export work files. Should "
                               "correspond to a template defined in "
                               "templates.yml. If configured, is made available"
                               "to publish plugins via the collected item's "
                               "properties. ",
            },
            # "Publish Template": {
            #     "type": "template",
            #     "default": None,
            #     "description": "Template path for published Alembic files. Should"
            #                    "correspond to a template defined in "
            #                    "templates.yml.",
            # },
            # "File Types": {
            #     "type": "list",
            #     "default": [
            #         ["Alembic Cache", "abc"],
            #         ["Alembic Camera", "abc"],
            #         ["Alembic Geo", "abc"],
            #         ["Maya Scene", "ma", "mb"],
            #         ["Rendered Image", "dpx", "exr"],
            #         ["Texture", "tiff", "tx", "tga", "dds"],
            #         ["Image", "jpeg", "jpg", "png"],
            #         ["Movie", "mov", "mp4"],
            #     ],
            #     "description": (
            #         "List of file types to include. Each entry in the list "
            #         "is a list in which the first entry is the Shotgun "
            #         "published file type and subsequent entries are file "
            #         "extensions that should be associated."
            #     )
            # },
        }

        # update the base settings with these settings
        collector_settings.update(maya_session_settings)

        icon_path = self._get_icon_path("image_sequence.png")

        self.common_file_info['Alembic Geo'] = {'item_type': 'file.alembic.geo',
                                                'extensions': ['abc'],
                                                'icon': icon_path}
        self.common_file_info['Alembic Camera'] = {'item_type': 'file.alembic.camera',
                                                   'extensions': ['abc'],
                                                   'icon': icon_path}
        self.common_file_info['Rendered Image'] = { "extensions": ["dpx", "exr"], 
                "icon": self._get_icon_path("image_sequence.png"),
                "item_type": "file.image", 
                }

        return collector_settings

    def process_current_session(self, settings, parent_item):
        """
        Analyzes the current session open in Maya and parents a subtree of
        items under the parent_item passed in.

        :param dict settings: Configured settings for this collector
        :param parent_item: Root item instance

        """

        self.logger.debug('Collector Settings ---')
        for k,v in settings.iteritems():
            self.logger.debug('\t%s: %s' % (k, v.value))

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
            
            self.logger.debug('Collector Settings ---')
            for k,v in settings.iteritems():
                self.logger.debug('\t%s: %s' % (k, v.value))

            self.collect_playblasts(item, project_root)
            self.collect_alembic_exports(item, project_root)
            
            # look at the render layers to find rendered images on disk
            # self.collect_rendered_images(item, project_root)
            self.collect_renders(item, project_root, settings)

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

        self.logger.info('-----Start with collecting Alembics  xx-----')

        # get sgtk engine
        eng = sgtk.platform.current_engine()

        # get context
        ctx = eng.context

        # get toolkit
        tk = ctx.sgtk

        # get necessary templates

        # maya_template_path = ''
        # abc_working_template_path = ''
        
        entity_type = ctx.entity['type'].lower()

        maya_template_path = tk.templates['maya_' + entity_type + '_work']
        abc_working_template_path = tk.templates['maya_' + entity_type + '_alembic']
        abc_publish_template_path = tk.templates['maya_' + entity_type + '_pub_alembic']
        cam_working_template_path = tk.templates['maya_' + entity_type + '_camera']
        cam_publish_template_path = tk.templates['maya_' + entity_type + '_pub_camera']

        # get current maya file path
        current_file_path = cmds.file(query=True, sn=True)

        # validate and get all the fields we need for writing out the working file
        path_fields = maya_template_path.validate_and_get_fields(current_file_path)

        if path_fields is not None:
            abc_output_path = abc_working_template_path.apply_fields(path_fields)
            abc_exports_dir = os.path.dirname(abc_output_path)
            cam_output_path = cam_working_template_path.apply_fields(path_fields)
            cam_exports_dir = os.path.dirname(cam_output_path)

        self.logger.debug("Alembic Geo working template path: %s" % (abc_working_template_path))
        self.logger.debug("Alembic Camera working template path: %s" % (cam_working_template_path))

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

        # check for geo dir
        if os.path.exists(abc_exports_dir):
            self.logger.debug('Alembic Geo directory exists')

        # look for alembic files in the cache folder
            for filename in os.listdir(abc_exports_dir):
                cache_path = os.path.join(abc_exports_dir, filename)

                # # do some early pre-processing to ensure the file is of the right
                # # type. use the base class item info method to see what the item
                # # type would be.
                # item_info = self._get_item_info(filename)
                # if item_info["item_type"] != "file.alembic.geo":
                #     continue

                self.logger.info('Adding Alembic Geo Item: %s' % (filename))

                # allow the base class to collect and create the item. it knows how
                # to handle alembic files
                # super(MayaSessionCollector, self)._collect_file(parent_item, cache_path)

                mesh_item = parent_item.create_item(
                    "file.alembic.geo",
                    "Alembic Geo",
                    filename
                )

                icon_path = os.path.join(
                    self.disk_location,
                    os.pardir,
                    "icons",
                    "maps-pin.png"
                )

                # set the icon for the item
                mesh_item.set_icon_from_path(icon_path)

                # finally, add information to the mesh item that can be used
                # by the publish plugin to identify and export it properly
                mesh_item.properties["object"] = 'geo'
                mesh_item.properties["path"] = cache_path
                mesh_item.properties["alembic_template"] = abc_working_template_path
                mesh_item.properties["publish_template"] = abc_publish_template_path
                mesh_item.properties["publish_type"] = 'Alembic Geo'

        # check for cam dir
        if os.path.exists(cam_exports_dir):
            self.logger.debug('Alembic Camera directory exists')

        # look for Camera alembics files in the cache folder
            for filename in os.listdir(cam_exports_dir):
                self.logger.debug(filename)
                cache_path = os.path.join(cam_exports_dir, filename)

                # # do some early pre-processing to ensure the file is of the right
                # # type. use the base class item info method to see what the item
                # # type would be.
                # item_info = self._get_item_info(filename)
                # if item_info["item_type"] != "file.alembic.camera":
                #     self.logger.debug('Not a camera')
                #     continue

                self.logger.info('Adding Alembic Camera Item: %s' % (filename))

                # allow the base class to collect and create the item. it knows how
                # to handle alembic files
                # super(MayaSessionCollector, self)._collect_file(parent_item, cache_path)

                mesh_item = parent_item.create_item(
                    "file.alembic.camera",
                    "Alembic Camera",
                    filename
                )

                icon_path = os.path.join(
                    self.disk_location,
                    os.pardir,
                    "icons",
                    "camera-flash.png"

                )

                # set the icon for the item
                mesh_item.set_icon_from_path(icon_path)

                # finally, add information to the mesh item that can be used
                # by the publish plugin to identify and export it properly
                mesh_item.properties["object"] = 'camera'
                mesh_item.properties["path"] = cache_path
                mesh_item.properties["alembic_template"] = cam_working_template_path
                mesh_item.properties["publish_template"] = cam_publish_template_path
                mesh_item.properties["publish_type"] = 'Alembic Camera'

        self.logger.debug('-----Finished with collecting Alembics -----')

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

    def collect_renders(self, parent_item, project_root, settings):
        """
        Creates items for Renders - ported from collect_playblasts.

        Looks for a 'project_root' property on the parent item, and if such
        exists, look for rendered sequences in the subfolder.

        :param parent_item: Parent Item instance
        :param str project_root: The maya project root to search for renders
        """

        self.logger.info('-----Start collecting Renders -----')

        # get context
        # ctx = self.parent.context

        # get entity type
        # entity_type = ctx.entity['type'].lower()

        # get necessary templates
        # maya_template_path = self.parent.get_template_by_name('maya_' + entity_type + '_work')
        maya_template_path = self.parent.get_template_by_name(settings["Work Template"].value)
        # render_working_template_path = self.parent.get_template_by_name('maya_' + entity_type + '_render')
        render_working_template_path = self.parent.get_template_by_name(settings['Render Work Template'].value)
        # render_publish_template_path = self.parent.get_template_by_name('maya_' + entity_type + '_render_pub')
        # render_publish_template_path = self.parent.get_template_by_name(settings.get('Render Publish Template'))

        # get current maya file path
        current_file_path = cmds.file(query=True, sn=True)

        # get and validate all the fields we need for writing out the working file
        path_fields = maya_template_path.validate_and_get_fields(current_file_path)

        seq = self.parent.get_template_by_name('SEQ')
        self.logger.info('SEQ: %s', seq)

        self.logger.debug('Path fields: %s ' % path_fields)

        if path_fields is None:
            self.logger.warn('No valid template paths')
            return

        # process each render layer
        for layer in cmds.ls(type="renderLayer"):

            self.logger.info("Processing render layer: %s", (layer,))

            path_fields['layer'] = layer

            render_output_path = render_working_template_path.apply_fields(path_fields)

            # get the SEQ key value from tempate eg. "%04d"
            SEQ_key = render_working_template_path.keys['SEQ'].str_from_value()

            self.logger.debug('SEQ: %s', SEQ_key)

            # render_exports_dir = os.path.dirname(render_output_path)
            # render_publish_path = render_publish_template_path.apply_fields(path_fields)

            self.logger.info('Render Path: %s', render_output_path)

            # we need to replace the SEQ key for proper file globbing
            self.logger.debug('glob path: %s', render_output_path.replace(SEQ_key, "*"))
            frame_glob = glob.glob(render_output_path.replace(SEQ_key, "*"))

            self.logger.debug('frame glob: %s', frame_glob)

            # set up for publishing if we find frames
            if frame_glob:
                # item_info = self._get_item_info(os.path.basename(frame_glob[0]))

                # allow the base class to collect and create the item. it knows how
                # to handle movie files
                item = super(MayaSessionCollector, self)._collect_file(
                    parent_item,
                    render_output_path
                )

                # the item has been created. update the display name to include
                # the an indication of what it is and why it was collected
                # item.name = "%s (%s)" % (item.name, "Rendered Image")
                item.name = "%s (Render Layer: %s)" % (item.name, layer)
                # self.logger.debug('Render Name: %s' % item.name)

                # item.properties["publish_template"] = render_publish_template_path
                # item.properties["publish_path"] = render_publish_path
                item.properties["frame_list"] = frame_glob
                item.properties["publish_type"] = 'Rendered Image'
                item.properties["version"] = path_fields['version']
                item.properties["path"] = render_output_path

                # self.logger.debug('publish_path: %s' % item.properties['publish_path'])
            else:
                self.logger.debug('No frames found')

        self.logger.info('-----End collecting Renders -----')

    def collect_playblasts(self, parent_item, project_root):
        """
        Creates items for quicktime playblasts.

        Looks for a 'project_root' property on the parent item, and if such
        exists, look for movie files in a 'movies' subfolder.

        :param parent_item: Parent Item instance
        :param str project_root: The maya project root to search for playblasts
        """

        self.logger.info('-----Start collecting Playblast -----')

        # get context
        ctx = self.parent.context

        # get entity type
        entity_type = ctx.entity['type'].lower()

        # get necessary templates
        maya_template_path = self.parent.get_template_by_name('maya_' + entity_type + '_work')
        playblast_working_template_path = self.parent.get_template_by_name('maya_' + entity_type + '_playblast')
        playblast_publish_template_path = self.parent.get_template_by_name('maya_' + entity_type + '_pub_playblast')

        # get current maya file path
        current_file_path = cmds.file(query=True, sn=True)

        # validate and get all the fields we need for writing out the working file
        path_fields = maya_template_path.validate_and_get_fields(current_file_path)

        if path_fields is not None:
            playblast_output_path = playblast_working_template_path.apply_fields(path_fields)
            playblast_exports_dir = os.path.dirname(playblast_output_path)
            playblast_publish_path = playblast_publish_template_path.apply_fields(path_fields)

        self.logger.debug("Playblast working template path: %s" % (playblast_working_template_path))
        self.logger.debug(playblast_output_path)

        self.logger.info(
            "Processing Playblasts exports folder: %s" % (playblast_exports_dir,),
            extra={
                "action_show_folder": {
                    "path": playblast_exports_dir
                }
            }
        )

        if os.path.exists(playblast_output_path):
            item_info = self._get_item_info(os.path.basename(playblast_output_path))

            self.logger.debug(item_info)

            # allow the base class to collect and create the item. it knows how
            # to handle movie files
            item = super(MayaSessionCollector, self)._collect_file(
                parent_item,
                playblast_output_path
            )

            # the item has been created. update the display name to include
            # the an indication of what it is and why it was collected
            self.logger.debug('Movie Name: %s' % item.name)
            item.name = "%s (%s)" % (item.name, "playblast")

            # item.properties["publish_template"] = playblast_publish_template_path
            # item.properties["publish_path"] = playblast_publish_path
            item.properties["publish_type"] = "Playblast"

            # self.logger.debug('publish_path: %s' % item.properties['publish_path'])
            

        self.logger.info('-----End collecting Playblast -----')

