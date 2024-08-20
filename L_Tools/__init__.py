import bpy
from bpy.props import FloatVectorProperty
from bpy.types import PropertyGroup
from .bat_operator import MyOperatorCr, MyOperatorCl,  MaterialInstanceSeparator
from .max_resolutionset import resSet, resSetOnlySelect, ConvertToJPG, SelectedOnly_Set
from .tools_panel import MyPanel, MyShaderPanel, MyPanel_MAT, MyPanel_RES
from .mat_operator import AddNode, AdjustColor, ChangeRoughness, ChangeMetallic,ChangeEmission, ChangeBackfaceCulling, ChangeBlendeMode,RemoveMixNode


bl_info = {
    "name": "批量工具",
    "category": "LTools",
    "author": "Light",
    "blender": (3, 6, 0),
    "location": "UI",
    "description": "批量处理",
    "version": (2, 3)
}


class ltProperties(PropertyGroup):
    color_picker: FloatVectorProperty(
        name="Color Picker",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0, 1.0),
        size=4,
        min=0.0,
        max=1.0
    )  # type: ignore
    texture_path: bpy.props.StringProperty(
        default="C:\\", subtype="DIR_PATH")  # type: ignore
    suffix_name: bpy.props.StringProperty(
        default="_VRayCompleteMap")  # type: ignore
    max_resolution: bpy.props.IntProperty(
        default=1024, min=1, name="")  # type: ignore
    jpg_quality: bpy.props.IntProperty(
        name="图像质量", description="JPEG 图像保存质量", default=90, min=0, max=100)  # type: ignore
    lt_metallic: bpy.props.FloatProperty(
        name="金属度", default=0, max=1, min=0, step=0.1, subtype="FACTOR")  # type: ignore
    lt_roughness: bpy.props.FloatProperty(
        name="粗糙度", default=0, max=1, min=0, step=0.1, subtype="FACTOR")  # type: ignore
    lt_backface_culling: bpy.props.BoolProperty(
        name="背面剔除", default=False)  # type: ignore
    # 定义混合模式枚举
    blend_modes = [
        ('OPAQUE', "不透明", "Opaque"),
        ('CLIP', "Alpha Clip", "Alpha Clip"),
        ('HASHED', "Alpha Hashed", "Alpha Hashed"),
        ('BLEND', "Alpha Blend", "Alpha Blend"),
    ]

    # 添加枚举属性到对象
    lt_blend_mode: bpy.props.EnumProperty(
        name="",
        description="选择材质的混合模式",
        items=blend_modes,
        default='OPAQUE'
    )  # type: ignore


clss = [MyOperatorCr, MyOperatorCl,  MaterialInstanceSeparator, ltProperties, ChangeRoughness, ChangeMetallic,
        resSet, resSetOnlySelect, ConvertToJPG, SelectedOnly_Set, MyPanel, MyShaderPanel, MyPanel_MAT, MyPanel_RES,
        AddNode, AdjustColor,ChangeEmission, ChangeBackfaceCulling, ChangeBlendeMode,RemoveMixNode]


def register():
    for i in clss:
        bpy.utils.register_class(i)

    bpy.types.Scene.ltprop = bpy.props.PointerProperty(type=ltProperties)


def unregister():
    for i in clss:
        bpy.utils.unregister_class(i)

    del bpy.types.Scene.ltprop


if __name__ == "__main__":
    register()
