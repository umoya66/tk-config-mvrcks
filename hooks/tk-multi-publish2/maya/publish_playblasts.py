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
from sgtk.platform.qt import QtCore
# import tank as sgtk for debugging
import tank as sgtk
from tank.platform.qt import QtCore

HookBaseClass = sgtk.get_hook_baseclass()


class MayaPlayblastPublishPlugin(HookBaseClass):
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
        <p>This plugin publishes previously created playblast quicktime for the current session. Please use 
        the Mavericks Playblast Shotgun export tool.
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
        base_settings = super(MayaPlayblastPublishPlugin, self).settings or {}

        # settings specific to this class
        maya_publish_settings = {
            "PB Publish Template": {
                "type": "template",
                "default": None,
                "description": "Template path for published work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
            },
            "PB Work Template": {
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

        accepted = True
        publisher = self.parent
        publish_template_name = settings["Publish Template"].value
        work_template_name = settings["Alembic Template"].value

        self.logger.info(
            'Work template name: %s    \n '
            'publish template name: %s ' % (work_template_name, publish_template_name)
        )

        # ensure the publish template is defined and valid and that we also have
        work_template = publisher.get_template_by_name(work_template_name)
        publish_template = publisher.get_template_by_name(publish_template_name)
        if not publish_template:
            self.logger.debug(
                "The valid publish template could not be determined for the "
                "session geometry item. Not accepting the item."
            )
            accepted = False
        else:
            self.logger.info(
                'Publish Template: %s \n'
                'Work Template: %s ' % (publish_template, work_template)
            )

        # we've validated the publish template. add it to the item properties
        # for use in subsequent methods

        local_properties = ['_MutableMapping__marker', '__abstractmethods__', '__class__', '__contains__', '__delattr__', '__delitem__',
         '__dict__', '__doc__', '__eq__', '__format__', '__getattribute__', '__getitem__', '__hash__', '__init__',
         '__iter__', '__len__', '__metaclass__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__',
         '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__',
         '_abc_cache', '_abc_negative_cache', '_abc_negative_cache_version', '_abc_registry', 'clear', 'from_dict',
         'get', 'items', 'iteritems', 'iterkeys', 'itervalues', 'keys', 'pop', 'popitem', 'setdefault', 'to_dict',
         'update', 'values']

        item.properties["publish_template"] = publish_template
        item.properties["alembic_template"] = work_template

        self.logger.info('------------- Item Properties --------------------')
        self.logger.info(dir(item.local_properties.items))
        self.logger.info(dir(item.properties.items))

        # Because a publish template is configured, disable context change. This
        # is a temporary measure until the publisher handles context switching
        # natively.
        item.context_change_allowed = False

        return {
            "accepted": accepted,
            "checked": True
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

        sg_publish_data = item.properties.get("sg_publish_data")
        if sg_publish_data is None:
            raise Exception("'sg_publish_data' was not found in the item's properties. "
                            "Review Submission for '%s' failed. This property must "
                            "be set by a publish plugin that has run before this one." % render_path)


        self.logger.info('--------- Publish Data ---------')
        self.logger.info(sg_publish_data)


        # Check if published files exist
        if os.path.exists(publish_path):
            error_msg = 'Published File already exists: %s' % (publish_path)
            self.logger.error(error_msg)
            raise Exception(error_msg)

        self.logger.info("Work Path: %s" % (alembic_path))
        self.logger.info("Publish Path: %s" % (publish_path))

        self.logger.info("working template path: %s" % (work_template))
        self.logger.info("publish template path: %s" % (publish_template))

        return True

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """

        render_path = item.properties.get("path")

        sg_publish_data = item.properties.get("sg_publish_data")
        if sg_publish_data is None:
            raise Exception("'sg_publish_data' was not found in the item's properties. "
                            "Review Submission for '%s' failed. This property must "
                            "be set by a publish plugin that has run before this one." % render_path)
        sg_task = self.parent.context.task
        comment = item.description
        thumbnail_path = item.get_thumbnail_as_path()
        progress_cb = lambda *args, **kwargs: None



        # THIS IS FOR NUKE ONLY.....

        # I will need to recreate the subit from tk-multi-reviewsubmission
        # or just a plain old manual submit
        # submit_version from 
        # tk-multi-reviewsubmission/python/tk_multi_reviewsubmission/submitter.py

        review_submission_app = self.parent.engine.apps.get("tk-multi-reviewsubmission")

        render_template = item.properties.get("alembic_template")
        if render_template is None:
            raise Exception("'work_template' property is missing from item's properties. "
                            "Review submission for '%s' failed." % render_path)
        publish_template = item.properties.get("publish_template")
        if publish_template is None:
            raise Exception("'publish_template' property not found on item. "
                            "Review submission for '%s' failed." % render_path)
        if not render_template.validate(render_path):
            raise Exception("'%s' did not match the render template. "
                            "Review submission failed." % render_path)

        render_path_fields = render_template.get_fields(render_path)
        # first_frame = item.properties.get("first_frame")
        # last_frame = item.properties.get("last_frame")
        first_frame = int(cmds.getAttr('defaultRenderGlobals.startFrame'))
        last_frame = int(cmds.getAttr('defaultRenderGlobals.endFrame'))

        # version = review_submission_app.render_and_submit_version(
        version = _submit_version(publish_template,
                                  render_path_fields,
                                  first_frame,
                                  last_frame,
                                  sg_publish_data,
                                  sg_task,
                                  comment,
                                  thumbnail_path,
                                  render_path
                                  )
        if version:
            self.logger.info(
                "Version uploaded for file: %s" % (render_path,),
                extra={
                    "action_show_in_shotgun": {
                        "label": "Show Version",
                        "tooltip": "Reveal the version in Shotgun.",
                        "entity": version
                    }
                }
            )
        else:
            raise Exception("Review submission failed. Could not render and "
                            "submit the review associated sequence.")

    def publish_OLD(self, settings, item):
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
        super(MayaPlayblastPublishPlugin, self).publish(settings, item)


def _submit_version_b():
    publish = sgtk.util.register_publish(tk, context, file_path, name, version_number,
                                         comment='Initial layout composition.', published_file_type='Maya Scene')


def _submit_version(publish_template,
                    render_path_fields,
                    first_frame,
                    last_frame,
                    sg_publish_data,
                    sg_task,
                    comment,
                    thumbnail_path,
                    path_to_movie):
    # def submit_version(self, path_to_frames, path_to_movie, thumbnail_path, sg_publishes,
    #                   sg_task, comment, store_on_disk, first_frame, last_frame,
    #                   upload_to_shotgun):
    """
    Create a version in Shotgun for this path and linked to this publish.
    """

    # get current shotgun user
    current_user = sgtk.util.get_current_user(sgtk)

    # create a name for the version based on the file name
    # grab the file name, strip off extension
    name = os.path.splitext(os.path.basename(path_to_movie))[0]
    # and capitalize
    name = name.capitalize()

    # Create the version in Shotgun

    eng = sgtk.platform.current_engine()
    # app = sgtk.platform.current_bundle()
    app = eng  # hack...

    # get context
    ctx = eng.context

    published_files = [{'type': 'PublishedFile', 'id': 79164, 'name': '036-030_editorial_Edit-180509_v003.mov'}]

    data = {
        "code": name,
        "sg_status_list": 'rev',
        "entity": ctx.entity,
        "sg_task": sg_task,
        "sg_first_frame": first_frame,
        "sg_last_frame": last_frame,
        "frame_count": (last_frame - first_frame + 1),
        "frame_range": "%s-%s" % (first_frame, last_frame),
        "sg_frames_have_slate": False,
        "created_by": current_user,
        "user": current_user,
        "description": comment,
        "sg_path_to_movie": path_to_movie,
        "sg_movie_has_slate": False,
        "project": ctx.project,
        "published_files": published_files
    }

    app.log_debug('DATA: ')
    app.log_debug(data)

    sample_data = {'code': u'Asset002_fx_shaderpublish_v022',
                   'sg_task': {'type': 'Task', 'name': 'fx', 'id': 139325},
                   'sg_movie_has_slate': False,
                   'entity': {'type': 'Asset', 'name': 'Asset002', 'id': 2271},
                   'user': {'name': 'Michael Hatton',
                            'firstname': 'Michael',
                            'lastname': 'Hatton',
                            'image': 'https://sg-media-usor-01.s3-accelerate.amazonaws.com/a7bec5eaea8660b045281f5181cf0975ad5e2893/aba60eab1aeba726d667ce4354daf45ba53fd48f/2012-12-17_18.09.43_t.jpg?response-content-disposition=filename%3D%222012-12-17_18.09.43_t.jpg%22&x-amz-meta-user-id=17&x-amz-meta-user-type=HumanUser&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAI3ABMYXRXQDDDLYQ%2F20190225%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20190225T212554Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host&X-Amz-Signature=7e6f40214db4ce7c01ac249fbae91dcfb333839437574ab27507d5f533f16a08',
                            'email': 'michael@mavericks-vfx.com',
                            'login': 'mhatton',
                            'type': 'HumanUser',
                            'id': 17},
                   'frame_range': '1-10',
                   'description': None,
                   'sg_path_to_movie': u'/mav/stor/prod/SandBox/assets/Plate/Asset002/fx/work/maya/playblasts/Asset002_fx_ShaderPublish_v022/Asset002_fx_ShaderPublish_v022.mov',
                   'sg_last_frame': 10,
                   'sg_first_frame': 1,
                   'created_by': {'name': 'Michael Hatton', 'firstname': 'Michael', 'lastname': 'Hatton',
                                  'image': 'https://sg-media-usor-01.s3-accelerate.amazonaws.com/a7bec5eaea8660b045281f5181cf0975ad5e2893/aba60eab1aeba726d667ce4354daf45ba53fd48f/2012-12-17_18.09.43_t.jpg?response-content-disposition=filename%3D%222012-12-17_18.09.43_t.jpg%22&x-amz-meta-user-id=17&x-amz-meta-user-type=HumanUser&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAI3ABMYXRXQDDDLYQ%2F20190225%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20190225T212554Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host&X-Amz-Signature=7e6f40214db4ce7c01ac249fbae91dcfb333839437574ab27507d5f533f16a08',
                                  'email': 'michael@mavericks-vfx.com', 'login': 'mhatton', 'type': 'HumanUser', 'id': 17},
                   'project': {'type': 'Project', 'name': 'SandBox', 'id': 321},
                   'sg_status_list': 'rev',
                   'frame_count': 10,
                   'sg_frames_have_slate': False}

    # if sgtk.util.get_published_file_entity_type(app.sgtk) == "PublishedFile":
    #     data["published_files"] = [path_to_movie]
    # else:  # == "TankPublishedFile"
    #     data["tank_published_file"] = path_to_movie


    # error here...
    sg_version = app.sgtk.shotgun.create("Version", data)
    app.log_debug("Created version in shotgun: %s" % str(data))

    upload_to_shotgun = True

    # upload files:
    _upload_files(app, sg_version, path_to_movie, thumbnail_path, upload_to_shotgun)

    return sg_version


def _upload_files(app, sg_version, output_path, thumbnail_path, upload_to_shotgun):
    """
    """
    # Upload in a new thread and make our own event loop to wait for the
    # thread to finish.
    event_loop = QtCore.QEventLoop()
    thread = UploaderThread(app, sg_version, output_path, thumbnail_path, upload_to_shotgun)
    thread.finished.connect(event_loop.quit)
    thread.start()
    event_loop.exec_()

    # log any errors generated in the thread
    for e in thread.get_errors():
        app.log_error(e)



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


class UploaderThread(QtCore.QThread):
    """
    Simple worker thread that encapsulates uploading to shotgun.
    Broken out of the main loop so that the UI can remain responsive
    even though an upload is happening
    """
    def __init__(self, app, version, path_to_movie, thumbnail_path, upload_to_shotgun):
        QtCore.QThread.__init__(self)
        self._app = app
        self._version = version
        self._path_to_movie = path_to_movie
        self._thumbnail_path = thumbnail_path
        self._upload_to_shotgun = upload_to_shotgun
        self._errors = []

    def get_errors(self):
        """
        can be called after execution to retrieve a list of errors
        """
        return self._errors

    def run(self):
        """
        Thread loop
        """
        upload_error = False

        if self._upload_to_shotgun:
            try:
                self._app.sgtk.shotgun.upload("Version", self._version["id"], self._path_to_movie, "sg_uploaded_movie")
            except Exception, e:
                self._errors.append("Movie upload to Shotgun failed: %s" % e)
                upload_error = True

        if not self._upload_to_shotgun or upload_error:
            try:
                self._app.sgtk.shotgun.upload_thumbnail("Version", self._version["id"], self._thumbnail_path)
            except Exception, e:
                self._errors.append("Thumbnail upload to Shotgun failed: %s" % e)
