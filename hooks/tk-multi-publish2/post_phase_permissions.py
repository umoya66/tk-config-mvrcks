    # Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sgtk

import pprint

HookBaseClass = sgtk.get_hook_baseclass()


class PostPhaseHook(HookBaseClass):
    """
    This hook defines methods that are executed after each phase of a publish:
    validation, publish, and finalization. Each method receives the
    :ref:`publish-api-tree` tree instance being used by the publisher, giving
    full control to further curate the publish tree including the publish items
    and the tasks attached to them. See the :ref:`publish-api-tree`
    documentation for additional details on how to traverse the tree and
    manipulate it.
    """

    def post_validate(self, publish_tree):
        """
        This method is executed after the validation pass has completed for each
        item in the tree, before the publish pass.

        A :ref:`publish-api-tree` instance representing the items to publish,
        and their associated tasks, is supplied as an argument. The tree can be
        traversed in this method to inspect the items and tasks and process them
        collectively. The instance can also be used to save the state of the
        tree to disk for execution later or on another machine.

        To glean information about the validation of particular items, you can
        iterate over the items in the tree and introspect their
        :py:attr:`~.api.PublishItem.properties` dictionary. This requires
        customizing your publish plugins to populate any specific validation
        information (failure/success) as well. You might, for example, set a
        ``validation_failed`` boolean in the item properties, indicating if any
        of the item's tasks failed. You could then include validation error
        messages in a ``validation_errors`` list on the item, appending error
        messages during task execution. Then, this method might look something
        like this:

        .. code-block:: python

            def post_validate(self, publish_tree):

                all_errors = []

                # the publish tree is iterable, so you can easily loop over
                # all items in the tree
                for item in publish_tree:

                    # access properties set on the item during the execution of
                    # the attached publish plugins
                    if item.properties.validation_failed:
                        all_errors.extend(item.properties.validation_errors)

                # process all validation issues here...

        .. warning:: You will not be able to use the item's
            :py:attr:`~.api.PublishItem.local_properties` in this hook since
            :py:attr:`~.api.PublishItem.local_properties` are only accessible
            during the execution of a publish plugin.

        :param publish_tree: The :ref:`publish-api-tree` instance representing
            the items to be published.
        """
        self.logger.debug("Executing post validate hook method...")

    def post_publish(self, publish_tree):
        """
        This method is executed after the publish pass has completed for each
        item in the tree, before the finalize pass.

        A :ref:`publish-api-tree` instance representing the items that were
        published is supplied as an argument. The tree can be traversed in this
        method to inspect the items and process them collectively.

        To glean information about the publish state of particular items, you
        can iterate over the items in the tree and introspect their
        :py:attr:`~.api.PublishItem.properties` dictionary. This requires
        customizing your publish plugins to populate any specific publish
        information that you want to process collectively here.

        .. warning:: You will not be able to use the item's
            :py:attr:`~.api.PublishItem.local_properties` in this hook since
            :py:attr:`~.api.PublishItem.local_properties` are only accessible
            during the execution of a publish plugin.

        :param publish_tree: The :ref:`publish-api-tree` instance representing
            the items to be published.
        """
        self.logger.debug("Executing post publish hook method...")

    def post_finalize(self, publish_tree):
        """
        This method is executed after the finalize pass has completed for each
        item in the tree.

        A :ref:`publish-api-tree` instance representing the items that were
        published and finalized is supplied as an argument. The tree can be
        traversed in this method to inspect the items and process them
        collectively.

        To glean information about the finalize state of particular items, you
        can iterate over the items in the tree and introspect their
        :py:attr:`~.api.PublishItem.properties` dictionary. This requires
        customizing your publish plugins to populate any specific finalize
        information that you want to process collectively here.

        .. warning:: You will not be able to use the item's
            :py:attr:`~.api.PublishItem.local_properties` in this hook since
            :py:attr:`~.api.PublishItem.local_properties` are only accessible
            during the execution of a publish plugin.

        :param publish_tree: The :ref:`publish-api-tree` instance representing
            the items to be published.
        """
        self.logger.debug("Executing post finalize Permissions hook method...")

        published_files = []
        playblast = None


        print('zzzDEBUGzzz')
        pprint.pprint(publish_tree)
        print('zzzDEBUGzzz')


        for item in publish_tree:

            # item = ['__class__', '__del__', '__delattr__', '__doc__', '__format__', '__getattribute__', '__hash__',
            #       '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__',
            #       '__sizeof__', '__slots__', '__str__', '__subclasshook__', '_active', '_allows_context_change',
            #       '_children', '_context', '_created_temp_files', '_current_temp_file_path', '_description', '_enabled',
            #       '_expanded', '_get_image', '_get_local_properties', '_get_type', '_global_properties', '_icon_path',
            #       '_icon_pixmap', '_local_properties', '_name', '_parent', '_persistent', '_set_type', '_tasks',
            #       '_thumbnail_enabled', '_thumbnail_explicit', '_thumbnail_path', '_thumbnail_pixmap', '_traverse_item',
            #       '_type_display', '_type_spec', '_validate_image', '_visit_recursive', 'active', 'add_task', 'checked',
            #       'children', 'clear_tasks', 'context', 'context_change_allowed', 'create_item', 'descendants',
            #       'description', 'display_type', 'enabled', 'expanded', 'from_dict', 'get_property',
            #       'get_thumbnail_as_path', 'icon', 'is_root', 'local_properties', 'name', 'parent', 'persistent',
            #       'properties', 'remove_item', 'set_icon_from_path', 'set_thumbnail_from_path', 'tasks', 'thumbnail',
            #       'thumbnail_enabled', 'thumbnail_explicit', 'to_dict', 'type', 'type_display', 'type_spec']
            self.logger.debug('Item: %s' % item.name)
            # self.logger.debug('Item properties publish data: %s' % item.properties.sg_publish_data)
            print('xxxDEBUGxxx')
            pprint.pprint(dir(item.properties))
            print('xxxxxxxxxxx')
            pprint.pprint(item.properties.sg_publish_data)
            print('endDEBUGxxx')

            self.logger.debug('Item path: %s' % item.properties.sg_publish_data['path']['local_path'])
            self.logger.debug('Item type: %s' % item.properties.sg_publish_data['type'])
            self.logger.debug('Item published_file_type: %s' % item.properties.sg_publish_data['published_file_type'])
            try:
                self.logger.debug('Locking permissions on: %s' % item.properties.sg_publish_data['path']['local_path'])
                os.chmod(item.properties.sg_publish_data['path']['local_path'], 0444)
            except OSError as error:
                self.logger.error(error)

            # sg_publish_data = {
            #         'version_number': 4, 
            #         'task': {
            #             'type': 'Task', 
            #             'id': 125080, 
            #             'name': '2hrcomp'}, 
            #         'description': None, 
            #         'type': 'PublishedFile', 
            #         'published_file_type': {
            #             'type': 'PublishedFileType', 
            #             'id': 5, 
            #             'name': 'Maya Scene'}, 
            #         'created_by': {
            #             'type': 'HumanUser', 
            #             'id': 17, 
            #             'name': 'Michael Hatton'}, 
            #         'entity': {
            #             'type': 'Shot', 
            #             'id': 10559, 
            #             'name': 'Shot001'}, 
            #         'project': {
            #             'type': 'Project', 
            #             'id': 321, 
            #             'name': 'SandBox'}, 
            #         'code': 'Shot001_lgt_scene_v004.ma', 
            #         'path': {
            #             'local_path_windows': 'P:\\SandBox\\pub\\episodes\\101\\Seq001\\Shot001\\lgt\\publish\\maya\\scenes\\Shot001_lgt_scene_v004.ma', 
            #             'name': 'Shot001_lgt_scene_v004.ma', 
            #             'local_path_linux': '/mav/stor/prod/SandBox/pub/episodes/101/Seq001/Shot001/lgt/publish/maya/scenes/Shot001_lgt_scene_v004.ma', 
            #             'url': 'file:///mav/stor/prod/SandBox/pub/episodes/101/Seq001/Shot001/lgt/publish/maya/scenes/Shot001_lgt_scene_v004.ma', 
            #             'local_storage': {
            #                 'type': 'LocalStorage', 
            #                 'id': 3, 
            #                 'name': 'primary'}, 
            #             'local_path': '/mav/stor/prod/SandBox/pub/episodes/101/Seq001/Shot001/lgt/publish/maya/scenes/Shot001_lgt_scene_v004.ma', 
            #             'content_type': None, 
            #             'local_path_mac': '/mav/stor/prod/SandBox/pub/episodes/101/Seq001/Shot001/lgt/publish/maya/scenes/Shot001_lgt_scene_v004.ma', 
            #             'type': 'Attachment', 
            #             'id': 606040, 
            #             'link_type': 'local'}, 
            #         'path_cache': 'SandBox/pub/episodes/101/Seq001/Shot001/lgt/publish/maya/scenes/Shot001_lgt_scene_v004.ma', 
            #         'id': 172563, 
            #         'name': 'Shot001_lgt_scene.ma'}, 
            

            # for task in item.tasks:
            #     # go through all the tasks on each publish item
            #     # self.logger.debug('--------------Task: %s -------------------' % task)
            #     # task =  ['__class__', '__delattr__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__',
            #     #         '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__',
            #     #         '__slots__', '__str__', '__subclasshook__', '_active', '_description', '_enabled', '_item',
            #     #         '_name', '_plugin', '_settings', '_visible', 'active', 'checked', 'description', 'enabled',
            #     #         'finalize', 'from_dict', 'is_same_task_type', 'item', 'name', 'plugin', 'publish', 'settings',
            #     #         'to_dict', 'validate', 'visible']

            #     self.logger.debug('Task: %s' % task.name)
            #     self.logger.debug('Task : %s' % task)

            #     # if task.name == 'Publish Playblast':
            #     #     self.logger.debug('Post Phase / Post Finalize / Publish Playblast')
            #     #     # We have a playblast to publish, so the filess need to be attached to the version
            #     #     playblast = item.properties.sg_publish_data

            #     # elif task.name == 'Publish Exported Alembics':
            #     #     self.logger.debug('Post Phase / Post Finalize / Publish Exported Alembics')
            #     #     published_files.append({'type': 'PublishedFile', 'id': item.properties['sg_publish_data']['id'], 'name': item.name})

            #     # elif task.name == 'Publish Session to Shotgun':
            #     #     self.logger.debug('Post Phase / Post Finalize / Publish Session to Shotgun')
            #     #     published_files.append({'type': 'PublishedFile', 'id': item.properties['sg_publish_data']['id'], 'name': item.name})



        self.logger.debug("...finished post finalize Permissions hook method")
