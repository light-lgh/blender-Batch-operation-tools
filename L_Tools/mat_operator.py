from typing import Set
import bpy
from bpy.types import Context


class MatOp:

    @staticmethod
    def add_mix_color_node(mat, sRGBa):
        # 获取材质节点树
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # 查找原理化 BSDF 节点和纹理贴图节点
        bsdf_node = None
        texture_node = None

        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                bsdf_node = node
            elif node.type == 'TEX_IMAGE':
                texture_node = node

        if not bsdf_node or not texture_node:
            return

        # 检查是否已经有混合颜色节点在纹理节点和 BSDF 节点之间
        base_color_input = bsdf_node.inputs['Base Color']
        if base_color_input.is_linked:
            existing_link = base_color_input.links[0]
            if existing_link.from_node.type == 'MIX':
                return

        # 添加混合颜色节点
        mix_node = nodes.new(type='ShaderNodeMix')
        mix_node.data_type = 'RGBA'
        mix_node.blend_type = 'MULTIPLY'
        mix_node.clamp_factor = True
        mix_node.inputs[7].default_value = sRGBa
        mix_node.inputs[0].default_value = 1.0
        # 设置混合颜色节点位置
        mix_node.location = (texture_node.location.x -
                             200, texture_node.location.y)

        # 连接原理化 BSDF 节点的基础色到混合颜色节点
        if base_color_input.is_linked:
            original_link = base_color_input.links[0]
            from_socket = original_link.from_socket  # 保存原始链接的输入节点
            links.remove(original_link)  # 删除旧的链接
            links.new(from_socket, mix_node.inputs[6])  # 用保存的输入节点创建新链接

        # 连接混合节点的第一个输出到基础色输入
        links.new(mix_node.outputs[2], base_color_input)

    @staticmethod
    def remove_mix_color_node(mat):
        # 获取材质节点树
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # 查找原理化 BSDF 节点和纹理贴图节点
        bsdf_node = None
        texture_node = None

        for node in nodes:
            if node.type == 'BSDF_PRINCIPLED':
                bsdf_node = node
            elif node.type == 'TEX_IMAGE':
                texture_node = node

        if not bsdf_node or not texture_node:
            return

        # 检查是否已经有混合颜色节点在纹理节点和 BSDF 节点之间
        base_color_input = bsdf_node.inputs['Base Color']
        if base_color_input.is_linked:
            existing_link = base_color_input.links[0]
            if existing_link.from_node.type == 'MIX':
                mix_node = existing_link.from_node
                texture_node = texture_node.outputs[0]
                links.remove(existing_link)  # 删除旧的链接
                links.new(texture_node, base_color_input)  # 用保存的输入节点创建新链接
                nodes.remove(mix_node)

    @staticmethod
    def adjust_mixnode_color(mat, sRGBa):
        nodes = mat.node_tree.nodes
        for node in nodes:
            if node.type == 'MIX':
                node.inputs[7].default_value = sRGBa


def get_color_picker_value(scene):
    scene = bpy.context.scene
    color_value = scene.ltprop.color_picker
    return color_value


class AddNode(bpy.types.Operator):
    bl_idname = "lt.add_node"
    bl_label = "添加混合颜色节点"
    bl_description = "添加混合颜色节点"
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = bpy.context.scene
        color_value = scene.ltprop.color_picker
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material and slot.material.node_tree:
                        MatOp.add_mix_color_node(slot.material, color_value)

        return {'FINISHED'}


class RemoveMixNode(bpy.types.Operator):
    bl_idname = "lt.remove_mix_node"
    bl_label = "移除混合颜色节点"
    bl_description = "移除混合颜色节点"
    bl_options = {'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material and slot.material.node_tree:
                        MatOp.remove_mix_color_node(slot.material)

        return {'FINISHED'}


class AdjustColor(bpy.types.Operator):
    bl_idname = "lt.adjust_color"
    bl_label = "调整混合颜色节点颜色"
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = bpy.context.scene
        color_value = scene.ltprop.color_picker

        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material and slot.material.node_tree:
                        MatOp.adjust_mixnode_color(
                            slot.material, color_value)

        return {'FINISHED'}


class ChangeMetallic(bpy.types.Operator):
    bl_idname = "lt.change_metallic"
    bl_label = "调整金属度"
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = bpy.context.scene
        metallic = scene.ltprop.lt_metallic
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material and slot.material.node_tree:
                        nodes = slot.material.node_tree.nodes
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                node.inputs['Metallic'].default_value = metallic
        return {'FINISHED'}


class ChangeRoughness(bpy.types.Operator):
    bl_idname = "lt.change_roughness"
    bl_label = "调整粗糙度"
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = bpy.context.scene
        roughness = scene.ltprop.lt_roughness
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material and slot.material.node_tree:
                        nodes = slot.material.node_tree.nodes
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                node.inputs['Roughness'].default_value = roughness
        return {'FINISHED'}


class ChangeEmission(bpy.types.Operator):
    bl_idname = "lt.change_emission"
    bl_label = "调整自发光"
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = bpy.context.scene
        emission_color = scene.ltprop.color_picker
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material and slot.material.node_tree:
                        nodes = slot.material.node_tree.nodes
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                node.inputs[19].default_value = emission_color
        return {'FINISHED'}


class ChangeBlendeMode(bpy.types.Operator):
    bl_idname = "lt.change_blend_mode"
    bl_label = "调整混合模式"
    bl_description = "调整混合模式"
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = bpy.context.scene
        blend_mode = scene.ltprop.lt_blend_mode
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material:
                        slot.material.blend_method = blend_mode
        return {'FINISHED'}


class ChangeBackfaceCulling(bpy.types.Operator):
    bl_idname = "lt.change_backface_culling"
    bl_label = "调整背面剔除"
    bl_description = "调整背面剔除"
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = bpy.context.scene
        backface_culling = scene.ltprop.lt_backface_culling
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material:
                        slot.material.use_backface_culling = backface_culling
        return {'FINISHED'}


def create_basic_material_with_existing_image(mat):
    # 检查材质是否启用了节点
    if not mat.use_nodes:
        mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # 查找现有的图像纹理节点
    base_color_node = None
    for node in nodes:
        if node.type == "TEX_IMAGE":
            base_color_node = node
            break

    if not base_color_node:
        print(f"材质 {mat.name} 中没有图像纹理节点，跳过。")
        return

    # 清除除图像纹理节点外的所有节点
    for node in list(nodes):
        if node != base_color_node:
            nodes.remove(node)

    # 调整图像纹理节点位置
    base_color_node.location = (-600, 0)

    # 添加其他所需节点
    color_factor_node = nodes.new(type="ShaderNodeMix")
    color_factor_node.location = (-300, -200)
    color_factor_node.label = "Color Factor"
    color_factor_node.data_type = 'RGBA'
    color_factor_node.blend_type = 'MULTIPLY'
    color_factor_node.inputs[0].default_value = 1.0
    color_factor_node.inputs[7].default_value = [1.0, 1.0, 1.0, 1.0]

    light_path_node = nodes.new(type="ShaderNodeLightPath")
    light_path_node.location = (-300, 200)

    transparent_node = nodes.new(type="ShaderNodeBsdfTransparent")
    transparent_node.location = (0, -200)

    emission_node = nodes.new(type="ShaderNodeEmission")
    emission_node.location = (0, -400)

    mix_shader_node = nodes.new(type="ShaderNodeMixShader")
    mix_shader_node.location = (200, 0)

    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    output_node.location = (400, 0)

    # 连接节点
    links.new(base_color_node.outputs[0], color_factor_node.inputs[6])
    links.new(color_factor_node.outputs[2], emission_node.inputs[0])
    links.new(emission_node.outputs[0], mix_shader_node.inputs[2])
    links.new(
        light_path_node.outputs['Is Camera Ray'], mix_shader_node.inputs[0])
    links.new(transparent_node.outputs[0], mix_shader_node.inputs[1])
    links.new(mix_shader_node.outputs[0], output_node.inputs[0])


class ConvertToBasicMaterial(bpy.types.Operator):
    bl_idname = "lt.convert_to_basic_material"
    bl_label = "转换为基础材质"
    bl_description = "将选中的对象的材质转换为基础材质"
    bl_options = {'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    mat = slot.material
                    if mat:
                        create_basic_material_with_existing_image(mat)
        return {'FINISHED'}


def bsdf_material(material):
    # Get the material's node tree
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    # Find all image texture nodes
    image_texture_nodes = [node for node in nodes if node.type == 'TEX_IMAGE']

    if not image_texture_nodes:
        return

    # Clear all nodes except the image texture nodes
    for node in nodes:
        if node not in image_texture_nodes:
            nodes.remove(node)

    # Create a new Principled BSDF node
    principled_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled_bsdf.location = (0, 0)

    # Get the material output node
    output_node = None
    for node in nodes:
        if node.type == 'OUTPUT_MATERIAL':
            output_node = node
            break

    if not output_node:
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (400, 0)

    # Link the image texture color to the base color of the Principled BSDF
    for image_texture in image_texture_nodes:
        links.new(image_texture.outputs['Color'],
                  principled_bsdf.inputs['Base Color'])

    # Link the Principled BSDF to the material output
    links.new(principled_bsdf.outputs['BSDF'], output_node.inputs['Surface'])


class ConverToBSDF(bpy.types.Operator):
    bl_idname = "lt.convert_to_bsdf"
    bl_label = "转换为BSDF"
    bl_description = "转换为BSDF"
    bl_options = {'UNDO'}

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    material = slot.material
                    if material and material.use_nodes:
                        bsdf_material(material)
        return {'FINISHED'}
