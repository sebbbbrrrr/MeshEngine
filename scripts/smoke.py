import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector
out = Path("build").resolve()
out.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.001
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=20, depth=12, location=(0,0,6))
obj = bpy.context.object
obj.name = "Generic test cylinder"
mod = obj.modifiers.new("Edge finish", "BEVEL")
mod.width = 1
mod.segments = 3
bpy.ops.object.modifier_apply(modifier=mod.name)
bm = bmesh.new()
bm.from_mesh(obj.data)
bad = sum(not e.is_manifold for e in bm.edges)
volume = bm.calc_volume(signed=True)
bm.free()
assert bad == 0 and volume > 0
assert abs(obj.dimensions.x-40) < .01 and abs(obj.dimensions.z-12) < .01
bpy.ops.wm.stl_export(filepath=str(out/"fixture.stl"), export_selected_objects=True)
assert (out/"fixture.stl").stat().st_size > 84
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.resolution_percentage = 100
scene.world = bpy.data.worlds.new("Studio")
scene.world.color = (.35,.35,.35)
def aim(o, point):
    o.rotation_euler = (Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
for pos,power in [((60,-70,100),1800000),((-60,30,70),1000000)]:
    bpy.ops.object.light_add(type='AREA', location=pos)
    light=bpy.context.object
    light.data.energy=power
    light.data.shape='DISK'
    light.data.size=60
    aim(light,(0,0,6))
bpy.ops.object.camera_add()
cam=bpy.context.object
scene.camera=cam
cam.data.type='ORTHO'
cam.data.ortho_scale=60
for name,pos in [('front',(0,-100,45)),('side',(100,0,45)),('rear',(0,100,45)),('perspective',(75,-90,75))]:
    cam.location=pos
    aim(cam,(0,0,6))
    scene.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/"fixture.blend"))
(out/"report.json").write_text(json.dumps({"fixture":"generic cylinder","nonmanifold_edges":bad,"volume_mm3":volume,"dimensions_mm":list(obj.dimensions),"physical_test":False,"slicer_test":False},indent=2))
