import math
import json
import bpy
from mathutils import Vector



def export_spline(spline, outpath, data, scale=100):
    for i, point in enumerate(spline.bezier_points):
        inTan = (point.co - point.handle_left) * 3
        outTan = (point.handle_right - point.co) * 3
        
        data.append({
            'Name': "point_{0:03}".format(i),
            'Xpos': point.co.x * -scale,
            'Ypos': point.co.y * scale,
            'Zpos': point.co.z * scale,
            'XinTan': inTan.x * -scale,
            'YinTan': inTan.y * scale,
            'ZinTan': inTan.z * scale,
            'XoutTan': outTan.x * -scale,
            'YoutTan': outTan.y * scale,
            'ZoutTan': outTan.z * scale,
            'Xtilt': math.degrees(point.tilt)
        })
                

def export_curve(object, outpath):
    assert object.type == 'CURVE'
    
    data = []
    for spline in object.data.splines:
        export_spline(spline, outpath, data)
        break  # TODO; multiple splines

    with open(outpath, 'w') as outfile:
        json.dump(data, outfile, indent=4)     



class ExportCurveData(bpy.types.Operator):
    """Save Curve Points to file"""
    bl_idname = "object.export_curve_data"
    bl_label = "Export Curve Data"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'CURVE'

    def execute(self, context):
        outpath = bpy.path.abspath('//{0}.json'.format(context.object.name))
        export_curve(context.object, outpath)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ExportCurveData)


def unregister():
    bpy.utils.unregister_class(ExportCurveData)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.export_curve_data()
