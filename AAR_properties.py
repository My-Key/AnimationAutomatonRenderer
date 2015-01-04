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

import bpy.props
import math

def ANIMAUTORENDER_rename_direction(self, context):
    AAR_props = context.scene.AnimAutoRender_properties
    if AAR_props.directions_same_name:
        direction = AAR_props.directionList[AAR_props.directionList_index]
        direction.name = direction.folderName

def ANIMAUTORENDER_rename_animation(self, context):
    AAR_props = context.scene.AnimAutoRender_properties
    if AAR_props.animations_same_name:
        animation = AAR_props.animation_collection[AAR_props.animation_collection_index]
        animation.name = animation.folderName


class FrameListPropertyGroup(bpy.types.PropertyGroup):
    frame = bpy.props.IntProperty(name="Frame", default=0, min=0, options={'SKIP_SAVE'})
    enabled = bpy.props.BoolProperty(name="", description="Check if you want to render this frame", default = True, options={'SKIP_SAVE'})


class DirectionEnableListPropertyGroup(bpy.types.PropertyGroup):
    enabled = bpy.props.BoolProperty(name="", description="Check if you want to render this direction for active animation", default=True, options={'SKIP_SAVE'})


class DirectionListPropertyGroup(bpy.types.PropertyGroup):
    folderName = bpy.props.StringProperty(name="Folder name", subtype="FILE_NAME", update=ANIMAUTORENDER_rename_direction)
    direction = bpy.props.FloatProperty(name="Direction", description="Direction in degrees", subtype = 'ANGLE',
                                        default = 0.0, min=-2*math.pi, max=2*math.pi)
    

class AnimationListPropertyGroup(bpy.types.PropertyGroup):
    folderName = bpy.props.StringProperty(name="Folder name", subtype="FILE_NAME", update=ANIMAUTORENDER_rename_animation,
                                          options={'SKIP_SAVE'})
    enabled = bpy.props.BoolProperty(name="", description="Check if you want to render this animation.", default = True,
                                    options={'SKIP_SAVE'})
    chosenDirection = bpy.props.CollectionProperty(type = DirectionEnableListPropertyGroup, options={'HIDDEN','SKIP_SAVE'})
    frames = bpy.props.CollectionProperty(type = FrameListPropertyGroup, options={'HIDDEN','SKIP_SAVE'})
    frames_index = bpy.props.IntProperty(min = -1, default = -1)
    
    override_first_frame_index = bpy.props.BoolProperty(name="Override global first frame number",
                                                        description="Override global first frame number", default = False,
                                                        options={'SKIP_SAVE'})
    first_frame_index = bpy.props.IntProperty(name="First frame number", description="Set first frame number for this animation", min = 0, default = 0, options={'SKIP_SAVE'})
    use_index_of_first_frame = bpy.props.BoolProperty(name="Frame number from first active frame",
                                                      description="Get first frame number from first active frame", default = False,
                                                      options={'SKIP_SAVE'})
    go_through_cycle_count = bpy.props.IntProperty(name="Go through animation cycle X times", min = 0, default = 0,
                                                   description="Go through animation cycle X times (useful for slow parent)", options={'SKIP_SAVE'})
    repeat_first_frame = bpy.props.IntProperty(name="Repeat first frame X times", description="Repeat first frame X times (useful for slow parent)",
                                               min = 0, default = 0, options={'SKIP_SAVE'})
    actionProp = bpy.props.StringProperty(name="Action", description="Specify action where animation is stored (it only stores name of action, it won't update when name of that action changes)", options={'SKIP_SAVE'})


class AnimAutoRenderPropertyGroup(bpy.types.PropertyGroup):
    animation_collection = bpy.props.CollectionProperty(type = AnimationListPropertyGroup)
    animation_collection_index = bpy.props.IntProperty(min = -1, default = -1)
    
    directionList = bpy.props.CollectionProperty(type = DirectionListPropertyGroup)
    directionList_index = bpy.props.IntProperty(min = -1, default = -1)
    first_frame_index = bpy.props.IntProperty(name="Global first frame number", description="Global first frame number", min = 0, default = 0)
    
    repeat_go_to_frame = bpy.props.BoolProperty(name="Go to frame twice",
                                                description="Go to frame twice to avoid driver or constraints delay bugs.",
                                                default = False)
    
    options_expand = bpy.props.BoolProperty(name="Options", description="Expand/hide options", default = True)
    
    directions_expand = bpy.props.BoolProperty(name="Direction properties", description="Expand/hide direction properties", default = True)
    directions_same_name = bpy.props.BoolProperty(name="Same name and folder name", description="", default = False,
                                                  update=ANIMAUTORENDER_rename_direction)
    
    animations_expand = bpy.props.BoolProperty(name="Animation properties", description="Expand/hide animation properties", default = True)
    animations_same_name = bpy.props.BoolProperty(name="Same name and folder name", description="", default = False,
                                                  update=ANIMAUTORENDER_rename_animation)
    
    simple_frame_name = bpy.props.BoolProperty(name="Simple frame file name (4 digits)",
                                               description="Simple frame name (4 digits)", default = True)
    
    frame_number_digits = bpy.props.IntProperty(name="Frame number max digits", description="Frame number max digits", min = 2, default = 4)
    use_anim_folder_name = bpy.props.BoolProperty(name="Use animation name in frame file name",
                                                  description="Use animation name in frame file name", default = False)
    use_dir_folder_name = bpy.props.BoolProperty(name="Use direction name in frame file name",
                                                 description="Use direction name in frame file name", default = False)
    file_name_separator = bpy.props.StringProperty(name="Separator", description="Separates animation, direction and frame number in frame filename", default = "_")
    
    rendering = bpy.props.BoolProperty(description="", default = False)
    total_frames = bpy.props.IntProperty(min = 0, default = 0)
    frames_done = bpy.props.IntProperty(min = 0, default = 0)
    percentage = bpy.props.IntProperty(name="", subtype = 'PERCENTAGE', default = 0, min=0, max=100)
    totalTime = bpy.props.FloatProperty(name="", default = 0.0)
    
    previewFPS = bpy.props.IntProperty(name="FPS", description="FPS preview will be displayed", min = 1, default = 24, max = 60)
    previewIsOn = bpy.props.BoolProperty(description="", default = False)
    loopType = bpy.props.IntProperty(name="Loop", description="Type of preview loop", min = 0, default = 0, max = 1)
    preview_skip_disabled_frames = bpy.props.BoolProperty(name="Skip disabled frames",description="Check to skip disabled frames in preview", default = True)
    
    specifyMainObject = bpy.props.BoolProperty(name="Specify main object", default = False,
                                               description="Specify main object which will be selected and rotated by Z axis by angles from direction list, else current object will be rotated")
    mainObject = bpy.props.StringProperty(name="Main object",
                                          description="Main object will be selected and rotated by Z axis by angles from direction list (it only stores name of object, it won't update when name of that object changes)")
    
    save_path = bpy.props.StringProperty(name = "Save path", default = "//", description = "Define the path where animation will be saved", subtype = 'DIR_PATH')  
    
    def propsToExport(self):
        out = []
        out.append("save_path")
        out.append("repeat_go_to_frame")
        out.append("directions_same_name")
        out.append("animations_same_name")
        out.append("simple_frame_name")
        out.append("frame_number_digits")
        out.append("use_anim_folder_name")
        out.append("use_dir_folder_name")
        out.append("file_name_separator")
        
        return out
