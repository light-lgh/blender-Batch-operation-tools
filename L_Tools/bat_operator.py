import bpy
from bpy.types import Operator
import os



class MaterialManager:

    def __init__(self):
        self.target_dir = bpy.context.scene.ltprop.texture_path
        self.suffix = bpy.context.scene.ltprop.suffix_name

    def assign_materials_to_selected(self):

        if not os.path.exists(self.target_dir):
            self.report_message(f"目录不存在: {self.target_dir}")
            return

        common_image_extensions = {
            '.png',
            '.jpg',
            '.jpeg',
            '.bmp',
            '.gif',
            '.tiff',
            '.tga',
            '.exr'
        }

        # 建立贴图索引
        texture_dict = {}

        for file in os.listdir(self.target_dir):

            full_path = os.path.join(self.target_dir, file)

            if not os.path.isfile(full_path):
                continue

            name, ext = os.path.splitext(file)

            if ext.lower() in common_image_extensions:
                texture_dict[name] = full_path

        assign_count = 0

        for obj in bpy.context.selected_objects:

            if obj.type != 'MESH':
                continue

            texture_name = obj.name + self.suffix

            if texture_name not in texture_dict:
                print(f"未找到贴图: {texture_name}")
                continue

            image_path = texture_dict[texture_name]

            mat = self.create_material(texture_name, image_path)

            obj.data.materials.clear()
            obj.data.materials.append(mat)

            assign_count += 1

            print(
                f"已赋予材质: {obj.name} -> {os.path.basename(image_path)}")

        print(f"完成，共处理 {assign_count} 个物体")

    def create_material(self, mat_name, image_path):

        # 已存在同名材质直接使用
        if mat_name in bpy.data.materials:
            return bpy.data.materials[mat_name]

        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        nodes.clear()

        tex_node = nodes.new("ShaderNodeTexImage")
        bsdf_node = nodes.new("ShaderNodeBsdfPrincipled")
        output_node = nodes.new("ShaderNodeOutputMaterial")

        tex_node.location = (-600, 0)
        bsdf_node.location = (-300, 0)
        output_node.location = (0, 0)

        tex_node.image = bpy.data.images.load(
            image_path,
            check_existing=True
        )

        links.new(
            tex_node.outputs["Color"],
            bsdf_node.inputs["Base Color"]
        )

        links.new(
            bsdf_node.outputs["BSDF"],
            output_node.inputs["Surface"]
        )

        # png自动连接Alpha
        if image_path.lower().endswith(".png"):
            try:
                links.new(
                    tex_node.outputs["Alpha"],
                    bsdf_node.inputs["Alpha"]
                )

                mat.blend_method = 'HASHED'
                mat.use_backface_culling = True

            except:
                pass

        return mat

    def clear_all_materials(self):

        selected_objects = bpy.context.selected_objects

        materials_to_remove = set()

        for obj in selected_objects:

            if obj.type != 'MESH':
                continue

            for mat in obj.data.materials:
                if mat:
                    materials_to_remove.add(mat)

            obj.data.materials.clear()

        for mat in materials_to_remove:
            if mat.users == 0:
                bpy.data.materials.remove(mat)


class MyOperatorCr(Operator):
    bl_idname = "lt.material_cr"
    bl_label = "一键贴图"
    bl_description = "根据物体名称匹配贴图"

    def execute(self, context):

        material_manager = MaterialManager()

        material_manager.assign_materials_to_selected()

        return {'FINISHED'}


class MyOperatorCl(Operator):
    bl_idname = "lt.material_cl"
    bl_label = "清空材质"
    bl_description = "清空选中物体材质"
    bl_options = {'UNDO'}

    def execute(self, context):

        material_manager = MaterialManager()

        material_manager.clear_all_materials()

        bpy.ops.outliner.orphans_purge(
            do_local_ids=True,
            do_linked_ids=True,
            do_recursive=True
        )

        return {'FINISHED'}

class MaterialInstanceSeparator(bpy.types.Operator):
    bl_idname = "lt.material_instance_separator"
    bl_label = "快速切图"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 新材质的序号
        i = 0
        # 存储选中的对象
        previously_selected_objects = [
            obj for obj in bpy.context.selected_objects]
        bpy.ops.object.select_all(action='DESELECT')

        for obj in previously_selected_objects:
            if obj.type == 'MESH' and obj.data.materials:
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
