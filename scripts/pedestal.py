# Standalone Blender fixture; coordinates are millimetres.
import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector
out=Path("build/pedestal").resolve()
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=.001
# Continuous closed surface: layered octagonal plinth with recessed gothic arch relief.
profile=[(0,39),(.8,40),(3,40),(4,38),(5,38),(6,34),(8,34),(9,32),(19,32),(20,34),(21,34),(22,39),(24,40),(25,39)]
# Sample each flat octagonal side to sculpt inset arch panels.
levels=sorted(set([z for z,r in profile]+[9+i*.25 for i in range(41)]))
def radius(z):
    for (a,r),(b,s) in zip(profile,profile[1:]):
        if a<=z<=b:return r+(s-r)*(z-a)/(b-a)
    return profile[-1][1]
N=8*24
v=[]
for z in levels:
    for i in range(N):
        side,j=divmod(i,24); t=j/24
        a=side*math.pi/4; b=a+math.pi/4
        r=radius(z)
        x=r*((1-t)*math.cos(a)+t*math.cos(b)); y=r*((1-t)*math.sin(a)+t*math.sin(b))
        u=abs(t-.5)
        top=18-12*u
        if 9<z<19:
            depth=1.3*max(0,min(1,(z-10)*2,(top-z)*2,(.32-u)*20))
            x-=depth*math.cos((a+b)/2); y-=depth*math.sin((a+b)/2)
        v.append((x,y,z))
f=[tuple(reversed(range(N)))]
for k in range(len(levels)-1):
    for i in range(N):
        j=(i+1)%N
        f.append((k*N+i,k*N+j,(k+1)*N+j,(k+1)*N+i))
f.append(tuple(range((len(levels)-1)*N,len(levels)*N)))
mesh=bpy.data.meshes.new("Pedestal geometry"); mesh.from_pydata(v,[],f); mesh.update()
obj=bpy.data.objects.new("Generic gothic pedestal",mesh); scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active=obj; obj.select_set(True)
bm=bmesh.new(); bm.from_mesh(mesh)
bad=sum(not e.is_manifold for e in bm.edges); volume=bm.calc_volume(signed=True); bm.free()
assert bad==0 and volume>0
assert all(abs(a-b)<.01 for a,b in zip(obj.dimensions,(80,80,25)))
bpy.ops.wm.stl_export(filepath=str(out/"pedestal.stl"),export_selected_objects=True)
scene.render.engine='CYCLES'; scene.cycles.samples=16; scene.cycles.device='CPU'
scene.render.resolution_x=512; scene.render.resolution_y=512; scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new("Studio"); scene.world.use_nodes=True
scene.world.node_tree.nodes.get("Background").inputs[0].default_value=(.18,.18,.18,1)
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for p,e in [((90,-100,130),150000),((-90,45,90),80000)]:
    bpy.ops.object.light_add(type='AREA',location=p); l=bpy.context.object;l.data.energy=e;l.data.size=90;aim(l,(0,0,12))
bpy.ops.object.camera_add(); cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=110
for name,p in [('front',(0,-150,55)),('side',(150,0,55)),('rear',(0,150,55)),('perspective',(100,-150,100))]:
    cam.location=p;aim(cam,(0,0,12));scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/"pedestal.blend"))
(out/"report.json").write_text(json.dumps({"dimensions_mm":list(obj.dimensions),"nonmanifold_edges":bad,"volume_mm3":volume,"physical_test":False,"slicer_test":False},indent=2))
