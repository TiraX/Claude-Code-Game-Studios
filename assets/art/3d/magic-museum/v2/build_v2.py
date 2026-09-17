"""从保留的 v1 场景构建 v2；重复执行不会累加到上次结果。"""
import bpy,math,random,os,ast,json
from mathutils import Vector,Matrix
from mathutils.noise import noise_vector
from math import sin,cos,pi
OUT=os.path.dirname(os.path.abspath(__file__));BASE=os.path.dirname(OUT)
bpy.ops.wm.open_mainfile(filepath=os.path.join(BASE,'museum_scene.blend'))
random.seed(91726);s=bpy.context.scene
wood=bpy.data.materials['深胡桃木｜顺纹'];wood_edge=bpy.data.materials['雕花木｜磨亮边缘'];wood_light=bpy.data.materials['抽屉老木面'];gold=bpy.data.materials['黄铜｜陈旧金属'];stone=bpy.data.materials['博物馆暖灰石灰岩'];dark=bpy.data.materials['缝隙阴影'];rockmat=bpy.data.materials['峡谷岩石'];moss=bpy.data.materials['湿润苔藓'];bone=bpy.data.materials['古旧象牙骨质'];fur=bpy.data.materials['鹿毛｜暖棕'];dinoskin=bpy.data.materials['恐龙皮肤'];eye=bpy.data.materials['眼与鼻'];paper=bpy.data.materials['泛黄纸张'];glass=bpy.data.materials['透明展示玻璃'];water=bpy.data.materials['山谷溪水'];crystal=bpy.data.materials['青蓝晶体']
source=ast.parse(open(os.path.join(BASE,'build_museum.py')).read());exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<已有建模函数>','exec'))
COL=None

def use(name):
    global COL
    COL=bpy.data.collections[name];print('执行：'+name,flush=True)

def mesh_obj(name,verts,faces,mat,smooth=False):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);COL.objects.link(o)
    if mat:me.materials.append(mat)
    if smooth:
        for p in me.polygons:p.use_smooth=True
    return o

# 批量创建细部时直接构造网格，避免每片植物调用操作器。
def box(name,loc,dim,mat,bevel=.015):
    x,y,z=loc;a,b,c=[v/2 for v in dim];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
    ob=mesh_obj(name,vs,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],mat)
    if bevel:mo=ob.modifiers.new('细倒角','BEVEL');mo.width=bevel;mo.segments=3
    return ob

def remove_names(prefixes):
    for o in list(s.objects):
        if any(o.name.startswith(p) for p in prefixes):bpy.data.objects.remove(o,do_unlink=True)

def shader(m):return m.node_tree.nodes.get('Principled BSDF')

def detail_noise(m,scale,strength,distance):
    n=m.node_tree.nodes;l=m.node_tree.links;p=shader(m);tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=3
    co=n.new('ShaderNodeTexCoord');l.new(co.outputs['Object'],tex.inputs['Vector'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=distance;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
    return tex

# 材质不再用同一噪声兼任大形、颜色和细纹理。
rockmat=textured('v2｜沉积岩断面',(.055,.064,.054),(.23,.225,.18),(2,2,7),.88,bump=.2);detail_noise(rockmat,32,.25,.018)
moss=textured('v2｜石隙苔藓',(.015,.032,.008),(.115,.16,.022),(7,7,7),.9,bump=.15);detail_noise(moss,95,.26,.007)
earth=textured('v2｜腐殖土与湿岸',(.023,.018,.009),(.12,.094,.035),(6,6,6),.89,bump=.2)
wetrock=rockmat.copy();wetrock.name='v2｜溪岸湿石';shader(wetrock).inputs['Roughness'].default_value=.36
leafmats=[]
for i,c in enumerate([(.03,.066,.012),(.075,.12,.016),(.16,.21,.035),(.044,.095,.022)]):
    m=material('v2｜蕨叶'+str(i),c,0,.58);p=shader(m);p.inputs['Subsurface Weight'].default_value=.035
    detail_noise(m,65,.1,.002);leafmats.append(m)
# 皮肤细鳞使用蜂窝边界，不再添加全身颗粒位移。
p=shader(dinoskin);n=dinoskin.node_tree.nodes;l=dinoskin.node_tree.links
v=n.new('ShaderNodeTexVoronoi');v.feature='DISTANCE_TO_EDGE';v.inputs['Scale'].default_value=105
b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.13;b.inputs['Distance'].default_value=.009;l.new(v.outputs['Distance'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
for nd in n:
    if nd.type=='VALTORGB':
        nd.color_ramp.elements[0].color=(.055,.060,.024,1);nd.color_ramp.elements[1].color=(.22,.21,.08,1)
for m in [wood,wood_edge,wood_light]:
    detail_noise(m,95,.16,.007)
    n=m.node_tree.nodes;l=m.node_tree.links;t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=8
    mp=n.new('ShaderNodeMapRange');mp.inputs['To Min'].default_value=.29;mp.inputs['To Max'].default_value=.57;l.new(t.outputs['Fac'],mp.inputs['Value']);l.new(mp.outputs[0],shader(m).inputs['Roughness'])
shader(gold).inputs['Roughness'].default_value=.34
for n in gold.node_tree.nodes:
    if n.type=='VALTORGB':n.color_ramp.elements[0].color=(.075,.038,.012,1);n.color_ramp.elements[1].color=(.40,.24,.075,1)
# 水体、玻璃与矿晶采用非金属。
p=shader(water);p.inputs['Metallic'].default_value=0;p.inputs['Base Color'].default_value=(.21,.29,.25,1);p.inputs['Transmission Weight'].default_value=.92;p.inputs['IOR'].default_value=1.333;p.inputs['Roughness'].default_value=.075;detail_noise(water,6,.14,.009)
p=shader(crystal);p.inputs['Metallic'].default_value=0;p.inputs['Base Color'].default_value=(.28,.69,.73,1);p.inputs['Transmission Weight'].default_value=.83;p.inputs['IOR'].default_value=1.46;p.inputs['Roughness'].default_value=.10;p.inputs['Emission Strength'].default_value=0
n=crystal.node_tree.nodes;l=crystal.node_tree.links;ab=n.new('ShaderNodeVolumeAbsorption');ab.inputs['Color'].default_value=(.055,.43,.47,1);ab.inputs['Density'].default_value=.38;l.new(ab.outputs[0],n.get('Material Output').inputs['Volume'])

# A/B：打开景观后方通道，保留高层收藏柜背板。
use('02｜巨型胡桃木收藏柜');remove_names(['柜体背板','背墙','恐龙箱土层','森林展箱苔藓土层'])
box('v2柜背上部',(0,2.65,8.0),(12.7,.25,6.95),wood)
box('v2柜背左侧',(-5.55,2.65,2.28),(1.7,.25,4.35),wood)
box('v2柜背右侧',(4.67,2.65,2.28),(3.35,.25,4.35),wood)
box('v2大厅后墙上部',(0,3.65,8.3),(20,.5,7.6),stone)
box('v2大厅后墙左翼',(-8,3.65,2.2),(6,.5,4.5),stone)
box('v2大厅后墙右翼',(7,3.65,2.2),(7,.5,4.5),stone)
# 左侧建筑移远；地面及柜旁标本保留。
use('01｜建筑与石砖')
for o in list(COL.objects):
    if not any(o.name.startswith(p) for p in ['地面','磨损石砖','背墙']):o.location+=Vector((-.8,.75,0))
# 缩短廊板与前景扶手对主体的遮挡。
for o in s.objects:
    if o.name.startswith('左侧二层走廊'):o.scale.x*=.84

use('03｜恐龙山谷生态箱')
for o in list(COL.objects):
    if not any(o.name.startswith(p) for p in ['近景长颈龙','远景长颈龙','展台细栏杆','栏杆铜球','展台前扶手']):bpy.data.objects.remove(o,do_unlink=True)

def river_center(y):return -.55+.35*sin(y*.85)+.10*sin(y*2.1)
def river_width(y):return .39 if y<-.6 else max(.14,.36-.022*(y+.6))
def terrain_z(x,y):
    d=abs(x-river_center(y));w=river_width(y)
    bank=max(0,min(1,(d-w)/.45))
    return 1.42+bank*(.22+.09*sin(x*3.1+y*2.5)+.055*cos(y*5-x*2))+.025*sin(y*2)

def terrain(name,x0,x1,y0,y1,height,mat,nx=70,ny=95):
    vs=[(x0+(x1-x0)*i/nx,y0+(y1-y0)*j/ny,height(x0+(x1-x0)*i/nx,y0+(y1-y0)*j/ny)) for j in range(ny+1) for i in range(nx+1)]
    fs=[]
    for j in range(ny):
        for i in range(nx):k=j*(nx+1)+i;fs.append((k,k+1,k+nx+2,k+nx+1))
    return mesh_obj(name,vs,fs,mat,True)
terrain('v2山谷连续河床',-4.24,3.01,-3.25,10,terrain_z,earth)
# 真正凹入地面的连续水面。
vs=[]
for i in range(130):
    y=-3.18+i*13.0/129;c=river_center(y);w=river_width(y)+.055*sin(i*.55)
    vs.extend([(c-w,y,1.53),(c+w,y,1.53)])
mesh_obj('v2溪流反射水面',vs,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(129)],water)

# 由不规则棱角截面和逐层退台构成的岩壁。
def cliff(name,x,y,z,w,d,h,seed,mat=rockmat):
    rng=random.Random(seed);outline=[(-.95,-.70),(-.35,-.95),(.12,-.70),(.56,-.93),(.96,-.45),(.75,.28),(.4,.83),(-.35,.75),(-.88,.28)]
    count=len(outline);levels=9;vs=[];fs=[];phase=rng.random()*5
    for k in range(levels):
        t=k/(levels-1);shrink=1-.40*t;step=(k%3)*.045
        for j,(u,v) in enumerate(outline):
            ridge=1+rng.uniform(-.08,.08)
            vs.append((x+w*(u*shrink*ridge+.16*sin(t*3+phase)+step),y+d*(v*shrink*ridge+.07*sin(t*8+j)),z+h*t+h*rng.uniform(-.025,.025)+(rng.uniform(-.13,.13)*h if k==levels-1 else 0)))
    for k in range(levels-1):
        for j in range(count):
            a=k*count+j;b=k*count+(j+1)%count;c=(k+1)*count+(j+1)%count;e=(k+1)*count+j
            fs.extend([(a,b,c),(a,c,e)])
    fs.extend([tuple(reversed(range(count))),tuple((levels-1)*count+j for j in range(count))])
    ob=mesh_obj(name,vs,fs,mat)
    be=ob.modifiers.new('磨损棱缘','BEVEL');be.width=min(.018,w*.06);be.segments=2
    be.limit_method='ANGLE';be.angle_limit=.7
    # 苔藓直接附着部分朝上斜面，而非球形绿块。
    patches=[];pf=[]
    for face in fs[:-2]:
        a,b,c=[Vector(vs[q]) for q in face];normal=(b-a).cross(c-a).normalized()
        if normal.z>.12 and rng.random()<.58:
            center=(a+b+c)/3;first=len(patches)
            patches.extend([center+(p-center)*rng.uniform(.35,.83)+normal*.012 for p in [a,b,c]]);pf.append((first,first+1,first+2))
    if pf:mesh_obj(name+'附生苔藓',patches,pf,moss)
    return ob

for item in [(-3.55,-.20,1.55,.85,.72,2.6,1),(2.60,.60,1.52,.65,1.05,2.55,2),(-2.85,2.6,1.5,.75,.9,2.6,3),(2.18,3.9,1.5,.78,.9,2.95,4),(-2.05,5.3,1.5,.7,.85,2.2,5),(1.48,7.0,1.5,.65,.9,2.1,6),(-1.18,8.8,1.5,.42,.65,1.6,7),(.5,9.7,1.5,.46,.5,1.75,8)]:
    cliff('v2峡谷断层主崖',*item)
for i in range(30):
    y=random.uniform(-2.9,7);x=random.choice([-1,1])*random.uniform(1.5,2.8)-.4
    if x<-4.05 or x>2.8:continue
    cliff('v2层理碎岩',x,y,terrain_z(x,y)-.1,random.uniform(.12,.40),random.uniform(.15,.40),random.uniform(.2,.7),100+i)
for i in range(28):
    y=random.uniform(-3.1,5);x=river_center(y)+random.choice([-1,1])*(river_width(y)+random.uniform(.03,.22))
    cliff('v2水岸半浸石',x,y,1.43,random.uniform(.045,.13),random.uniform(.06,.15),random.uniform(.08,.20),200+i,wetrock)
# 景观远处为程序渐变天空，不使用原画投影。
sky=material('v2｜峡谷远处天色',(.17,.24,.26));n=sky.node_tree.nodes;l=sky.node_tree.links;p=shader(sky)
coord=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.11,.17,.18,1);r.color_ramp.elements[1].color=(.36,.47,.49,1);l.new(coord.outputs['Generated'],sep.inputs[0]);l.new(sep.outputs['Z'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color']);l.new(r.outputs[0],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.35
box('v2峡谷远天',(-.5,10.8,3.1),(9,.12,5),sky,0)

# 蕨类带主轴、分叶、起伏叶面；每株单一叶片网格。
def fern_v2(x,y,z,size=1,seed=0):
    rng=random.Random(seed);verts=[];faces=[];mids=[];stemverts=[];stemfaces=[]
    def rod(a,b,r):
        a=Vector(a);b=Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,0,1)))
        if u.length<.01:u=Vector((1,0,0))
        u.normalize();v=d.cross(u);k=len(stemverts)
        for p in [a,b]:
            for j in range(5):stemverts.append(p+r*(u*cos(j*2*pi/5)+v*sin(j*2*pi/5)))
        for j in range(5):stemfaces.append((k+j,k+(j+1)%5,k+5+(j+1)%5,k+5+j))
    for fr in range(8):
        angle=fr*2.399+rng.uniform(-.25,.25);L=size*rng.uniform(.70,1.20);D=Vector((cos(angle),sin(angle),0));side=Vector((-sin(angle),cos(angle),0))
        def pos(t):return Vector((x,y,z))+D*L*t+Vector((0,0,L*(1.2*t-.88*t*t)+.025))
        last=pos(0)
        for j in range(1,21):
            t=j/21;q=pos(t);rod(last,q,.0045*size*(1-t*.7));last=q
            length=L*.24*sin(pi*t)**.72
            for sign in [-1,1]:
                start=q+side*sign*.004;end=start+side*sign*length+D*L*.035
                delta=end-start;across=D*(L*.032*sin(pi*t)**.7);k=len(verts)
                for m in range(6):
                    f=m/5;center=start+delta*f+Vector((0,0,.014*size*sin(f*pi)))
                    width=sin(f*pi)**.7*(1 if m%2 else .79)
                    verts.extend([center-across*width,center+across*width])
                for m in range(5):faces.append((k+2*m,k+2*m+1,k+2*m+3,k+2*m+2));mids.append(rng.randrange(4))
    ob=mesh_obj('v2羽状蕨叶',verts,faces,None,True)
    for mat in leafmats:ob.data.materials.append(mat)
    for poly,idx in zip(ob.data.polygons,mids):poly.material_index=idx
    mesh_obj('v2蕨叶主轴',stemverts,stemfaces,leafmats[1],True)
    return ob
for i in range(100):
    x=random.uniform(-4.1,2.85);y=random.uniform(-3.08,8)
    if abs(x-river_center(y))<river_width(y)+.22:continue
    if (x+1.8)**2+(y-.42)**2<.5 or (x-1.55)**2+(y+1.75)**2<.5:continue
    fern_v2(x,y,terrain_z(x,y)+.012,random.uniform(.22,.55)*(1 if y<3 else .7),400+i)
# 河岸苔草成簇，避免均匀绿垫。
verts=[];faces=[]
for i in range(2600):
    x=random.uniform(-4.1,2.85);y=random.uniform(-3.1,7)
    if abs(x-river_center(y))<river_width(y)+.1:continue
    if sin(x*5+y*2.8)+sin(y*4.4)<-.5:continue
    z=terrain_z(x,y);h=random.uniform(.025,.095);w=.007;k=len(verts);a=random.random()*pi;d=Vector((cos(a)*w,sin(a)*w,0));p=Vector((x,y,z));verts.extend([p-d,p+d,p+Vector((.016,0,h))]);faces.append((k,k+1,k+2))
mesh_obj('v2溪岸苔草',verts,faces,moss)
# 小型卷叶，前景近看可见。
for x,y in [(-2.6,-2.7),(2.4,-2.3),(-1.4,-2.5)]:
    z=terrain_z(x,y);tube('v2新生卷蕨',[(x,y,z),(x,y,z+.18),(x+.05,y,z+.25),(x+.10,y,z+.24),(x+.09,y,z+.20)],.008,leafmats[1])

# C：森林地形、枝干围合与自然鹿角。
use('04｜双鹿森林生态箱')
for o in list(COL.objects):
    if not any(o.name.startswith(p) for p in ['站立雄鹿','卧姿雄鹿','青色森林光点']):bpy.data.objects.remove(o,do_unlink=True)
remove_names(['森林箱前细柱'])
def forest_z(x,y):return 5.74+.10*sin(x*3+y*2)+.08*cos(y*3-x)+.10*max(0,y)
terrain('v2森林腐殖地形',-5.98,-2.28,-2.38,1.34,forest_z,earth,42,38)
for i in range(12):
    x=random.uniform(-5.8,-2.5);y=random.uniform(-2.1,1.1)
    cliff('v2森林风化基岩',x,y,forest_z(x,y)-.10,random.uniform(.18,.35),random.uniform(.15,.28),random.uniform(.18,.38),800+i)
for i in range(45):
    x=random.uniform(-5.8,-2.4);y=random.uniform(-2.2,1.2)
    if y<-1 and -5.35<x<-4.15:continue
    fern_v2(x,y,forest_z(x,y),random.uniform(.22,.45),900+i)
# 林中枝干形成背景拱形，绝不横穿动物头部。
for x,lean in [(-5.78,.45),(-2.42,-.6)]:
    y=.78;z=forest_z(x,y)
    tapered('v2森林扭曲树干',[(x,y,z),(x-.08,y,z+.65),(x+lean*.4,y+.12,z+1.4),(x+lean,y+.2,z+2.15)],[.16,.12,.095,.045],wood_edge)
    for j in range(5):
        end=(x+lean*(1.1+j*.15),y+.1-random.random()*.25,z+1.3+j*.19)
        tube('v2树干分叉',[(x+lean*.25,y,z+.9),end,(end[0]+lean*.65,end[1],end[2]+.3)],.028,wood_edge)
    for j in range(5):
        a=j*1.25;tapered('v2外露根系',[(x,y,z+.2),(x+cos(a)*.36,y+sin(a)*.3,z),(x+cos(a)*.7,y+sin(a)*.6,forest_z(x+cos(a)*.7,y+sin(a)*.6))],[.07,.045,.002],wood_edge)
# 精细叶片网格，沿顶部和两侧布置，中央留出鹿角轮廓。
vs=[];fs=[]
for i in range(1100):
    x=random.uniform(-5.95,-2.22);y=random.uniform(.6,1.42);z=random.uniform(6,8.5)
    if -5.15<x<-2.8 and z<7.85:continue
    if random.random()>.5+.3*sin(x*5+z*7):continue
    p=Vector((x,y,z));a=random.random()*pi;u=Vector((cos(a),sin(a),.25))*.075;v=Vector((-sin(a),cos(a),.3))*.03;k=len(vs);vs.extend([p-u,p-v,p+Vector((0,-.018,0)),p+u,p+v]);fs.extend([(k,k+1,k+2),(k+1,k+3,k+2),(k+3,k+4,k+2),(k+4,k,k+2)])
mesh_obj('v2森林围合细叶',vs,fs,leafmats[1])
# 替换直杆鹿角，增加弯曲主干和前后错落分叉。
remove_names(['站立雄鹿主鹿角','站立雄鹿分叉鹿角','站立雄鹿鹿角细叉','卧姿雄鹿主鹿角','卧姿雄鹿分叉鹿角','卧姿雄鹿鹿角细叉'])
antler=textured('v2｜鹿角角质',(.12,.065,.021),(.39,.27,.13),(4,4,12),.61,bump=.1)
for name,origin,scale,height in [('站立雄鹿',(-4.95,-1.25,5.88),.98,1.52),('卧姿雄鹿',(-3.45,-1.2,5.90),.78,.92)]:
    ox,oy,oz=origin
    def dp(x,y,z):return Vector((ox+x*scale,oy+y*scale,oz+z*scale))
    for side in [-1,1]:
        pts=[dp(.34,side*.11,height+.15),dp(.30,side*.20,height+.36),dp(.12,side*.34,height+.58),dp(-.07,side*.40,height+.76),dp(-.22,side*.44,height+.89)]
        tapered(name+'v2弯曲主角',pts,[a*scale for a in [.041,.035,.026,.016,.001]],antler)
        for k in [1,2,3]:
            root=pts[k];tapered(name+'v2弧形角枝',[root,root+Vector((.07,side*.035,.10))*scale,root+Vector((.23,side*.075,.21+.035*k))*scale,root+Vector((.27,side*.07,.29+.03*k))*scale],[a*scale for a in [.021,.017,.009,.001]],antler)
    # 眼眶和吻部小结构采用已有位置，保留主模型的连续体表。
    for yy in [-.11,.11]:
        uv(name+'v2眼眶高光',dp(.493,yy,height+.10),(.01*scale,.012*scale,.01*scale),bone,12,8)
    # 同步新建对象的缩放，再应用整体变换。
    bpy.context.view_layer.update()
    # 整体缩小与左移，留出森林及鹿角负空间。
    tr=Matrix.Translation(Vector((-.15,.08,0))) @ Matrix.Translation(Vector(origin)) @ Matrix.Diagonal((.91,.91,.91,1)) @ Matrix.Translation(-Vector(origin))
    for o in list(COL.objects):
        if o.name.startswith(name):o.matrix_world=tr@o.matrix_world
# 恐龙接地、趾爪、口鼻；远景个体缩小并后移强化尺度差。
use('03｜恐龙山谷生态箱')
origin=Vector((-1.8,.42,1.52));tr=Matrix.Translation(Vector((.15,1.10,.06)))@Matrix.Translation(origin)@Matrix.Diagonal((.80,.80,.80,1))@Matrix.Translation(-origin)
for o in list(COL.objects):
    if o.name.startswith('远景长颈龙'):o.matrix_world=tr@o.matrix_world
for xx in [-.4,.39]:
    for yy in [-.21,.21]:
        for toe in range(3):
            uv('v2近景恐龙趾爪',(1.55-(xx+.11)*.83,-1.75+(yy+(toe-1)*.035)*.83,1.62),(.044,.019,.028),antler,12,8)
for side in [-1,1]:uv('v2近景恐龙鼻孔',(.47,-1.75+side*.06,2.46),(.018,.008,.011),eye,12,8)
# 消减整齐背部疙瘩，保留断续背脊。
for i,o in enumerate([o for o in COL.objects if '背脊鳞' in o.name]):
    if i%3==0:bpy.data.objects.remove(o,do_unlink=True)
    else:o.scale*=.65

# D：柜体实体截面和浮雕木饰。
use('02｜巨型胡桃木收藏柜')
remove_names(['柱头雕花','抽屉角部卷草','柜门卷草','立柱细槽','黄铜展签'])
for o in list(s.objects):
    if o.type=='FONT':o.hide_render=True
for o in COL.objects:
    if o.name.startswith('贯通木立柱'):o.scale.x=1.38
# 叶形浮雕为凸起的有厚度表面，中央脊和波浪边缘形成木雕阴影。
def relief_leaf(name,loc,w,h,mat,angle=0):
    vs=[];fs=[];x,y,z=loc
    for i in range(15):
        t=i/14;ww=w*sin(pi*t)**.65*(.82+.18*cos(t*pi*8))
        for j in [-1,0,1]:
            u=ww*j;v=h*t;vs.append((x+u*cos(angle)-v*sin(angle),y-(1-abs(j))*.065*sin(pi*t)-.018*sin(t*pi*5),z+u*sin(angle)+v*cos(angle)))
    for i in range(14):
        for j in range(2):k=i*3+j;fs.append((k,k+1,k+4,k+3))
    o=mesh_obj(name,vs,fs,mat,True);so=o.modifiers.new('雕花厚度','SOLIDIFY');so.thickness=.025
    return o
for x in [-6.25,-2.6,2.25,5.55,6.25]:
    for z in [4.5,8.6,10.7]:
        box('v2柱头分层台座',(x,-.1,z),(.54,.77,.16),wood_edge)
        for a in [-.45,0,.45]:relief_leaf('v2茛苕叶柱头',(x,-.42,z-.50),.10,.45,wood_edge,a)
    for zz in [2.7,6.8]:
        tube('v2木柱菱形嵌饰',[(x,-.29,zz-.45),(x-.12,-.32,zz),(x,-.32,zz+.45),(x+.12,-.32,zz),(x,-.29,zz-.45)],.022,wood_edge)
# 鹿箱檐口与主抽屉增厚而非只加色线。
for z,d,w in [(8.66,4.08,4.05),(8.73,4.18,4.18),(8.82,4.26,4.28)]:box('v2鹿箱檐口',(-4.12,-.55,z),(w,d,.075),wood_edge,.016)
for x in [-6,-2.25]:
    box('v2鹿箱后部支柱',(x,1.25,7.08),(.17,.22,3.05),wood_edge)
    relief_leaf('v2鹿箱角部雕花',(x,-2.46,8.1),.13,.46,wood_edge)
for x,y,z,w in [(-.65,-3.5,.84,7.7),(-4.12,-2.68,5.05,3.85),(-.15,-.23,4.96,4.6),(3.93,-.23,4.96,3.15)]:
    for dz in [-.28,.29]:
        box('v2抽屉深线脚',(x,y-.015,z+dz),(w-.15,.075,.07),wood_edge)
    for side in [-1,1]:
        xx=x+side*(w/2-.2);relief_leaf('v2抽屉木雕角花',(xx,y-.065,z-.23),.075,.43,wood_edge,side*.10)
# 贝壳壳体压浅，增加安装底板与下缘阴影。
for o in list(COL.objects):
    if not o.name.startswith('黄铜贝壳拉手'):continue
    vs=[v.co for v in o.data.vertices];lo=Vector(tuple(min(v[k] for v in vs) for k in range(3)));hi=Vector(tuple(max(v[k] for v in vs) for k in range(3)));center=(lo+hi)/2
    for v in o.data.vertices:v.co.y=hi.y+(v.co.y-hi.y)*.64
    box('v2把手安装底板',(center.x,hi.y+.015,center.z),((hi.x-lo.x)*1.12,.024,(hi.z-lo.z)*1.13),gold,.012)
# 小幅增添实际抽屉板缝，而不是规则金线。
for z in [.62,.97]:box('v2前抽屉细板缝',(-.65,-3.492,z),(7.25,.008,.006),dark,0)

# E：重新构建有空腔、骨桥及薄颈盾的角龙头骨。
use('05｜角龙头骨研究室')
remove_names(['角龙头骨主体','角龙喙鼻','扇形角龙颈盾','颈盾边缘骨刺','角龙眉角','角龙鼻角','头骨下颌','角龙齿列','头骨眼窝深腔','头骨鼻腔深处'])
for n in bone.node_tree.nodes:
    if n.type=='VALTORGB':n.color_ramp.elements[0].color=(.16,.103,.052,1);n.color_ramp.elements[1].color=(.48,.35,.18,1)
shader(bone).inputs['Roughness'].default_value=.58;detail_noise(bone,58,.16,.006)
def bone_shell(name,loc,scale,thickness=.06):
    o=uv(name,loc,scale,bone,32,20);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.select_set(False)
    carve(o,loc,tuple(max(.02,v-thickness) for v in scale));return o
cranium=bone_shell('v2角龙中空脑颅',(.0,.4,7.19),(.65,.33,.34),.065)
carve(cranium,(-.20,.14,7.29),(.22,.44,.185));carve(cranium,(.27,.36,7.20),(.18,.43,.13));carve(cranium,(-.02,.4,6.88),(.65,.38,.20))
snout=bone_shell('v2角龙中空上颌',(-.68,.37,7.04),(.48,.245,.195),.053);carve(snout,(-.86,.18,7.08),(.19,.32,.102))
# 骨桥与颧骨的可读连接。
for yy in [.12,.62]:
    tapered('v2颧骨桥',[(.31,yy,7.17),(.02,yy-.04,6.96),(-.38,yy-.015,6.94),(-.70,yy,7.01)],[.065,.072,.049,.043],bone)
    tapered('v2分离下颌',[(.24,yy,7.01),(-.08,yy,6.78),(-.64,yy,6.79),(-1.08,yy,6.97)],[.072,.049,.038,.015],bone)
tapered('v2角龙喙缘',[(-1.02,.22,7.12),(-1.16,.35,7.02),(-1.04,.51,7.10)],[.035,.025,.03],bone)
# 放射颈盾，薄骨板而非厚圆盘。
center=Vector((.52,.60,7.34));U=Vector((.80,.60,0));N=Vector((.60,-.80,0));Z=Vector((0,0,1));vs=[center];fs=[];nr=5;nt=52
for k in range(1,nr+1):
    r=k/nr
    for i in range(nt):
        a=i*2*pi/nt;wide=.65*(.86+.16*sin(a));edge=1+.045*sin(a*13)+.025*sin(a*7)
        vs.append(center+U*(cos(a)*wide*r*edge)+Z*(sin(a)*.77*r*edge)+N*(.14*(1-r*r)+.02*cos(a*8)*r))
for i in range(nt):fs.append((0,1+i,1+(i+1)%nt))
for k in range(nr-1):
    for i in range(nt):a=1+k*nt+i;b=1+k*nt+(i+1)%nt;fs.append((a,b,b+nt,a+nt))
shield=mesh_obj('v2薄骨颈盾',vs,fs,bone,True);sol=shield.modifiers.new('骨片厚度','SOLIDIFY');sol.thickness=.045;bpy.context.view_layer.objects.active=shield;bpy.ops.object.modifier_apply(modifier=sol.name)
for side in [-1,1]:
    loc=center+U*(side*.27)+Z*.22;cut=uv('临时颈盾孔',loc,(.13,.22,.20),None,24,16);cut.rotation_euler.z=-.65
    mod=shield.modifiers.new('颈盾薄骨孔','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=shield;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
for i in range(15):
    a=i*2*pi/15;end=center+U*(cos(a)*.63)+Z*(sin(a)*.77)
    tube('v2颈盾骨脊',[center+N*.15,center+(end-center)*.55+N*.12,end+N*.02],.015,bone)
    tapered('v2颈盾缘齿',[end,end+(end-center).normalized()*.075],[.032,.001],bone)
for yy in [.16,.60]:tapered('v2弯曲眉角',[(.0,yy,7.46),(-.16,yy,7.74),(-.42,yy+.03,7.94),(-.65,yy+.02,8.06)],[.105,.073,.033,.001],bone)
tapered('v2鼻角',[(-.76,.36,7.2),(-.91,.36,7.43),(-1.04,.37,7.49)],[.085,.038,.001],bone)
for i in range(13):
    for yy in [.19,.54]:uv('v2颌内齿列',(-.93+i*.07,yy,6.94+random.uniform(-.012,.012)),(.021,.024,.034),bone,12,8)

# F：晶洞分层石台和有高低主次的晶簇。
use('06｜青蓝水晶岩洞')
remove_names(['青蓝石英晶簇','水晶洞岩层','洞穴侧崖'])
for i,(x,y,h) in enumerate([(2.8,1.4,.6),(4.9,1.7,1.55),(5.15,1.8,2.4),(3.9,.9,.35),(3.05,.3,.25)]):cliff('v2晶洞层岩',x,y,5.45,.53,.56,h,1500+i)
for i in range(23):
    a=i*2.399;radius=.53*math.sqrt(i/23);pos=(3.70+radius*cos(a),.74+radius*sin(a),5.73)
    h=1.92 if i==0 else random.uniform(.26,1.15);r=.125 if i==0 else random.uniform(.045,.12)
    gem(pos,r,h,(sin(a)*.24,cos(a)*.32,a))
# 少量内部断面：细小透明平面，避免满体噪声。
for i in range(4):
    z=6.2+i*.24;mesh_obj('v2晶内生长面',[(3.6,.70,z),(3.77,.68,z+.06),(3.82,.80,z+.03)],[(0,1,2)],glass)
for i in range(9):fern_v2(random.uniform(2.65,5.08),1.7,5.76,random.uniform(.20,.38),1700+i)

# G：楼梯节点和工作室道具。
use('08｜木阶与黄铜楼梯')
for o in list(COL.objects):
    if o.name.startswith('独立木踏板'):
        o.data.materials.clear();o.data.materials.append(wood_light)
        p=o.location
        for dx in [-.26,.26]:uv('v2踏板铜钉',p+Vector((dx,-.02,.058)),(.013,.013,.005),gold,10,6)
    if o.name.startswith('楼梯栏杆节点'):o.scale*=.82
# 弯曲端部扶手，实际接合原有楼梯端点。
tube('v2楼梯起步扶手卷头',[(6.21,-3.22,.98),(6.25,-3.37,.96),(6.2,-3.46,.89),(6.13,-3.44,.86)],.025,gold)
use('05｜角龙头骨研究室')
# 墙上仪器、测量工具与图纸。
for x in [-1.8,1.45]:
    torus('v2墙上标本镜框',(x,2.04,7.3),.26,.028,gold,(pi/2,0,0))
    beam('v2仪器支架',(x,2.06,6.88),(x,2.06,7.06),.016,gold)
for i in range(3):
    o=cyl('v2卷起研究图纸',(-1.3+i*.21,.62,6.44),.035,.35,paper,16);o.rotation_euler.x=pi/2
for i in range(4):beam('v2桌面测绘笔',(-1.25+i*.09,.9,6.39),(-1.04+i*.08,.66,6.39),.009,wood_edge)
# 前景研究图册。
bookmat=bpy.data.materials['书籍封面0'];box('v2台面图册封面',(.98,1.0,6.42),(.43,.34,.06),bookmat,.008);box('v2台面图册纸页',(.98,1.0,6.46),(.40,.32,.05),paper,.002)
use('07｜书房与藏品')
for i in range(4):
    o=box('v2书房横放图册',(3.13,.83,3.16+i*.055),(.42,.30,.05),bpy.data.materials['书籍封面'+str(i%4)],.005)
# 几个高层仪器打破整齐排列，不增加铺满式杂物。
for xx in [-4.1,.55]:
    cyl('v2浑天仪底座',(xx,.6,9.7),.17,.065,gold)
    for rot in [(pi/2,.4,0),(.25,.9,0),(0,0,0)]:torus('v2天文仪铜环',(xx,.6,10.02),.25,.014,gold,rot)
    beam('v2天文仪极轴',(xx-.12,.6,9.72),(xx+.12,.6,10.32),.013,gold)
# 减弱瓶子标签的一致亮度。
for o in s.objects:
    if o.name.startswith('瓶身标签') and random.random()<.45:o.hide_render=True
# 标本骨架变成有节律的弯曲肋骨。
use('09｜大厅标本柜与灯具');remove_names(['标本肋骨'])
for i in range(18):
    z=1.15+i*.105;xx=7+.17*sin(i*.12);w=.13+.16*sin(i/18*pi)
    for side in [-1,1]:tube('v2标本弯曲肋骨',[(xx,-.12,z),(xx+side*w*.75,-.12,z-.04),(xx+side*w,-.28,z-.14),(xx+side*w*.70,-.36,z-.21)],.013,bone)
# 地面增加真实区域材质差异。
for i in range(5):
    m=stone.copy();m.name='v2｜石砖色阶'+str(i)
    for n in m.node_tree.nodes:
        if n.type=='VALTORGB':
            for el in n.color_ramp.elements:el.color=tuple(v*(.62+.065*i) for v in el.color[:3])+(1,)
    shader(m).inputs['Roughness'].default_value=.52+.055*i
floor_mats=[bpy.data.materials['v2｜石砖色阶'+str(i)] for i in range(5)]
for o in s.objects:
    if o.name.startswith('磨损石砖'):o.data.materials.clear();o.data.materials.append(random.choice(floor_mats))

# H：按窗光、生态箱主光、灯具和弱填充分组布光。
use('10｜灯光与相机')
def aim(o,loc,target):o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def setlight(name,energy,size,color,loc=None,target=None,group='局部展品'):
    o=bpy.data.objects.get(name)
    if not o:return
    o.data.energy=energy;o.data.color=color
    if o.data.type=='AREA':o.data.size=size
    if loc is not None:aim(o,loc,target)
    o['v2灯组']=group
setlight('左窗漫射天光',1150,3.2,(.72,.81,1),(-7.8,-2.5,8.8),(-1,-.5,3.7),'窗光')
setlight('正面柔光',130,7,(1,.80,.61),group='弱填充')
setlight('顶层暖反光',185,4,(1,.66,.34),group='弱填充')
setlight('山谷内部冷天光',270,1.8,(.60,.79,.87),(-1.9,2.7,4.5),(-.5,-1,1.9))
setlight('山谷后侧轮廓光',140,1.3,(.55,.73,.88),(-.5,6.5,4.6),(-.8,1,1.8))
setlight('鹿箱顶部光',170,1.35,(1,.68,.30),(-5.2,-.4,8.45),(-4.2,-1.1,6.5))
setlight('头骨重点灯',160,.9,(1,.71,.39),(-1.3,-.6,8.3),(-.1,.4,7.2))
setlight('晶洞顶光',65,1.2,(.78,.90,1));setlight('晶洞青光',8,.2,(.19,.72,1));setlight('晶洞后窗柔光',90,1.2,(.74,.85,1))
setlight('标本柜内暖光',16,.3,(1,.59,.23),group='灯具')
for o in s.objects:
    if o.type=='LIGHT' and o.name.startswith('灯笼暖光'):o.data.energy*=.78;o.data.color=(1,.51,.19);o['v2灯组']='灯具'
light('v2山谷远方天空',(-.6,9,4.9),(.61,.75,.84),190,3,(-.6,3.5,2.2))['v2灯组']='局部展品'
light('v2主抽屉暖反射',(-.3,-5,2.3),(1,.61,.27),85,3,(-.8,-2.5,1.3))['v2灯组']='弱填充'
s.world.node_tree.nodes['Background'].inputs[1].default_value=.09
# 左窗不再是无层次白板。
wm=bpy.data.materials['窗外柔蓝天光'];p=shader(wm);p.inputs['Emission Strength'].default_value=.32
n=wm.node_tree.nodes;l=wm.node_tree.links;co=n.new('ShaderNodeTexCoord');se=n.new('ShaderNodeSeparateXYZ');r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.25,.32,.35,1);r.color_ramp.elements[1].color=(.55,.62,.64,1);l.new(co.outputs['Generated'],se.inputs[0]);l.new(se.outputs['Z'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color']);l.new(r.outputs[0],p.inputs['Emission Color'])
shader(bpy.data.materials['灯芯｜暖金']).inputs['Emission Strength'].default_value=1.5
shader(bpy.data.materials['灯芯｜暖金']).inputs['Emission Color'].default_value=(1,.50,.14,1)
for o in s.objects:
    if o.name.startswith('暖色灯芯'):o.scale*=.78
wm=bpy.data.materials.get('晶洞后窗日光')
if wm:shader(wm).inputs['Emission Strength'].default_value=.40
# 只在后半峡谷使用薄体积，前景保持清晰。
vol=bpy.data.materials.new('v2｜远峡薄雾');vol.use_nodes=True;n=vol.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');v=n.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.018;v.inputs['Color'].default_value=(.48,.63,.68,1);v.inputs['Anisotropy'].default_value=.25;vol.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume'])
box('v2后峡局部空气',(-.5,6.3,3),(6.5,7.5,3.4),vol,0)
# 主相机小幅降低，保留原始主要焦点布局。
cam=s.camera;cam.location=(9.0,-23.0,6.9);target=Vector((-.55,0,4.95));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=44;cam.data.shift_y=-.025
s.view_settings.exposure=0;s.view_settings.view_transform='AgX'
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=55;s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.max_bounces=10;s.cycles.transmission_bounces=8
try:
    pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
    for d in pref.devices:d.use=d.type=='METAL'
    if any(d.type=='METAL' for d in pref.devices):s.cycles.device='GPU'
except Exception as e:print('使用当前渲染设备：',e,flush=True)
s.render.filepath=os.path.join(OUT,'museum_preview_v2_01.png');s['版本']='v2';s['说明']='原画对照迭代：真实峡谷纵深、羽状蕨类、薄壳头骨、柜体浮雕与分组灯光。男孩未建模。'
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'museum_scene_v2.blend'))
with open(os.path.join(OUT,'inventory_v2.json'),'w') as f:json.dump({'对象数':len(s.objects),'网格数':sum(o.type=='MESH' for o in s.objects),'集合数':len(s.collection.children),'种子':91726,'状态':'首轮待视觉验证'},f,ensure_ascii=False,indent=2)
print('v2首轮场景保存完成，开始渲染',flush=True)
bpy.ops.render.render(write_still=True)
