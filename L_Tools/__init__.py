import bpy
from bpy.types import Operator, Panel
import os

bl_info = {
    "name": "批量材质",
    "category": "3D View",
    "author": "Light",
    "blender": (2, 81, 0),
    "location": "UI",
    "description": "批量上材质",
    "version": (1, 0)
}

desktop_path = os.path.expanduser("~/Desktop")
target_dir = os.path.join(desktop_path, "tex")

# 获取文件名和扩展名
texture_files = [(os.path.splitext(files)[0], os.path.splitext(files)[1])
                 for files in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, files))]


class MaterialManager:
    def __init__(self, target_dir, texture_files):
        self.target_dir = target_dir
        self.texture_files = texture_files

    def create_materials(self):

        for file_name, file_extension in texture_files:
            mat = bpy.data.materials.new(name=file_name)
            mat.use_nodes = True

            if file_extension == ".png":
                # 处理 PNG 文件
                self.setup_material_for_image(mat, file_name, file_extension)

            elif file_extension == ".jpg":
                # 处理 JPG 文件
                self.setup_material_for_image(mat, file_name, file_extension)

    def setup_material_for_image(self, mat, file_name, file_extension):
        for node in mat.node_tree.nodes:
            mat.node_tree.nodes.remove(node)

        texImage = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        texImage.image = bpy.data.images.load(
            os.path.join(self.target_dir, file_name + file_extension))
        PBSDF_node = mat.node_tree.nodes.new(
            type='ShaderNodeBsdfPrincipled')
        material_output = mat.node_tree.nodes.new(
            type='ShaderNodeOutputMaterial')
        mat.node_tree.links.new(
            texImage.outputs[0], PBSDF_node.inputs['Base Color'])
        if file_extension == ".png":
            mat.node_tree.links.new(
                texImage.outputs['Alpha'], PBSDF_node.inputs['Alpha'])
        mat.node_tree.links.new(
            PBSDF_node.outputs['BSDF'], material_output.inputs['Surface'])

        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.name == file_name:
                # 清空材质槽
                obj.data.materials.clear()

                # 添加新材质
                obj.data.materials.append(mat)

                if not obj.material_slots:
                    # 如果材质槽不存在，添加一个新的材质槽
                    material_slot = obj.material_slots.add()
                    material_slot.material = mat
                if file_extension == ".png":
                    materialAlphaMix = obj.material_slots[0].material
                    materialAlphaMix.blend_method = 'HASHED'
                    materialAlphaMix.use_backface_culling = True

    def clear_all_materials(self):
        # 获取当前场景中的所有物体
        objects = bpy.context.scene.objects

        # 遍历每个物体
        for obj in objects:
            # 检查对象类型是否为网格（MESH）并且是否具有材质
            if obj.type == 'MESH' and obj.data.materials:
                obj.data.materials.clear()

        # 获取当前场景中的所有材质
        materials = bpy.data.materials

        # 删除所有材质
        for material in materials:
            bpy.data.materials.remove(material)


class My_Panel(Panel):
    bl_label = '操作'
    bl_idname = 'batchmat'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "批量材质"

    def draw(self, context):
        layout = self.layout
        layout.operator(My_Operator_1.bl_idname)
        layout.operator(My_Operator_2.bl_idname)


class My_Operator_1(Operator):
    bl_idname = "material_cr.operator"
    bl_label = "赋予材质"
    bl_description = "批量上材质"

    def execute(self, context):
        material_manager = MaterialManager(target_dir, texture_files)
        material_manager.create_materials()
        return {"FINISHED"}


class My_Operator_2(Operator):
    bl_idname = "material_cl.operator"
    bl_label = "清空材质"
    bl_description = "清空所有材质"

    def execute(self, context):
        material_manager = MaterialManager(target_dir, texture_files)
        material_manager.clear_all_materials()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(My_Panel)
    bpy.utils.register_class(My_Operator_1)
    bpy.utils.register_class(My_Operator_2)
    bpy.utils.register_class(MaterialManager)


def unregister():
    bpy.utils.unregister_class(My_Panel)
    bpy.utils.unregister_class(My_Operator_1)
    bpy.utils.unregister_class(My_Operator_2)
    bpy.utils.unregister_class(MaterialManager)


if __name__ == "__main__":
    register()
