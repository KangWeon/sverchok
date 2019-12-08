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

import numpy as np

import bpy
from bpy.props import StringProperty, IntProperty, CollectionProperty, PointerProperty

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, match_long_repeat, fullList

class SvMaterialIndexNode(bpy.types.Node, SverchCustomTreeNode):
    '''
    Triggers: material index
    Tooltip: Set material index per object face
    '''

    bl_idname = 'SvMaterialIndexNode'
    bl_label = "Set Material Index"
    bl_icon = 'MATERIAL'

    material_index : IntProperty(name = "Material Index", default = 0,
            description = "Material index to set (starting from 0)",
            min = 0,
            update = updateNode)

    def sv_init(self, context):
        self.inputs.new('SvObjectSocket', 'Object')
        self.inputs.new('SvStringsSocket', 'FaceIndex')
        self.inputs.new('SvStringsSocket', 'MaterialIndex').prop_name = 'material_index'
        self.outputs.new('SvObjectSocket', 'Object')

    def set_material_indices(self, obj, faces, materials):
        prev_material_index_layer = obj.data.polygon_layers_int.get("prev_material_index")
        if prev_material_index_layer is None:
            self.info("Creating a layer")
            prev_material_index_layer = obj.data.polygon_layers_int.new(name="prev_material_index")
            prev_material_indices = np.full(len(obj.data.polygons), 0, dtype=int)
            obj.data.polygons.foreach_get("material_index", prev_material_indices)
            for face_index in range(len(obj.data.polygons)):
                prev_material_index_layer.data[obj.data.polygons[face_index]].value = prev_material_indices[face_index]

        material_indices = np.full(len(obj.data.polygons), 0, dtype=int)
        material_by_face = dict(zip(faces, materials))
        for face_index in range(len(obj.data.polygons)):
            material_index = material_by_face.get(face_index, None)
            if material_index is None:
                material_index = prev_material_index_layer.data[face_index].value
            #self.info("[%s] = %s", face_index, material_index)
            material_indices[face_index] = material_index
        #self.info("Materials: %s", material_indices)
        obj.data.polygons.foreach_set("material_index", material_indices)

    def process(self):
        objects = self.inputs['Object'].sv_get()
        faces_s = self.inputs['FaceIndex'].sv_get(default = [[]])
        materials_s = self.inputs['MaterialIndex'].sv_get(default = [[]])

        inputs = match_long_repeat([objects, faces_s, materials_s])
        for obj, faces, materials in zip(*inputs):
            fullList(materials, len(faces))
            self.set_material_indices(obj, faces, materials)
            obj.data.update()

        self.outputs['Object'].sv_set(objects)

classes = [SvMaterialIndexNode]

def register():
    for name in classes:
        bpy.utils.register_class(name)


def unregister():
    for name in reversed(classes):
        bpy.utils.unregister_class(name)

