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

bl_info = {
    "name": "Animation Automaton Renderer",
    "category": "Render",
    "description": "Addon for rendering sprite animation",
    "author": "Maciej Paluszek (My-Key)",
    "location": "Render",
    "version": (1, 2, 0)
}


if "bpy" in locals():
    import imp
    imp.reload(AAR_operators)
    imp.reload(AAR_properties)
    imp.reload(AAR_ui)
    imp.reload(AAR_render)
    imp.reload(AAR_preview)
    imp.reload(AAR_watchers)
else:
    import bpy
    from . import (AAR_operators,
                   AAR_properties,
                   AAR_ui,
                   AAR_render,
                   AAR_preview,
                   AAR_watchers)

import bpy.utils
import bpy.props
import math
from bpy.app.handlers import persistent

def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.Scene.AnimAutoRender_properties = bpy.props.PointerProperty(type = AAR_properties.AnimAutoRenderPropertyGroup)

    if AAR_watchers.InitWatchers not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(AAR_watchers.InitWatchers)
    
    bpy.app.handlers.scene_update_post.append(AAR_watchers.RegisterInitialisation)
    

def unregister():
    bpy.utils.unregister_module(__name__)
    
    if AAR_watchers.InitWatchers in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(AAR_watchers.InitWatchers)
        
    AAR_watchers.RemoveWatchers()
        
    del bpy.types.Scene.AnimAutoRender_properties

if __name__ == "__main__" :
    register()