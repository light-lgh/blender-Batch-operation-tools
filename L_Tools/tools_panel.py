import bpy
from bpy.types import Panel
from .bat_operator import MyOperatorCr, MyOperatorCl, MaterialInstanceSeparator
from .max_resolutionset import MaxResSet, MaxResSetOnlySelect, ConvertToJPG, SelectedOnly_Set


class MyPanel(Panel):
    bl_label = '操作'
    bl_idname = "IMAGE2MAT_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "批量工具"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.label(text="设置贴图路径:")
        row.prop(context.scene.matprop, "texture_path", text="")
        row = layout.row(align=True)
        row.operator(MyOperatorCr.bl_idname, icon='MATERIAL_DATA')
        row.operator(MyOperatorCl.bl_idname, icon='CANCEL')
        row = layout.row(align=True)
        row.label(text="调整分辨率:")
        row = layout.row(align=True)
        row.prop(context.scene.maxres, "max_resolution")
        row = layout.row(align=True)
        row.operator(SelectedOnly_Set.bl_idname, icon='IMAGE_DATA')
        row = layout.row(align=True)
        row.operator(MaterialInstanceSeparator.bl_idname, icon='DUPLICATE')


class MyShaderPanel(Panel):
    bl_label = "操作"
    bl_idname = "MAXRES_PT_Panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "批量工具"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.label(text="调整分辨率(仅限选定节点):")
        row = layout.row(align=True)
        row.prop(context.scene.maxres, "max_resolution")
        row.operator(MaxResSetOnlySelect.bl_idname, icon='IMAGE_DATA')
        row = layout.row(align=True)
        row.operator(MaxResSet.bl_idname, icon='IMAGE_DATA')
        row = layout.row(align=True)
        row.label(text="另存为jpg:")
        row = layout.row(align=True)
        row.prop(context.scene.maxres, "jpg_quality")
        row.operator(ConvertToJPG.bl_idname, icon='IMAGE_DATA')
