"""首轮成图反馈：缩放异常、地形封口、岩壁体量及植物覆盖。仅对首轮 v2 执行一次。"""
import bpy,math,random,os,ast,json
from mathutils import Vector,Matrix
from math import sin,cos,pi
OUT=os.path.dirname(os.path.abspath(__file__));BASE=os.path.dirname(OUT);random.seed(91727);s=bpy.context.scene
wood=bpy.data.materials['深胡桃木｜顺纹'];wood_edge=bpy.data.materials['雕花木｜磨亮边缘'];wood_light=bpy.data.materials['抽屉老木面'];gold=bpy.data.materials['黄铜｜陈旧金属'];stone=bpy.data.materials['博物馆暖灰石灰岩'];dark=bpy.data.materials['缝隙阴影'];rockmat=bpy.data.materials['v2｜沉积岩断面'];moss=bpy.data.materials['v2｜石隙苔藓'];earth=bpy.data.materials['v2｜腐殖土与湿岸'];bone=bpy.data.materials['古旧象牙骨质'];leafmats=[bpy.data.materials['v2｜蕨叶'+str(i)] for i in range(4)];glass=bpy.data.materials['透明展示玻璃']
for filename in [os.path.join(BASE,'build_museum.py'),os.path.join(OUT,'build_v2.py')]:
    source=ast.parse(open(filename).read());exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<复用几何>','exec'))
remove_names(['站立雄鹿v2眼眶高光','卧姿雄鹿v2眼眶高光'])
# 所有地形边界补侧壁，与木柜底层接合。
def skirt(name,base):
    o=bpy.data.objects[name];edges={}
    for p in o.data.polygons:
        ids=list(p.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):key=tuple(sorted((a,b)));edges[key]=edges.get(key,0)+1
    verts=[];faces=[]
    for (a,b),count in edges.items():
        if count!=1:continue
        p=o.data.vertices[a].co.copy();q=o.data.vertices[b].co.copy();k=len(verts);verts.extend([p,q,(q.x,q.y,base),(p.x,p.y,base)]);faces.append((k,k+1,k+2,k+3))
    mesh_obj(name+'地层封边',verts,faces,earth)
use('03｜恐龙山谷生态箱');skirt('v2山谷连续河床',1.07)
use('04｜双鹿森林生态箱');skirt('v2森林腐殖地形',5.40)
# 太平的森林地表补斑块苔藓，仍保持地形高差。
for objname in ['v2山谷连续河床','v2森林腐殖地形']:
    ob=bpy.data.objects[objname];ob.data.materials.append(moss)
    for p in ob.data.polygons:
        c=p.center
        if sin(c.x*5+c.y*2.1)+cos(c.y*7.2-c.x)>.18 and (objname.startswith('v2森林') or abs(c.x-river_center(c.y))>river_width(c.y)+.17):p.material_index=1
# 巨崖脚部连成坡面，消除独立尖柱感。
use('03｜恐龙山谷生态箱')
for i,(x,y,w,h) in enumerate([(-3.55,-.35,1.05,1.50),(-3.1,1.6,.80,1.20),(2.42,.55,.86,1.30),(2.1,2.5,.80,1.55),(-2.0,4.9,.75,1.15)]):cliff('v2峡谷崩积坡',x,y,1.48,w,.83,h,2100+i)
# 中层已有人为断面；细分位移只负责小尺度风化。
tex=bpy.data.textures.new('v2岩面细风化',type='CLOUDS');tex.noise_scale=.22;tex.noise_depth=2
for o in list(s.objects):
    if o.type!='MESH' or '附生苔藓' in o.name:continue
    if o.name.startswith(('v2峡谷断层主崖','v2峡谷崩积坡','v2层理碎岩','v2森林风化基岩','v2晶洞层岩')):
        cx=sum(v.co.x for v in o.data.vertices)/len(o.data.vertices)
        if o.name.startswith('v2峡谷断层主崖'):
            for v in o.data.vertices:v.co.x=cx+(v.co.x-cx)*1.10
        for p in o.data.polygons:p.use_smooth=True
        sub=o.modifiers.new('风化采样细分','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=2
        dis=o.modifiers.new('细尺度石面侵蚀','DISPLACE');dis.texture=tex;dis.texture_coords='GLOBAL';dis.strength=.045
# 苔藓附着方式改为材质随位置与坡向分布，清除旧悬浮三角补片。
for o in list(s.objects):
    if '附生苔藓' in o.name:bpy.data.objects.remove(o,do_unlink=True)
n=rockmat.node_tree.nodes;l=rockmat.node_tree.links;p=shader(rockmat);previous=p.inputs['Base Color'].links[0].from_socket
geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Normal'],sep.inputs[0]);no=n.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=3.5;no.inputs['Detail'].default_value=3;l.new(geo.outputs['Position'],no.inputs['Vector'])
mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(no.outputs['Fac'],mul.inputs[0]);l.new(sep.outputs['Z'],mul.inputs[1]);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.04;r.color_ramp.elements[1].position=.30;l.new(mul.outputs[0],r.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';l.new(r.outputs[0],mix.inputs[0]);l.new(previous,mix.inputs[1]);mix.inputs[2].default_value=(.07,.105,.016,1);l.new(mix.outputs[0],p.inputs['Base Color'])
# 大株蕨类落在实际地形上，前景带出羽片轮廓。
use('03｜恐龙山谷生态箱')
for i in range(55):
    x=random.uniform(-4.0,2.8);y=random.uniform(-2.95,2.5)
    if abs(x-river_center(y))<river_width(y)+.3:continue
    if (x-1.55)**2+(y+1.75)**2<.65:continue
    fern_v2(x,y,terrain_z(x,y),random.uniform(.52,.88),2300+i)
# 贴附岩面的垂藤、苔叶，最近点查询确保不悬空。
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();verts=[];faces=[]
cliffs=[o for o in COL.objects if o.name.startswith('v2峡谷断层主崖')]
for ii,o in enumerate(cliffs[:4]):
    ev=o.evaluated_get(deps);bounds=[o.matrix_world@Vector(v) for v in o.bound_box];xmin=min(v.x for v in bounds);xmax=max(v.x for v in bounds);zmin=min(v.z for v in bounds);zmax=max(v.z for v in bounds);ymin=min(v.y for v in bounds)
    for j in range(5):
        xx=xmin+(xmax-xmin)*(j+.5)/5;path=[]
        for k in range(13):
            zz=zmax-.20-(zmax-zmin)*.70*k/12;ok,hit,normal,idx=ev.closest_point_on_mesh(Vector((xx+.08*sin(k),ymin-.5,zz)))
            if not ok:continue
            pos=hit+normal*.02;path.append(pos)
            for side in [-1,1]:
                q=pos+Vector((side*.045,0,-.015));u=Vector((.06,0,.025));v=Vector((0,-.025,.032));base=len(verts);verts.extend([q-u,q-v,q+u,q+v]);faces.append((base,base+1,base+2,base+3))
        if len(path)>1:tube('v2岩面贴附垂藤',path,.008,leafmats[0])
mesh_obj('v2岩面垂藤叶片',verts,faces,leafmats[1],True)
# 连续低矮远峰，建立地平线而不是远处石柱。
for o in list(COL.objects):
    if o.name.startswith('v2峡谷断层主崖') and sum(v.co.y for v in o.data.vertices)/len(o.data.vertices)>7.5:bpy.data.objects.remove(o,do_unlink=True)
far=material('v2｜远峰蓝灰',(.09,.14,.14),0,.95)
for depth,offset in [(8.4,0),(10.0,.17)]:
    verts=[];faces=[]
    for i in range(45):
        x=-3.4+i*6.7/44;top=2.2+.65*abs(sin(x*2.5+offset))+.22*sin(x*7.4)
        verts.extend([(x,depth,1.43),(x,depth,top),(x,depth+.4,1.43)])
    for i in range(44):k=3*i;faces.extend([(k,k+3,k+4,k+1),(k+1,k+4,k+5,k+2)])
    mesh_obj('v2远景连绵山脊',verts,faces,far)
# 森林增加中层蕨叶和叶幕，轮廓保持不挡鹿。
use('04｜双鹿森林生态箱')
for i in range(22):
    x=random.uniform(-5.9,-2.35);y=random.uniform(-.4,1.2);fern_v2(x,y,forest_z(x,y),random.uniform(.4,.63),2500+i)
verts=[];faces=[]
for i in range(700):
    x=random.uniform(-5.9,-2.25);y=random.uniform(.90,1.35);z=random.uniform(6.1,8.4)
    if sin(x*5+z*4)<-.3:continue
    q=Vector((x,y,z));a=random.random()*pi;u=Vector((cos(a),0,sin(a)))*.072;v=Vector((-sin(a),-.12,cos(a)))*.025;k=len(verts);verts.extend([q-u,q-v,q+u,q+v]);faces.append((k,k+1,k+2,k+3))
mesh_obj('v2森林中层叶幕',verts,faces,leafmats[0])
# 首轮偏暗的主体增加局部反射，保持窗光方向。
use('10｜灯光与相机')
setlight('正面柔光',180,7,(1,.75,.49),group='弱填充')
setlight('山谷内部冷天光',380,2.0,(.69,.81,.85),(-2.1,2.9,4.9),(-.8,-1.2,1.8))
setlight('鹿箱顶部光',190,1.3,(1,.72,.39),(-5.0,-.8,8.4),(-4.3,-1,6.3))
light('v2森林低位反射',(-4.1,-2.5,6.2),(1,.70,.35),25,1.8,(-4.2,.8,6.7))['v2灯组']='弱填充'
# 柜体细节补正：底部黑缝由地形封边解决，不通过加灯掩盖。
s.render.filepath=os.path.join(OUT,'museum_preview_v2_02.png');s.cycles.samples=64
s['迭代记录']='第二轮修复：鹿眼缩放、地形封口、岩壁坡脚与植被覆盖'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'museum_scene_v2.blend'))
print('v2第二轮保存完成',flush=True);bpy.ops.render.render(write_still=True)
