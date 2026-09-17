"""最终全景反馈：撤销过于符号化的远树，降低远峰并恢复岩面层次。"""
import bpy,os,math,random
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__));s=bpy.context.scene
for o in list(s.objects):
    if o.name.startswith('v2远景微缩针叶林'):bpy.data.objects.remove(o,do_unlink=True)
o=bpy.data.objects['v2真实起伏远峰']
for v in o.data.vertices:v.co.z=1.45+(v.co.z-1.45)*.60
m=bpy.data.materials['v2｜远峰蓝灰'];n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=11;tex.inputs['Detail'].default_value=5
r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.065,.11,.115,1);r.color_ramp.elements[1].color=(.19,.25,.24,1);l.new(tex.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color'])
b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=.025;l.new(tex.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
# 局部检查发现原柜柱贯穿生态箱，截去开口内柱段，保留上部受力结构。
col=bpy.data.collections['02｜巨型胡桃木收藏柜']
for o in list(col.objects):
    if o.name.startswith('贯通木立柱') and min(abs(o.location.x+2.6),abs(o.location.x-2.25))<.1:
        top=11.5;bottom=4.43;o.dimensions.z=top-bottom;o.location.z=(top+bottom)/2
    if o.name.startswith('v2木柱菱形嵌饰'):
        pts=[o.matrix_world@Vector(v) for v in o.bound_box];cx=sum(v.x for v in pts)/8;cz=sum(v.z for v in pts)/8
        if cz<4.4 and min(abs(cx+2.6),abs(cx-2.25))<.2:bpy.data.objects.remove(o,do_unlink=True)
# 原放射骨脊穿过颈盾孔，改为外缘短浮雕，避开空腔。
for o in list(s.objects):
    if o.name.startswith('v2颈盾骨脊'):bpy.data.objects.remove(o,do_unlink=True)
col=bpy.data.collections['05｜角龙头骨研究室'];bone=bpy.data.materials['古旧象牙骨质'];center=Vector((.8,.60,7.34));U=Vector((.8,.6,0));N=Vector((.6,-.8,0));Z=Vector((0,0,1))
for i in range(15):
    a=i*math.pi*2/15;pts=[]
    for j in range(5):
        r=.80+j*.037;wide=.65*(.86+.16*math.sin(a));edge=1+.045*math.sin(a*13)+.025*math.sin(a*7)
        pts.append(center+U*(math.cos(a)*wide*r*edge)+Z*(math.sin(a)*.77*r*edge)+N*(.14*(1-r*r)+.02*math.cos(a*8)*r+.008))
    cu=bpy.data.curves.new('颈盾外缘浮雕','CURVE');cu.dimensions='3D';cu.bevel_depth=.009;cu.bevel_resolution=2;sp=cu.splines.new('BEZIER');sp.bezier_points.add(4)
    for bp,p in zip(sp.bezier_points,pts):bp.co=p;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
    ob=bpy.data.objects.new('v2颈盾外缘短骨脊',cu);col.objects.link(ob);cu.materials.append(bone)
# 体素融合的体表统一回正确鹿毛材质，取消因材料槽遗留造成的浅白主体。
fur=bpy.data.materials['鹿毛｜暖棕']
for o in s.objects:
    if o.name.startswith(('站立雄鹿连续体表','卧姿雄鹿连续体表')):
        o.data.materials.clear();o.data.materials.append(fur)
        for poly in o.data.polygons:poly.material_index=0
# 岩面藤叶减小并轻微错开，消除成排方片感。
random.seed(918)
o=bpy.data.objects.get('v2岩面垂藤叶片')
if o:
    for poly in o.data.polygons:
        center=sum((o.data.vertices[i].co.copy() for i in poly.vertices),Vector())/len(poly.vertices);scale=random.uniform(.45,.85)
        jitter=Vector((random.uniform(-.025,.025),0,random.uniform(-.025,.025)))
        for i in poly.vertices:o.data.vertices[i].co=center+(o.data.vertices[i].co-center)*scale+jitter

def cleanup_exhibit_shelves(scene):
    # 柜柱移除后显露的旧瓶架位于生态箱内部，应清理以维持景观边界。
    for obj in list(scene.objects):
        if not obj.name.startswith(('底层架板','标本瓶','标本瓶塞','瓶身标签')):continue
        if obj.type!='MESH':continue
        points=[obj.matrix_world@Vector(p) for p in obj.bound_box]
        center=sum(points,Vector())/8
        if -4.3<center.x<-2.9 and .5<center.y<2.3 and center.z<4.45:bpy.data.objects.remove(obj,do_unlink=True)
cleanup_exhibit_shelves(s)

s['远景修订']='已撤销符号化针叶林，降低远峰高度并细化岩面'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'museum_scene_v2.blend'));s.render.filepath=os.path.join(OUT,'museum_final_v2.png');bpy.ops.render.render(write_still=True)
