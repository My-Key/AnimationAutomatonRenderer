'''
Created by Maciej Paluszek
0my0key0@gmail.com
'''

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

#
#    Directions
#
class ANIMAUTORENDER_OT_add_direction(bpy.types.Operator):
    bl_label = "Add direction"
    bl_idname = "animautorender.add_direction"  
    bl_description = "Add direction"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        
        collection = AAR_props.directionList
        added = collection.add()        # This add at the end of the collection list
        added.name = "Dir"+ str(len(collection))
        added.folderName = "Dir"+ str(len(collection))
        
        for item in AAR_props.animation_collection:
            item.chosenDirection.add()
        
        AAR_props.directionList_index = len(collection) - 1
       
        return {'FINISHED'}
    
class ANIMAUTORENDER_OT_clear_direction(bpy.types.Operator):
    bl_label = "Clear direction list"
    bl_idname = "animautorender.clear_direction"  
    bl_description = "Clear direction list"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        
        collection = AAR_props.directionList
        collection.clear()
        AAR_props.directionList_index = -1
        
        for item in AAR_props.animation_collection:
            item.chosenDirection.clear()
       
        return {'FINISHED'}


class ANIMAUTORENDER_OT_remove_direction(bpy.types.Operator):
    bl_label = "Remove direction"
    bl_idname = "animautorender.remove_direction"  
    bl_description = "Remove direction"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        collection = AAR_props.directionList
        index = AAR_props.directionList_index
        if index >= 0:
            for item in AAR_props.animation_collection:
                item.chosenDirection.remove(index)
                
            collection.remove(index)
            AAR_props.directionList_index -= 1
            
            if AAR_props.directionList_index < 0 and len(collection) > 0:
                AAR_props.directionList_index = 0
       
        return {'FINISHED'}
    
class ANIMAUTORENDER_OT_disable_enable_directions(bpy.types.Operator):
    bl_label = "Disable/enable all"
    bl_idname = "animautorender.disable_enable_directions"  
    bl_description = "Disable/enable all"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        index = AAR_props.animation_collection_index
        if index >= 0:
            collection = AAR_props.animation_collection[AAR_props.animation_collection_index].chosenDirection
            enabledDirectionsCount = sum(1 for y in collection if y.enabled)
            for item in collection:
                item.enabled = enabledDirectionsCount == 0
       
        return {'FINISHED'}
    
  
#
#    Animations
#  
class ANIMAUTORENDER_OT_add_animation(bpy.types.Operator):
    bl_label = "Add animation"
    bl_idname = "animautorender.add_animation"  
    bl_description = "Add animation"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        collection = AAR_props.animation_collection
        
        added = collection.add()
        added.name = "Anim"+ str(len(collection))
        added.folderName = "Anim"+ str(len(collection))
        
        for _ in range(0, len(AAR_props.directionList)):
            added.chosenDirection.add()
            
        AAR_props.animation_collection_index = len(collection) - 1
       
        return {'FINISHED'}
    
class ANIMAUTORENDER_OT_clear_animation(bpy.types.Operator):
    bl_label = "Clear animation list"
    bl_idname = "animautorender.clear_animation"  
    bl_description = "Clear animation list"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        
        collection = AAR_props.animation_collection
        collection.clear()

        AAR_props.animation_collection_index = -1
       
        return {'FINISHED'}


class ANIMAUTORENDER_OT_remove_animation(bpy.types.Operator):
    bl_label = "Remove animation"
    bl_idname = "animautorender.remove_animation"  
    bl_description = "Remove animation"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        collection = AAR_props.animation_collection
        index = AAR_props.animation_collection_index
        
        if index >= 0:
            collection.remove(index)
            AAR_props.animation_collection_index -= 1
            
            if AAR_props.animation_collection_index < 0 and len(collection) > 0:
                AAR_props.animation_collection_index = 0
       
        return {'FINISHED'}

class ANIMAUTORENDER_OT_disable_enable_animations(bpy.types.Operator):
    bl_label = "Disable/enable all"
    bl_idname = "animautorender.disable_enable_animations"  
    bl_description = "Disable/enable all"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        
        collection = AAR_props.animation_collection
        enabledAnimationCount = sum(1 for y in collection if y.enabled)
        for item in collection:
            item.enabled = enabledAnimationCount == 0
       
        return {'FINISHED'}


#
#    Frames
#  
class ANIMAUTORENDER_OT_add_frame(bpy.types.Operator):
    bl_label = "Add frame"
    bl_idname = "animautorender.add_frame"  
    bl_description = "Add frame"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        collection = AAR_props.animation_collection[AAR_props.animation_collection_index].frames
        added = collection.add()
        added.frame = context.scene.frame_current
       
        return {'FINISHED'}
    
class ANIMAUTORENDER_OT_clear_frame(bpy.types.Operator):
    bl_label = "Clear frame list"
    bl_idname = "animautorender.clear_frame"  
    bl_description = "Clear frame list"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        collection = AAR_props.animation_collection[AAR_props.animation_collection_index].frames
        
        collection.clear()
        AAR_props.animation_collection[AAR_props.animation_collection_index].frames_index = -1
       
        return {'FINISHED'}


class ANIMAUTORENDER_OT_remove_frame(bpy.types.Operator):
    bl_label = "Remove frame"
    bl_idname = "animautorender.remove_frame"  
    bl_description = "Remove frame"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        collection = AAR_props.animation_collection[AAR_props.animation_collection_index].frames
        index = AAR_props.animation_collection[AAR_props.animation_collection_index].frames_index
        
        if index >= 0:                        
            collection.remove(index)
            AAR_props.animation_collection[AAR_props.animation_collection_index].frames_index -= 1
            
            if AAR_props.animation_collection[AAR_props.animation_collection_index].frames_index < 0 and len(collection) > 0:
                AAR_props.animation_collection[AAR_props.animation_collection_index].frames_index = 0
       
        return {'FINISHED'}
    
class ANIMAUTORENDER_OT_current_frame(bpy.types.Operator):
    bl_label = "Set to current frame"
    bl_idname = "animautorender.current_frame"  
    bl_description = "Set to current frame"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        animation = AAR_props.animation_collection[AAR_props.animation_collection_index]
        animation.frames[animation.frames_index].frame = context.scene.frame_current
       
        return {'FINISHED'}
    
        
class ANIMAUTORENDER_OT_add_next_frame(bpy.types.Operator):
    bl_label = "Add next frame"
    bl_idname = "animautorender.add_next_frame"  
    bl_description = "Add next frame"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        collection = AAR_props.animation_collection[AAR_props.animation_collection_index].frames
        context.scene.frame_current += 1
        added = collection.add()
        added.frame = context.scene.frame_current
       
        return {'FINISHED'}
  
    
class ANIMAUTORENDER_OT_add_range_frame(bpy.types.Operator):
    bl_label = "Add frames from start to end"
    bl_idname = "animautorender.add_range_frame"  
    bl_description = "Add frame from start to end"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        collection = AAR_props.animation_collection[AAR_props.animation_collection_index].frames
        for i in range(context.scene.frame_start, context.scene.frame_end + 1):
            added = collection.add()
            added.frame = i
       
        return {'FINISHED'}

class ANIMAUTORENDER_OT_disable_enable_frames(bpy.types.Operator):
    bl_label = "Disable/enable all"
    bl_idname = "animautorender.disable_enable_frames"  
    bl_description = "Disable/enable all"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        index = AAR_props.animation_collection_index
        if index >= 0:
            collection = AAR_props.animation_collection[AAR_props.animation_collection_index].frames
            enabledFramesCount = sum(1 for y in collection if y.enabled)
            for item in collection:
                item.enabled = enabledFramesCount == 0
       
        return {'FINISHED'}
    
class ANIMAUTORENDER_OT_keep_active_unique_frames(bpy.types.Operator):
    bl_label = "Keep active only unique frames"
    bl_idname = "animautorender.keep_active_unique_frames"  
    bl_description = "Keep active only first frame of frames with the same number"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        index = AAR_props.animation_collection_index
        if index >= 0:
            collection = AAR_props.animation_collection[AAR_props.animation_collection_index].frames
            
            list_of_used_frames = []
            
            for item in collection:
                if item.frame not in list_of_used_frames:
                    item.enabled = True
                    list_of_used_frames.append(item.frame)
                else:
                    item.enabled = False
       
        return {'FINISHED'}
    
    
    
class ANIMAUTORENDER_OT_play_rendered_preview(bpy.types.Operator):
    bl_label = "Preview rendered animation"
    bl_idname = "animautorender.play_rendered_preview"  
    bl_description = "Preview rendered animation"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        index = AAR_props.animation_collection_index
        if index >= 0 and AAR_props.directionList_index >= 0:
            animation = AAR_props.animation_collection[AAR_props.animation_collection_index]
            folderName = animation.folderName
            
            collection = animation.frames
            
            direction = AAR_props.directionList[AAR_props.directionList_index]
                
            animFolder = animation.folderName
            separator = AAR_props.file_name_separator
            dirFolder = direction.folderName
            
            scene = bpy.context.scene
            
            path = AAR_props.save_path + animFolder + "\\" + dirFolder + "\\"
            prevPath = scene.render.filepath
            
            scene.render.filepath = path
            
            frame_start = scene.frame_start
            frame_end = scene.frame_end
            
            scene.frame_start = 0
            
            first_frame_found = False
                        
            list_of_used_frames = []
            
            for item in collection:
                if item.frame not in list_of_used_frames:
                    list_of_used_frames.append(item.frame)
                if item.enabled and not first_frame_found:
                    if animation.override_first_frame_index:
                        scene.frame_start = item.frame
                        first_frame_found = True
                    
                    
            scene.frame_end = scene.frame_start + len(list_of_used_frames) - 1
            
            fps = scene.render.fps
            scene.render.fps = AAR_props.previewFPS
            
            frame_step = scene.frame_step
            scene.frame_step = 1
            
            
            bpy.ops.render.play_rendered_anim()
            
            scene.render.filepath = prevPath
            scene.frame_start = frame_start
            scene.frame_end = frame_end
            scene.render.fps = fps
            scene.frame_step = frame_step
       
        return {'FINISHED'}
   
#
#    Object
#   
class ANIMAUTORENDER_OT_use_current_object(bpy.types.Operator):
    bl_label = "Use current active object"
    bl_idname = "animautorender.use_current_object"  
    bl_description = "Use current active object"
     
    def invoke(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        AAR_props.mainObject = context.active_object.name
       
        return {'FINISHED'}