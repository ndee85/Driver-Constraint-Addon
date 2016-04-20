'''
Copyright (C) 2016 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
from math import radians,degrees
from mathutils import Vector,Quaternion,Euler

class CreateDriverConstraint(bpy.types.Operator):
    #"""This Operator creates a driver for a shape and connects it to a posebone transformation"""
    bl_idname = "object.create_driver_constraint"
    bl_label = "Create Driver Constraint"
    bl_description = "This Operator creates a driver for a shape and connects it to a posebone transformation"
    
    def get_shapes(self,context):
        shapes = []
        i=0
        
        if len(context.selected_objects) > 1:
            obj = context.selected_objects[1]
        else:
            obj = context.selected_objects[0]
        shape_keys = None
        if obj.type == "MESH" and obj.data.shape_keys != None:
            shape_keys = obj.data.shape_keys.key_blocks
              
        if shape_keys != None:
            for shape in shape_keys:
                if shape.relative_key != shape:
                    shapes.append((shape.name,shape.name,shape.name,'SHAPEKEY_DATA',i)) 
                    i+=1
        shapes.append(("CREATE_NEW_SHAPE","create new shape","create new shape",'NEW',i)) 
        
            
        return shapes
    
    
    def get_property_type_items(self,context):
        if len(context.selected_objects) > 1:
            obj = context.selected_objects[1]
        else:
            obj = context.selected_objects[0]
        
        object_data_icon = "MESH_DATA"
        if obj.type == "ARMATURE":
            object_data_icon = "ARMATURE_DATA"
        
        items = []
        items.append(("OBJECT_PROPERTY","Object Property","Object Property","OBJECT_DATAMODE",0))
        if obj.type == "MESH":
            items.append(("SHAPEKEY_PROPERTY","Shapekey Property","Shapekey Property","SHAPEKEY_DATA",1))
            items.append(("MODIFIER_PROPERTY","Modifier Property","Modifier Property","MODIFIER",5))            
        items.append(("OBECT_DATA_PROPERTY","Data Property","Data Property",object_data_icon,2))
        items.append(("MATERIAL_PROPERTY","Material Property","Material Property","MATERIAL",3))
        items.append(("TEXTURE_PROPERTY","Texture Property","Texture Property","TEXTURE",4))
#        items.append(("SCENE_PROPERTY","Scene Property","Scene Property","SCENE_DATA",5))
#        items.append(("RENDER_PROPERTY","Render Property","Render Property","SCENE",6))
        return items
    
    property_type = bpy.props.EnumProperty(name = "Mode",items=get_property_type_items, description="Set the space the bone is transformed in. Local Space recommended.")
    
    prop_data_path = bpy.props.StringProperty(name="Property Data Path", default="")
    
    shape_name = bpy.props.EnumProperty(items = get_shapes, name = "Shape", description="Select the shape you want to add a driver to.")
    get_limits_auto = bpy.props.BoolProperty(name = "Get Limits",default=True,description="This will set the limits based on the bone location/rotation/scale automatically.")
    
    type_values = []
    type_values.append(("LOC_X","X Location","X Location","None",0))
    type_values.append(("LOC_Y","Y Location","Y Location","None",1))
    type_values.append(("LOC_Z","Z Location","Z Location","None",2))
    type_values.append(("ROT_X","X Rotation","X Rotation","None",3))
    type_values.append(("ROT_Y","Y Rotation","Y Rotation","None",4))
    type_values.append(("ROT_Z","Z Rotation","Z Rotation","None",5))
    type_values.append(("SCALE_X","X Scale","X Scale","None",6))
    type_values.append(("SCALE_Y","Y Scale","Y Scale","None",7))
    type_values.append(("SCALE_Z","Z Scale","Z Scale","None",8))
    
    type = bpy.props.EnumProperty(name = "Type",items=type_values, description="Set the type you want to be used as input to drive the shapekey.")
    
    
    space_values = []
    space_values.append(("LOCAL_SPACE","Local Space","Local Space","None",0))
    space_values.append(("TRANSFORM_SPACE","Transform Space","Transform Space","None",1))
    space_values.append(("WORLD_SPACE","World Space","World Space","None",2))
    space = bpy.props.EnumProperty(name = "Space",items=space_values, description="Set the space the bone is transformed in. Local Space recommended.")
    
    min_value = bpy.props.FloatProperty(name = "Min Value",default=0.0, description="That value is used as 0.0 value for the shapekey.")
    max_value = bpy.props.FloatProperty(name = "Max Value",default=1.0, description="That value is used as 1.0 value for the shapekey.")
    
    prop_min_value = bpy.props.FloatProperty(name = "Min Value",default=0.0, description="That value is used as 0.0 value for the Property.")
    prop_max_value = bpy.props.FloatProperty(name = "Max Value",default=1.0, description="That value is used as 1.0 value for the Property.")
    
    def draw(self,context):
        layout = self.layout
        
        row = layout.row()
        row.label(text="Property Type")
        row.prop(self,"property_type",text="")
        
        row = layout.row()
        row.label(text="Get Limits")
        row.prop(self,"get_limits_auto",text="")
        
        if self.property_type == "SHAPEKEY_PROPERTY":
            row = layout.row()
            row.label(text="Shape")
            row.prop(self,"shape_name",text="")
        else:
            row = layout.row()
            row.label(text="Property Data Path")
            row.prop(self,"prop_data_path",text="")
        
        row = layout.row()
        row.label(text="Transform Type")
        row.prop(self,"type",text="")
        
        row = layout.row()
        row.label(text="Space")
        row.prop(self,"space",text="")
        
        row = layout.row()
        col = row.column()
        col.label(text="Bone Limits")
        col = row.column(align=True)
        col.prop(self,"min_value",text="Min Value")
        col.prop(self,"max_value",text="Max Value")
        
        if self.property_type != "SHAPEKEY_PROPERTY":
            row = layout.row()
            col = row.column()
            col.label(text="Property Limits")
            col = row.column(align=True)
            col.prop(self,"prop_min_value",text="Min Value")
            col.prop(self,"prop_max_value",text="Max Value")
            
    def check(self,context):
        return True
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def set_defaults(self,context):
        bone = context.active_pose_bone
        ### set location
        if bone.location != Vector((0,0,0)):
            l = [abs(bone.location.x),abs(bone.location.y),abs(bone.location.z)]
            m = max(l)
            type = ["LOC_X","LOC_Y","LOC_Z"]
            
            for i,value in enumerate(l):
                if l[i] == m:
                    self.min_value = 0.0
                    self.max_value = bone.location[i]
                    self.type = type[i]        
            return
        
        ### set rotation
        bone_rotation = Euler()
        if bone.rotation_mode == "QUATERNION":
            bone_rotation = bone.rotation_quaternion.to_euler("XYZ")
        else:
            bone_rotation = bone.rotation_euler
        
        if Vector((bone_rotation.x,bone_rotation.y,bone_rotation.z)) != Vector((0,0,0)):
            l = [abs(bone_rotation.x),abs(bone_rotation.y),abs(bone_rotation.z)]
            m = max(l)
            type = ["ROT_X","ROT_Y","ROT_Z"]
            
            for i,value in enumerate(l):
                if l[i] == m:
                    self.min_value = 0.0
                    self.max_value = degrees(bone_rotation[i])
                    self.type = type[i]
            return
        
        ### set scale
        if bone.scale != Vector((1,1,1)):
            l = [abs(bone.location.x),abs(bone.location.y),abs(bone.location.z)]
            m = max(l)
            type = ["SCALE_X","SCALE_Y","SCALE_Z"]
            
            for i,value in enumerate(l):
                if l[i] == m:
                    self.min_value = 1.0
                    self.max_value = bone.scale[i]
                    self.type = type[i]
            return
    
    def create_new_shape(self,context,object):
        new_shape = object.shape_key_add(name=context.active_pose_bone.name,from_mix=False)
        return new_shape.name
    
    def get_prop_object(self,context,prop_name):
        wm = context.window_manager
        
        if len(context.selected_objects) > 1:
            obj = context.selected_objects[1]
        else:
            obj = context.selected_objects[0]
        data = obj.data
        shape_keys = None
        mat = obj.active_material
        tex = None
        modifier = None
        scene = context.scene
        render = scene.render
        
        
        if obj.type == "MESH" and obj.data.shape_keys != None:
            shape_keys = obj.data.shape_keys
                        
        if mat != None:
            tex = mat.active_texture
            
        
        if len(obj.modifiers) > 0 and '"' in prop_name:
            modifier_name = prop_name.split('"')[1]
            if modifier_name in obj.modifiers:
                modifier = obj.modifiers[modifier_name]
                return modifier, "MODIFIER_PROPERTY"
            
        if shape_keys != None and '"' in prop_name:
            shape_name = prop_name.split('"')[1]
            if shape_name in shape_keys.key_blocks:
                return shape_keys, "SHAPEKEY_PROPERTY"
            
        if hasattr(obj,prop_name):
            return obj, "OBJECT_PROPERTY"
        if hasattr(data,prop_name):
            return data, "OBECT_DATA_PROPERTY"
#        if hasattr(scene,prop_name):
#            return scene, "SCENE_PROPERTY"
#        if "." in prop_name and hasattr(render,prop_name.split(".")[1]):
#            return render, "RENDER_PROPERTY"
        if mat != None and hasattr(mat,prop_name):
            return mat, "MATERIAL_PROPERTY"
        if tex != None and hasattr(tex,prop_name):
            return tex, "TEXTURE_PROPERTY"
            
    
    def execute(self, context):
        wm = context.window_manager
        context = bpy.context
        scene = context.scene
        if len(context.selected_objects) > 1:
            obj = context.selected_objects[1]
        else:
            obj = context.selected_objects[0]    
        
        if self.property_type == "SHAPEKEY_PROPERTY":
            shape = None
            if self.shape_name != "CREATE_NEW_SHAPE":
                shape = obj.data.shape_keys.key_blocks[self.shape_name]
            else:
                if obj.data.shape_keys == None:
                    obj.shape_key_add(name="Basis",from_mix=False)
                shape = obj.data.shape_keys.key_blocks[self.create_new_shape(context,obj)]
            
            curve = shape.driver_add("value")
        else:
            if self.get_prop_object(context,self.prop_data_path) != None:
                prop_type = self.get_prop_object(context,self.prop_data_path)[1]
                if prop_type in ["MODIFIER_PROPERTY","RENDER_PROPERTY"]:
                    data_path = self.prop_data_path.split(".")[1]
                    curve = self.get_prop_object(context,self.prop_data_path)[0].driver_add(data_path)    
                else:    
                    curve = self.get_prop_object(context,self.prop_data_path)[0].driver_add(self.prop_data_path)
            else:
                curve = None
        
        curves = [curve]
        if type(curve) == list:
            curves = curve
            
        for curve in curves:
            if curve != None:
                if len(curve.driver.variables) < 1:
                    curve_var = curve.driver.variables.new()
                else:
                    curve_var = curve.driver.variables[0]
                
                if len(curve.modifiers) > 0:
                    curve.modifiers.remove(curve.modifiers[0])
                curve.driver.type = "SUM"
                curve_var.type = "TRANSFORMS"
                curve_var.targets[0].id = bpy.context.active_object
                curve_var.targets[0].bone_target = bpy.context.active_pose_bone.name
                curve_var.targets[0].transform_space = self.space
                curve_var.targets[0].transform_type = self.type
                
                if self.type in ["ROT_X","ROT_Y","ROT_Z"]:
                    min_value = radians(self.min_value)
                    max_value = radians(self.max_value)
                else:
                    min_value = self.min_value
                    max_value = self.max_value
                
                delete_len = 0
                for point in curve.keyframe_points:
                    delete_len += 1
                for i in range(delete_len):    
                    curve.keyframe_points.remove(curve.keyframe_points[0])
                
                point_a = curve.keyframe_points.insert(min_value,self.prop_min_value)
                point_a.interpolation = "LINEAR"
                
                point_b = curve.keyframe_points.insert(max_value,self.prop_max_value)
                point_b.interpolation = "LINEAR"
            else:
                msg = "No Property found to add a Driver for, or Property is not supported."
                self.report({'INFO'},msg)
                return {'FINISHED'}
        
        msg = "Shape: "+ self.shape_name +" constraint to Bone: " + context.active_pose_bone.name
        self.report({'INFO'},msg)
        return {'FINISHED'}
    
    
        
    def invoke(self, context, event):
        wm = context.window_manager 
        
        if wm.clipboard != "":
            if self.get_prop_object(context,wm.clipboard) != None:
                self.prop_data_path = wm.clipboard
                self.property_type = self.get_prop_object(context,wm.clipboard)[1]

                if self.get_prop_object(context,wm.clipboard)[1] == "SHAPEKEY_PROPERTY":
                    shape_name = wm.clipboard.split('"')[1]
                    self.shape_name = shape_name
            else:
                self.prop_data_path = "OBJECT_PROPERTY"  
                    
                
        
#        if len(context.selected_objects) != 2:
#            self.report({'WARNING'},'Select a Mesh Object and then a Pose Bone')
#            return{'FINISHED'}
#        
#        if context.selected_objects[0].type != "ARMATURE":
#            self.report({'WARNING'},'Select a Mesh Object and then a Pose Bone')
#            return{'FINISHED'}
#        
#        if context.selected_objects[1].type != "MESH":
#            self.report({'WARNING'},'Select a Mesh Object and then a Pose Bone')
#            return{'FINISHED'}
        
        if context.active_pose_bone == None:
            self.report({'WARNING'},'Select a Mesh Object and then a Pose Bone')
            return{'FINISHED'}
        
        if self.get_limits_auto:
            self.set_defaults(context)
                
        return wm.invoke_props_dialog(self)

