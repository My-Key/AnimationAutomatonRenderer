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

import bpy, time

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
    _defPath = ""
    _startTime = 0.0
    _frameDone = False
    _nextFrameDelay = 0.0

    def modal(self, context, event):
        if event.type in {'ESC'} or self._calcs_done:
            return self.cancel(context)
        
        if event.type == 'TIMER' and not self._updating:
            self._updating = True
            self._startTime = time.time()
            self._updating = self.render_one_frame(context)
            
        if event.type == 'TIMER' and self._updating and self._frameDone:
            self._nextFrameDelay += 0.1
            
            if self._nextFrameDelay >= 0.2:
                self._frameDone = False
                self._updating = False
                self._nextFrameDelay = 0.0

        return {'PASS_THROUGH'}
    
    def complete_render(self, scene):
        AAR_props = bpy.context.scene.AnimAutoRender_properties
        AAR_props.totalTime += time.time() - self._startTime
        self._frameDone = True

    def execute(self, context):
        AAR_props = context.scene.AnimAutoRender_properties
        if AAR_props.mainObject and context.scene.objects.find(AAR_props.mainObject) < 0:
            return {'CANCELLED'}
        
        bpy.app.handlers.render_complete.append(self.complete_render)
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        AAR_props.totalTime = 0
        
        if AAR_props.mainObject and AAR_props.specifyMainObject:
            bpy.ops.object.select_all(action='DESELECT') 
            bpy.context.scene.objects.active = context.scene.objects[AAR_props.mainObject]
            context.scene.objects[AAR_props.mainObject].select = True
        
        self._defPath = context.scene.render.filepath
        
        for animation in AAR_props.animation_collection:
            
            if not animation.enabled:
                continue
            
            dirsCount = 0
            framesCount = 0
            
            for directionChosen in animation.chosenDirection:
                if directionChosen.enabled:
                    dirsCount += 1
                 
            if dirsCount > 0:
                for frame in animation.frames:
                    if not frame.enabled:
                        continue
                    framesCount+=1
            AAR_props.total_frames += dirsCount * framesCount
        
        AAR_props.rendering = True
        self._updating = False
        self._frameDone = False
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        bpy.context.scene.render.filepath = self._defPath
        context.area.header_text_set()
        self._animationIndex = 0
        self._directionIndex = 0
        self._frameIndex = 0
        self._updating = False
        self._frameDone = False
        
        bpy.app.handlers.render_complete.remove(self.complete_render)
        
        AAR_props = context.scene.AnimAutoRender_properties
        AAR_props.total_frames = 0
        AAR_props.rendering = False
        AAR_props.frames_done = 0
        AAR_props.percentage = 0
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        return {'CANCELLED'}
    
    def render_one_frame(self, context):
        AAR_props = context.scene.AnimAutoRender_properties
        
        animation = None
        
        for _ in range(self._animationIndex, len(AAR_props.animation_collection)):
            if AAR_props.animation_collection[self._animationIndex].enabled:
                animation = AAR_props.animation_collection[self._animationIndex]
                break
            else:
                self._animationIndex += 1
                self._directionIndex = 0
                self._frameIndex = 0
        
        if animation == None:
            self._calcs_done = True
            return False
        
        if AAR_props.mainObject and len(bpy.data.actions) > 1 and self._directionIndex == 0 and self._frameIndex == 0:
            context.active_object.animation_data.action = bpy.data.actions[animation.actionProp]
        
        dirsCount = 0
            
        for directionChosen in animation.chosenDirection:
            if directionChosen.enabled:
                dirsCount += 1
        
        if dirsCount > 0:            
            directionChosen = None
            
            for _ in range(self._directionIndex, len(animation.chosenDirection)):
                if animation.chosenDirection[self._directionIndex].enabled:
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
                if directionChosen.enabled:
                
                    direction = AAR_props.directionList[self._directionIndex]
                    
                    if self._frameIndex == 0:
                        bpy.ops.transform.rotate(value=direction.direction, axis=(0,0,1))
                        if animation.override_first_frame_index:
                            if animation.use_index_of_first_frame:
                                for frame in animation.frames:
                                    if frame.enabled:
                                        self._index = frame.frame
                                        break
                            else:
                                self._index = animation.first_frame_index
                        else:
                            self._index = AAR_props.first_frame_index
                        
                        for _ in range(animation.go_through_cycle_count):
                            for frame in animation.frames:
                                bpy.context.scene.frame_set(frame.frame)
                                
                        for _ in range(animation.repeat_first_frame):
                            bpy.context.scene.frame_set(animation.frames[0].frame)
                            
                    frame = None
                    
                    for _ in range(self._frameIndex, len(animation.frames)):
                        if animation.frames[self._frameIndex].enabled:
                            frame = animation.frames[self._frameIndex]
                            break
                        else:
                            self._frameIndex += 1
                    
                    if frame == None:
                        self._directionIndex += 1
                        self._frameIndex = 0
                        bpy.ops.object.rotation_clear()
                    else:
                        if not frame.enabled:
                            return False
                        
                        animFolder = animation.folderName
                        separator = AAR_props.file_name_separator
                        dirFolder = direction.folderName
                        
                        path = AAR_props.save_path + animFolder + "\\"
                        
                        if AAR_props.simple_frame_name:
                            frameName = ("%04d") % self._index
                        else:
                            # animFolder_dirFolder_frameNumber
                            frameName = (((animFolder + separator) if AAR_props.use_anim_folder_name else "") +
                                         ((dirFolder + separator) if AAR_props.use_dir_folder_name else "") +
                                         ("%0" + str(AAR_props.frame_number_digits) + "d") % self._index)
                        
                        
                        if dirsCount > 1:
                            bpy.context.scene.render.filepath = path + dirFolder + "\\" + frameName
                        else:
                            bpy.context.scene.render.filepath = path + frameName
                        
                        if AAR_props.repeat_go_to_frame:
                            bpy.context.scene.frame_set(frame.frame)
                        
                        bpy.context.scene.frame_set(frame.frame)
                        self._frameIndex += 1
                        self._index += 1
                        AAR_props.frames_done += 1
                        AAR_props.percentage = (AAR_props.frames_done / AAR_props.total_frames) * 100
                        bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)
                        return True
        return False
