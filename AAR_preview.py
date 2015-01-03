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


class VIEW3D_OT_aar_preview(bpy.types.Operator):
    """Animation Automaton Renderer preview operator"""
    bl_idname = "view3d.aar_preview"
    bl_label = "AAR Preview Operator"

    _timer = None
    _index = 0
    _direction = 1
    _animationIndex = 0

    def modal(self, context, event):
        AAR_props = context.scene.AnimAutoRender_properties
        if event.type in {'ESC'} or not AAR_props.previewIsOn or len(AAR_props.animation_collection[self._animationIndex].frames) == 0:
            return self.cancel(context)

        if event.type == 'TIMER':
            animation = AAR_props.animation_collection[self._animationIndex]
            self._index += self._direction
            
            if self._index < 0:
                self._direction = 1
                self._index = 1
            
            if self._index >= len(animation.frames):
                if AAR_props.loopType == 0:
                    self._index = 0
                elif AAR_props.loopType == 1:
                    self._direction = -1
                    self._index = len(animation.frames) - 2
            
            frame = animation.frames[self._index]
            bpy.context.scene.frame_set(frame.frame)

        return {'PASS_THROUGH'}

    def execute(self, context):
        AAR_props = context.scene.AnimAutoRender_properties
        
        if AAR_props.previewIsOn:
            AAR_props.previewIsOn = False
            return {'CANCELLED'}
        
        AAR_props.previewIsOn = True
        
        refresh = 1.0/AAR_props.previewFPS
        
        self._animationIndex = AAR_props.animation_collection_index
        
        if AAR_props.mainObject and len(bpy.data.actions) > 1:
            context.active_object.animation_data.action = bpy.data.actions[AAR_props.animation_collection[self._animationIndex].actionProp]
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(refresh, context.window)
        wm.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        
        AAR_props = context.scene.AnimAutoRender_properties
        AAR_props.previewIsOn = False
        return {'CANCELLED'}