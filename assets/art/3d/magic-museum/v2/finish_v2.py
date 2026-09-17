"""第二轮反馈：森林枝叶围合、岩台生长、远景透光与最终输出。"""
import bpy,math,random,os,ast,json
from mathutils import Vector,Matrix
from math import sin,cos,pi
OUT=os.path.dirname(os.path.abspath(__file__));BASE=os.path.dirname(OUT);s=bpy.context.scene;random.seed(91728)
wood=bpy.data.materials['深胡桃木｜顺纹'];wood_edge=bpy.data.materials['雕花木｜磨亮边缘'];wood_light=bpy.data.materials['抽屉老木面'];gold=bpy.data.materials['黄铜｜陈旧金属'];stone=bpy.data.materials['博物馆暖灰石灰岩'];dark=bpy.data.materials['缝隙阴影'];rockmat=bpy.data.materials['v2｜沉积岩断面'];moss=bpy.data.materials['v2｜石隙苔藓'];earth=bpy.data.materials['v2｜腐殖土与湿岸'];bone=bpy.data.materials['古旧象牙骨质'];leafmats=[bpy.data.materials['v2｜蕨叶'+str(i)] for i in range(4)]
for filename in [os.path.join(BASE,'build_museum.py'),os.path.join(OUT,'build_v2.py')]:
    source=ast.parse(open(filename).read());exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<复用几何>','exec'))
# 枝叶集中在有树枝承托的位置，取代随机墙面散点。
use('04｜双鹿森林生态箱');remove_names(['v2森林中层叶幕'])
verts=[];faces=[];indices=[]
for j in range(38):
    x=random.uniform(-5.95,-2.3);y=random.uniform(.85,1.8);z=random.uniform(6.1,8.5)
    if j<12:z=random.uniform(8,8.5)
    root=Vector((-5.55 if x<-4.2 else -2.55,1.18,6.55));end=Vector((x,y,z))
    tube('v2树冠承托枝',[root,root+(end-root)*.55+Vector((0,.13,.08)),end],random.uniform(.008,.020),wood_edge)
    for i in range(95):
        a=random.random()*2*pi;rr=random.random()**.5;v=random.uniform(-1,1)
        pos=end+Vector((cos(a)*.31*rr,sin(a)*.24*rr,v*.23))
        angle=random.uniform(-pi,pi);u=Vector((cos(angle),sin(angle)*.4,sin(angle)))*random.uniform(.06,.10);cross=Vector((-u.z,-.015,u.x))*.38;k=len(verts)
        verts.extend([pos-u,pos-cross,pos+Vector((0,-.018,0)),pos+u,pos+cross]);faces.extend([(k,k+1,k+2),(k+1,k+3,k+2),(k+3,k+4,k+2),(k+4,k,k+2)]);indices.extend([random.randrange(4)]*4)
ob=mesh_obj('v2有枝支撑的森林叶簇',verts,faces,None,True)
for m in leafmats:ob.data.materials.append(m)
for p,i in zip(ob.data.polygons,indices):p.material_index=i
# 倒木与交织根系，位置在双鹿身后。
for i in range(7):
    x=-5.55+i*.45;tube('v2森林横卧枯枝',[(x,.42,5.83),(x+.25,.6,6.06),(x+.65,.82,6.24),(x+1.0,1.0,6.10)],.025,wood_edge)
# 减小正面遮挡感，站鹿再略左移。
for o in list(COL.objects):
    if o.name.startswith('站立雄鹿'):o.location.x-=.14
# 让现有动物肤色在暖光下有深浅分区，避免整体奶白。
fur=bpy.data.materials['鹿毛｜暖棕']
for n in fur.node_tree.nodes:
    if n.type=='VALTORGB':n.color_ramp.elements[0].color=(.065,.028,.009,1);n.color_ramp.elements[1].color=(.27,.14,.048,1)
# 岩壁上方的蕨类先向下投射求交，放到真正的岩台上。
use('03｜恐龙山谷生态箱');bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
cliffs=[o for o in COL.objects if o.name.startswith(('v2峡谷断层主崖','v2峡谷崩积坡'))]
for ci,o in enumerate(cliffs):
    ev=o.evaluated_get(deps);bound=[o.matrix_world@Vector(p) for p in o.bound_box];xmin=min(p.x for p in bound);xmax=max(p.x for p in bound);ymin=min(p.y for p in bound);ymax=max(p.y for p in bound)
    for j in range(9):
        x=random.uniform(xmin,xmax);y=random.uniform(ymin,ymax);ok,hit,normal,idx=ev.ray_cast(Vector((x,y,12)),Vector((0,0,-1)))
        if ok and normal.z>.20 and hit.z<4.3:fern_v2(hit.x,hit.y,hit.z+.015,random.uniform(.26,.46),3000+ci*10+j)
# 植物之间补低矮带叶枝，让生态箱具有多种叶型。
verts=[];faces=[]
for i in range(170):
    x=random.uniform(-4,2.85);y=random.uniform(-2.8,5)
    if abs(x-river_center(y))<river_width(y)+.3:continue
    z=terrain_z(x,y);h=random.uniform(.12,.28)
    for j in range(4):
        a=j*2.4+i;pos=Vector((x+.055*cos(a),y+.055*sin(a),z+h*j/4));u=Vector((cos(a),sin(a),.3))*.10;v=Vector((-sin(a),cos(a),.1))*.035;k=len(verts);verts.extend([pos-u*.2,pos-v,pos+u,pos+v]);faces.append((k,k+1,k+2,k+3))
mesh_obj('v2溪边阔叶地被',verts,faces,leafmats[1],True)
# 中后景的蓝灰空气感由局部天光承担。
use('10｜灯光与相机')
shader(bpy.data.materials['v2｜峡谷远处天色']).inputs['Emission Strength'].default_value=.65
light('v2远峰正向天空反射',(-.5,5.4,4.2),(.60,.76,.83),110,2.7,(-.5,9.5,2.5))['v2灯组']='局部展品'
setlight('山谷内部冷天光',460,2.0,(.75,.84,.82),(-2.1,2.9,4.9),(-.8,-1.2,1.8))
light('v2溪岸暖反光',(1.5,-3.1,3.6),(1,.78,.42),65,2.4,(.5,-1.3,1.7))['v2灯组']='弱填充'
# 轻微加深木材的暖红棕，保留照明塑形。
for mat in [wood,wood_edge,wood_light]:
    for nd in mat.node_tree.nodes:
        if nd.type=='VALTORGB':
            for e in nd.color_ramp.elements:
                c=e.color;e.color=(c[0]*1.10,c[1]*.98,c[2]*.86,1)
# 记录可复核的构图坐标。原画目标为人工标记近似值，非机器测量。
from bpy_extras.object_utils import world_to_camera_view
marks={'主抽屉把手':(-.65,-3.55,.87),'头骨焦点':(-.2,.4,7.28),'主晶柱尖端':(3.7,.74,7.65),'站鹿焦点':(-4.9,-1.1,6.9),'楼梯底端':(5.95,-3.28,.20)}
uv={k:[round(world_to_camera_view(s,s.camera,Vector(v)).x,4),round(1-world_to_camera_view(s,s.camera,Vector(v)).y,4)] for k,v in marks.items()}
with open(os.path.join(OUT,'camera_landmarks.json'),'w') as f:json.dump({'说明':'左上为原点，按画幅归一化；用于下一轮人工对照，不代表已满足3%容差','v2主视角':uv},f,ensure_ascii=False,indent=2)
s.render.resolution_percentage=100;s.cycles.samples=128;s.render.filepath=os.path.join(OUT,'museum_final_v2.png')
s['迭代记录']='完成第三轮：森林枝叶成簇、岩台植物、远峰天光、材质暖棕与128采样成图'
s['验收边界']='主要布局与生态细节已迭代；有机解剖、手工雕花与原画仍存在差异，不宣称逐像素一致。'
bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'museum_scene_v2.blend'))
print('v2最终候选已保存，开始高分辨率渲染',flush=True);bpy.ops.render.render(write_still=True)
