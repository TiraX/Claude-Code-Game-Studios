"""第三轮：构图、峭壁、动物轮廓、水晶后窗与最终输出。"""
import bpy,math,random,os,ast,json
from mathutils import Vector
from math import sin,cos,pi
OUT=os.path.dirname(os.path.abspath(__file__));random.seed(2618);s=bpy.context.scene
wood=bpy.data.materials['深胡桃木｜顺纹'];wood_edge=bpy.data.materials['雕花木｜磨亮边缘'];gold=bpy.data.materials['黄铜｜陈旧金属'];stone=bpy.data.materials['博物馆暖灰石灰岩'];rockmat=bpy.data.materials['峡谷岩石'];dinoskin=bpy.data.materials['恐龙皮肤'];moss=bpy.data.materials['湿润苔藓'];leafmats=[bpy.data.materials['蕨叶'+str(i)] for i in range(4)];dark=bpy.data.materials['缝隙阴影']
source=ast.parse(open(os.path.join(OUT,'build_museum.py')).read());exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<geometry_helpers>','exec'))
cam=s.camera;cam.data.lens=43;target=Vector((-.45,-.1,4.75));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
# 降低木材的大面积塑料反光，强化木纹频率。
for name in ['深胡桃木｜顺纹','雕花木｜磨亮边缘','抽屉老木面']:
    m=bpy.data.materials[name];p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.49;p.inputs['Specular IOR Level'].default_value=.28
    for n in m.node_tree.nodes:
        if n.type=='TEX_NOISE':n.inputs['Scale'].default_value=7;n.inputs['Detail'].default_value=5
        if n.type=='BUMP':n.inputs['Strength'].default_value=.27;n.inputs['Distance'].default_value=.022
for name,factor in [('鹿毛｜暖棕',.58),('鹿腹浅毛',.7)]:
    m=bpy.data.materials[name]
    for n in m.node_tree.nodes:
        if n.type=='VALTORGB':
            for e in n.color_ramp.elements:e.color=tuple(v*factor for v in e.color[:3])+(1,)
    if name=='鹿腹浅毛':
        p=m.node_tree.nodes.get('Principled BSDF');c=p.inputs['Base Color'].default_value;p.inputs['Base Color'].default_value=tuple(v*factor for v in c[:3])+(1,)
# 连续纵向峡谷峭壁，用不规则截面替代圆形巨石。
COL=bpy.data.collections['03｜恐龙山谷生态箱']
for old in list(s.objects):
    if not old.name.startswith('山谷峭壁'):continue
    center=old.location.copy();sx,sy,sz=old.scale;verts=[];faces=[];rings=9;segments=14
    ridges=[random.uniform(.73,1.19) for i in range(segments)]
    for k in range(rings):
        t=k/(rings-1);rad=(1-.46*t)*(1+.07*sin(t*13));bend=.15*sin(t*5)
        for j in range(segments):
            a=j*2*pi/segments;r=ridges[j]*rad*(1+random.uniform(-.10,.10))
            verts.append((center.x+sx*(cos(a)*r+bend),center.y+sy*sin(a)*r,center.z+sz*(2*t-1)+random.uniform(-.12,.12)*sz))
    for k in range(rings-1):
        for j in range(segments):faces.append((k*segments+j,k*segments+(j+1)%segments,(k+1)*segments+(j+1)%segments,(k+1)*segments+j))
    faces.extend([tuple(reversed(range(segments))),tuple((rings-1)*segments+j for j in range(segments))])
    me=bpy.data.meshes.new('峡谷层理峭壁');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('纵向风化峭壁',me);COL.objects.link(o);me.materials.append(rockmat)
    for p in me.polygons:p.use_smooth=True
    mod=o.modifiers.new('岩面细分','SUBSURF');mod.subdivision_type='SIMPLE';mod.levels=1
    mod=o.modifiers.new('岩面侵蚀','DISPLACE');mod.texture=bpy.data.textures['岩石侵蚀纹理'];mod.strength=.065
    bpy.data.objects.remove(old,do_unlink=True)
# 近景长颈龙改为低头探水的姿态。
old=bpy.data.objects.get('近景长颈龙长颈')
if old:bpy.data.objects.remove(old,do_unlink=True)
def p(x,y,z):return (1.55-x*.83,-1.75+y*.83,1.55+z*.83)
tapered('近景长颈龙长颈',[p(.37,0,1),p(.61,0,.91),p(.83,0,.79),p(1.05,0,.79),p(1.22,0,1.03),p(1.25,0,1.08)],[v*.83 for v in [.26,.23,.18,.13,.105,.09]],dinoskin)
for o in list(s.objects):
    if o.name.startswith('近景长颈龙头') or o.name.startswith('近景长颈龙眼'):o.location.z-=.83
# 将躯干、颈和肢体融合成连续皮肤，眼、角、蹄和背鳞保留独立可编辑。
for prefix in ['近景长颈龙','远景长颈龙','站立雄鹿','卧姿雄鹿']:
    parts=[o for o in s.objects if o.type=='MESH' and o.name.startswith(prefix) and any(part in o.name[len(prefix):] for part in ['躯干','腹部','颈部','长颈','长尾','细腿','收拢腿','腿','脚','头','吻部','短尾']) and '眼' not in o.name]
    if not parts:continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();obj=bpy.context.object;obj.name=prefix+'连续体表'
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    mod=obj.modifiers.new('体表融合','REMESH');mod.mode='VOXEL';mod.voxel_size=.025;mod.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=obj.modifiers.new('柔化肌肉过渡','SMOOTH');mod.factor=.65;mod.iterations=3
    bpy.ops.object.modifier_apply(modifier=mod.name)
    for poly in obj.data.polygons:poly.use_smooth=True
# 晶洞背部的小拱窗，置于柜背前方，保留柜体整体结构。
COL=bpy.data.collections['06｜青蓝水晶岩洞']
wm=emissive('晶洞后窗日光',(.53,.66,.65),.9)
x,y,z,w,h=3.9,2.48,6.33,1.55,1.8
coords=[(-w/2,0),(-w/2,h*.65)]+[(cos(pi-i*pi/16)*w/2,h*.65+sin(pi-i*pi/16)*h*.35) for i in range(17)]+[(w/2,0)]
verts=[(x+u,y,z+v) for u,v in coords];me=bpy.data.meshes.new('晶洞后窗面');me.from_pydata(verts,[],[tuple(range(len(verts)))]);me.update();o=bpy.data.objects.new('晶洞透亮拱窗',me);COL.objects.link(o);me.materials.append(wm)
tube('晶洞后窗石套',[(x+u,y-.04,z+v) for u,v in coords],.065,stone)
for dx in [-.45,0,.45]:beam('晶洞窗竖棂',(x+dx,y-.09,z),(x+dx,y-.09,z+h-.1),.018,wood_edge)
for dz in [.6,1.2]:beam('晶洞窗横棂',(x-w/2,y-.09,z+dz),(x+w/2,y-.09,z+dz),.018,wood_edge)
light('晶洞后窗柔光',(x,2.23,z+.9),(.65,.85,1),70,1.2,(3.7,.5,6.5))
# 恐龙山谷的后方光束增强纵深。
COL=bpy.data.collections['10｜灯光与相机']
light('山谷后侧轮廓光',(-.3,1.95,3.8),(.55,.75,1),170,1.6,(-.8,-1.8,2))
# 可选的细节相机留在文件中，主相机仍作为默认渲染相机。
for name,loc,target,lens in [('细节相机｜双鹿与头骨',(1,-12,8),(-3,0,6.8),54),('细节相机｜恐龙山谷',(5,-11,5),(-.6,-.8,2.5),54)]:
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.lens=lens
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=96;s.render.filepath=os.path.join(OUT,'museum_final.png')
s['迭代版本']='第三轮：完整地面构图、纵向峡谷、连续动物体表、低头恐龙、水晶后窗'
s['范围说明']='完整环境重建；未建模男孩。植物、动物解剖与雕花采用程序化建模，细节与原画仍有差异。'
# 保存面向后续编辑的工作区。
bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'museum_scene.blend'))
stats={'对象数':len(s.objects),'网格数':sum(o.type=='MESH' for o in s.objects),'材质数':len(bpy.data.materials),'集合':[c.name for c in s.collection.children],'渲染器':s.render.engine,'Blender版本':bpy.app.version_string,'最终尺寸':[1920,1080],'最终采样':96}
with open(os.path.join(OUT,'scene_inventory.json'),'w') as f:json.dump(stats,f,ensure_ascii=False,indent=2)
print('最终场景保存完成',stats,flush=True)
bpy.ops.render.render(write_still=True)
