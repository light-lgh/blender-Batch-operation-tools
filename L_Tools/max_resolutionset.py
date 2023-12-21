import bpy
from bpy.types import Operator


class MaxResProp(bpy.types.PropertyGroup):
    max_resolution: bpy.props.IntProperty(default=1024, min=1, name="")


class MaxResSet(Operator):
    bl_idname = "maxres_set.operator"
    bl_label = "调整最大分辨率"
    bl_description = "调整所有图像的最大分辨率并输出到源文件"

    def execute(self, context):
        max_resolution = bpy.context.scene.maxres.max_resolution

        # 遍历所有图像数据块
        for img in bpy.data.images:
            # 获取图像的原始分辨率
            original_width = img.size[0]
            original_height = img.size[1]

            # 判断是否需要调整分辨率
            if original_width > max_resolution \
                or original_height > max_resolution \
                    or (original_width == original_height and original_width > max_resolution):

                scale_factor = max_resolution / \
                    max(original_width, original_height)
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                print(bpy.data.images[img.name])

                # 设置图像的新分辨率
                img.scale(new_width, new_height)

        # 保存所有修改后的图像
        for img in bpy.data.images:
            if img.is_dirty:
                img.save()
        return {'FINISHED'}


class MaxResSetOnlySelect(Operator):
    bl_idname = "image.maxres_set_onlyselect"
    bl_label = "调整最大分辨率 (仅选定图像节点)"
    bl_description = "调整选定图像节点的最大分辨率并输出到源文件"

    def execute(self, context):
        max_resolution = bpy.context.scene.maxres.max_resolution
        active_tree = bpy.context.active_object.active_material.node_tree

        if active_tree and active_tree.bl_idname == 'ShaderNodeTree':
            # 获取选中的节点
            selected_nodes = [node for node in active_tree.nodes if node.select and isinstance(
                node, bpy.types.ShaderNodeTexImage)]

            for selected_node in selected_nodes:
                # 获取每个节点的图像
                active_image = selected_node.image

                # 判断是否有活动图像
                if active_image:
                    # 获取图像的原始分辨率
                    original_width = active_image.size[0]
                    original_height = active_image.size[1]

                # 判断是否需要调整分辨率
                if original_width > max_resolution or original_height > max_resolution \
                        or (original_width == original_height and original_width > max_resolution):
                    scale_factor = max_resolution / \
                        max(original_width, original_height)
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)

                    # 设置图像的新分辨率
                    active_image.scale(new_width, new_height)

                    # 保存修改后的图像
                    if active_image.is_dirty:
                        active_image.save()

        return {'FINISHED'}
