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
from bpy.app.handlers import persistent


# Thanks for Jerryno from:
# http://blender.stackexchange.com/questions/19668/execute-a-python-function-whenever-the-user-interacts-with-the-program       
class WatcherObject:
    def __init__(self, object, property, function, scene):
        #if the property object needs deep copy
        try :
            self.oldValue = getattr(object, property).copy()
            self.newValue = getattr(object, property).copy()
        #if the property object doesn't need it (and don't have a copy method)
        except AttributeError:
            self.oldValue = getattr(object, property)
            self.newValue = getattr(object, property)

        self.scene = scene
        self.object = object
        self.property = property
        self.function = function

    #Call the function if the object property changed
    def update(self):
        try :
            self.oldValue = self.newValue.copy()
            self.newValue = getattr(self.object, self.property).copy()
        except AttributeError:
            self.oldValue = self.newValue
            self.newValue = getattr(self.object, self.property)

        if self.oldValue != self.newValue:
            self.function(object=self.object, new=self.newValue, old=self.oldValue, scene=self.scene)


def add_watcher_object(name, property, function, scene):
    if (name != None or str(name) != '' or str(name) != "") and str(name) in bpy.data.objects:
        watchersObjects[str(name)] = WatcherObject(bpy.data.objects[str(name)], property, function, scene)


def remove_watcher_object(name):    
    if name in watchersObjects:
        del watchersObjects[name]
        
        
def name_change(object, new, old, scene):
    remove_watcher_object(str(old))
    
    if str(new) in watchersObjects:
        watchersObjects[str(new)].update()
    
    add_watcher_object(str(new), 'name', name_change, scene)
    AAR_props = scene.AnimAutoRender_properties
    AAR_props.mainObject = str(new)
    return



class WatcherActions:
    def __init__(self, object, property, function, scene, animationId):
        #if the property object needs deep copy
        try :
            self.oldValue = getattr(object, property).copy()
            self.newValue = getattr(object, property).copy()
        #if the property object doesn't need it (and don't have a copy method)
        except AttributeError:
            self.oldValue = getattr(object, property)
            self.newValue = getattr(object, property)

        self.scene = scene
        self.animationId = animationId
        self.object = object
        self.property = property
        self.function = function

    #Call the function if the object property changed
    def update(self):
        try :
            self.oldValue = self.newValue.copy()
            self.newValue = getattr(self.object, self.property).copy()
        except AttributeError:
            self.oldValue = self.newValue
            self.newValue = getattr(self.object, self.property)

        if self.oldValue != self.newValue:
            self.function(object=self.object, new=self.newValue, old=self.oldValue, scene=self.scene, animationId=self.animationId)



def add_watcher_action(name, property, function, scene, animationId):
    if (name != None or str(name) != '' or str(name) != "") and str(name) in bpy.data.actions:
        watchersActions[str(name)] = WatcherActions(bpy.data.actions[str(name)], property, function, scene, animationId)


def remove_watcher_action(name):    
    if name in watchersActions:
        del watchersActions[name]
   
def name_change_action(object, new, old, scene, animationId):
    remove_watcher_action(str(old))
    
    if str(new) in watchersActions:
        watchersActions[str(new)].update()
    
    add_watcher_action(str(new), 'name', name_change_action, scene, animationId)
    AAR_props = scene.AnimAutoRender_properties
    AAR_props.animation_collection[animationId].actionProp = str(new)
    return


def watcher(scene):
    for watcher in list(watchersObjects.values()):
        watcher.update()
    
    for watcher in list(watchersActions.values()):
        watcher.update()
    
    return

@persistent
def InitWatchers(scene):    
    if watcher not in bpy.app.handlers.scene_update_post:
        bpy.app.handlers.scene_update_post.append(watcher)
    
    # Add watchers for existing mainObject fields
    for scene in bpy.data.scenes:
        if scene.AnimAutoRender_properties.mainObject != "":
            add_watcher_object(str(scene.AnimAutoRender_properties.mainObject), 'name', name_change, scene)
        
        for i in range(len(scene.AnimAutoRender_properties.animation_collection)):
            animation = scene.AnimAutoRender_properties.animation_collection[i]
            if animation.actionProp != "":
                add_watcher_action(str(animation.actionProp), 'name', name_change_action, scene, i)
                
def RegisterInitialisation(scene):
    InitWatchers(None)
    
    bpy.app.handlers.scene_update_post.remove(RegisterInitialisation)
            
def RemoveWatchers():
    if watcher in bpy.app.handlers.scene_update_post:
        bpy.app.handlers.scene_update_post.remove(watcher) 

watchersObjects = {}
watchersActions = {}
