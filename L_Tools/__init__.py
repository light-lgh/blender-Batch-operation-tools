import bpy
from .bat_operator import MyOperatorCr, MyOperatorCl, prop_mat, MaterialInstanceSeparator
from .max_resolutionset import MaxResProp, MaxResSet, MaxResSetOnlySelect, ConvertToJPG, SelectedOnly_Set
from .tools_panel import MyPanel, MyShaderPanel


bl_info = {
    "name": "批量工具",
    "category": "LTools",
    "author": "Light",
    "blender": (3, 6, 0),
    "location": "UI",
    "description": "批量处理",
    "version": (2, 2)
}


def register():
    bpy.utils.register_class(MyPanel)
    bpy.utils.register_class(MyOperatorCr)
    bpy.utils.register_class(MyOperatorCl)
    bpy.utils.register_class(prop_mat)
    bpy.utils.register_class(MaxResProp)
    bpy.utils.register_class(MaxResSet)
    bpy.utils.register_class(MaxResSetOnlySelect)
    bpy.utils.register_class(MyShaderPanel)
    bpy.utils.register_class(ConvertToJPG)
    bpy.utils.register_class(SelectedOnly_Set)
    bpy.utils.register_class(MaterialInstanceSeparator)
    bpy.types.Scene.matprop = bpy.props.PointerProperty(type=prop_mat)
    bpy.types.Scene.maxres = bpy.props.PointerProperty(type=MaxResProp)


def unregister():
    bpy.utils.unregister_class(MyPanel)
    bpy.utils.unregister_class(MyOperatorCr)
    bpy.utils.unregister_class(MyOperatorCl)
    bpy.utils.unregister_class(prop_mat)
    bpy.utils.unregister_class(MaxResProp)
    bpy.utils.unregister_class(MaxResSet)
    bpy.utils.unregister_class(MaxResSetOnlySelect)
    bpy.utils.unregister_class(MyShaderPanel)
    bpy.utils.unregister_class(ConvertToJPG)
    bpy.utils.unregister_class(SelectedOnly_Set)
    bpy.utils.unregister_class(MaterialInstanceSeparator)
    del bpy.types.Scene.maxres
    del bpy.types.Scene.matprop


if __name__ == "__main__":
    register()
