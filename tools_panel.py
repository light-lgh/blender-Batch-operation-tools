import bpy
from bpy.types import Panel
from .bat_operator import MyOperatorCr, MyOperatorCl
from .max_resolutionset import MaxResSet, MaxResSetOnlySelect


class MyPanel(Panel):
    bl_label = '操作'
    bl_idname = "IMAGE2MAT_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "批量工具"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.label(text="贴图路径:")
        row.prop(bpy.context.scene.matprop, "texture_path", text="")
        row = layout.row(align=True)
        row.operator(MyOperatorCr.bl_idname, icon='MATERIAL_DATA')
        row.operator(MyOperatorCl.bl_idname, icon='CANCEL')
        row = layout.row(align=True)
        row.label(text="最大分辨率:")
        row.prop(context.scene.maxres, "max_resolution")
        row = layout.row(align=True)
        row.operator(MaxResSet.bl_idname, icon='IMAGE_DATA')


class MyShaderPanel(Panel):
    bl_label = "操作"
    bl_idname = "MaxRes_PT_Panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "批量工具"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.label(text="最大分辨率:")
        row.prop(context.scene.maxres, "max_resolution")
        row = layout.row(align=True)
        row.operator(MaxResSetOnlySelect.bl_idname, icon='IMAGE_DATA')
