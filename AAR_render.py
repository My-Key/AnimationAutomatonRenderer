'''
Copyright (C) 2014 EVERYDAYiPLAY
http://www.everydayiplay.com/
contact@everydayiplay.com

Created by Maciej Paluszek
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
#    Rendering modal operator
#
class RENDER_OT_animation_automaton_render(bpy.types.Operator):
    bl_label = "Animation Automaton Render"
    bl_idname = "render.animation_automaton_render"
    __doc__ = """Render selected animations"""

    _timer = None
    _calcs_done = False
    _updating = False
    _animationIndex = 0
    _directionIndex = 0
    _frameIndex = 0
    _index = 0

    def modal(self, context, event):
        if event.type in {'ESC'} or self._calcs_done:
            return self.cancel(context)

        if event.type == 'TIMER' and not self._updating:
            self._updating = True
            self.render_one_frame(context)
            self._updating = False

        return {'PASS_THROUGH'}

    def execute(self, context):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        
        if AnimAutoRender_props.mainObject and context.scene.objects.find(AnimAutoRender_props.mainObject) < 0:
            return {'CANCELLED'}
        
        bpy.ops.object.mode_set(mode = 'OBJECT') 
        
        if AnimAutoRender_props.mainObject and AnimAutoRender_props.specifyMainObject:
            bpy.ops.object.select_all(action='DESELECT') 
            bpy.context.scene.objects.active = context.scene.objects[AnimAutoRender_props.mainObject]
            context.scene.objects[AnimAutoRender_props.mainObject].select = True
        
        self.defPath = context.scene.render.filepath
        
        for animation in AnimAutoRender_props.animation_collection:
            
            if not animation.active:
                continue
            
            dirsCount = 0
            framesCount = 0
            
            for directionChosen in animation.chosenDirection:
                if directionChosen.directionEnable:
                    dirsCount += 1
                 
            if dirsCount > 0:
                for frame in animation.frames:
                    if not frame.render:
                        continue
                    framesCount+=1
            AnimAutoRender_props.total_frames += dirsCount * framesCount
        
        AnimAutoRender_props.rendering = True
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        bpy.ops.render.view_show('INVOKE_DEFAULT')
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        bpy.context.scene.render.filepath = self.defPath
        context.area.header_text_set()
        self._animationIndex = 0
        self._directionIndex = 0
        self._frameIndex = 0
        
        obj = context.scene.AnimAutoRender_properties
        obj.total_frames = 0
        obj.rendering = False
        obj.frames_done = 0
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        bpy.ops.render.view_show('INVOKE_DEFAULT')
        return {'CANCELLED'}
    
    def render_one_frame(self, context):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        
        animation = None
        
        for _ in range(self._animationIndex, len(AnimAutoRender_props.animation_collection)):
            if AnimAutoRender_props.animation_collection[self._animationIndex].active:
                animation = AnimAutoRender_props.animation_collection[self._animationIndex]
                break
            else:
                self._animationIndex += 1
                self._directionIndex = 0
                self._frameIndex = 0
        
        if animation == None:
            self._calcs_done = True
            return
        
        if AnimAutoRender_props.mainObject and len(bpy.data.actions) > 1 and self._directionIndex == 0 and self._frameIndex == 0:
            context.active_object.animation_data.action = bpy.data.actions[animation.actionProp]
        
        dirsCount = 0
            
        for directionChosen in animation.chosenDirection:
            if directionChosen.directionEnable:
                dirsCount += 1
        
        if dirsCount > 0:            
            directionChosen = None
            
            for _ in range(self._directionIndex, len(animation.chosenDirection)):
                if animation.chosenDirection[self._directionIndex].directionEnable:
                    directionChosen = animation.chosenDirection[self._directionIndex]
                    break
                else:
                    self._directionIndex += 1
                    self._frameIndex = 0
                    
            if directionChosen == None:
                self._animationIndex += 1
                self._directionIndex = 0
                self._frameIndex = 0
            else:
                if directionChosen.directionEnable:
                
                    direction = AnimAutoRender_props.directionList[self._directionIndex]
                    
                    if self._frameIndex == 0:
                        bpy.ops.transform.rotate(value=direction.direction, axis=(0,0,1))
                        if animation.override_first_frame_index:
                            if animation.use_index_of_first_frame:
                                for frame in animation.frames:
                                    if frame.render:
                                        self._index = frame.frame
                                        break
                            else:
                                self._index = animation.first_frame_index
                        else:
                            self._index = AnimAutoRender_props.first_frame_index
                        
                        for _ in range(animation.go_through_cycle_count):
                            for frame in animation.frames:
                                bpy.context.scene.frame_set(frame.frame)
                                
                        for _ in range(animation.repeat_first_frame):
                            bpy.context.scene.frame_set(animation.frames[0].frame)
                            
                    frame = None
                    
                    for _ in range(self._frameIndex, len(animation.frames)):
                        if animation.frames[self._frameIndex].render:
                            frame = animation.frames[self._frameIndex]
                            break
                        else:
                            self._frameIndex += 1
                    
                    if frame == None:
                        self._directionIndex += 1
                        self._frameIndex = 0
                        bpy.ops.object.rotation_clear()
                        return
                    else:
                        if not frame.render:
                            return
                        
                        animFolder = animation.folderName
                        separator = AnimAutoRender_props.file_name_separator
                        dirFolder = direction.folderName
                        
                        path = AnimAutoRender_props.save_path + animFolder + "\\"
                        
                        if AnimAutoRender_props.simple_frame_name:
                            frameName = ("%04d") % self._index
                        else:
                            # animFolder_dirFolder_frameNumber
                            frameName = ((animFolder + separator) if AnimAutoRender_props.use_anim_folder_name else "") + ((dirFolder + separator) if AnimAutoRender_props.use_dir_folder_name else "") + ("%0" + str(AnimAutoRender_props.frame_number_digits) + "d") % self._index
                        
                        
                        if dirsCount > 1:
                            bpy.context.scene.render.filepath = path + dirFolder + "\\" + frameName
                        else:
                            bpy.context.scene.render.filepath = path + frameName
                        
                        if AnimAutoRender_props.repeat_go_to_frame:
                            bpy.context.scene.frame_set(frame.frame)
                        
                        bpy.context.scene.frame_set(frame.frame)
                        bpy.ops.render.render(write_still=True)
                        self._frameIndex += 1
                        self._index += 1
                        AnimAutoRender_props.frames_done += 1
                        AnimAutoRender_props.percentage = (AnimAutoRender_props.frames_done / AnimAutoRender_props.total_frames) * 100