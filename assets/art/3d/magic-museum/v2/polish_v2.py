"""最终候选反馈：完整楼梯构图、立体远峰、叶面反光。"""
import bpy,os,math,random,ast,json
from mathutils import Vector
from math import sin,cos,pi
from mathutils.noise import noise_vector
OUT=os.path.dirname(os.path.abspath(__file__));BASE=os.path.dirname(OUT);s=bpy.context.scene;random.seed(91729)
rockmat=bpy.data.materials['v2｜沉积岩断面'];moss=bpy.data.materials['v2｜石隙苔藓'];wood_edge=bpy.data.materials['雕花木｜磨亮边缘'];gold=bpy.data.materials['黄铜｜陈旧金属'];leafmats=[bpy.data.materials['v2｜蕨叶'+str(i)] for i in range(4)]
for filename in [os.path.join(BASE,'build_museum.py'),os.path.join(OUT,'build_v2.py')]:
    src=ast.parse(open(filename).read());exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<复用几何>','exec'))
s.camera.data.lens=42;s.camera.data.shift_y=-.032
for m in leafmats:
    p=shader(m);p.inputs['Roughness'].default_value=.76;p.inputs['Specular IOR Level'].default_value=.19;p.inputs['Subsurface Weight'].default_value=.018
# 头骨轻微右移，支架与底座同步移动。
use('05｜角龙头骨研究室')
for o in COL.objects:
    if (o.type in {'MESH','CURVE'} and any(m.name=='古旧象牙骨质' for m in o.data.materials)) or o.name.startswith(('头骨基座','头骨铜支撑')):o.location.x+=.28
# 原有远峰是折线面，改为真实二维高度场山体。
use('03｜恐龙山谷生态箱');remove_names(['v2远景连绵山脊'])
far=bpy.data.materials['v2｜远峰蓝灰']
peaks=[(-2.3,9,2.3,.55,1.05),(-.9,10.3,2.0,.62,.95),(.35,11.4,2.45,.53,1.05),(1.8,9.8,2.2,.68,.9)]
def mountain(x,y):
    h=max(height*math.exp(-((x-cx)/wx)**2-((y-cy)/wy)**2) for cx,cy,height,wx,wy in peaks)
    v=noise_vector(Vector((x*3.1,y*2.8,1.2))).z
    return 1.45+h+.14*v*min(1,h)+.07*sin(x*16+y*4)*min(1,h)
terrain('v2真实起伏远峰',-4.3,3.3,7.1,13.1,mountain,far,95,78)
# 微型树群与远峰共同提供尺度感。
verts=[];faces=[]
for i in range(85):
    x=random.uniform(-3.1,2.3);y=random.uniform(5.2,9.8)
    if abs(x-river_center(y))<.5:continue
    z=mountain(x,y) if y>7.1 else terrain_z(x,y);h=random.uniform(.20,.45)
    for j in range(3):
        zz=z+j*h*.20;r=h*(.27-j*.045);k=len(verts)
        for q in range(7):verts.append((x+cos(q*2*pi/7)*r,y+sin(q*2*pi/7)*r,zz))
        verts.append((x,y,zz+h*.52))
        for q in range(7):faces.append((k+q,k+(q+1)%7,k+7))
mesh_obj('v2远景微缩针叶林',verts,faces,leafmats[0])
# 玻璃标本柜内部加暗铜遮光环，避免窗反光成为大白带。
use('09｜大厅标本柜与灯具')
inner=gold.copy();inner.name='v2｜遮光罩内铜';shader(inner).inputs['Roughness'].default_value=.62
vs=[];fs=[]
for r in [.36,.64]:
    for i in range(48):vs.append((7+r*cos(i*2*pi/48),-.12+r*sin(i*2*pi/48),3.68))
for i in range(48):fs.append((i,(i+1)%48,48+(i+1)%48,48+i))
mesh_obj('v2标本柜内遮光环',vs,fs,inner)
s['迭代记录']='v2最终：峡谷纵深、自然叶簇与羽片、薄壳头骨、实体浮雕、分组布光；补齐楼梯底端取景'
s.render.filepath=os.path.join(OUT,'museum_final_v2.png');s.render.resolution_percentage=100;s.cycles.samples=128
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'museum_scene_v2.blend'))
print('v2修正后最终场景保存完成',flush=True);bpy.ops.render.render(write_still=True)
