# This is Mavericks Shotgun Default configuration
## based on tk-config-default2


Things to note on finalising dev merges to the project final
- check that any app_locations that are git sourced will need to be turned back on
- check the primary storage name
-

1. **TODO:** return app_store locations to git for the release
2. **TODO:** test without a core/pipeline_configuration.yml file
3. **TODO:** set tank_name as a required field in shotgun project setup.
4. **TODO:** set up change permissions on folder - needs  new hooks and app OR add to tk-shotgun-folders - FORK or HOOK?
OR it could be a sg_event daemon thing. How to trigger though? Can AMI or hooks create events tracked by sg_event daemon

5. **TODO:** distributing apps with virtualenv 
5. **TODO:** virtualenv with PyCharm


----
Typical confguration chages for projects
- env/include/settings/tk-nuke.yml
    ```project_colorspace: {int8Lut: sRGB, int16Lut: sRGB, logLut: AlexaV3LogC, floatLut: AlexaV3LogC}```
- env/include/settings/tk-nuke-writenode.yml
        edit for required Nuke Nodes to show up
- core/templates.yml
        edit for new file path configs, if directory structure changes this must be reflected in the core/schema.

- core/pipeline_configuration.yml
        project id etc ---???? is this really a necessary file - this should be specified in the ``tank_name``  in the project settings
        tank_name and the root.yml will specify where the project root is.

-------------------------------------------------------------------------
The Shotgun Pipeline Toolkit Default Configuration
-------------------------------------------------------------------------

Welcome to the Shotgun Pipeline Toolkit default configuration! 

For more information, go to the following url:
https://support.shotgunsoftware.com/hc/en-us/articles/115000067493-Integrations-Admin-Guide

-------------------------------------------------------------------------
