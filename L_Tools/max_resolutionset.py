import bpy
import os
import time
from bpy.types import Operator
from datetime import datetime


def get_selected_nodes(context):
    active_tree = bpy.context.active_object.active_material.node_tree
    selected_nodes = [node for node in active_tree.nodes if node.select and isinstance(
        node, bpy.types.ShaderNodeTexImage)]
    return selected_nodes, active_tree


def get_image_scale_factor(image):
    original_width = image.size[0]
    original_height = image.size[1]
    max_resolution = bpy.context.scene.maxres.max_resolution

    # 判断是否需要调整分辨率
    if original_width > max_resolution \
            or original_height > max_resolution \
            or (original_width == original_height and original_width > max_resolution):

        scale_factor = max_resolution / \
            max(original_width, original_height)
        return original_width, original_height, scale_factor
    else:

        return None


class MaxResProp(bpy.types.PropertyGroup):
    max_resolution: bpy.props.IntProperty(default=1024, min=1, name="")
    jpg_quality: bpy.props.IntProperty(
        name="图像质量", description="JPEG 图像保存质量", default=90, min=0, max=100)


class MaxResSet(Operator):
    bl_idname = "maxres_set.operator"
    bl_label = "调整最大分辨率"
    bl_description = "调整所有图像的最大分辨率并输出到源文件"

    def execute(self, context):
        # 遍历所有图像数据块
        for img in bpy.data.images:
            scale_info = get_image_scale_factor(img)
            if scale_info is not None:
                original_width, original_height, scale_factor = scale_info
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                print(bpy.data.images[img.name])

                # 设置图像的新分辨率
                img.scale(new_width, new_height)
            else:
                continue

        # 保存所有修改后的图像
        for img in bpy.data.images:
            if img.is_dirty:
                img.save()

        self.report({'INFO'}, "完成")
        return {'FINISHED'}


class MaxResSetOnlySelect(Operator):
    bl_idname = "maxres_set_onlyselect.operator"
    bl_label = "调整最大分辨率 (仅选定图像节点)"
    bl_description = "调整选定图像节点的最大分辨率并输出到源文件"

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
                    if active_image.is_dirty:
                        active_image.save()
                        self.report({'INFO'}, f"已修改 {active_image.name}")

        return {'FINISHED'}


class ConvertToJPG(Operator):
    bl_idname = "convert_to_jpg_onlyselect.operator"
    bl_label = "另存为jpg格式 (仅选定图像节点)"
    bl_description = "将选定图像节点的格式保存为jpg(覆盖保存)"

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
                        original_filepath = active_image.filepath
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
                            filepath=new_filepath, quality=bpy.context.scene.maxres.jpg_quality)
                        # 更新节点树
                        active_tree = get_selected_nodes(context)[1]
                        new_image_texture_node = active_tree.nodes.new(
                            type='ShaderNodeTexImage')
                        new_image_texture_node.image = bpy.data.images.load(
                            new_filepath)
                        # 获取原始节点的位置
                        original_location = selected_node.location.copy()
                        # 设置新节点的位置在原始节点的左侧
                        new_location = (original_location.x -
                                        300, original_location.y)
                        new_image_texture_node.location = new_location
                        active_image.file_format = originalformat
                        selected_node.select = False

                        self.report({'INFO'}, f"成功转换{active_image.name}")
                    except Exception as e:
                        self.report({'ERROR'}, f"转换\
                                    {active_image.name} 为JPEG时出错: {e}")
                elif active_image.file_format.lower() == 'jpeg':
                    self.report({'INFO'}, f"{active_image.name} 已经是JPEG格式")

        return {'FINISHED'}
