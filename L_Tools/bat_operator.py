import bpy
from bpy.types import Operator
import os


class prop_mat(bpy.types.PropertyGroup):
    texture_path: bpy.props.StringProperty(default="C:\\", subtype="DIR_PATH") # type: ignore


class MaterialManager():

    def __init__(self, target_dir):
        self.target_dir = bpy.context.scene.matprop.texture_path

    def create_materials(self):
        texture_files = [(os.path.splitext(files)[0], os.path.splitext(files)[1])
                         for files in os.listdir(self.target_dir) if os.path.isfile(os.path.join(self.target_dir, files))]
        for file_name, file_extension in texture_files:
            print("图像：{} 已创建材质".format(file_name))
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
        # 连接节点
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
                # 清空材质
                obj.data.materials.clear()
                # 添加新材质
                obj.data.materials.append(mat)

                if file_extension == ".png":
                    materialAlphaMix = obj.material_slots[0].material
                    materialAlphaMix.blend_method = 'BLEND'
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


class MyOperatorCr(Operator):
    bl_idname = "material_cr.operator"
    bl_label = "赋予材质"
    bl_description = "批量上材质,未正常执行时尝试清空材质"

    def execute(self, context):
        material_manager = MaterialManager(
            bpy.context.scene.matprop.texture_path)
        material_manager.create_materials()
        return {"FINISHED"}


class MyOperatorCl(Operator):
    bl_idname = "material_cl.operator"
    bl_label = "清空材质"
    bl_description = "清空所有材质"

    def execute(self, context):
        material_manager = MaterialManager(
            bpy.context.scene.matprop.texture_path)
        material_manager.clear_all_materials()
        return {'FINISHED'}


class MaterialInstanceSeparator(bpy.types.Operator):
    bl_idname = "object.material_instance_separator"
    bl_label = "快速切图"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 获取当前选择的物体
        # selected_objects = bpy.context.selected_objects
        i = 0
        # 存储当前选中的对象
        previously_selected_objects = [
            obj for obj in bpy.context.selected_objects]
        bpy.ops.object.select_all(action='DESELECT')

        for obj in previously_selected_objects:
            obj.select_set(True)
            # 遍历物体的所有材质槽
            for slot in obj.material_slots:
                if slot.material and slot.material.users > 1:
                    i += 1
                    # 如果材质有多个用户（即它是实例化的），则创建一个副本
                    new_material = slot.material.copy()
                    new_material.name = slot.material.name + "_" +\
                        str(i)
                    slot.material = new_material
            bpy.ops.object.lily_texture_packer()
            obj.select_set(False)

        bpy.ops.image.save_all_modified()

        return {'FINISHED'}
