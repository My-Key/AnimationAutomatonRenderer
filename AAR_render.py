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

class Frame_To_Render():
    animationIndex = 0
    directionIndex = 0
    frameIndex = 0
    render = True
    dirsCount = 0
    
    def __init__(self, animIndex, dirIndex, frameIndex, dirsCount = 0, render = True):
        self.animationIndex = animIndex
        self.directionIndex = dirIndex
        self.frameIndex = frameIndex
        self.dirsCount = dirsCount
        self.render = render
    
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
    _index = 0
    _defPath = ""
    _startTime = 0.0
    _frameDone = False
    _nextFrameDelay = 0.0
    _framesList = []

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
        
    def cancel_render(self, scene):
        self._calcs_done = True

    def execute(self, context):
        AAR_props = context.scene.AnimAutoRender_properties
        if AAR_props.mainObject and context.scene.objects.find(AAR_props.mainObject) < 0:
            return {'CANCELLED'}
        
        AAR_props.previewIsOn = False
        
        bpy.app.handlers.render_complete.append(self.complete_render)
        bpy.app.handlers.render_cancel.append(self.cancel_render)
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        AAR_props.totalTime = 0
        
        if AAR_props.mainObject and AAR_props.specifyMainObject:
            bpy.ops.object.select_all(action='DESELECT') 
            bpy.context.scene.objects.active = context.scene.objects[AAR_props.mainObject]
            context.scene.objects[AAR_props.mainObject].select = True
        
        self._defPath = context.scene.render.filepath
        
        AAR_props.total_frames = sum( sum(1 for y in a.chosenDirection if y.enabled) * sum(1 for y in a.frames if y.enabled)
                                   for a in AAR_props.animation_collection if a.enabled)
        
        AAR_props.rendering = True
        self._updating = False
        self._frameDone = False
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        
        self.create_list_of_frames(context)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        bpy.context.scene.render.filepath = self._defPath
        
        self._updating = False
        self._frameDone = False
        
        bpy.ops.object.rotation_clear()
        
        bpy.app.handlers.render_complete.remove(self.complete_render)
        bpy.app.handlers.render_cancel.remove(self.cancel_render)
        
        AAR_props = context.scene.AnimAutoRender_properties
        AAR_props.total_frames = 0
        AAR_props.rendering = False
        AAR_props.frames_done = 0
        AAR_props.percentage = 0
        
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        
        return {'CANCELLED'}
    
    def create_list_of_frames(self, context):
        AAR_props = context.scene.AnimAutoRender_properties
        
        for animationIndex in range(len(AAR_props.animation_collection)):
            animation = AAR_props.animation_collection[animationIndex]
            if not animation.enabled:
                continue
            
            dirsCount = 0
                
            for direction in animation.chosenDirection:
                if direction.enabled:
                    dirsCount += 1
            
            for directionIndex in range(len(animation.chosenDirection)):
                direction = animation.chosenDirection[directionIndex]
                
                if not direction.enabled:
                    continue
                
                for _ in range(animation.go_through_cycle_count):
                    for frameIndex in range(len(animation.frames)):
                        self._framesList.append(Frame_To_Render(animationIndex, directionIndex, frameIndex, render = False))
                        
                for _ in range(animation.repeat_first_frame):
                    self._framesList.append(Frame_To_Render(animationIndex, directionIndex, 0, render = False))
                        
                for frameIndex in range(len(animation.frames)):
                    if animation.frames[frameIndex].enabled:
                        self._framesList.append(Frame_To_Render(animationIndex, directionIndex, frameIndex, dirsCount))
                    
    def render_one_frame(self, context):
        if len(self._framesList) == 0:
            self._calcs_done = True
            return False
        
        AAR_props = context.scene.AnimAutoRender_properties
        
        ftr = None
        animation = None
        direction = None
        frame = None
        
        while len(self._framesList) > 0:
            ftr = self._framesList.pop(0)
            animation = AAR_props.animation_collection[ftr.animationIndex]
            direction = AAR_props.directionList[ftr.directionIndex]
            frame = animation.frames[ftr.frameIndex]
            
            bpy.context.scene.frame_set(frame.frame)
            
            if ftr.render:
                break
        
        
        firstActiveFrame = -1
        
        for i in range(len(animation.frames)):
            if animation.frames[i].enabled:
                firstActiveFrame = i
                break
        
        if firstActiveFrame < 0:
            return False
        
        if ftr.frameIndex == firstActiveFrame:
            bpy.ops.object.rotation_clear()
            bpy.ops.transform.rotate(value=direction.direction, axis=(0,0,1))
            
            if AAR_props.mainObject and len(bpy.data.actions) > 1:
                context.active_object.animation_data.action = bpy.data.actions[animation.actionProp]
            
            if animation.override_first_frame_index:
                if animation.use_index_of_first_frame:
                    self._index = firstActiveFrame
                else:
                    self._index = animation.first_frame_index
            else:
                self._index = AAR_props.first_frame_index
        
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
        
        
        bpy.context.scene.render.filepath = (path + dirFolder + "\\" + frameName) if ftr.dirsCount > 1 else (path + frameName)

        if AAR_props.repeat_go_to_frame:
            bpy.context.scene.frame_set(frame.frame)
        
        self._index += 1
        AAR_props.frames_done += 1
        AAR_props.percentage = (AAR_props.frames_done / AAR_props.total_frames) * 100
        bpy.ops.render.render('INVOKE_DEFAULT', write_still=True)
        
        return True