"""对已保存的 v2 输出灰模、灯组及固定局部视图；不保存检查时的临时场景状态。"""
import bpy,os,json
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__));s=bpy.context.scene
try:
    pref=bpy.context.preferences.addons['cycles'].preferences
    pref.compute_device_type='METAL';pref.get_devices()
    for device in pref.devices:device.use=device.type=='METAL'
    if any(device.type=='METAL' for device in pref.devices):s.cycles.device='GPU'
except Exception:
    pass
main=s.camera;energies={o.name:o.data.energy for o in s.objects if o.type=='LIGHT'}
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=50;s.cycles.samples=32
# 灯组检查保留发光材质，因此不是严格的光路贡献分解。
for group in ['窗光','局部展品','灯具','弱填充']:
    for name,e in energies.items():
        o=bpy.data.objects[name];o.data.energy=e if o.get('v2灯组')==group else 0
    s.render.filepath=os.path.join(OUT,'check_light_'+{'窗光':'window','局部展品':'exhibits','灯具':'practicals','弱填充':'fill'}[group]+'.png')
    print('检查灯组：',group,flush=True);bpy.ops.render.render(write_still=True)
for name,e in energies.items():bpy.data.objects[name].data.energy=e
# 灰模时关闭体积容器，防止材质覆盖把空气体积变成不透明盒子。
clay=bpy.data.materials.new('检查用中性灰');clay.use_nodes=True;p=clay.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.4,.4,.4,1);p.inputs['Roughness'].default_value=.8
vol=bpy.data.objects.get('v2后峡局部空气');hidden=vol.hide_render if vol else None
if vol:vol.hide_render=True
s.view_layers[0].material_override=clay;s.render.resolution_percentage=75;s.render.filepath=os.path.join(OUT,'check_clay.png');bpy.ops.render.render(write_still=True)
s.view_layers[0].material_override=None
if vol:vol.hide_render=hidden
# 局部图片均由三维场景直接渲染，无图像后期拼接。
data=bpy.data.cameras.new('临时检查相机');cam=bpy.data.objects.new('临时检查相机',data);s.collection.objects.link(cam);s.camera=cam;data.lens=50
s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=64
views=[('rock',(-.7,-4.9,3.7),(-3.25,-.2,2.65),49),('skull',(1.8,-4.1,7.8),(.08,.45,7.22),55),('wood',(.3,-5.75,1.8),(-.65,-3.43,.91),48)]
# 从实际前景蕨叶边界选择示范植株，避免拍到空地。
ferns=[]
for o in s.objects:
    if o.name.startswith('v2羽状蕨叶'):
        pts=[o.matrix_world@Vector(p) for p in o.bound_box];center=sum(pts,Vector())/8
        if center.z<2.3 and center.y<-1.7:ferns.append((abs(center.x+2.5)+abs(center.y+2.4),center))
if ferns:
    center=min(ferns,key=lambda p:p[0])[1];views.append(('fern',center+Vector((.65,-1.4,1.2)),center,55))
for name,loc,target,lens in views:
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;s.render.filepath=os.path.join(OUT,'detail_'+name+'.png')
    print('检查局部：',name,flush=True);bpy.ops.render.render(write_still=True)
print('检查图完成，原场景未保存修改',flush=True)
