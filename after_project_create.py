# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
The after_project_create file is executed as part of creating a new project.
If your starter config needs to create any data in shotgun or do any other
special configuration, you can add it to this file.

The create() method will be executed as part of the setup and is passed
the following keyword arguments:

* sg -         A shotgun connection
* project_id - The shotgun project id that is being setup
* log -        A logger instance to which progress can be reported via
               standard logger methods (info, warning, error etc)

"""

def create(sg, project_id, log, **kwargs):
    """
    Insert post-project code here
    """
    # pass
    admin_entities = [
        {'code': 'Artist-Miscellaneous',
         'description': 'Time Log entry for all non-shot, non-asset, miscellaneous artist tasks.',
         'sg_status_list': 'ip'},
        {'code': 'On-Set',
         'description': 'Time Log entry for all on-set supervision, coordination, and/or artist time on set.',
         'sg_status_list': 'ip'},
        {'code': 'Production-Management',
         'description': 'Time Log entry for all producers, production managers, coordinators, editors, and PAs.',
         'sg_status_list': 'ip'},
    ]

    batch_data = []

    for entity in admin_entities:

        entity['project'] =  {'type': 'Project','id': project_id}

        # Check if Admin Entity exists

        filters = [['project','is', {'type': 'Project','id': project_id}], ['code', 'is', entity['code']] ]
        if len(sg.find("CustomEntity02", filters)) > 0:
            print 'Admin entity exists'
        else:
            batch_data.append({"request_type": "create", "entity_type": "CustomEntity02", "data": entity})

    sg.batch(batch_data)


    batch_data = []

    admin_tasks = [{'content': 'Dailies',
                    'sg_description': 'Log time here for extended dailies reviews',
                    'sg_priority': 15,
                    'entity': 'Artist-Miscellaneous'},  # link to Admin Entity
                   {'content': 'QC',
                    'sg_description': 'Log time here for any type of QC work',
                    'sg_priority': 10,
                    'entity': 'Artist-Miscellaneous'},  # link to Admin Entity
                   {'content': 'Supervisor-Lead',
                    'sg_description': 'Log time here for extended time assisting other artists',
                    'sg_priority': 5,
                    'entity': 'Artist-Miscellaneous'},  # link to Admin Entity
                   {'content': 'Learning-Tutorials',
                    'sg_description': 'Log time here for extended downtown learning new software, etc. Includes Research.',
                    'sg_priority': 30,
                    'entity': 'Artist-Miscellaneous'},  # link to Admin Entity
                   {'content': 'Meetings',
                    'sg_description': 'Log time here for extended meetings',
                    'sg_priority': 25,
                    'entity': 'Artist-Miscellaneous'},  # link to Admin Entity
                   {'content': 'Slate, QT, and Publish Creation for Outsource Vendors',
                    'sg_description': 'Log time here for creating slates, QTs, and/or publishes for outsource vendors',
                    'sg_priority': 20,
                    'entity': 'Artist-Miscellaneous'},  # link to Admin Entity
                   {'content': 'Render Tech Support',
                    'sg_description': 'Log time here for extended time monitoring and providing tech support to renders either in studio or remotely.',
                    'sg_priority': 35,
                    'entity': 'Artist-Miscellaneous'},  # link to Admin Entity
                   {'content': 'Breakdowns',
                    'sg_description': 'Log time here for time spent creating breakdowns for shots',
                    'sg_priority': 40,
                    'entity': 'Artist-Miscellaneous'},  # link to Admin Entity
                   {'content': 'CG-Asset-Management',
                    'sg_description': 'Log time here for time spent managing assets to the library.',
                    'sg_priority': 45,
                    'entity': 'Artist-Miscellaneous'},  # link to Admin Entity
                   {'content': 'Down-time',
                    'sg_description': 'Log time here for down time due to technical or other reasons.',
                    'sg_priority': 3,
                    'entity': 'Artist-Miscellaneous'},  # link to Admin Entity
                   {'content': 'Pipeline-Development',
                    'sg_description': 'Log time here for work spent developing he vfx pipeline for the project.',
                    'sg_priority': 45,
                    'entity': 'Artist-Miscellaneous'},  # link to Admin Entity
                   {'content': 'VFX-Artist',
                    'sg_description': 'Artist time spent on a show that is not shot specific.',
                    'sg_priority': 50,
                    'entity': 'Artist-Miscellaneous'},  # link to Admin Entity

                   {'content': 'On-Set Supervisor',
                    'sg_description': 'Log time here for all on-set supervision',
                    'sg_priority': 5,
                    'entity': 'On-Set'},  # link to Admin Entity
                   {'content': 'On-Set Coordinator',
                    'sg_description': 'Log time here for all on-set coordination',
                    'sg_priority': 10,
                    'entity': 'On-Set'},  # link to Admin Entity
                   {'content': 'On-Set Artist',
                    'sg_description': 'Log time here for all on-set assistance, reference gathering, etc. (for artists)',
                    'sg_priority': 15,
                    'entity': 'On-Set'},  # link to Admin Entity

                   {'content': 'VFX Production Manager',
                    'sg_description': 'Log time here for all production manager time',
                    'sg_priority': 10,
                    'entity': 'Production-Management'},  # link to Admin Entity
                   {'content': 'VFX Coordinator',
                    'sg_description': 'Log time here for all Coordinator time',
                    'sg_priority': 15,
                    'entity': 'Production-Management'},  # link to Admin Entity
                   {'content': 'VFX Editor',
                    'sg_description': 'Log time here for all Editor time',
                    'sg_priority': 20,
                    'entity': 'Production-Management'},  # link to Admin Entity
                   {'content': 'VFX PA',
                    'sg_description': 'Log time here for all PA time',
                    'sg_priority': 25,
                    'entity': 'Production-Management'},  # link to Admin Entity
                   {'content': 'VFX Producer',
                    'sg_description': 'Log time here for all Producer time',
                    'sg_priority': 5,
                    'entity': 'Production-Management'},  # link to Admin Entity
                   ]

    for task in admin_tasks:
        task['project'] = {'type': 'Project','id': project_id}

        filters = [['code', 'is', 'Admin']]
        step = sg.find_one('Step', filters)

        task['step'] = {'type': 'Step', 'id': step['id']}
        
        task['sg_status_list'] = 'ip'
        
        filters = [['project', 'is', {'type': 'Project', 'id': project_id}], ['code', 'is', task['entity']]]
        entity = sg.find_one('CustomEntity02', filters)
        
        task['entity'] = {'type': 'CustomEntity02', 'id': entity['id']}

        filters = [['project', 'is', {'type': 'Project', 'id': project_id}], ['content', 'is', task['content']]]
        if len(sg.find("Task", filters)) > 0:
            print 'Tasks entity exists'
        else:
            batch_data.append({"request_type": "create", "entity_type": "Task", "data": task})

    sg.batch(batch_data)
