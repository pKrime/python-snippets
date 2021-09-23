# ====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation, version 3.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ======================= END GPL LICENSE BLOCK ========================

bl_info = {
    "name": "Die Über Noiser",
    "version": (0, 0, 1),
    "author": "Paolo Acampora",
    "blender": (2, 90, 0),
    "description": "Adds Noise on objects/bones",
    "category": "Object",
}


import bpy
from bpy.props import FloatProperty
from bpy.props import IntProperty


class DieUberNoiser(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.die_ubernoiser"
    bl_label = "Die Über Noiser"
    bl_options = {'REGISTER', 'UNDO'}

    noise_scale: FloatProperty(name="Scale", description="Noise Scale", default=1.0)
    noise_strength: FloatProperty(name="Strength", description="Noise Strength", default=1.0)
    noise_offset: FloatProperty(name="Offset", description="Noise Offset", default=1.0)
    noise_phase: FloatProperty(name="Phase", description="Noise Phase", default=1.0)
    noise_depth: IntProperty(name="Depth", description="Noise Depth", default=0, min=0)

    _vars_registered_ = False
    _allowed_modes_ = ['POSE', 'OBJECT']
    _bone_names_ = []

    @classmethod
    def poll(cls, context):
        if context.mode not in cls._allowed_modes_:
            return False

        return context.active_object is not None

    def execute(self, context):
        if context.mode == 'POSE':
            self._bone_names_ = list([b.name for b in context.selected_pose_bones])
            self.add_noise_ani(context.active_object)
        else:
            for ob in context.selected_objects:
                self.add_noise_ani(ob)

        return {'FINISHED'}

    def add_noise_ani(self, ob):
        anim_data = ob.animation_data

        if not anim_data:
            return
        action = anim_data.action
        if not action:
            return
        if not action.fcurves:
            # TODO: perhaps add fcurves in the future
            return

        for fcurve in action.fcurves:
            data_path = fcurve.data_path
            p_bone_prefix = 'pose.bones['
            if self._bone_names_:
                # process only curves of selected bones
                if not data_path.startswith(p_bone_prefix):
                    continue

                bone_name = data_path[len(p_bone_prefix):].rsplit('"]', 1)[0].strip('"[')
                if bone_name not in self._bone_names_:
                    continue
            else:
                # don't process bone curves
                if data_path.startswith(p_bone_prefix):
                    continue

            try:
                noise_mod = next(mod for mod in fcurve.modifiers if mod.type == 'NOISE')
            except StopIteration:
                noise_mod = fcurve.modifiers.new('NOISE')
            else:
                if not self._vars_registered_:
                    self.noise_scale = noise_mod.scale
                    self.noise_strength = noise_mod.strength
                    self.noise_offset = noise_mod.offset
                    self.noise_phase = noise_mod.phase
                    self.noise_depth = noise_mod.depth
                    self._vars_registered_ = True

            noise_mod.scale = self.noise_scale
            noise_mod.strength = self.noise_strength
            noise_mod.offset = self.noise_offset
            noise_mod.phase = self.noise_phase
            noise_mod.depth = self.noise_depth



def menu_header(layout):
    row = layout.row()
    row.separator()

    row = layout.row()
    row.label(text="Uber Noiser", icon='MOD_NOISE')


def noiser_menu(self, context):
    layout = self.layout
    menu_header(layout)

    row = layout.row()
    row.operator(DieUberNoiser.bl_idname)


def register():
    bpy.utils.register_class(DieUberNoiser)
    bpy.types.VIEW3D_MT_pose_context_menu.append(noiser_menu)
    bpy.types.VIEW3D_MT_object_context_menu.append(noiser_menu)


def unregister():
    bpy.utils.unregister_class(DieUberNoiser)
    bpy.types.VIEW3D_MT_pose_context_menu.remove(noiser_menu)
    bpy.types.VIEW3D_MT_object_context_menu.remove(noiser_menu)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.die_ubernoiser()
