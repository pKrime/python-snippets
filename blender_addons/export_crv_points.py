bl_info = {
    "name": "Export Curve Data",
    "author": "Paolo Acampora",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "File > Export",
    "description": "Export curve data as json",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

import os
import math
import json
import bpy
from mathutils import Vector


def export_spline(spline, data, scale=100):
    for i, point in enumerate(spline.bezier_points):
        in_tan = (point.co - point.handle_left) * 3
        out_tan = (point.handle_right - point.co) * 3
        
        data.append({
            'Name': "point_{0:03}".format(i),
            'Xpos': point.co.x * -scale,
            'Ypos': point.co.y * scale,
            'Zpos': point.co.z * scale,
            'XinTan': in_tan.x * -scale,
            'YinTan': in_tan.y * scale,
            'ZinTan': in_tan.z * scale,
            'XoutTan': out_tan.x * -scale,
            'YoutTan': out_tan.y * scale,
            'ZoutTan': out_tan.z * scale,
            'Xtilt': math.degrees(point.tilt)
        })


def available_extensions(self, context):
    return [
        (".json", ".json", ".json"),
        (".csv", ".csv", ".csv")
    ]


def set_output_extension(self, context):
    """Change output extension with current extension value"""
    out_file, _ = os.path.splitext(self.output_path)
    self.output_path = "{0}{1}".format(out_file, self.output_ext)


def set_output_default(self, context):
    """Set output path to current scene path + objec_name + extension"""
    self.output_path = bpy.path.abspath('//{0}{1}'.format(context.object.name, self.output_ext))


class ExportCurveData(bpy.types.Operator):
    """Save Curve Points to file"""
    bl_idname = "object.export_curve_data"
    bl_label = "Export Curve Data"

    output_path: bpy.props.StringProperty(name="output", description="output file", default="")
    output_ext: bpy.props.EnumProperty(name="extension", description="output file format", items=available_extensions,
                                       update=set_output_extension)
    scale_prop: bpy.props.FloatProperty(name="scale",
                                        description="scale transform for curve coordinates (100 for Unreal)",
                                        default=100.0, min=0.1)

    def export_curve(self, crv_object, outpath):
        assert crv_object.type == 'CURVE'

        data = []
        for spline in crv_object.data.splines:
            export_spline(spline, data, scale=self.scale_prop)
            break  # TODO; multiple splines

        if self.output_ext == ".json":
            with open(outpath, 'w') as outfile:
                json.dump(data, outfile, indent=4)
        else:
            raise NotImplementedError

    @classmethod
    def poll(cls, context):
        if context.active_object is None:
            return False
        if context.active_object.type != 'CURVE':
            return False
        if not context.active_object.data.splines:
            return False
        if not context.active_object.data.splines[0].bezier_points:
            return False

        return True

    def execute(self, context):
        output_path = self.output_path
        if not output_path.endswith(self.output_ext):
            output_path += self.output_ext

        self.export_curve(context.object, self.output_path)
        return {'FINISHED'}

    def invoke(self, context, event):
        set_output_default(self, context)
        return context.window_manager.invoke_props_dialog(self)


def menu_func_export(self, context):
    self.layout.operator(ExportCurveData.bl_idname)


def register():
    bpy.utils.register_class(ExportCurveData)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportCurveData)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.export_curve_data()
