from typing import Set
import bpy
import os
import time
from bpy.types import Context, Operator
from datetime import datetime


def get_selected_nodes(context):
    active_tree = bpy.context.active_object.active_material.node_tree
    selected_nodes = [node for node in active_tree.nodes if node.select and isinstance(
        node, bpy.types.ShaderNodeTexImage)]
    return selected_nodes, active_tree


def get_image_scale_factor(image):
    if image is None:
        return None

    original_width = image.size[0]
    original_height = image.size[1]
    max_resolution = bpy.context.scene.ltprop.max_resolution

    # 判断是否需要调整分辨率
    if original_width > max_resolution \
            or original_height > max_resolution \
            or (original_width == original_height and original_width > max_resolution):

        scale_factor = max_resolution / \
            max(original_width, original_height)

        return original_width, original_height, scale_factor
    else:

        return None


class resSet(Operator):
    bl_idname = "lt.res_set"
    bl_label = "全局最大分辨率"
    bl_description = "调整所有图像的最大分辨率并输出到源文件"

    def execute(self, context):
        # 遍历所有图像数据块
        for img in bpy.data.images:
            scale_info = get_image_scale_factor(img)
            if scale_info is not None:
                original_width, original_height, scale_factor = scale_info
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)

                # 设置图像的新分辨率
                img.scale(new_width, new_height)
            else:
                continue

        # 保存所有修改后的图像
        bpy.ops.image.save_all_modified()
        # for img in bpy.data.images:
        #     if img.is_dirty:
        #         img.save()

        self.report({'INFO'}, "完成")
        return {'FINISHED'}


class resSetOnlySelect(Operator):
    bl_idname = "lt.res_set_onlyselect"
    bl_label = "调整最大分辨率 (仅选定图像节点)"
    bl_description = "调整材质编辑器选定图像节点的最大分辨率并输出到源文件"

    def execute(self, context):

        # 获取选中的节点
        selected_nodes = get_selected_nodes(context)[0]

        for selected_node in selected_nodes:
            # 获取每个节点的图像
            active_image = selected_node.image

            # 判断是否有活动图像
            if active_image:
                scale_info = get_image_scale_factor(active_image)
                if scale_info is not None:
                    # 获取图像的原始分辨率
                    original_width, original_height, scale_factor = scale_info
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)

                    # 设置图像的新分辨率
                    active_image.scale(new_width, new_height)
                    # 保存修改后的图像
                    # if active_image.is_dirty:
                    #     active_image.save()
                    #     self.report({'INFO'}, f"已修改 {active_image.name}")
        bpy.ops.image.save_all_modified()
        return {'FINISHED'}


def are_nodes_overlapping(node1, node2, threshold=10):

    x1, y1 = node1.location
    x2, y2 = node2

    # 计算节点之间的欧几里得距离
    distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    # 如果距离小于阈值，则认为节点重叠
    return distance < threshold


class ConvertToJPG(Operator):
    bl_idname = "lt.convert_func_onlyselect"
    bl_label = "另存为jpg格式 (仅选定图像节点)"
    bl_description = "将选定图像节点的格式保存为jpg,打包的图像节点不可用,先解包"

    def execute(self, context):
        # 选择图像
        selected_nodes = get_selected_nodes(context)[0]
        for selected_node in selected_nodes:
            if selected_node:
                active_image = selected_node.image
                if active_image and active_image.file_format.lower() != 'jpeg':
                    # 转换为JPEG格式
                    try:
                        # 设置图像文件格式为JPEG
                        originalformat = active_image.file_format
                        active_image.file_format = 'JPEG'

                        # 获取原始文件路径和文件名
                        original_filepath = bpy.path.abspath(
                            active_image.filepath)

                        filename, _ = os.path.splitext(
                            os.path.basename(original_filepath))

                        # 时间戳
                        timestamp = int(time.time())
                        # 从时间戳创建 datetime 对象
                        dt_object = datetime.fromtimestamp(timestamp)

                        # 将 datetime 对象格式化为字符串，显示两位数的年月日时分秒
                        convert_time = dt_object.strftime(
                            "%m%d-%H%M%S")
                        # 构建新的文件路径，将文件扩展名更改为.jpg

                        new_filepath = os.path.join(os.path.dirname(
                            original_filepath), f'{filename} {convert_time}.jpg')

                        # 保存文件，设置质量
                        active_image.save(
                            filepath=new_filepath, quality=bpy.context.scene.ltprop.jpg_quality)
                        active_image.file_format = originalformat
                        # 更新节点树
                        active_tree = get_selected_nodes(context)[1]

                        # 获取原始节点的位置
                        original_location = selected_node.location.copy()
                        offset_x = 300
                        new_location = (original_location.x -
                                        offset_x, original_location.y)
                        # 设置新节点的位置在原始节点的左侧

                        for existing_node in active_tree.nodes:

                            if are_nodes_overlapping(existing_node, new_location):

                                # 如果重叠，调整新节点的位置
                                new_location = (
                                    existing_node.location.x - offset_x, existing_node.location.y)

                        new_image_texture_node = active_tree.nodes.new(
                            type='ShaderNodeTexImage')
                        new_image_texture_node.image = bpy.data.images.load(
                            new_filepath)
                        new_image_texture_node.location = new_location

                        selected_node.select = False

                        self.report({'INFO'}, f"成功转换{active_image.name}")
                    except Exception as e:
                        self.report({'ERROR'}, f"转换\
                                    {active_image.name} 为JPEG时出错: {e}")
                elif active_image.file_format.lower() == 'jpeg':
                    try:
                        # 设置图像文件格式为JPEG

                        # active_image.file_format = 'JPEG'

                        # 获取原始文件路径和文件名
                        original_filepath = bpy.path.abspath(
                            active_image.filepath)

                        filename, _ = os.path.splitext(
                            os.path.basename(original_filepath))

                        # 时间戳
                        timestamp = int(time.time())
                        # 从时间戳创建 datetime 对象
                        dt_object = datetime.fromtimestamp(timestamp)

                        # 将 datetime 对象格式化为字符串，显示两位数的年月日时分秒
                        convert_time = dt_object.strftime(
                            "%m%d-%H%M%S")
                        # 构建新的文件路径，将文件扩展名更改为.jpg

                        new_filepath = os.path.join(os.path.dirname(
                            original_filepath), f'{filename} {convert_time}.jpg')

                        # 保存文件，设置质量
                        active_image.save(
                            filepath=new_filepath, quality=bpy.context.scene.ltprop.jpg_quality)

                        # 更新节点树
                        active_tree = get_selected_nodes(context)[1]

                        # 获取原始节点的位置
                        original_location = selected_node.location.copy()
                        offset_x = 300
                        new_location = (original_location.x -
                                        offset_x, original_location.y)
                        # 设置新节点的位置在原始节点的左侧

                        for existing_node in active_tree.nodes:

                            if are_nodes_overlapping(existing_node, new_location):

                                # 如果重叠，调整新节点的位置
                                new_location = (
                                    existing_node.location.x - offset_x, existing_node.location.y)

                        new_image_texture_node = active_tree.nodes.new(
                            type='ShaderNodeTexImage')
                        new_image_texture_node.image = bpy.data.images.load(
                            new_filepath)
                        new_image_texture_node.location = new_location

                        selected_node.select = False

                    except Exception as e:
                        self.report({'ERROR'}, f"转换\
                                    {active_image.name} 为JPEG时出错: {e}")

                        self.report({'INFO'}, f"{active_image.name} 已经是JPEG格式")

        return {'FINISHED'}


class SelectedOnly_Set(Operator):
    bl_idname = "lt.visable_set"
    bl_label = "调整选中对象的贴图分辨率"
    bl_description = "调整选中对象的贴图分辨率"

    def execute(self, context):

        # 遍历选中的对象
        for obj in bpy.context.selected_objects:

            for slot in obj.material_slots:
                if slot.material:
                    # 遍历材质节点
                    for node in slot.material.node_tree.nodes:

                        if isinstance(node, bpy.types.ShaderNodeTexImage):

                            image = node.image
                            # 获取图像的分辨率
                            scale_info = get_image_scale_factor(
                                image)
                            if scale_info is not None:
                                # 获取图像节点
                                original_width, original_height, scale_factor = scale_info

                                # 设置新的分辨率（这里假设你要将分辨率设置为1024x1024）

                                new_width = int(
                                    original_width * scale_factor)
                                new_height = int(
                                    original_height * scale_factor)

                                # 设置图像的新分辨率
                                image.scale(new_width, new_height)
                                # if image.is_dirty:
                                #     image.save()
                                #     self.report(
                                #         {'INFO'}, f"已修改 {image.name}")

                            else:
                                self.report(
                                    {'INFO'}, f"{image.name}无需调整")
        bpy.ops.image.save_all_modified()

        return {'FINISHED'}
