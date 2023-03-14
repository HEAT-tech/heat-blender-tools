import bpy
import random
import math
from bpy import context


# Deselect all objects
# Get the armature named "T69H" if it exists
# Deselect all objects


# Select all objects except armature named 'T69H'
for obj in bpy.context.scene.objects:
    if obj.type != 'ARMATURE' and not obj.name.startswith('T69H'):
        obj.select_set(True)

# Delete selected objects
bpy.ops.object.delete(use_global=False)

bpy.context.scene.eevee.use_bloom = True


scene = context.scene

num_shapes = 50
shape_size = random.uniform(0.01, 0.05)
shape_types = ['CUBE', 'UV_SPHERE', 'MONKEY']
light_types = ['POINT']
mats = bpy.data.materials


def scene_setup():

    bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=(
        0, -5.39, 0.95), rotation=(1.570796, 0.0, 0.0), scale=(1, 1, 1))


def create_gradient_background():
    bpy.ops.import_scene.gltf(filepath="D:\\HEAT\\Backdrop.glb", files=[
                              {"name": "Backdrop.glb", "name": "Backdrop.glb"}], loglevel=50)

    mat = mats.new("Gradient")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    nodes.new(type="ShaderNodeValToRGB")
    color_ramp = nodes['ColorRamp']

    gradient = nodes.new(type="ShaderNodeTexGradient")
    diffuse_bdsf = nodes.get("Principled BSDF")

    mat.node_tree.links.new(gradient.outputs[0], color_ramp.inputs[0])
    mat.node_tree.links.new(color_ramp.outputs[0], diffuse_bdsf.inputs[0])

    color_ramp.color_ramp.elements.new(1)
    color_ramp.color_ramp.elements[0].color = (
        random.random(), random.random(), random.random(), 1.0)
    color_ramp.color_ramp.elements[1].color = (
        random.random(), random.random(), random.random(), 1.0)
    color_ramp.color_ramp.elements[2].color = (
        random.random(), random.random(), random.random(), 1.0)

    bpy.context.object.active_material = mat


def create_shapes():

    #    empty = bpy.data.objects.new("Background", None)
    #    bpy.context.scene.collection.objects.link(empty)

    for i in range(num_shapes):
        shape_type = random.choice(shape_types)
        x = random.uniform(-2, 2)
        y = random.uniform(-1.5, 0)
        z = random.uniform(0, 2)

        # Check distance to center of scene
        while math.sqrt(x**2 + y**2 + z**2) < 2:
            x = random.uniform(-2, 2)
            y = random.uniform(-1.5, 0)
            z = random.uniform(0, 2)

        bpy.ops.mesh.__getattr__(
            "primitive_" + shape_type.lower() + "_add")(location=(x, y, z), rotation=(random.random(), random.random(), random.random()))
        bpy.context.object.name = "Shape{}".format(i+1)

        if shape_type == 'UV_SPHERE':
            random_scale = random.uniform(0.05, 0.1)
            bpy.context.object.scale = (
                random_scale, random_scale, random_scale)
        else:
            bpy.context.object.scale = (shape_size, shape_size, shape_size)

        # Add bevel to shape
        bpy.ops.object.modifier_add(type='BEVEL')
        bpy.context.object.modifiers["Bevel"].offset_type = 'PERCENT'
        bpy.context.object.modifiers["Bevel"].width_pct = 1
        bpy.context.object.modifiers["Bevel"].segments = 3
        bpy.context.object.modifiers["Bevel"].profile = 0.75

        # Add color to shape
        red = random.random()
        green = random.random()
        blue = random.random()
        alpha = 1.0
        color = (red, green, blue, alpha)
        mat = mats.new("Material")
        mat.diffuse_color = color
        bpy.context.object.active_material = mat


def create_lights():
    for i in range(3):
        light_type = random.choice(light_types)
        x = random.uniform(-1, 1)
        y = random.uniform(-2.3, 1.3)
        z = random.uniform(1, 2)

        if light_type == 'POINT':
            bpy.ops.object.light_add(type='POINT', location=(x, y, z))
        elif light_type == 'SUN':
            bpy.ops.object.light_add(type='SUN', location=(x, y, z))
        elif light_type == 'SPOT':
            bpy.ops.object.light_add(type='SPOT', location=(x, y, z))

        bpy.context.object.name = "Light{}".format(i+1)

        # Set light energy
        bpy.context.object.data.energy = random.uniform(110.0, 150.0)

        red = random.random()
        green = random.random()
        blue = random.random()
        bpy.context.object.data.color = (red, green, blue)


scene_setup()
create_gradient_background()
create_shapes()
create_lights()

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.shade_smooth()

camera_obj = bpy.data.objects['Camera']  # Replace with your camera object name
bpy.context.scene.camera = camera_obj
# set the viewport camera
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        space_data = area.spaces.active
        space_data.overlay.show_extras = False
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.region_3d.view_perspective = 'CAMERA'


bpy.ops.object.select_all(action='DESELECT')
