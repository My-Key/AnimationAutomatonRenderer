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

import bpy, bl_operators
import math

# 
#    List elements
#
class AnimAutoRender_UL_animation(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            AAR_props = context.scene.AnimAutoRender_properties
            
            layout.label(text=item.name)
            
            if not AAR_props.animations_same_name:
                layout.label(item.folderName)
            
            layout.prop(item, "enabled")
            
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name + " - " + item.folderName)

      
class AnimAutoRender_UL_direction(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        AAR_props = context.scene.AnimAutoRender_properties
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)
            
            if not AAR_props.directions_same_name:
                layout.label(item.folderName)
            
            layout.label("%d" % math.degrees(item.direction) +'\N{DEGREE SIGN}')
            
            if AAR_props.animation_collection_index >= 0:
                layout.prop(AAR_props.animation_collection[AAR_props.animation_collection_index].chosenDirection[index],
                            "enabled")
            
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name + " - " + item.folderName + " - " +
                         "%d" % math.degrees(item.direction) + '\N{DEGREE SIGN}')

      
class AnimAutoRender_UL_frame(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=str(item.frame))
            layout.prop(item, "enabled")
            
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=str(item.frame))


class PreviewLoopMenu(bpy.types.Menu):
    bl_label = "Preview Loop Menu"
    bl_idname = "VIEW3D_MT_preview_loop_menu"

    def draw(self, context):
        layout = self.layout

        props = layout.operator("wm.context_set_value", text="Repeat", icon="FILE_REFRESH")
        props.data_path = "scene.AnimAutoRender_properties.loopType"
        props.value = "0"
        
        props = layout.operator("wm.context_set_value", text="Ping pong", icon="ARROW_LEFTRIGHT")
        props.data_path = "scene.AnimAutoRender_properties.loopType"
        props.value = "1"
            
#
#    Presets
#
class AnimAutoRender_MT_options_presets(bpy.types.Menu):
    bl_label = "AnimAutoRender Options Presets"
    preset_subdir = "AnimAutoRender/Options"
    preset_operator = "script.execute_preset"
    def draw(self, context):
        return bpy.types.Menu.draw_preset(self, context)
    
class AnimAutoRender_OT_preset_options_add(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    '''Save the current settings as a preset'''
    bl_idname = 'animautorender.options_preset_add'
    bl_label = 'Add options preset'
    preset_menu = 'AnimAutoRender_MT_options_presets'
    preset_values = []
    preset_defines = ["AAR_p = bpy.context.scene.AnimAutoRender_properties"]
    preset_subdir = 'AnimAutoRender/Options'
    
    def execute(self, context):
        self.preset_values = ['AAR_p.%s' % v for v in context.scene.AnimAutoRender_properties.propsToExport()]
        return super().execute(context)
    
    
class AnimAutoRender_MT_directions_presets(bpy.types.Menu):
    bl_label = "AnimAutoRender Directions Presets"
    preset_subdir = "AnimAutoRender/Directions"
    preset_operator = "script.execute_preset"
    def draw(self, context):
        return bpy.types.Menu.draw_preset(self, context)
    
class AnimAutoRender_OT_preset_directions_add(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    '''Save the current settings as a preset'''
    bl_idname = 'animautorender.directions_preset_add'
    bl_label = 'Add options preset'
    preset_menu = 'AnimAutoRender_MT_directions_presets'
    preset_values = []
    preset_subdir = 'AnimAutoRender/Directions'
    
    def execute(self, context):
        self.preset_values = ['bpy.context.scene.AnimAutoRender_properties.directionList']

        return super().execute(context)
    
"""
class AnimAutoRender_MT_animations_presets(bpy.types.Menu):
    bl_label = "AnimAutoRender animations Presets"
    preset_subdir = "AnimAutoRender/Animations"
    preset_operator = "script.execute_preset"
    def draw(self, context):
        return bpy.types.Menu.draw_preset(self, context)
    
class AnimAutoRender_OT_preset_animations_add(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    '''Save the current settings as a preset'''
    bl_idname = 'animautorender.animations_preset_add'
    bl_label = 'Add options preset'
    preset_menu = 'AnimAutoRender_MT_animations_presets'
    preset_values = []
    preset_subdir = 'AnimAutoRender/Animations'
    
    def execute(self, context):
        self.preset_values = ['bpy.context.scene.AnimAutoRender_properties.animation_collection']

        return super().execute(context)
"""


def SecToStr(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02.2f' % (hours, mins, secs)
#
#    Panel
#
class RENDER_PT_Animation_Automaton_Renderer(bpy.types.Panel):
    bl_label = 'Animation Automaton Renderer'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    
    def draw(self, context):
        layout = self.layout
        
        AAR_props = context.scene.AnimAutoRender_properties
        
        #
        #    Rendering
        #
    
        row = layout.row()
        row.operator("render.animation_automaton_render", icon="CLIP", text="Render animation")
        
        col = layout.column()
        col.alert = True
        enableRendering = True
        
        framesToRenderCount = sum( sum(1 for y in a.chosenDirection if y.enabled) * sum(1 for y in a.frames if y.enabled)
                                   for a in AAR_props.animation_collection if a.enabled)
        
        if AAR_props.mainObject and len(bpy.data.actions) > 1:
            for animation in AAR_props.animation_collection:
                if animation.enabled and bpy.data.actions.find(animation.actionProp) < 0:
                    enableRendering = False
                    col.label("Missing or wrong action define in " + animation.name, icon='ERROR')
        
        if AAR_props.specifyMainObject and context.scene.objects.find(AAR_props.mainObject) < 0:
            enableRendering = False
            col.label("Missing or wrong main object", icon='ERROR')
        
        if len(AAR_props.animation_collection) == 0:
            enableRendering = False
            col.label("Empty list of animations", icon='ERROR')
            
        if len(AAR_props.directionList) == 0:
            enableRendering = False
            col.label("Empty list of directions", icon='ERROR')
            
        if framesToRenderCount == 0:
            enableRendering = False
            col.label("No frames to render", icon='ERROR')
        
        row.enabled = enableRendering and not AAR_props.rendering
        
        if AAR_props.rendering:
            col = layout.column()
            col.label(text="RENDERING ANIMATION: " + "%d" % AAR_props.frames_done + "/" +
                      "%d" % AAR_props.total_frames)
            col.prop(AAR_props, 'percentage')
            col.label("Total time: " + SecToStr(AAR_props.totalTime))
            
            if AAR_props.frames_done > 0:
                averageRenderTime = AAR_props.totalTime / AAR_props.frames_done
                col.label("Average render time: " + SecToStr(averageRenderTime))
                col.label("Estimated time to finish: " +
                          SecToStr(averageRenderTime *(AAR_props.total_frames - AAR_props.frames_done) ))
            
            col.enabled = True
        else:
            if AAR_props.totalTime > 0:
                col.label("Last render time: " + SecToStr(AAR_props.totalTime))
            
            layout.label(text="Total frames to render: " + "%d" % framesToRenderCount)
        
        layout.separator()
        
        
        animation = None
        if len(AAR_props.animation_collection) > 0:
            animation = AAR_props.animation_collection[AAR_props.animation_collection_index]
        
        framesEnabledCount = (sum(1 for y in animation.frames if y.enabled) if animation else 0)
        
        if framesEnabledCount <= 1 and animation:
            layout.label("Preview requires more than 1 enabled frame", icon='ERROR')
        
        if not animation:
            layout.label("No animation to preview", icon='ERROR')
            
        col = layout.column()
            
        if not AAR_props.previewIsOn:
            col.operator("view3d.aar_preview", icon="PLAY", text="Preview - " + (animation.name if animation else ""))
        else:
            col.operator("view3d.aar_preview", icon="PAUSE", text="Preview - " + (animation.name if animation else ""))
    
        col.enabled = framesEnabledCount > 1
    
        row = col.row()
        col.prop(AAR_props, "preview_skip_disabled_frames")
        col = row.column()
        col.prop(AAR_props, 'previewFPS')
        col.enabled = not AAR_props.previewIsOn
        row.menu('VIEW3D_MT_preview_loop_menu', text="Repeat" if AAR_props.loopType == 0 else "Ping pong",
                 icon="FILE_REFRESH" if AAR_props.loopType == 0 else "ARROW_LEFTRIGHT")
        
        layout.separator()
        
        layout = layout.column()
        layout.enabled = not AAR_props.rendering and not AAR_props.previewIsOn
        
        #
        #    Options
        #
        row = layout.row(align=True)
        
        if AAR_props.options_expand:
            row.prop(AAR_props, "options_expand", icon="DOWNARROW_HLT", text="", icon_only=True, emboss=False)
            row.label(text="Options")
            
            row = layout.row(align=True)
            row.menu("AnimAutoRender_MT_options_presets", text=bpy.types.AnimAutoRender_MT_options_presets.bl_label)
            row.operator("animautorender.options_preset_add", text="", icon="ZOOMIN")
            row.operator("animautorender.options_preset_add", text="", icon="ZOOMOUT").remove_active = True
            
            layout.prop(AAR_props, 'save_path') 
            layout.prop(AAR_props, 'first_frame_index')
            layout.prop(AAR_props, 'repeat_go_to_frame')
            layout.prop(AAR_props, 'simple_frame_name')
            
            if not AAR_props.simple_frame_name:
                layout.separator()
                layout.label(text="Filename options")
                
                row = layout.row()
                row.prop(AAR_props, 'frame_number_digits')
                row.prop(AAR_props, 'file_name_separator')
                layout.prop(AAR_props, 'use_anim_folder_name')
                layout.prop(AAR_props, 'use_dir_folder_name')
                
                exampleName = ((("anim" + AAR_props.file_name_separator) if AAR_props.use_anim_folder_name else "") +
                               (("dir" + AAR_props.file_name_separator) if AAR_props.use_dir_folder_name else "") +
                                ("%0" + str(AAR_props.frame_number_digits) + "d") % 1)
                
                layout.label(text="Example: " + exampleName + context.scene.render.file_extension)
            
            layout.prop(AAR_props, 'specifyMainObject')
            if AAR_props.specifyMainObject:
                row = layout.row(align=True)
                row.prop_search(AAR_props, "mainObject", context.scene, "objects")
                row.operator("animautorender.use_current_object", icon="OBJECT_DATA", text="")
        else:
            row.prop(AAR_props, "options_expand", icon="RIGHTARROW", text="", icon_only=True, emboss=False)
            row.label(text="Options")
        
        
        layout.separator()
        
        #
        #    Directions menu
        #
        row = layout.row()
        if AAR_props.animation_collection_index < 0:
            row.label(text="Directions")
        else:
            row.label(text="Directions: " +
                      "%d" % sum(1 for y in AAR_props.animation_collection[AAR_props.animation_collection_index].chosenDirection
                                 if y.enabled) + " / " +
                                 "%d" % len(AAR_props.animation_collection[AAR_props.animation_collection_index].chosenDirection))
        
        row = layout.row(align=True)
        row.menu("AnimAutoRender_MT_directions_presets", text=bpy.types.AnimAutoRender_MT_directions_presets.bl_label)
        row.operator("animautorender.directions_preset_add", text="", icon="ZOOMIN")
        row.operator("animautorender.directions_preset_add", text="", icon="ZOOMOUT").remove_active = True
        
        row = layout.row(align=True)
        row.template_list("AnimAutoRender_UL_direction", "", AAR_props, "directionList", AAR_props, "directionList_index", rows=3)
        col = row.column(align=True)
        
        col.operator("animautorender.add_direction", icon="ZOOMIN", text="")
        col.operator("animautorender.remove_direction", icon="ZOOMOUT", text="")
        col.operator("animautorender.clear_direction", icon="X", text="")
        col.operator("animautorender.invert_selection_direction", icon="FILE_REFRESH", text="")
        
        #
        #    Options to selected direction
        #
        if AAR_props.directionList and AAR_props.directionList_index >= 0:
            row = layout.row()
            if AAR_props.directions_expand:
                row.prop(AAR_props, "directions_expand", icon="DOWNARROW_HLT", text="", icon_only=True, emboss=False)
                row.label(text="Direction properties")
                direction = AAR_props.directionList[AAR_props.directionList_index]
                
                layout.prop(AAR_props, "directions_same_name")
                
                if not AAR_props.directions_same_name:
                    layout.prop(direction, "name")
                    
                layout.prop(direction, "folderName")
                layout.prop(direction, "direction")
            else:
                row.prop(AAR_props, "directions_expand", icon="RIGHTARROW", text="", icon_only=True, emboss=False)
                row.label(text="Direction properties")
        
        layout.separator()
        
        
        #
        #    Animations menu
        #
        row = layout.row()
        row.label(text="Animations: " + "%d" % sum(1 for y in AAR_props.animation_collection if y.enabled) + " / " +
                  "%d" % len(AAR_props.animation_collection))
        
        '''
        row = layout.row(align=True)
        row.menu("AnimAutoRender_MT_animations_presets", text=bpy.types.AnimAutoRender_MT_animations_presets.bl_label)
        row.operator("animautorender.animations_preset_add", text="", icon="ZOOMIN")
        row.operator("animautorender.animations_preset_add", text="", icon="ZOOMOUT").remove_active = True
        '''
        
        
        row = layout.row(align=True)
        row.template_list("AnimAutoRender_UL_animation", "", AAR_props, "animation_collection", AAR_props,
                          "animation_collection_index", rows=3)
        col = row.column(align=True)
        
        col.operator("animautorender.add_animation", icon="ZOOMIN", text="")
        col.operator("animautorender.remove_animation", icon="ZOOMOUT", text="")
        col.operator("animautorender.clear_animation", icon="X", text="")
        col.operator("animautorender.invert_selection_animation", icon="FILE_REFRESH", text="")
        
        #
        #    Options to selected animation
        #
        if AAR_props.animation_collection and AAR_props.animation_collection_index >= 0:
            entry = AAR_props.animation_collection[AAR_props.animation_collection_index]
            
            row = layout.row()
            if AAR_props.animations_expand:
                row.prop(AAR_props, "animations_expand", icon="DOWNARROW_HLT", text="", icon_only=True, emboss=False)
                row.label(text="Animation properties")
                
                layout.prop(AAR_props, "animations_same_name")
                
                if not AAR_props.animations_same_name:
                    layout.prop(entry, "name")
                    
                layout.prop(entry, "folderName")
                layout.prop(entry, "go_through_cycle_count")
                layout.prop(entry, "repeat_first_frame")
                
                
                layout.prop(entry, "override_first_frame_index")
                if entry.override_first_frame_index:
                    layout.prop(entry, "first_frame_index")
                    layout.prop(entry, "use_index_of_first_frame")
                
                if AAR_props.mainObject and len(bpy.data.actions) > 1:
                    layout.prop_search(entry, "actionProp", bpy.data, "actions")
                    
            else:
                row.prop(AAR_props, "animations_expand", icon="RIGHTARROW", text="", icon_only=True, emboss=False)
                row.label(text="Animation properties")
                
            layout.separator()
            
            #
            #    Frames menu
            #
            row = layout.row()
            row.label(text="Frames: " + "%d" % sum(1 for y in entry.frames if y.enabled) + " / " + "%d" % len(entry.frames))
            row = layout.row(align=True)
            row.template_list("AnimAutoRender_UL_frame", "", entry, "frames", entry, "frames_index", rows=5)
            col = row.column(align=True)
            
            col.operator("animautorender.add_frame", icon="ZOOMIN", text="")
            col.operator("animautorender.remove_frame", icon="ZOOMOUT", text="")
            col.operator("animautorender.add_next_frame", icon="FORWARD", text="")
            col.operator("animautorender.add_range_frame", icon="ARROW_LEFTRIGHT", text="")
            col.operator("animautorender.clear_frame", icon="X", text="")
            col.operator("animautorender.invert_selection_frame", icon="FILE_REFRESH", text="")
            
            
            #
            #    Options to selected frame
            #
            if entry.frames and entry.frames_index >= 0:
                frame = entry.frames[entry.frames_index]
                row = layout.row(align=True)
                row.prop(frame, "frame")
                row.operator("animautorender.current_frame", icon="TIME", text="Set current frame")