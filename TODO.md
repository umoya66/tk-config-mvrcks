TODO

- Resolution, sourced from render resolution or Shotgun
- image format png
- filenaming  <Scene>/<RenderLayer>/<Scene>_<RenderLayer>
- padding  #### (4)
- film gate  (sourced from alembic camera and shotgun )
- resolution gate (sourced from alembic camera and shotgun )
- show ornaments  (artist name)
- camera info...  Cam name , take , focal length 


Error Message from Phil

```
inside maya script window
// Error: Shotgun dialog: Finalize error stack:
Traceback (most recent call last):
 File "/home/palexy/.shotgun/bundle_cache/app_store/tk-multi-publish2/v2.2.2/python/tk_multi_publish2/dialog.py", line 1122, in do_publish
   task_generator=self._finalize_task_generator())
 File "/home/palexy/.shotgun/bundle_cache/app_store/tk-multi-publish2/v2.2.2/python/tk_multi_publish2/api/manager.py", line 388, in finalize
   self._post_phase_hook.post_finalize(self.tree)
 File "/home/palexy/.shotgun/bundle_cache/sg/mavericks/v356357/hooks/tk-multi-publish2/maya/post_phase.py", line 165, in post_finalize
   published_files.append({'type': 'PublishedFile', 'id': item.properties['sg_publish_data']['id'], 'name': item.name})
 File "/home/palexy/.shotgun/bundle_cache/app_store/tk-multi-publish2/v2.2.2/python/tk_multi_publish2/api/data.py", line 66, in __getitem__
   return self.__dict__[key]
KeyError: 'sg_publish_data'
// 
Collecting items to Publish...
 Collected current Maya scene
 Current Maya project is: /mav/stor/prod/wlg/sequences/WWD-107-022/WWD-107-022-100/anim/work/maya/.
 Processing Playblasts exports folder: /mav/stor/prod/wlg/sequences/WWD-107-022/WWD-107-022-100/anim/work/maya/movies
 ----- Start collecting Alembics -----
 Adding alembic Item: WWD-107-022-100_anim_scene_v003_geo.abc
 Processing alembic exports folder: /mav/stor/prod/wlg/sequences/WWD-107-022/WWD-107-022-100/anim/work/maya/alembic/WWD-107-022-100_anim_scene_v003/geo
 Maya 'Begin file versioning' plugin rejected the current session...
   There is already a version number in the file...
   Maya file path: /mav/stor/prod/wlg/sequences/WWD-107-022/WWD-107-022-100/anim/work/maya/scenes/WWD-107-022-100_anim_scene_v003.ma
 Maya 'Publish to Shotgun' plugin accepted the current Maya session.
 Version upload plugin accepted: /mav/stor/prod/wlg/sequences/WWD-107-022/WWD-107-022-100/anim/work/maya/movies/WWD-107-022-100_anim_scene_v003_playblast.mov
3 items discovered by publisher.
Running validation pass
 Validating: Item Summary
 Validating: anim, Shot WWD-107-022-100
 Validating: Maya Session WWD-107-022-100_anim_scene_v003.ma
 Validating: Publish Session to Shotgun
   A Publish will be created in Shotgun and linked to:
     /mav/stor/prod/wlg/sequences/WWD-107-022/WWD-107-022-100/anim/work/maya/scenes/WWD-107-022-100_anim_scene_v003.ma
 Validating: Playblast WWD-107-022-100_anim_scene_v003_playblast.mov (playblast)
 Validating: Publish Playblast
Validation Complete. All checks passed.
Running publishing pass
 Publishing: Item Summary
 Publishing: anim, Shot WWD-107-022-100
 Publishing: Maya Session WWD-107-022-100_anim_scene_v003.ma
 Publishing: Publish Session to Shotgun
   Registering publish...
   Publish registered!
 Publishing: Playblast WWD-107-022-100_anim_scene_v003_playblast.mov (playblast)
 Publishing: Publish Playblast
   Creating Version...
   Version created!
   Uploading content...
   Upload complete!
Running finalizing pass
 Finalizing: Item Summary
 Finalizing: anim, Shot WWD-107-022-100
 ```