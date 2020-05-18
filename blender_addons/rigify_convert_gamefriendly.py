import bpy
from mathutils import Vector


bl_info = {
    "name": "Rigify - Make Game Friendly",
    "author": "Paolo Acampora",
    "version": (1, 01),
    "blender": (2, 8, 0),
    "location": "Armature properties",
    "description": "Brings the DEF- bones of rigify 0.5 rigs into a single, game friendly hierarchy",
    "category": "Rigging",
    }


def copy_bone_constraints(bone_a, bone_b):
    """Copy all bone constraints from bone_A to bone_b and sets their writable attributes.
       Doesn't delete constraints that already exist
    """
    for constr_a in bone_a.constraints:
        constr_b = bone_b.constraints.new(constr_a.type)

        for c_attr in dir(constr_b):
            if c_attr.startswith("_"):
                continue
            try:
                setattr(constr_b, c_attr, getattr(constr_a, c_attr))
            except AttributeError:
                continue


def copy_bone(obj, bone_name, assign_name='', constraints=False):
    """ Makes a copy of the given bone in the given armature object.
        Returns the resulting bone's name.

        NOTE: taken from rigify module utils.py, added the contraints option and stripped the part about rna properties
    """
    if bone_name not in obj.data.edit_bones:
        raise Exception("copy_bone(): bone '%s' not found, cannot copy it" % bone_name)

    if obj == bpy.context.active_object and bpy.context.mode == 'EDIT_ARMATURE':
        if assign_name == '':
            assign_name = bone_name
        # Copy the edit bone
        edit_bone_1 = obj.data.edit_bones[bone_name]
        edit_bone_2 = obj.data.edit_bones.new(assign_name)
        bone_name_1 = bone_name
        bone_name_2 = edit_bone_2.name

        edit_bone_2.parent = edit_bone_1.parent
        edit_bone_2.use_connect = edit_bone_1.use_connect

        # Copy edit bone attributes
        edit_bone_2.layers = list(edit_bone_1.layers)

        edit_bone_2.head = Vector(edit_bone_1.head)
        edit_bone_2.tail = Vector(edit_bone_1.tail)
        edit_bone_2.roll = edit_bone_1.roll

        edit_bone_2.use_inherit_rotation = edit_bone_1.use_inherit_rotation
        edit_bone_2.use_inherit_scale = edit_bone_1.use_inherit_scale
        edit_bone_2.use_local_location = edit_bone_1.use_local_location

        edit_bone_2.use_deform = edit_bone_1.use_deform
        edit_bone_2.bbone_segments = edit_bone_1.bbone_segments
        edit_bone_2.bbone_custom_handle_start = edit_bone_1.bbone_custom_handle_start
        edit_bone_2.bbone_custom_handle_end = edit_bone_1.bbone_custom_handle_end

        bpy.ops.object.mode_set(mode='OBJECT')

        # Get the pose bones
        pose_bone_1 = obj.pose.bones[bone_name_1]
        pose_bone_2 = obj.pose.bones[bone_name_2]

        # Copy pose bone attributes
        pose_bone_2.rotation_mode = pose_bone_1.rotation_mode
        pose_bone_2.rotation_axis_angle = tuple(pose_bone_1.rotation_axis_angle)
        pose_bone_2.rotation_euler = tuple(pose_bone_1.rotation_euler)
        pose_bone_2.rotation_quaternion = tuple(pose_bone_1.rotation_quaternion)

        pose_bone_2.lock_location = tuple(pose_bone_1.lock_location)
        pose_bone_2.lock_scale = tuple(pose_bone_1.lock_scale)
        pose_bone_2.lock_rotation = tuple(pose_bone_1.lock_rotation)
        pose_bone_2.lock_rotation_w = pose_bone_1.lock_rotation_w
        pose_bone_2.lock_rotations_4d = pose_bone_1.lock_rotations_4d

        if constraints:
            copy_bone_constraints(pose_bone_1, pose_bone_2)

        return bone_name_2
    else:
        raise Exception("Cannot copy bones outside of edit mode")


def remove_bone_constraints(pbone):
    for constr in pbone.constraints:
        pbone.constraints.remove(constr)


def remove_all_bone_constraints(ob):
    for pbone in ob.pose.bones:
        remove_bone_constraints(pbone)


def get_armature_bone(ob, bone_name):
    """Return the Armature Bone with given bone_name, None if not found"""
    return ob.data.bones.get(bone_name, None)


def get_edit_bone(ob, bone_name):
    """Return the Edit Bone with given bone name, None if not found"""
    return ob.data.edit_bones.get(bone_name, None)


def is_def_bone(ob, bone_name):
    """Return True if the bone with given name is a deforming bone,
       False if it isn't, None if the bone is not found"""
    bone = get_armature_bone(ob, bone_name)

    if not bone:
        return

    return bone.use_deform


def find_def_parent(ob, org_bone):
    """Return the first DEF- bone that is suitable as parent bone of given ORG- bone"""
    org_par = org_bone.parent
    if not org_par:
        return

    if org_par.name.startswith("MCH-"):  # MCH bones risk to be named after the bone we have started with
        return find_def_parent(ob, org_par)

    par_def_name = "DEF-{0}".format(org_par.name[4:])
    try:
        par_def = ob.pose.bones[par_def_name]
        return par_def
    except KeyError:
        return find_def_parent(ob, org_par)


def gamefriendly_hierarchy(ob):
    """Changes Rigify (0.5) rigs to a single root deformation hierarchy.
    Create ITD- (InTermeDiate) bones in the process"""
    assert(ob.mode == 'EDIT')

    pbones = list(ob.pose.bones)  # a list of pose bones is safer when switching through modes
    new_bone_names = []  # collect newly added bone names so that they can be edited later in Object Mode

    # we want deforming bone (i.e. the ones on layer 29) to have deforming bone parents
    for pbone in pbones:
        bone_name = pbone.name

        if not is_def_bone(ob, bone_name):
            continue
        if not pbone.parent:
            # root bones are fine
            continue
        if is_def_bone(ob, pbone.parent.name):
            continue
        if not bone_name.startswith("DEF-"):
            # we are only dealing with Rigify DEF- bones so far
            print("WARNING: {0}, not supported for Game Friendly Conversion".format(bone_name))
            continue

        # Intermediate Bone
        itd_name = copy_bone(ob, bone_name, assign_name=bone_name.replace("DEF-", "ITD-"), constraints=True)
        new_bone_names.append(itd_name)

        itd_bone = ob.data.bones[itd_name]
        itd_bone.use_deform = False

        # ITD- bones go to MCH layer
        itd_bone.layers[30] = True
        itd_bone.layers[31] = False
        for i in range(30):
            itd_bone.layers[i] = False

        bpy.ops.object.mode_set(mode='EDIT')  # bone copy has set Object Mode

        # DEF- bone will now follow the ITD- bone
        remove_bone_constraints(pbone)
        cp_trans = pbone.constraints.new('COPY_TRANSFORMS')
        cp_trans.target = ob
        cp_trans.subtarget = itd_name

        # Look for a DEF- bone that would be a good parent. Unlike DEF- bones, ORG- bones retain the
        # hierarchy from the metarig, so we are going to reproduce the ORG- hierarchy
        org_name = "ORG-{0}".format(bone_name[4:])

        try:
            org_bone = ob.pose.bones[org_name]
        except KeyError:
            print("WARNING: 'ORG-' bone not found ({0})", org_name)
            continue
        else:
            def_par = find_def_parent(ob, org_bone)
            if not def_par:
                print("WARNING: Parent not found for {0}".format(bone_name))
                # as a last resort, look for a DEF- bone with the same name but a lower number
                # (i.e. try to parent DEF-tongue.002 to DEF-tongue.001)
                if bone_name[-4] == "." and bone_name[-3:].is_digit():
                    bname, number = bone_name.rsplit(".")
                    number = int(number)
                    if number > 1:
                        def_par_name = "{0}.{1:03d}".format(bname, number - 1)
                        print("Trying to use {0}".format(def_par_name))
                        try:
                            def_par = ob.pose.bones[def_par_name]
                        except KeyError:
                            print("No suitable DEF- parent for {0}".format(bone_name))
                            continue
                    else:
                        continue
                else:
                    continue

        ebone = get_edit_bone(ob, bone_name)
        ebone_par = get_edit_bone(ob, def_par.name)
        ebone.parent = ebone_par


class ConvertGameFriendly(bpy.types.Operator):
    """Convert Rigify (0.5) rigs to a Game Friendly hierarchy"""
    bl_idname = "armature.rigify_convert_gamefriendly"
    bl_label = "Make the rigify deformation bones a one root rig"

    keep_backup = bpy.props.BoolProperty("Keep copy of datablock", default=True)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if not obj:
            return False
        if obj.mode != 'EDIT':
            return False
        if obj.type != 'ARMATURE':
            return False
        return bool(context.active_object.data.get("rig_id"))

    def execute(self, context):
        ob = context.active_object
        if self.keep_backup:
            backup_data = ob.data.copy()
            backup_data.name = ob.name + "_GameUnfriendly_backup"
            backup_data.use_fake_user = True

        gamefriendly_hierarchy(ob)
        return {'FINISHED'}


class DATA_PT_rigify_makefriendly(bpy.types.Panel):
    bl_label = "Rigify Games"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.object.type == 'ARMATURE' and bool(context.active_object.data.get("rig_id"))

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj.mode == 'EDIT':
            pass

        row = layout.row()
        props = layout.operator("armature.rigify_convert_gamefriendly", text="Make Game Friendly")


def register():
    bpy.utils.register_class(ConvertGameFriendly)
    bpy.utils.register_class(DATA_PT_rigify_makefriendly)


def unregister():
    bpy.utils.unregister_class(ConvertGameFriendly)
    bpy.utils.unregister_class(DATA_PT_rigify_makefriendly)


if __name__ == "__main__":
    register()
