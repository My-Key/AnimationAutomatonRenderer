bl_info = {
    "name": "Animation Automaton Renderer",
    "category": "Render",
    "description": "Addon for rendering sprite animation",
    "author": "My-Key, EVERYDAYiPLAY",
    "location": "Render"
}

import bpy, bl_operators
import bpy.utils
import bpy.props
import math


def ANIMAUTORENDER_rename_direction(self, context):
    obj = context.scene.AnimAutoRender_properties
    if obj.directions_same_name:
        direction = obj.directionList[obj.directionList_index]
        direction.name = direction.folderName

def ANIMAUTORENDER_rename_animation(self, context):
    obj = context.scene.AnimAutoRender_properties
    if obj.animations_same_name:
        animation = obj.animation_collection[obj.animation_collection_index]
        animation.name = animation.folderName


class FrameListPropertyGroup(bpy.types.PropertyGroup):
    frame = bpy.props.IntProperty(name="Frame", default=0, min=0, options={'SKIP_SAVE'})
    render = bpy.props.BoolProperty(name="", description="Render this frame", default = True, options={'SKIP_SAVE'})


class DirectionEnableListPropertyGroup(bpy.types.PropertyGroup):
    directionEnable = bpy.props.BoolProperty(name="", description="Render this direction", default = True, options={'SKIP_SAVE'})


class DirectionListPropertyGroup(bpy.types.PropertyGroup):
    folderName = bpy.props.StringProperty(name="Folder name", subtype="FILE_NAME", update=ANIMAUTORENDER_rename_direction)
    direction = bpy.props.FloatProperty(name="Direction", description="Direction in degrees", subtype = 'ANGLE', default = 0.0, min=-2*math.pi, max=2*math.pi)
    

class AnimationListPropertyGroup(bpy.types.PropertyGroup):
    folderName = bpy.props.StringProperty(name="Folder name", subtype="FILE_NAME", update=ANIMAUTORENDER_rename_animation, options={'SKIP_SAVE'})
    active = bpy.props.BoolProperty(name="", description="Check if you want to export the action set.", default = True, options={'SKIP_SAVE'})
    chosenDirection = bpy.props.CollectionProperty(type = DirectionEnableListPropertyGroup, options={'HIDDEN','SKIP_SAVE'})
    frames = bpy.props.CollectionProperty(type = FrameListPropertyGroup, options={'HIDDEN','SKIP_SAVE'})
    frames_index = bpy.props.IntProperty(min = -1, default = -1)
    
    override_first_frame_index = bpy.props.BoolProperty(name="Override global first frame number", description="Override global first frame number", default = False, options={'SKIP_SAVE'})
    first_frame_index = bpy.props.IntProperty(name="First frame number", min = 0, default = 0, options={'SKIP_SAVE'})
    use_index_of_first_frame = bpy.props.BoolProperty(name="Frame number from first active frame", description="Get first frame number from first active frame", default = False, options={'SKIP_SAVE'})
    go_through_cycle_count = bpy.props.IntProperty(name="Go through animation cycle X times", min = 0, default = 0, options={'SKIP_SAVE'})
    repeat_first_frame = bpy.props.IntProperty(name="Repeat first frame X times", min = 0, default = 0, options={'SKIP_SAVE'})
    actionProp = bpy.props.StringProperty(name="Action", options={'SKIP_SAVE'})


class AnimAutoRenderPropertyGroup(bpy.types.PropertyGroup):
    animation_collection = bpy.props.CollectionProperty(type = AnimationListPropertyGroup)
    animation_collection_index = bpy.props.IntProperty(min = -1, default = -1)
    
    directionList = bpy.props.CollectionProperty(type = DirectionListPropertyGroup)
    directionList_index = bpy.props.IntProperty(min = -1, default = -1)
    first_frame_index = bpy.props.IntProperty(name="Global first frame number", min = 0, default = 0)
    
    repeat_go_to_frame = bpy.props.BoolProperty(name="Go to frame twice", description="Go to frame twice to avoid driver or constraints delay bugs.", default = False)
    
    options_expand = bpy.props.BoolProperty(name="Options", description="", default = True)
    
    directions_expand = bpy.props.BoolProperty(name="Direction properties", description="", default = True)
    directions_same_name = bpy.props.BoolProperty(name="Same name and folder name", description="", default = False, update=ANIMAUTORENDER_rename_direction)
    
    animations_expand = bpy.props.BoolProperty(name="Animation properties", description="", default = True)
    animations_same_name = bpy.props.BoolProperty(name="Same name and folder name", description="", default = False, update=ANIMAUTORENDER_rename_animation)
    
    simple_frame_name = bpy.props.BoolProperty(name="Simple frame file name (4 digits)", description="Simple frame name (4 digits)", default = True)
    
    frame_number_digits = bpy.props.IntProperty(name="Frame number max digits", min = 2, default = 4)
    use_anim_folder_name = bpy.props.BoolProperty(name="Use animation name in frame file name", description="Use animation name in frame file name", default = False)
    use_dir_folder_name = bpy.props.BoolProperty(name="Use direction name in frame file name", description="Use direction name in frame file name", default = False)
    file_name_separator = bpy.props.StringProperty(name="Separator", default = "_")
    
    rendering = bpy.props.BoolProperty(description="", default = False)
    total_frames = bpy.props.IntProperty(min = 0, default = 0)
    frames_done = bpy.props.IntProperty(min = 0, default = 0)
    percentage = bpy.props.IntProperty(name="", subtype = 'PERCENTAGE', default = 0, min=0, max=100)
    
    specifyMainObject = bpy.props.BoolProperty(name="Specify main object", description="Specify main object", default = False)
    mainObject = bpy.props.StringProperty(name="Main object")
    
    save_path = bpy.props.StringProperty \
      (
      name = "Save path",
      default = "//",
      description = "Define the path where animation will be saved",
      subtype = 'DIR_PATH'
      )  
    
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




class ANIMAUTORENDER_OT_add_direction(bpy.types.Operator):
    bl_label = "Add direction"
    bl_idname = "animautorender.add_direction"  
    bl_description = "Add direction"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        
        collection = AnimAutoRender_props.directionList
        added = collection.add()        # This add at the end of the collection list
        added.name = "Dir"+ str(len(collection))
        added.folderName = "Dir"+ str(len(collection))
        
        for item in AnimAutoRender_props.animation_collection:
            item.chosenDirection.add()
        
        AnimAutoRender_props.directionList_index = len(collection) - 1
       
        return {'FINISHED'}
    
class ANIMAUTORENDER_OT_clear_direction(bpy.types.Operator):
    bl_label = "Clear direction list"
    bl_idname = "animautorender.clear_direction"  
    bl_description = "Clear direction list"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        
        collection = AnimAutoRender_props.directionList
        collection.clear()
        AnimAutoRender_props.directionList_index = -1
        
        for item in AnimAutoRender_props.animation_collection:
            item.chosenDirection.clear()
       
        return {'FINISHED'}


class ANIMAUTORENDER_OT_remove_direction(bpy.types.Operator):
    bl_label = "Remove direction"
    bl_idname = "animautorender.remove_direction"  
    bl_description = "Remove direction"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        collection = AnimAutoRender_props.directionList
        index = AnimAutoRender_props.directionList_index
        if index >= 0:
            for item in AnimAutoRender_props.animation_collection:
                item.chosenDirection.remove(index)
                
            collection.remove(index)
            AnimAutoRender_props.directionList_index -= 1
            
            if AnimAutoRender_props.directionList_index < 0 and len(collection) > 0:
                AnimAutoRender_props.directionList_index = 0
       
        return {'FINISHED'}
    
class ANIMAUTORENDER_OT_invert_selection_direction(bpy.types.Operator):
    bl_label = "Invert selection"
    bl_idname = "animautorender.invert_selection_direction"  
    bl_description = "Invert selection"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        index = AnimAutoRender_props.animation_collection_index
        if index >= 0:
            collection = AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].chosenDirection
            for item in collection:
                item.directionEnable = not item.directionEnable
       
        return {'FINISHED'}
    
    
class ANIMAUTORENDER_OT_add_animation(bpy.types.Operator):
    bl_label = "Add animation"
    bl_idname = "animautorender.add_animation"  
    bl_description = "Add animation"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        collection = AnimAutoRender_props.animation_collection
        
        added = collection.add()
        added.name = "Anim"+ str(len(collection))
        added.folderName = "Anim"+ str(len(collection))
        
        for _ in range(0, len(AnimAutoRender_props.directionList)):
            added.chosenDirection.add()
            
        AnimAutoRender_props.animation_collection_index = len(collection) - 1
       
        return {'FINISHED'}
    
class ANIMAUTORENDER_OT_clear_animation(bpy.types.Operator):
    bl_label = "Clear animation list"
    bl_idname = "animautorender.clear_animation"  
    bl_description = "Clear animation list"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        
        collection = AnimAutoRender_props.animation_collection
        collection.clear()

        AnimAutoRender_props.animation_collection_index = -1
       
        return {'FINISHED'}


class ANIMAUTORENDER_OT_remove_animation(bpy.types.Operator):
    bl_label = "Remove animation"
    bl_idname = "animautorender.remove_animation"  
    bl_description = "Remove animation"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        collection = AnimAutoRender_props.animation_collection
        index = AnimAutoRender_props.animation_collection_index
        
        if index >= 0:
            collection.remove(index)
            AnimAutoRender_props.animation_collection_index -= 1
            
            if AnimAutoRender_props.animation_collection_index < 0 and len(collection) > 0:
                AnimAutoRender_props.animation_collection_index = 0
       
        return {'FINISHED'}

class ANIMAUTORENDER_OT_invert_selection_animation(bpy.types.Operator):
    bl_label = "Invert selection"
    bl_idname = "animautorender.invert_selection_animation"  
    bl_description = "Invert selection"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        
        collection = AnimAutoRender_props.animation_collection
        for item in collection:
            item.active = not item.active
       
        return {'FINISHED'}
    

class ANIMAUTORENDER_OT_add_frame(bpy.types.Operator):
    bl_label = "Add frame"
    bl_idname = "animautorender.add_frame"  
    bl_description = "Add frame"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        collection = AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].frames
        added = collection.add()
        added.frame = context.scene.frame_current
       
        return {'FINISHED'}
    
class ANIMAUTORENDER_OT_clear_frame(bpy.types.Operator):
    bl_label = "Clear frame list"
    bl_idname = "animautorender.clear_frame"  
    bl_description = "Clear frame list"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        collection = AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].frames
        
        collection.clear()
        AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].frames_index = -1
       
        return {'FINISHED'}


class ANIMAUTORENDER_OT_remove_frame(bpy.types.Operator):
    bl_label = "Remove frame"
    bl_idname = "animautorender.remove_frame"  
    bl_description = "Remove frame"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        collection = AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].frames
        index = AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].frames_index
        
        if index >= 0:                        
            collection.remove(index)
            AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].frames_index -= 1
            
            if AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].frames_index < 0 and len(collection) > 0:
                AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].frames_index = 0
       
        return {'FINISHED'}
    
class ANIMAUTORENDER_OT_current_frame(bpy.types.Operator):
    bl_label = "Set to current frame"
    bl_idname = "animautorender.current_frame"  
    bl_description = "Set to current frame"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        collection = AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].frames
        collection[AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].frames_index].frame = context.scene.frame_current
       
        return {'FINISHED'}
    
        
class ANIMAUTORENDER_OT_add_next_frame(bpy.types.Operator):
    bl_label = "Add next frame"
    bl_idname = "animautorender.add_next_frame"  
    bl_description = "Add next frame"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        collection = AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].frames
        context.scene.frame_current += 1
        added = collection.add()
        added.frame = context.scene.frame_current
       
        return {'FINISHED'}
  
    
class ANIMAUTORENDER_OT_add_range_frame(bpy.types.Operator):
    bl_label = "Add frames from start to end"
    bl_idname = "animautorender.add_range_frame"  
    bl_description = "Add frame from start to end"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        collection = AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].frames
        for i in range(context.scene.frame_start, context.scene.frame_end + 1):
            added = collection.add()
            added.frame = i
       
        return {'FINISHED'}

class ANIMAUTORENDER_OT_invert_selection_frame(bpy.types.Operator):
    bl_label = "Invert selection"
    bl_idname = "animautorender.invert_selection_frame"  
    bl_description = "Invert selection"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        index = AnimAutoRender_props.animation_collection_index
        if index >= 0:
            collection = AnimAutoRender_props.animation_collection[AnimAutoRender_props.animation_collection_index].frames
            for item in collection:
                item.render = not item.render
       
        return {'FINISHED'}
    
class ANIMAUTORENDER_OT_use_current_object(bpy.types.Operator):
    bl_label = "Use current active object"
    bl_idname = "animautorender.use_current_object"  
    bl_description = "Use current active object"
     
    def invoke(self, context, event):
        AnimAutoRender_props = context.scene.AnimAutoRender_properties
        AnimAutoRender_props.mainObject = context.active_object.name
       
        return {'FINISHED'}
    

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


class RENDER_PT_Animation_Automaton_Renderer(bpy.types.Panel):
    bl_label = 'Animation Automaton Renderer'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    
    def draw(self, context):
        layout = self.layout
        
        animAutoRender_props = context.scene.AnimAutoRender_properties
        
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
        
        # Directions menu
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
        
        
        # Animations menu
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
            
            
            # Frames menu
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
            
            if entry.frames and entry.frames_index >= 0:
                frame = entry.frames[entry.frames_index]
                row = layout.row(align=True)
                row.prop(frame, "frame")
                row.operator("animautorender.current_frame", icon="TIME", text="Set current frame")
                
        


def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.Scene.AnimAutoRender_properties = bpy.props.PointerProperty(type = AnimAutoRenderPropertyGroup)


def unregister():
    bpy.utils.unregister_module(__name__)
    
    del bpy.types.Scene.AnimAutoRender_properties


if __name__ == "__main__" :
    register()