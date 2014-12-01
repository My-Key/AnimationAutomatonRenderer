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
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name + " - " + item.folderName)
            layout.prop(item, "active")
            
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name + " - " + item.folderName)

      
class AnimAutoRender_UL_direction(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name + " - " + item.folderName + " - " + "%d" % math.degrees(item.direction) + '\N{DEGREE SIGN}')
            if AnimAutoRender_props.animation_collection_index >= 0:
                layout.prop(AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].chosenDirection[index], "directionEnable")
            
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.name + " - " + item.folderName + " - " + "%d" % math.degrees(item.direction) + '\N{DEGREE SIGN}')

      
class AnimAutoRender_UL_frame(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=str(item.frame))
            layout.prop(item, "render")
            
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=str(item.frame))


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
    preset_defines = [
        "AAR_p = bpy.context.scene.AnimAutoRender_properties"
    ]
    preset_subdir = 'AnimAutoRender/Options'
    
    def execute(self, context):
        self.preset_values = [
            'AAR_p.%s' % v for v in context.scene.AnimAutoRender_properties.propsToExport()
        ]
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
        
        animAutoRender_props = context.scene.AnimAutoRender_properties
        
        #
        #    Rendering
        #
        layout.enabled = not animAutoRender_props.rendering
    
        row = layout.row()
        row.operator("render.animation_automaton_render", icon="CLIP", text="Render animation")
        
        col = layout.column()
        col.alert = True
        enableRendering = True
        
        if animAutoRender_props.mainObject and len(bpy.data.actions) > 1:
            for animation in animAutoRender_props.animation_collection:
                if bpy.data.actions.find(animation.actionProp) < 0:
                    enableRendering = False
                    col.label("Missing or wrong action define in " + animation.name, icon='ERROR')
        
        if animAutoRender_props.specifyMainObject and context.scene.objects.find(animAutoRender_props.mainObject) < 0:
            enableRendering = False
            col.label("Missing or wrong main object", icon='ERROR')
        
        if len(animAutoRender_props.animation_collection) == 0:
            enableRendering = False
            col.label("Empty list of animations", icon='ERROR')
            
        if len(animAutoRender_props.directionList) == 0:
            enableRendering = False
            col.label("Empty list of directions", icon='ERROR')
        
        row.enabled = enableRendering
        
        if animAutoRender_props.rendering:
            layout.label(text="RENDERING ANIMATION: " + "%d" % animAutoRender_props.frames_done + "/" + "%d" % animAutoRender_props.total_frames)
            layout.prop(animAutoRender_props, 'percentage')
        
        layout.separator()
        
        
        #
        #    Options
        #
        row = layout.row(align=True)
        if animAutoRender_props.options_expand:
            row.prop(animAutoRender_props, "options_expand", icon="DOWNARROW_HLT", text="", icon_only=True, emboss=False)
            row.label(text="Options")
            
            row = layout.row(align=True)
            row.menu("AnimAutoRender_MT_options_presets", text=bpy.types.AnimAutoRender_MT_options_presets.bl_label)
            row.operator("animautorender.options_preset_add", text="", icon="ZOOMIN")
            row.operator("animautorender.options_preset_add", text="", icon="ZOOMOUT").remove_active = True
            
            layout.prop(animAutoRender_props, 'save_path') 
            layout.prop(animAutoRender_props, 'first_frame_index')
            layout.prop(animAutoRender_props, 'repeat_go_to_frame')
            layout.prop(animAutoRender_props, 'simple_frame_name')
            
            if not animAutoRender_props.simple_frame_name:
                layout.separator()
                layout.label(text="Filename options")
                
                row = layout.row()
                row.prop(animAutoRender_props, 'frame_number_digits')
                row.prop(animAutoRender_props, 'file_name_separator')
                layout.prop(animAutoRender_props, 'use_anim_folder_name')
                layout.prop(animAutoRender_props, 'use_dir_folder_name')
                
                exampleName = (("anim" + animAutoRender_props.file_name_separator) if animAutoRender_props.use_anim_folder_name else "") + (("dir" + animAutoRender_props.file_name_separator) if animAutoRender_props.use_dir_folder_name else "") + ("%0" + str(animAutoRender_props.frame_number_digits) + "d") % 1
                
                layout.label(text="Example: " + exampleName + context.scene.render.file_extension)
            
            layout.prop(animAutoRender_props, 'specifyMainObject')
            if animAutoRender_props.specifyMainObject:
                row = layout.row(align=True)
                row.prop_search(animAutoRender_props, "mainObject", context.scene, "objects")
                row.operator("animautorender.use_current_object", icon="OBJECT_DATA", text="")
        else:
            row.prop(animAutoRender_props, "options_expand", icon="RIGHTARROW", text="", icon_only=True, emboss=False)
            row.label(text="Options")
        
        
        layout.separator()
        
        #
        #    Directions menu
        #
        row = layout.row()
        if animAutoRender_props.animation_collection_index < 0:
            row.label(text="Directions")
        else:
            row.label(text="Directions: " + "%d" % sum(1 for y in animAutoRender_props.animation_collection[animAutoRender_props.animation_collection_index].chosenDirection if y.directionEnable) + " / " + "%d" % len(animAutoRender_props.animation_collection[animAutoRender_props.animation_collection_index].chosenDirection))
        
        row = layout.row(align=True)
        row.menu("AnimAutoRender_MT_directions_presets", text=bpy.types.AnimAutoRender_MT_directions_presets.bl_label)
        row.operator("animautorender.directions_preset_add", text="", icon="ZOOMIN")
        row.operator("animautorender.directions_preset_add", text="", icon="ZOOMOUT").remove_active = True
        
        row = layout.row(align=True)
        row.template_list("AnimAutoRender_UL_direction", "", animAutoRender_props, "directionList", animAutoRender_props, "directionList_index", rows=3)
        col = row.column(align=True)
        
        col.operator("animautorender.add_direction", icon="ZOOMIN", text="")
        
        col.operator("animautorender.remove_direction", icon="ZOOMOUT", text="")
        
        col.operator("animautorender.clear_direction", icon="X", text="")
        
        col.operator("animautorender.invert_selection_direction", icon="FILE_REFRESH", text="")
        
        #
        #    Options to selected direction
        #
        if animAutoRender_props.directionList and animAutoRender_props.directionList_index >= 0:
            row = layout.row()
            if animAutoRender_props.directions_expand:
                row.prop(animAutoRender_props, "directions_expand", icon="DOWNARROW_HLT", text="", icon_only=True, emboss=False)
                row.label(text="Direction properties")
                direction = animAutoRender_props.directionList[animAutoRender_props.directionList_index]
                
                layout.prop(animAutoRender_props, "directions_same_name")
                
                if not animAutoRender_props.directions_same_name:
                    layout.prop(direction, "name")
                    
                layout.prop(direction, "folderName")
                layout.prop(direction, "direction")
            else:
                row.prop(animAutoRender_props, "directions_expand", icon="RIGHTARROW", text="", icon_only=True, emboss=False)
                row.label(text="Direction properties")
        
        layout.separator()
        
        
        #
        #    Animations menu
        #
        row = layout.row()
        row.label(text="Animations: " + "%d" % sum(1 for y in animAutoRender_props.animation_collection if y.active) + " / " + "%d" % len(animAutoRender_props.animation_collection))
        
        '''
        row = layout.row(align=True)
        row.menu("AnimAutoRender_MT_animations_presets", text=bpy.types.AnimAutoRender_MT_animations_presets.bl_label)
        row.operator("animautorender.animations_preset_add", text="", icon="ZOOMIN")
        row.operator("animautorender.animations_preset_add", text="", icon="ZOOMOUT").remove_active = True
        '''
        
        
        row = layout.row(align=True)
        row.template_list("AnimAutoRender_UL_animation", "", animAutoRender_props, "animation_collection", animAutoRender_props, "animation_collection_index", rows=3)
        col = row.column(align=True)
        
        col.operator("animautorender.add_animation", icon="ZOOMIN", text="")
        
        col.operator("animautorender.remove_animation", icon="ZOOMOUT", text="")
        
        col.operator("animautorender.clear_animation", icon="X", text="")
        
        col.operator("animautorender.invert_selection_animation", icon="FILE_REFRESH", text="")
        
        #
        #    Options to selected animation
        #
        if animAutoRender_props.animation_collection and animAutoRender_props.animation_collection_index >= 0:
            entry = animAutoRender_props.animation_collection[animAutoRender_props.animation_collection_index]
            
            row = layout.row()
            if animAutoRender_props.animations_expand:
                row.prop(animAutoRender_props, "animations_expand", icon="DOWNARROW_HLT", text="", icon_only=True, emboss=False)
                row.label(text="Animation properties")
                
                layout.prop(animAutoRender_props, "animations_same_name")
                
                if not animAutoRender_props.animations_same_name:
                    layout.prop(entry, "name")
                    
                layout.prop(entry, "folderName")
                
                layout.prop(entry, "go_through_cycle_count")
                
                layout.prop(entry, "repeat_first_frame")
                
                
                layout.prop(entry, "override_first_frame_index")
                if entry.override_first_frame_index:
                    layout.prop(entry, "first_frame_index")
                    layout.prop(entry, "use_index_of_first_frame")
                
                if animAutoRender_props.mainObject and len(bpy.data.actions) > 1:
                    layout.prop_search(entry, "actionProp", bpy.data, "actions")
                    
            else:
                row.prop(animAutoRender_props, "animations_expand", icon="RIGHTARROW", text="", icon_only=True, emboss=False)
                row.label(text="Animation properties")
                
            
            layout.separator()
            
            #
            #    Frames menu
            #
            row = layout.row()
            row.label(text="Frames: " + "%d" % sum(1 for y in entry.frames if y.render) + " / " + "%d" % len(entry.frames))
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