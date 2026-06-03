import bpy
from bpy.types import Panel
from .bat_operator import MyOperatorCr, MyOperatorCl, MaterialInstanceSeparator
from .max_resolutionset import resSet, resSetOnlySelect, ConvertToJPG, SelectedOnly_Set
from .mat_operator import ConverToBSDF, ConvertToBasicMaterial, AddNode, AdjustColor, ChangeRoughness, ChangeMetallic, ChangeEmission, ChangeBackfaceCulling, ChangeBlendeMode, RemoveMixNode


class View3DPanel():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'


class MyPanel(View3DPanel, Panel):
    bl_label = '贴图'
    bl_idname = "IMAGE2MAT_PT_panel"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.label(text="设置贴图路径:")
        row.prop(context.scene.ltprop, "texture_path", text="")
        row = layout.row(align=True)
        row.label(text="图像后缀名:")
        row.prop(context.scene.ltprop, "suffix_name", text="")
        row = layout.row(align=True)
        row.operator(MyOperatorCr.bl_idname, icon='SEQ_PREVIEW')
        row.operator(MyOperatorCl.bl_idname, icon='CANCEL')
        row = layout.row(align=True)
        row.operator("image.save_all_modified",
                     text="Save All Images", icon='FILE_TICK')


class MyPanel_RES(View3DPanel, Panel):
    bl_label = '分辨率调整 !!!操作不可逆!!!'
    bl_idname = "RES_PT_panel"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row = layout.row(align=True)
        row.label(text="设置分辨率:")
        row.prop(context.scene.ltprop, "max_resolution")
        row = layout.row(align=True)
        row.operator(SelectedOnly_Set.bl_idname, icon='IMAGE_DATA')
        row = layout.row(align=True)
        row.operator(MaterialInstanceSeparator.bl_idname, icon='DUPLICATE')


class MyPanel_MAT(View3DPanel, Panel):
    bl_label = '材质'
    bl_idname = "MAT_PT_panel"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator(ConvertToBasicMaterial.bl_idname,
                     text="转为基础材质", icon='MATERIAL')
        row.operator(ConverToBSDF.bl_idname,
                     text="转为BSDF材质", icon='MATERIAL')
        row = layout.row(align=True)
        row.operator(AddNode.bl_idname, text="添加", icon='KEYTYPE_JITTER_VEC')
        row.operator(RemoveMixNode.bl_idname, text="移除",
                     icon='KEYTYPE_BREAKDOWN_VEC')
        row.prop(context.scene.ltprop, "color_picker", text="")
        row.operator(AdjustColor.bl_idname, text="", icon="PLAY")
        row = layout.row(align=True)
        row.prop(context.scene.ltprop, "lt_metallic", text="金属度")
        row.operator(ChangeMetallic.bl_idname, text="", icon="PLAY")

        row = layout.row(align=True)
        row.prop(context.scene.ltprop, "lt_roughness", text="粗糙度")
        row.operator(ChangeRoughness.bl_idname, text="", icon="PLAY")
        row = layout.row(align=True)
        row.separator
        row = layout.row(align=True)
        row.operator(ChangeEmission.bl_idname, text="", icon="PLAY")

        # row = layout.row(align=True)
        # box = row.box()
        # box.label(text="其他设置", icon='HANDLETYPE_AUTO_CLAMP_VEC')
        # box.prop(context.scene.ltprop, "lt_backface_culling",
        #          icon="SEQUENCE_COLOR_04")
        # box.prop(context.scene.ltprop, "lt_blend_mode")

        # box = row.box()
        # box.label(text="")
        # box.operator(ChangeBackfaceCulling.bl_idname, text="🐍setting🐍")
        # box.operator(ChangeBlendeMode.bl_idname, text="🐍setting🐍")


class MyShaderPanel(Panel):
    bl_label = "操作"
    bl_idname = "LT_PT_Panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.label(text="调整分辨率:")
        row = layout.row(align=True)
        row.prop(context.scene.ltprop, "max_resolution")
        row.operator(resSetOnlySelect.bl_idname, icon='IMAGE_DATA')
        row = layout.row(align=True)
        row.operator(resSet.bl_idname, icon='IMAGE_DATA')
        row = layout.row(align=True)
        row.label(text="另存为jpg:")
        row = layout.row(align=True)
        row.prop(context.scene.ltprop, "jpg_quality")
        row.operator(ConvertToJPG.bl_idname, icon='IMAGE_DATA')
