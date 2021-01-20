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

import logging

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

        app = self.parent

        # logging.basicConfig(filename='/array/X/Library/systems/logs/shotgun_permissions.log', 
        #         encoding='utf-8', 
        #         level=logging.DEBUG, 
        #         format='%(asctime)s %(message)s')


        # user = sgtk.get_authenticated_user()


        for item in publish_tree:

            published_file_types = [2, 4, 40]  # 2 = 'Rendered Image', 4 = 'Plate', 40 = 'Hiero Plate'

            # check for file type
            if item.properties.sg_publish_data['published_file_type']['id'] in published_file_types:

                # get file sequences - there may be multiple
                sequences = app.util.get_frame_sequences(os.path.dirname(item.properties.sg_publish_data['path']['local_path']) )

                self.logger.debug('Locking frame sequence permissions...')
                for seq in sequences:
                    for filepath in seq[1]:
                        # it is possible to have multiple sequences published
                        # TODO: publish multiple sequences
                        self.set_permission(filepath)

            else:
                self.logger.debug('Locking scene file permissions...')
                filepath = item.properties.sg_publish_data['path']['local_path']
                # logging.debug('User %s locking file: %s' % (user['name'], filepath))
                self.set_permission(filepath)

        self.logger.debug("...finished post finalize Permissions hook method")
        

    def set_permission(self, path):
        """
        Set file permissions to locked for the specified path

        """
        # TODO: cross platform file locking
        #   TODO: test OSX permissions


        if sgtk.util.is_windows():
            self.logger.debug("Changing permissions in windows is not implemented...")

        if sgtk.util.is_macos():
            self.logger.debug("Changing permissions in macos is not implemented...")

        if sgtk.util.is_linux():
            # script_path = '/home/mhatton/dev/mvrcks/tk-config-mvrcks/hooks/tk-multi-publish2/shotgun_permissions.sh'
            script_path = '/array/X/Library/systems/scripts/shotgun_permissions.sh'
            if os.path.exists(script_path):
                try:
                    self.logger.debug('Locking permissions on: %s' % path)
                    os.system('sudo -n %s %s ' % (script_path, path))
                except OSError as error:
                    self.logger.debug('Unable to lock permissions on: %s' % path)
                    self.logger.error(error)

            else:
                self.logger.warning('Permission script path %s does not exist:' % script_path)



