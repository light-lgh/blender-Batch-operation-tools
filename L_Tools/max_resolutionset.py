import bpy
from bpy.types import Operator


class MaxResProp(bpy.types.PropertyGroup):
    max_resolution: bpy.props.IntProperty(default=1024, min=1, name="最大分辨率")


class MaxResSet(Operator):
    bl_idname = "maxres_set.operator"
    bl_label = "设置最大分辨率"
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
