#  This is Mavericks Shotgun Default configuration
## based on tk-config-default2


Things to note on finalising dev merges to the project final
- check the primary storage name

----
##Typical configuration changes for projects
- env/include/settings/tk-nuke.yml

    ``project_colorspace: {int8Lut: sRGB, int16Lut: sRGB, logLut: AlexaV3LogC, floatLut: AlexaV3LogC}``
- env/include/settings/tk-nuke-writenode.yml
        edit for required Nuke Nodes to show up
        
```   
- file_type: exr
    name: Delivery EXR
    promote_write_knobs: []
    proxy_publish_template:
    proxy_render_template:
    publish_template: nuke_shot_render_pub_mono_exr
    render_template: nuke_shot_render_mono_exr
    settings: {datatype: 16 bit half, colorspace: linear}
    settings: {}
    tank_type: Rendered Image
    tile_color: []
 ```
- core/templates.yml
        edit for new file path configs, if directory structure changes this must be reflected in the core/schema.


-------------------------------------------------------------------------
The Shotgun Pipeline Toolkit Default Configuration
-------------------------------------------------------------------------

Welcome to the Shotgun Pipeline Toolkit default configuration! 

For more information, go to the following url:
https://support.shotgunsoftware.com/hc/en-us/articles/115000067493-Integrations-Admin-Guide

-------------------------------------------------------------------------
