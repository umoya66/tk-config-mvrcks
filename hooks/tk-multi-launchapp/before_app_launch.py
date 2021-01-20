# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Before App Launch Hook

This hook is executed prior to application launch and is useful if you need
to set environment variables or run scripts as part of the app initialization.
"""

import os
import tank


class BeforeAppLaunch(tank.Hook):
    """
    Hook to set up the system prior to app launch.
    """

    def execute(
        self, app_path, app_args, version, engine_name, software_entity=None, **kwargs
    ):
        """
        The execute function of the hook will be called prior to starting the required application

        :param app_path: (str) The path of the application executable
        :param app_args: (str) Any arguments the application may require
        :param version: (str) version of the application being run if set in the
            "versions" settings of the Launcher instance, otherwise None
        :param engine_name (str) The name of the engine associated with the
            software about to be launched.
        :param software_entity: (dict) If set, this is the Software entity that is
            associated with this launch command.
        """

        # accessing the current context (current shot, etc)
        # can be done via the parent object
        #
        # > multi_launchapp = self.parent
        # > current_entity = multi_launchapp.context.entity

        # you can set environment variables like this:
        # os.environ["MY_SETTING"] = "foo bar"

        if engine_name == "tk-maya":
            self.logger.debug('[PIPELINE] Launching Maya version: %s' % version)

            # disable Maya reporting
            os.environ["MAYA_DISABLE_CIP"] = "1"
            os.environ["MAYA_DISABLE_CER"] = "1"

            os.environ["SHARED_MAYA_DIR"] = "/array/X/Library/MayaScripts"
            os.environ["MAYA_SCRIPT_PATH"] = os.environ["SHARED_MAYA_DIR"]
            os.environ["MAYA_PLUG_IN_PATH"] = ("/usr/autodesk/maya" + version + "/bin/plug-ins:/usr/autodesk/maya" 
                                               + version + "/plug-ins:/usr/autodesk/maya" + version + "/plug-ins/fbx/plug-ins:/usr/autodesk/maya" 
                                               + version + "/plug-ins/bifrost:/usr/autodesk/maya" + version + "/plug-ins/bifrost/plug-ins" )
            os.environ["MAYA_PLUG_IN_PATH"]=os.environ["SHARED_MAYA_DIR"] + "/plugins"
            os.environ["MAYA_RENDER_ENGINE"] = "/array/X/Library/renderer"
            del os.environ["XBMLANGPATH"]
            os.environ["XBMLANGPATH"] = os.environ["SHARED_MAYA_DIR"] + "/icons/"

            if version == "2020":
                self.logger.debug("[PIPELINE] Setting up Maya 2020.x environment variables")
                os.environ["MAYA_MODULE_PATH"]= "/opt/walter/maya:/array/X/Library/renderer/yeti/maya2020:/array/X/Library/renderer/yeti/maya2020/bin:/array/X/Library/MayaScripts/modules/HoudiniEngine"

                # enable Maya Render Setup
                del os.environ["MAYA_ENABLE_LEGACY_RENDER_LAYERS"]
                os.environ["MAYA_RENDER_SETUP_DISPLAY_RS_NODES"] = "1"
                os.environ["MAYA_RENDER_SETUP_GLOBAL_TEMPLATE_PATH"] = "/array/X/Library/3d/Maya_Templates/LookDev/renderSetup/RSTemplates"
                os.environ["MAYA_RENDER_SETUP_GLOBAL_PRESETS_PATH"] = "/array/X/Library/3d/Maya_Templates/LookDev/renderSetup/Presets"

                # Arnold
                #del os.environ["MTOA_HOME"]
                os.environ["MTOA_HOME"] = os.environ["MAYA_RENDER_ENGINE"] + "/renderer/mtoa/2020"
                tank.util.append_path_to_env_var("MAYA_MODULE_PATH", "MTOA_HOME")

                # Bifrost
                os.environ["BIFROST_HOME"] = os.environ["MAYA_RENDER_ENGINE"] + "/renderer/Arnold/bifrost/maya2020/2.0.5.1"

                # FumeFX AFTERRLICS
                os.environ["AFLICS_INI"] = "/array/X/Library/licenses/FumeFX/AfterFLICS.ini"

                # MayaBonustools
                os.environ["MAYA_PACKAGE_PATH"] = os.environ["SHARED_MAYA_DIR"] + "/modules/MayaBonusTools-2017-2020"

                # multiverse
                os.environ["MV_ROOT"] = "/mav/stor/sw/lin/opt/multiverse/USD"
                os.environ[" USD_PLUG_IN_PATH "] = os.environ["MV_ROOT"] + "/lib/plugin/usd"
                tank.util.append_path_to_env_var("PYTHON_PATH", os.environ["MV_ROOT"] + "/lib/python" )
                tank.util.append_path_to_env_var("PATH", os.environ["MV_ROOT"] + "/bin")
                tank.util.append_path_to_env_var("LD_LIBRARY_PATH", os.environ["MV_ROOT"] +  "/lib")
                tank.util.append_path_to_env_var("MAYA_MODULE_PATH", os.environ["MV_ROOT"] + "/Maya")

                # Used by Maya to Arnold and Arnold standalone
                tank.util.append_path_to_env_var("ARNOLD_PLUGIN_PATH", os.environ["MV_ROOT"] + "/lib/procedurals/arnold")

                # Used by Renderman for Maya
                tank.util.append_path_to_env_var("RFM_PLUGINS_PATH", os.environ["MV_ROOT"] + "/lib/procedurals/renderman")

                # NOTE: As of 3Delight NSI no searchpath is needed for procedurals

                print ( "Multiverse Environment is set" )

                #Red9Studios
                os.environ["RED9STUDIOPACK_HOME"] = "/array/X/Library/MayaScripts/plugins/Red9StudioPack"
                tank.util.append_path_to_env_var("MAYA_PLUG_IN_PATH", os.environ["RED9STUDIOPACK_HOME"] + "/Contents/scripts/:" + 
                                                  os.environ["RED9STUDIOPACK_HOME"] + "/Contents/plug-ins/")
                
                # RedShift
                #os.environ["REDSHIFT_HOME"] = os.environ["MAYA_RENDER_ENGINE"] + "/redshift"
                #os.environ["REDSHIFT_SCRIPT_PATH"] = os.environ["MAYA_RENDER_ENGINE"] + "/redshift/redshift4maya/common/scripts/"
                #tank.util.append_path_to_env_var(os.environ["MAYA_PLUG_IN_PATH"], os.environ["REDSHIFT_HOME"] + "/redshift4maya/" + version)
                #tank.util.append_path_to_env_var(os.environ["MAYA_SCRIPT_PATH"], os.environ["REDSHIFT_SCRIPT_PATH"])

                # SpeedTree
                os.environ["SPEEDTREEDIR"] = os.environ["SHARED_MAYA_DIR"] + "/modules/SpeedTree/Maya"
                tank.util.append_path_to_env_var("MAYA_PLUG_IN_PATH", os.environ["SPEEDTREEDIR"])
                
                # usd
                os.environ["USD_ROOT"] = os.environ["SHARED_MAYA_DIR"] + "/plugins/USD"
                tank.util.append_path_to_env_var(os.environ["MAYA_PLUG_IN_PATH"], os.environ["USD_ROOT"] + "/plugin/usd")
                tank.util.append_path_to_env_var(os.environ["MAYA_PLUG_IN_PATH"], os.environ["SHARED_MAYA_DIR"] + "/third_party/maya/plugin")
                tank.util.append_path_to_env_var(os.environ["MAYA_SCRIPT_PATH"], os.environ["USD_ROOT"] + "/third_party/maya/lib/usd/usdMaya/resources")
                tank.util.append_path_to_env_var(os.environ["MAYA_SCRIPT_PATH"], os.environ["USD_ROOT"] + "/third_party/maya/plugin/pxrUsdPreviewSurface/resources")
                tank.util.append_path_to_env_var(os.environ["MAYA_SCRIPT_PATH"], os.environ["USD_ROOT"] + "/plugin/usd/usdAbc/resources")
                
                # Yeti
                del os.environ["YETI_HOME"]
                os.environ["YETI_HOME"] = "/array/X/Library/renderer/yeti/maya2020"
                os.environ["DL_PROCEDURALS_PATH"] = os.environ["YETI_HOME"] + "/bin:" + os.environ["YETI_HOME"] + "/plug-ins"
                tank.util.append_path_to_env_var(os.environ["MAYA_PLUG_IN_PATH"], os.environ["YETI_HOME"] + "/plug-ins")
                tank.util.append_path_to_env_var("XBMLANGPATH", os.environ["YETI_HOME"] + "/icons")

                # V-Ray
                del os.environ["VRAY_DIR"]
                os.environ["VRAY_DIR"] = os.environ["MAYA_RENDER_ENGINE"] + "/ChaosGroup/V-Ray/Maya2020"
                os.environ["VRAY_PLUGINS_x86"] = os.environ["VRAY_DIR"] + "/maya_vray/vrayplugins:" + os.environ["YETI_HOME"] + "/bin:" + os.environ["MV_ROOT"] + "/lib/procedurals/vray"
                os.environ["VRAY_FOR_MAYA2020_MAIN"] = os.environ["VRAY_DIR"] + "/maya_vray"
                os.environ["VRAY_FOR_MAYA2020_PLUGINS"] = os.environ["VRAY_DIR"] + "/maya_vray/plug-ins:" + os.environ["VRAY_DIR"] + "/maya_vray/vrayplugins:" + os.environ["YETI_HOME"] + "/bin:" + os.environ["MV_ROOT"] + "/lib/procedurals/vray"
                os.environ["VRAY_OSL_PATH_MAYA_MAYA2020"] = os.environ["VRAY_DIR"] + "/vray/opensl"
                os.environ["MAYA_RENDER_DESC_PATH"] = os.environ["VRAY_DIR"] + "/maya_root/bin/rendererDesc"
                os.environ["VRAY_TOOLS_MAYA2020"] = os.environ["VRAY_DIR"] + "/vray/bin"
                os.environ["VRAY_AUTH_CLIENT_FILE_PATH"] = "/array/X/Library/systems/licenses/Chaos_Vray/"
                tank.util.append_path_to_env_var("PYTHONPATH", os.environ["VRAY_DIR"] + "/maya_vray/scripts")
                tank.util.append_path_to_env_var("MAYA_PLUG_IN_PATH", os.environ["VRAY_DIR"] + "/maya_vray/plug-ins")
                tank.util.append_path_to_env_var("LD_LIBRARY_PATH", os.environ["VRAY_DIR"] + "/maya_root/lib")
                tank.util.append_path_to_env_var("MAYA_SCRIPT_PATH", os.environ["VRAY_DIR"] + "/maya_vray/scripts")
                tank.util.append_path_to_env_var("XBMLANGPATH", os.environ["VRAY_DIR"] + "/maya_vray/icons/")

            if version == "2018":
                self.logger.debug("[PIPELINE] Setting up Maya 2018.x environment variables")

                # Yeti 3.6.4
                #os.environ["MAYA_MODULE_PATH"]= "/opt/walter/maya:/array/X/Library/renderer/yeti/maya2018:/array/X/Library/renderer/yeti/maya2018/bin:/array/X/Library/MayaScripts/modules/HoudiniEngine"
                os.environ["MAYA_MODULE_PATH"]= "/opt/walter/maya:/array/X/Library/MayaScripts/modules/Yeti:/array/X/Library/MayaScripts/modules/Yeti/bin:/array/X/Library/MayaScripts/modules/HoudiniEngine"

                # disable Maya Render Setup
                os.environ["MAYA_ENABLE_LEGACY_RENDER_LAYERS"] = "1"

                # multiverse
                os.environ["MV_ROOT"] = "/mav/stor/sw/lin/opt/multiverse/multiverse"
                os.environ[" USD_PLUG_IN_PATH "] = os.environ["MV_ROOT"] + "/lib/plugin/usd"
                tank.util.append_path_to_env_var("PYTHON_PATH", os.environ["MV_ROOT"] + "/lib/python" )
                tank.util.append_path_to_env_var("PATH", os.environ["MV_ROOT"] + "/bin")
                tank.util.append_path_to_env_var("LD_LIBRARY_PATH", os.environ["MV_ROOT"] +  "/lib")
                tank.util.append_path_to_env_var("MAYA_MODULE_PATH", os.environ["MV_ROOT"] + "/Maya")

                # Used by Maya to Arnold and Arnold standalone
                tank.util.append_path_to_env_var("ARNOLD_PLUGIN_PATH", os.environ["MV_ROOT"] + "/lib/procedurals/arnold")

                # Used by Renderman for Maya
                tank.util.append_path_to_env_var("RFM_PLUGINS_PATH", os.environ["MV_ROOT"] + "/lib/procedurals/renderman")

                # NOTE: As of 3Delight NSI no searchpath is needed for procedurals

                print ( "Multiverse Environment is set" )

                # SpeedTree
                os.environ["SPEEDTREEDIR"] = os.environ["SHARED_MAYA_DIR"] + "/modules/SpeedTree/Maya"
                tank.util.append_path_to_env_var("MAYA_PLUG_IN_PATH", os.environ["SPEEDTREEDIR"])

                # V-Ray
                os.environ["VRAY_DIR"] = os.environ["MAYA_RENDER_ENGINE"] + "/ChaosGroup/V-Ray/Maya2018"
                os.environ["VRAY_PLUGINS_x86"] = os.environ["VRAY_DIR"] + "/maya_vray/vrayplugins:" + os.environ["YETI_HOME"] + "/bin"
                os.environ["VRAY_FOR_MAYA2018_MAIN_x64"] = os.environ["VRAY_DIR"] + "/maya_vray"
                os.environ["VRAY_FOR_MAYA2018_PLUGINS_x64"] = os.environ["VRAY_DIR"] + "/maya_vray/plug-ins:" + os.environ["VRAY_DIR"] + "/maya_vray/vrayplugins:" + os.environ["YETI_HOME"] + "/bin:" + os.environ["MV_ROOT"] + "/lib/procedurals/vray"
                os.environ["VRAY_OSL_PATH_MAYA_MAYA2018_x64"] = os.environ["VRAY_DIR"] + "/vray/opensl"
                os.environ["MAYA_RENDER_DESC_PATH"] = os.environ["VRAY_DIR"] + "/maya_root/bin/rendererDesc"
                os.environ["VRAY_TOOLS_MAYA2020"] = os.environ["VRAY_DIR"] + "/vray/bin"
                os.environ["VRAY_AUTH_CLIENT_FILE_PATH"] = "/array/X/Library/systems/licenses/Chaos_Vray/"
                tank.util.append_path_to_env_var("PYTHONPATH", os.environ["VRAY_DIR"] + "/maya_vray/scripts")
                tank.util.append_path_to_env_var("MAYA_PLUG_IN_PATH", os.environ["VRAY_DIR"] + "/maya_vray/plug-ins")
                tank.util.append_path_to_env_var("LD_LIBRARY_PATH", os.environ["VRAY_DIR"] + "/maya_root/lib")
                tank.util.append_path_to_env_var("MAYA_SCRIPT_PATH", os.environ["VRAY_DIR"] + "/maya_vray/scripts")
                tank.util.append_path_to_env_var("XBMLANGPATH", os.environ["VRAY_DIR"] + "/maya_vray/icons/")

                # Yeti
                del os.environ["YETI_HOME"]
                os.environ["YETI_HOME"] = "/array/X/Library/MayaScripts/modules/Yeti"
                os.environ["VRAY_TOOLS_MAYA2018"] = os.environ["VRAY_DIR"] + "/vray/bin"
                os.environ["DL_PROCEDURALS_PATH"] = os.environ["YETI_HOME"] + "/bin:" + os.environ["YETI_HOME"] + "/plug-ins"
                tank.util.append_path_to_env_var(os.environ["MAYA_PLUG_IN_PATH"], os.environ["YETI_HOME"] + "/plug-ins")
                tank.util.append_path_to_env_var("XBMLANGPATH", os.environ["YETI_HOME"] + "/icons")


                # Arnold
                #del os.environ["MTOA_HOME"]
                os.environ["MTOA_HOME"] = os.environ["MAYA_RENDER_ENGINE"] + "/renderer/mtoa/2018"
                tank.util.append_path_to_env_var("MAYA_MODULE_PATH", "MTOA_HOME")

                # Bifrost
                os.environ["BIFROST_HOME"] = os.environ["MAYA_RENDER_ENGINE"] + "/renderer/Arnold/bifrost/maya2018/2.0.5.1"

            
        if engine_name == "tk-nuke":
            self.logger.debug('[PIPELINE] Launching Nuke')
            self.logger.debug('[PIPELINE] Nuke version: %s' % version)

            # stop temp license expiry warning message - people get confused.
            os.environ['FN_NUKE_DISABLE_TMPLIC_NOTIFY_DIALOG'] = "1"
            
            # disable crash dumps to Foundry - do they even read them?
            os.environ['NUKE_CRASH_HANDLING'] = "0"
            
            # split out Nuke version naming
            major, minorrelease = version.split('.')
            minor, release = minorrelease.split('v')

            nuke_version = major + '.' + minor

            if nuke_version == '11.2':
                self.logger.debug('[PIPELINE] Setting up Nuke %s' % nuke_version)

            if nuke_version == '12.0':
                self.logger.debug('[PIPELINE] Setting up Nuke %s' % nuke_version)

            if nuke_version == '12.2':
                self.logger.debug('[PIPELINE] Setting up Nuke %s' % nuke_version)

            if nuke_version == '13.0':
                self.logger.debug('[PIPELINE] Setting up Nuke %s' % nuke_version)


        if engine_name == "tk-houdini":
            self.logger.debug('[PIPELINE] Launching Houdini')
            self.logger.debug('[PIPELINE] Houdini version: %s' % version)


        if engine_name == "tk-photoshopcc":
            self.logger.debug('[PIPELINE] Launching Photoshop')
            self.logger.debug('[PIPELINE] Photoshop version: %s' % version)

        if engine_name == "tk-mari":
            self.logger.debug('[PIPELINE] Launching Mari')
            self.logger.debug('[PIPELINE] Mari version: %s' % version)

