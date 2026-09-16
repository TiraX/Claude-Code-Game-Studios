"""根据博物馆原画生成可编辑场景。运行：Blender --background --python 本文件。"""
import bpy, math, random, os, json, sys
from mathutils import Vector
from math import sin, cos, pi
random.seed(2616)
OUT = os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
COL = None

def group(name):
    global COL
    print('开始集合：',name,flush=True)
    COL = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(COL)

def finish(obj, name, mat=None):
    obj.name = name
    for c in list(obj.users_collection): c.objects.unlink(obj)
    COL.objects.link(obj)
    if mat: obj.data.materials.append(mat)
    return obj

def material(name, color, metal=0, rough=.5):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m

def textured(name, a, b, scale, rough=.6, metal=0, bump=.12):
    m=material(name,a,metal,rough); n=m.node_tree.nodes; l=m.node_tree.links
    tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=3.4; tex.inputs['Detail'].default_value=3
    coord=n.new('ShaderNodeTexCoord'); mapping=n.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=scale
    l.new(coord.outputs['Generated'],mapping.inputs[0]); l.new(mapping.outputs[0],tex.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.18; ramp.color_ramp.elements[0].color=(*a,1)
    ramp.color_ramp.elements[1].position=.83; ramp.color_ramp.elements[1].color=(*b,1)
    l.new(tex.outputs['Fac'],ramp.inputs[0]); p=n.get('Principled BSDF'); l.new(ramp.outputs[0],p.inputs['Base Color'])
    bu=n.new('ShaderNodeBump'); bu.inputs['Strength'].default_value=bump; bu.inputs['Distance'].default_value=.055
    l.new(tex.outputs['Fac'],bu.inputs['Height']); l.new(bu.outputs[0],p.inputs['Normal']); return m

wood=textured('深胡桃木｜顺纹',(.028,.012,.005),(.19,.082,.028),(1,28,35),.35,bump=.23)
wood_edge=textured('雕花木｜磨亮边缘',(.038,.017,.007),(.12,.053,.016),(2,3,25),.3)
wood_light=textured('抽屉老木面',(.065,.025,.009),(.255,.115,.047),(1,45,32),.42)
gold=textured('黄铜｜陈旧金属',(.19,.095,.023),(.62,.39,.12),(3,3,3),.27,.82,.08)
dark=material('缝隙阴影',(.009,.006,.004),0,.7)
stone=textured('博物馆暖灰石灰岩',(.19,.18,.15),(.39,.365,.30),(4,4,4),.84)
rockmat=textured('峡谷岩石',(.045,.065,.054),(.24,.26,.18),(4,4,6),.92,bump=.45)
moss=textured('湿润苔藓',(.025,.045,.009),(.17,.24,.029),(4,4,4),.9,bump=.3)
leafmats=[material('蕨叶'+str(i),c,0,.67) for i,c in enumerate([(.075,.15,.014),(.15,.22,.025),(.035,.09,.022),(.24,.29,.044)])]
bone=textured('古旧象牙骨质',(.29,.19,.086),(.72,.57,.31),(6,6,6),.49,bump=.15)
fur=textured('鹿毛｜暖棕',(.17,.073,.022),(.48,.29,.11),(4,4,12),.85,bump=.1)
fur_light=material('鹿腹浅毛',(.53,.40,.23),0,.88)
eye=material('眼与鼻',(.006,.004,.002),0,.15)
dinoskin=textured('恐龙皮肤',(.09,.115,.048),(.33,.35,.16),(10,10,10),.74,bump=.5)
water=material('山谷溪水',(.037,.20,.20),.3,.14); water.node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.28
crystal=material('青蓝晶体',(.06,.50,.58),.22,.16); cp=crystal.node_tree.nodes.get('Principled BSDF'); cp.inputs['Transmission Weight'].default_value=.3; cp.inputs['Emission Color'].default_value=(.02,.28,.33,1); cp.inputs['Emission Strength'].default_value=.22
bottle=material('古绿玻璃',(.08,.19,.10),.1,.2)
paper=material('泛黄纸张',(.51,.38,.19),0,.8)
bookmats=[material('书籍封面'+str(i),c,0,.65) for i,c in enumerate([(.11,.031,.019),(.045,.065,.039),(.15,.087,.027),(.032,.045,.06)])]

def emissive(name,c,power):
    m=material(name,c); p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=power; return m
amber=emissive('灯芯｜暖金', (1,.55,.17),5)
magic=emissive('森林精灵光',(.13,.85,1),7)
windowmat=emissive('窗外柔蓝天光',(.55,.73,.85),.8)
glass=material('透明展示玻璃',(.72,.84,.8),0,.1); gp=glass.node_tree.nodes.get('Principled BSDF'); gp.inputs['Transmission Weight'].default_value=1; gp.inputs['IOR'].default_value=1.45

def cube(n,loc,dim,mat,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=finish(bpy.context.object,n,mat); o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mo=o.modifiers.new('边缘倒角','BEVEL'); mo.width=bevel; mo.segments=2
        mo=o.modifiers.new('加权法线','WEIGHTED_NORMAL')
    return o

def uv(n,loc,sc,mat,seg=24,rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc)
    o=finish(bpy.context.object,n,mat); o.scale=sc
    for p in o.data.polygons:p.use_smooth=True
    return o

def ico(n,loc,sc,mat,sub=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,location=loc); o=finish(bpy.context.object,n,mat); o.scale=sc; o.rotation_euler=(random.random(),random.random(),random.random()); return o

def cyl(n,loc,r,depth,mat,vertices=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc); o=finish(bpy.context.object,n,mat)
    mo=o.modifiers.new('边缘柔化','BEVEL'); mo.width=.01; mo.segments=2
    for p in o.data.polygons:p.use_smooth=True
    return o

def beam(n,a,b,r,mat,r2=None):
    d=Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=r,radius2=r if r2 is None else r2,depth=d.length,location=(Vector(a)+Vector(b))/2)
    o=finish(bpy.context.object,n,mat); o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    for p in o.data.polygons:p.use_smooth=True
    return o

def tube(n,pts,r,mat):
    cu=bpy.data.curves.new(n,'CURVE'); cu.dimensions='3D'; cu.resolution_u=16; cu.bevel_depth=r; cu.bevel_resolution=3
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
    for p,co in zip(sp.bezier_points,pts):p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(n,cu); COL.objects.link(o); cu.materials.append(mat); return o

def tapered(n,pts,radii,mat):
    verts=[]; faces=[]; count=12
    for i,p in enumerate(pts):
        tang=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)])
        tang.normalize(); ref=Vector((0,1,0))
        if abs(tang.dot(ref))>.9:ref=Vector((1,0,0))
        u=tang.cross(ref).normalized(); v=tang.cross(u).normalized()
        for j in range(count): verts.append(Vector(p)+radii[i]*(u*cos(j*2*pi/count)+v*sin(j*2*pi/count)))
    for i in range(len(pts)-1):
        for j in range(count):faces.append((i*count+j,i*count+(j+1)%count,(i+1)*count+(j+1)%count,(i+1)*count+j))
    faces.extend([tuple(reversed(range(count))),tuple((len(pts)-1)*count+j for j in range(count))])
    me=bpy.data.meshes.new(n); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(n,me); COL.objects.link(o); me.materials.append(mat)
    sub=o.modifiers.new('有机曲面','SUBSURF'); sub.levels=2
    for p in me.polygons:p.use_smooth=True
    return o

def torus(n,loc,major,minor,mat,rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=32,minor_segments=8,location=loc,rotation=rot); return finish(bpy.context.object,n,mat)

def light(n,loc,color,power,size=1,target=None,kind='AREA'):
    data=bpy.data.lights.new(n,kind); data.energy=power; data.color=color
    if kind=='AREA':data.shape='DISK'; data.size=size
    else:data.shadow_soft_size=size
    o=bpy.data.objects.new(n,data); COL.objects.link(o); o.location=loc
    if target:o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    return o

def shell_handle(x,y,z,s=1):
    # 贝壳形黄铜抽屉拉手：前向四分之一球壳与弧边。
    verts=[]; faces=[]
    for i in range(9):
        a=i/8*pi/2
        for j in range(25):
            t=j/24*pi
            verts.append((x+.40*s*cos(t)*sin(a),y-.23*s*cos(a),z+.28*s*sin(t)*sin(a)))
    for i in range(8):
        for j in range(24): k=i*25+j; faces.append((k,k+1,k+26,k+25))
    me=bpy.data.meshes.new('贝壳曲面'); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new('黄铜贝壳拉手',me); COL.objects.link(o); me.materials.append(gold)
    for p in me.polygons:p.use_smooth=True
    tube('把手拱形镶边',[(x+.43*s*cos(t*pi/16),y-.008,z+.31*s*sin(t*pi/16)) for t in range(17)],.022*s,gold)
    beam('把手下沿',(x-.40*s,y-.02,z),(x+.40*s,y-.02,z),.022*s,gold)
    for dx in [-.43,.43]:uv('把手固定铆钉',(x+dx*s,y-.03,z+.02),(.037*s,.025*s,.04*s),gold,12,8)

def panel(n,x,y,z,w,h):
    cube(n,(x,y,z),(w,.19,h),wood_light)
    for dz in [-h/2+.08,h/2-.08]:cube('抽屉水平框线',(x,y-.12,z+dz),(w-.1,.06,.055),wood_edge,.01)
    for dx in [-w/2+.07,w/2-.07]:cube('抽屉竖框线',(x+dx,y-.12,z),(.055,.06,h-.1),wood_edge,.01)
    for dz in [-h*.23,h*.13]:cube('拼板接缝',(x,y-.098,z+dz),(w-.22,.005,.012),dark,0)
    shell_handle(x,y-.13,z-.08,min(1.2,w/2.4))

def trim(x,y,z,w,d):
    for off,extra,th in [(0,0,.15),(.11,.14,.09),(-.10,.08,.055)]:cube('层叠木线脚',(x,y,z+off),(w+extra,d+extra,th),wood_edge,.018)

def plaque(x,y,z,w,text):
    cube('黄铜展签',(x,y,z),(w,.018,.13),gold,.01)
    cu=bpy.data.curves.new('铭牌文字','FONT'); cu.body=text; cu.align_x='CENTER'; cu.size=.058; cu.extrude=.0005
    o=bpy.data.objects.new(text,cu); COL.objects.link(o); cu.materials.append(dark); o.location=(x,y-.014,z-.022); o.rotation_euler=(pi/2,0,0)

def lantern(x,y,z,s=1):
    cyl('灯座',(x,y,z-.34*s),.17*s,.07*s,gold)
    uv('暖色灯芯',(x,y,z),(.075*s,.075*s,.23*s),amber,12,8)
    for dx in [-1,1]:
        for dy in [-1,1]:beam('灯笼框架',(x+dx*.13*s,y+dy*.13*s,z-.3*s),(x+dx*.13*s,y+dy*.13*s,z+.3*s),.015*s,gold)
    bpy.ops.mesh.primitive_cone_add(vertices=6,radius1=.23*s,radius2=.075*s,depth=.18*s,location=(x,y,z+.36*s));finish(bpy.context.object,'灯笼铜顶',gold)
    torus('悬挂环',(x,y,z+.52*s),.08*s,.014*s,gold,(pi/2,0,0))
    light('灯笼暖光',(x,y-.04,z),(1,.58,.24),45*s*s,.22*s,kind='POINT')

# 建筑：石砖地面、左侧高窗和走廊。
group('01｜建筑与石砖')
cube('地面基底',(0,0,-.18),(27,22,.3),dark)
for i in range(-10,11):
    for j in range(-8,6):
        x=i*1.24+(j%2)*.62; y=j*1.12
        o=cube('磨损石砖',(x,y,-.025+random.uniform(-.006,.006)),(1.215,1.092,.12),stone,.025)
# 左侧墙位于 x=-8.5，窗户面朝场景内部。
for yy in [-5,-.7,3.6,7.9]:
    cube('石砌窗间墙',(-8.5,yy,6),(.6,.65,12),stone,.06)
    for zz in [1,3.9,7.1,10.5]:cube('柱身束带',(-8.15,yy,zz),(.9,.8,.16),stone)
for zz,hh in [(1.0,2),(5.0,.6),(11.6,1)]:cube('石墙水平带',(-8.55,1.5,zz),(.65,17,hh),stone)

def arch_window(y,z,w,h):
    # 尖拱轮廓，底部矩形，上部收尖。
    coords=[(-w/2,0),(-w/2,h*.65)]
    coords += [(-w/2*(1-t/10),h*.65+h*.35*sin(t/10*pi/2)) for t in range(1,11)]
    coords += [(w/2*(t/10),h*.65+h*.35*cos(t/10*pi/2)) for t in range(1,11)]
    coords += [(w/2,0)]
    verts=[(-8.48,y+u,z+v) for u,v in coords]
    me=bpy.data.meshes.new('尖拱窗玻璃'); me.from_pydata(verts,[],[tuple(range(len(verts)))]); me.update(); ob=bpy.data.objects.new('高侧窗',me); COL.objects.link(ob); me.materials.append(windowmat)
    tube('尖拱石质窗套',[(-8.12,y+u,z+v) for u,v in coords],.10,stone)
    for dx in [-.28,0,.28]:beam('窗棂',(-8.08,y+w*dx,z),(-8.08,y+w*dx,z+h*(.97-abs(dx)*.4)),.035,wood_edge)
    for dz in [.25,.50,.72]:beam('横向窗棂',(-8.07,y-w/2,z+h*dz),(-8.07,y+w/2,z+h*dz),.033,wood_edge)
    for dy in [-.28,.28]:tube('窗花分叉',[(-8.07,y+w*dy,z+h*.70),(-8.07,y+w*dy*.65,z+h*.84),(-8.07,y,z+h*.92)],.032,wood_edge)
for yy in [-2.85,1.45,5.75]:
    arch_window(yy,5.35,2.75,5.1); arch_window(yy,.25,2.75,4.2)
# 中层左侧廊道。
cube('左侧二层走廊',(-6.9,2.3,4.8),(3.1,14,.28),wood_edge)
for y in [i*.45-4.3 for i in range(31)]:
    beam('走廊栏杆',(-5.4,y,4.93),(-5.4,y,5.75),.045,wood_edge)
    uv('栏杆节点',(-5.4,y,5.38),(.07,.07,.09),wood_edge,12,8)
for z in [5.0,5.8]:beam('走廊扶手',(-5.4,-4.5,z),(-5.4,9,z),.085,wood_edge)
for yy in [-3,1.2,5.4]:
    tube('廊下拱撑',[(-8.1,yy,2.7),(-7.5,yy,4),(-6.5,yy,4.55),(-5.35,yy,4.65)],.13,wood_edge)
    lantern(-7.4,yy,6.3,.85)
# 背后的墙不使用原画贴图。
cube('背墙',(0,3.6,6),(18,.5,13),stone)

# 巨型柜体。
group('02｜巨型胡桃木收藏柜')
cube('柜体背板',(0,2.65,5.8),(12.7,.25,11.4),wood,.04)
for x in [-6.25,-2.6,2.25,5.55,6.25]:
    cube('贯通木立柱',(x,.08,5.8),(.25,.52,11.4),wood_edge)
    for z in [.5,4.6,8.7,10.7]:
        cube('柱头方座',(x,-.04,z),(.47,.68,.19),wood_edge)
        cube('柱头金饰',(x,-.4,z-.15),(.16,.04,.17),gold)
    for dx in [-.07,.07]:cube('立柱细槽',(x+dx,-.194,5.8),(.025,.014,10.5),gold,.004)
for z in [.35,4.5,8.6,10.7,11.3]:trim(0,1.25,z,12.7,3.0)
# 中层三个敞开场景的横隔板。
for x,w in [(-4.4,3.5),(-.15,4.6),(3.93,3.15)]:
    panel('中层抽屉',x,-.1,4.96,w,.78)
    panel('顶层抽屉',x,-.1,9.1,w,.74)
    cube('展区上盖',(x,1.2,8.6),(w,2.9,.20),wood)
    cube('展区地板',(x,1.2,5.39),(w,2.9,.15),wood)
# 最右侧雕花窄柜。
for z,h in [(2.2,3.1),(6.55,3.15),(10,1.2)]:
    cube('右侧窄柜门',(5.91,-.01,z),(.65,.19,h),wood)
    for dz in [-h*.4,h*.4]:tube('柜门卷草',[(5.66,-.13,z+dz),(5.8,-.18,z+dz+.13),(5.97,-.18,z+dz),(6.08,-.14,z+dz+.18)],.022,gold)
# 下层右侧工作室与储物格。
panel('右侧工作室抽屉',3.92,-.1,1.8,3.12,.72)
cube('右侧工作室底板',(3.9,1.15,2.2),(3.2,2.8,.14),wood)
# 下层左侧陈列橱。
for x in [-5.7,-4.6,-3.5]:
    for z in [.8,2.0,3.2,4.4]:cube('底层架板',(x,1.5,z),(.95,1.3,.08),wood)
# 恐龙主抽屉伸向前景。
trim(-.65,-.76,1.0,7.6,5.1)
cube('恐龙箱土层',(-.65,-.85,1.26),(7.4,5.0,.46),rockmat,.1)
panel('恐龙箱正面大抽屉',-.65,-3.39,.84,7.7,.85)
for x in [-4.43,3.13]:
    cube('恐龙抽屉侧板',(x,-.95,.85),(.16,4.9,.84),wood_light)
    for y in [-2.9,1]:
        cyl('抽屉铜脚',(x,y,.18),.3,.18,gold)
        uv('柜脚曲面',(x,y,.3),(.20,.20,.17),gold)
for y in [-2.4,-1.1,.3]:shell_handle(3.235,y,.8,.5) # 侧边装饰
# 左上向前伸出的鹿展柜。
trim(-4.12,-.55,5.3,3.8,3.95)
cube('森林展箱苔藓土层',(-4.12,-.6,5.53),(3.6,3.75,.26),moss,.1)
panel('鹿展区前抽屉',-4.12,-2.57,5.05,3.85,.65)
for x in [-6.06,-2.18]:
    cube('森林箱侧板',(x,-.55,5.06),(.14,3.9,.65),wood_light)
    cube('森林箱前细柱',(x,-2.37,7.13),(.12,.14,3.15),wood_edge)
trim(-4.12,-.55,8.76,4.05,4.1)
for x in [-6,-2.23]:tube('展柜弧形角撑',[(x,-2.32,7.5),(x,-2.32,8.15),(x+(.5 if x<-4 else -.5),-2.32,8.64)],.065,wood_edge)

# 岩石与植物。
def rock(n,loc,sc,mat=rockmat):return ico(n,loc,sc,mat,2)
def fern(x,y,z,s=1):
    verts=[]; faces=[]
    for j in range(7):
        a=j*2*pi/7+random.uniform(-.2,.2); length=s*random.uniform(.65,1.1)
        spine=[]
        for k in range(8):
            t=k/7; spine.append((x+cos(a)*length*t,y+sin(a)*length*t,z+s*(.55*sin(t*pi*.85)+.04)))
        tube('蕨叶主脉',spine,.008*s,leafmats[0])
        for k in range(1,7):
            t=k/7; p=Vector(spine[k]); side=Vector((-sin(a),cos(a),.2)); wid=s*.18*sin(t*pi)**.7
            for sign in [-1,1]:
                tip=p+side*wid*sign+Vector((cos(a),sin(a),.1))*s*.08
                q=len(verts); verts.extend([p-Vector((cos(a),sin(a),0))*.045*s,tip,p+Vector((cos(a),sin(a),0))*.07*s]); faces.append((q,q+1,q+2))
    me=bpy.data.meshes.new('蕨类羽状叶');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('蕨类叶片',me);COL.objects.link(o);me.materials.append(random.choice(leafmats))

def tree(x,y,z,s=1):
    beam('微缩树干',(x,y,z),(x+.05*s,y,z+1.15*s),.065*s,wood_edge,.025*s)
    for i in range(4):
        a=i*2.4; end=(x+cos(a)*.42*s,y+sin(a)*.42*s,z+s*(.72+i*.15))
        beam('树枝',(x,y,z+.55*s),end,.027*s,wood_edge,.008*s)
        for j in range(3):ico('树冠叶团',(end[0]+random.uniform(-.17,.17)*s,end[1]+random.uniform(-.17,.17)*s,end[2]+j*.08*s),(.33*s,.26*s,.17*s),random.choice(leafmats),1)

group('03｜恐龙山谷生态箱')
# 后部高峭壁，两侧递减，中间留出纵深。
for x,y,z,sx,sy,sz in [(-3.5,1.1,2.6,.85,.85,1.5),(-2.8,1.6,3.1,.62,.65,1.9),(1.65,1.3,2.7,.85,.72,1.5),(2.65,.8,2.35,.62,.9,1.2),(-3.7,-.4,1.8,.5,.6,.8),(2.7,-1.4,1.7,.5,.8,.5)]:
    rock('山谷峭壁',(x,y,z),(sx,sy,sz))
    for i in range(8):rock('峭壁苔藓',(x+random.uniform(-sx,sx)*.7,y-.4,z+random.uniform(-sz,sz)*.75),(.25,.16,.12),moss)
# 水流是独立曲面，中心向前蜿蜒。
verts=[]
for i in range(24):
    y=1.55-i*.20; center=-.4+.43*sin(i*.24); w=.32+.12*sin(i*.3)
    verts.extend([(center-w,y,1.512),(center+w,y,1.512)])
me=bpy.data.meshes.new('蜿蜒溪流');me.from_pydata(verts,[],[(2*i,2*i+1,2*i+3,2*i+2) for i in range(23)]);me.update();o=bpy.data.objects.new('山谷溪流',me);COL.objects.link(o);me.materials.append(water)
for i in range(115):
    x=random.uniform(-4.15,2.95);y=random.uniform(-3.14,1.45)
    if abs(x-(-.4+.43*sin((1.55-y)/.2*.24)))<.5:continue
    rock('山谷苔藓石',(x,y,1.49),(random.uniform(.12,.38),random.uniform(.12,.33),random.uniform(.07,.19)),moss if i%3 else rockmat)
for i in range(38):
    x=random.uniform(-4,2.85); y=random.uniform(-3.1,1.3)
    if abs(x+.4)>.7:fern(x,y,1.58,random.uniform(.23,.48))
for x,y,s in [(-3.4,.4,1),(-2.4,1.5,1.3),(1.2,1.5,1.1),(2.4,.2,.9),(-3.8,-1.4,.6)]:tree(x,y,1.5,s)
# 岩壁背面有独立远山几何，不用平面背景冒充景深。
for x in [-2,-1,0,1]:rock('远山',(x,2.15,2.7),(random.uniform(.6,.9),.27,random.uniform(.9,1.4)))

def dinosaur(n,origin,s=1,flip=1):
    ox,oy,oz=origin
    def p(x,y,z):return (ox+x*s*flip,oy+y*s,oz+z*s)
    uv(n+'躯干',p(0,0,.9),(.68*s,.30*s,.36*s),dinoskin)
    tapered(n+'长颈',[p(.37,0,1),p(.6,0,1.25),p(.79,0,1.6),p(.9,0,1.94),p(1.1,0,2.10),p(1.25,0,2.09)],[v*s for v in [.26,.23,.18,.12,.105,.09]],dinoskin)
    uv(n+'头',p(1.29,-.01,2.09),(.18*s,.105*s,.095*s),dinoskin)
    tapered(n+'长尾',[p(-.46,0,.96),p(-.85,0,.92),p(-1.24,.04,.82),p(-1.58,.12,.94),p(-1.87,.16,1.14)],[v*s for v in [.23,.16,.10,.048,.008]],dinoskin)
    for xx in [-.4,.39]:
        for yy in [-.21,.21]:
            bend=.1 if yy<0 else -.08
            tapered(n+'腿',[p(xx,yy,.85),p(xx+bend,yy,.46),p(xx-.04,yy,.13),p(xx+.04,yy,.09)],[v*s for v in [.16,.12,.078,.09]],dinoskin)
            uv(n+'脚',p(xx+.03,yy,.09),(.16*s,.095*s,.085*s),dinoskin,16,10)
    for yy in [-.095,.095]:uv(n+'眼',p(1.30,yy,2.12),(.018*s,.012*s,.018*s),eye,12,8)
    for i in range(13):uv(n+'背脊鳞',p(-.65+i*.09,0,1.2+.05*sin(i/13*pi)),(.04*s,.04*s,.055*s),rockmat,12,8)
dinosaur('远景长颈龙',(-1.8,.42,1.52),.84,1)
dinosaur('近景长颈龙',(1.55,-1.75,1.55),.83,-1)
# 山谷前护栏。
for x in [i*.72-4.13 for i in range(11)]:
    beam('展台细栏杆',(x,-3.23,1.34),(x,-3.23,1.91),.019,gold);uv('栏杆铜球',(x,-3.23,1.91),(.04,.04,.04),gold,12,8)
beam('展台前扶手',(-4.2,-3.23,1.9),(3,-3.23,1.9),.023,gold)
plaque(-.68,-3.51,1.0,1.65,'THE LOST VALLEY')

# 鹿生态箱。
group('04｜双鹿森林生态箱')
for i in range(56):rock('森林苔藓石',(-4.1+random.uniform(-1.65,1.65),random.uniform(-2.35,1.1),5.72),(random.uniform(.15,.4),random.uniform(.13,.33),random.uniform(.09,.25)),moss)
for i in range(22):fern(random.uniform(-5.8,-2.45),random.uniform(-2.25,1.1),5.8,random.uniform(.22,.42))
for x in [-5.7,-4.7,-2.65]:tree(x,.95,5.76,1.3)
# 后景盘绕枯木。
for i in range(7):tube('盘绕古木',[(-5.8,1,5.8),(-4.7+i*.12,.95,6.1),(-3.2,.85,6.8+i*.06),(-2.5,.8,6.6+i*.06)],.035,wood_edge)

def deer(n,origin,s=1,rest=False):
    ox,oy,oz=origin
    def p(x,y,z):return (ox+x*s,oy+y*s,oz+z*s)
    bodyz=.34 if rest else .94
    uv(n+'躯干',p(-.1,0,bodyz),(.52*s,.235*s,.28*s),fur)
    uv(n+'腹部',p(-.06,-.015,bodyz-.12),(.39*s,.205*s,.15*s),fur_light)
    necktop=bodyz+.58
    tapered(n+'颈部',[p(.23,0,bodyz),p(.37,0,bodyz+.27),p(.4,0,necktop)],[.22*s,.16*s,.105*s],fur)
    uv(n+'头',p(.44,-.02,necktop+.05),(.20*s,.12*s,.14*s),fur)
    uv(n+'吻部',p(.60,-.025,necktop+.015),(.13*s,.08*s,.08*s),fur_light)
    uv(n+'鼻',p(.70,-.03,necktop+.025),(.045*s,.058*s,.04*s),eye)
    for yy in [-.105,.105]:
        uv(n+'眼',p(.49,yy,necktop+.09),(.026*s,.014*s,.029*s),eye,12,8)
        o=uv(n+'耳',p(.32,yy*1.9,necktop+.15),(.145*s,.058*s,.057*s),fur);o.rotation_euler[1]=-.4
    for xx in [-.4,.24]:
        for yy in [-.16,.16]:
            if rest:
                tapered(n+'收拢腿',[p(xx,yy,.32),p(xx+.26,yy,.12),p(xx-.04,yy,.1)],[.1*s,.06*s,.04*s],fur)
            else:
                tapered(n+'细腿',[p(xx,yy,.86),p(xx-.08,yy,.47),p(xx+.015,yy,.10)],[.10*s,.057*s,.034*s],fur)
                uv(n+'蹄',p(xx+.03,yy,.055),(.067*s,.05*s,.053*s),wood_edge,12,8)
    uv(n+'短尾',p(-.65,0,bodyz+.03),(.14*s,.09*s,.07*s),fur_light)
    for side in [-1,1]:
        yy=side*.1
        trunk=[p(.34,yy,necktop+.14),p(.22,yy*2,necktop+.43),p(.06,yy*3,necktop+.74),p(-.08,yy*3.8,necktop+.99),p(-.22,yy*4,necktop+1.18)]
        tapered(n+'主鹿角',trunk,[v*s for v in [.05,.042,.03,.016,.002]],bone)
        for k in range(1,4):
            root=Vector(trunk[k]); tip=root+Vector((.24*s,side*.10*s,.24*s))
            tapered(n+'分叉鹿角',[root,root+Vector((.14*s,side*.03*s,.12*s)),tip],[.024*s,.015*s,.001*s],bone)
            if k==2:tapered(n+'鹿角细叉',[root,root+Vector((-.19*s,side*.09*s,.21*s)),root+Vector((-.24*s,side*.11*s,.34*s))],[.02*s,.014*s,.001*s],bone)
deer('站立雄鹿',(-4.95,-1.25,5.88),.98)
deer('卧姿雄鹿',(-3.45,-1.2,5.90),.78,True)
for i in range(9):
    loc=(random.uniform(-5.6,-2.6),random.uniform(-1.8,.5),random.uniform(6.15,7.9));uv('青色森林光点',loc,(.025,.025,.025),magic,12,8)
plaque(-4.13,-2.7,5.13,1.5,'THE ENCHANTED GROVE')

# 室内物件与收藏架。
def jar(x,y,z,s=.15):
    cyl('标本瓶',(x,y,z+s),s*.52,s*1.65,bottle,12);cyl('标本瓶塞',(x,y,z+s*1.92),s*.38,s*.24,gold,12)
    cube('瓶身标签',(x,y-s*.53,z+s),(.62*s,.007,.57*s),paper,.003)
def books(x,y,z,w,h):
    pos=x-w/2
    while pos<x+w/2-.1:
        bw=random.uniform(.07,.13);bh=random.uniform(h*.6,h)
        o=cube('古籍',(pos+bw/2,y,z+bh/2),(bw,.23,bh),random.choice(bookmats),.008)
        for dz in [.07,bh-.06]:cube('书脊烫金',(pos+bw/2,y-.12,z+dz),(bw*.85,.009,.012),gold,.001)
        pos+=bw+.017

def shelf(x,y,z,w,h,rows=3):
    cube('书架背板',(x,y+.13,z+h/2),(w,.12,h),wood)
    for xx in [x-w/2,x+w/2]:cube('书架侧板',(xx,y,z+h/2),(.075,.5,h),wood_edge)
    for i in range(rows+1):
        zz=z+i*h/rows;cube('书架横板',(x,y,zz),(w,.5,.075),wood_edge)
        if i<rows:
            if i%2:books(x,y-.05,zz+.045,w-.12,h/rows*.8)
            else:
                for j in range(max(2,int(w/.28))):jar(x-w/2+.16+j*.28,y-.09,zz+.04,.12+random.random()*.04)

def desk(x,y,z,w):
    cube('工作台台面',(x,y,z+ .82),(w,.82,.11),wood_light)
    for xx in [-w/2+.12,w/2-.12]:
        for yy in [-.3,.3]:cube('工作台腿',(x+xx,y+yy,z+.4),(.09,.09,.82),wood_edge)
    for xx in [-w*.27,0,w*.27]:
        cube('书桌小抽屉',(x+xx,y-.42,z+.66),(w*.24,.08,.23),wood);uv('小铜拉钮',(x+xx,y-.48,z+.66),(.04,.03,.035),gold)
    for i in range(4):cube('研究纸页',(x-.35+i*.12,y-.12+i*.07,z+.884+i*.005),(.42,.32,.004),paper,.001)
    jar(x+w*.34,y,z+.88,.13)

def chair(x,y,z):
    cube('椅座',(x,y,z+.42),(.44,.45,.09),wood_edge)
    for dx in [-.17,.17]:
        for dy in [-.17,.17]:beam('椅脚',(x+dx,y+dy,z),(x+dx,y+dy,z+.43),.027,wood_edge)
    for dx in [-.19,.19]:beam('椅背立柱',(x+dx,y+.18,z+.4),(x+dx,y+.18,z+1.0),.026,wood_edge)
    cube('椅背',(x,y+.18,z+.83),(.39,.065,.22),wood_light,.07)

group('05｜角龙头骨研究室')
shelf(-.22,2.37,5.5,4.15,2.83,4)
for x in [-2.25,1.85]:lantern(x,.6,6.85,.68)
desk(-.15,.95,5.5,3.1);chair(.95,-.05,5.48)
# 骨架展示基座。
cube('头骨基座',(-.2,.52,6.47),(2.35,1,.13),wood_edge)
for x in [-.75,.5]:beam('头骨铜支撑',(x,.58,6.5),(x,.58,7.04),.036,gold)
# 头骨局部坐标：鼻朝左，眼窝朝相机。
base=Vector((-.1,.38,7.13)); skullparts=[]
def skull_uv(n,p,sc):
    o=uv(n,base+Vector(p),sc,bone,32,20);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.select_set(False);return o
cranium=skull_uv('角龙头骨主体',(-.14,0,0),(.68,.33,.39))
snout=skull_uv('角龙喙鼻',(-.73,-.035,-.16),(.48,.28,.22))
# 真实布尔孔洞，避免画黑圆假装眼窝。
def carve(obj,loc,sc):
    cut=uv('临时开孔刀具',loc,sc,None,24,16)
    bpy.context.view_layer.objects.active=cut;cut.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);cut.select_set(False)
    mod=obj.modifiers.new('骨骼孔洞','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
carve(cranium,base+Vector((-.27,-.29,.10)),(.20,.30,.185))
carve(snout,base+Vector((-.86,-.22,-.1)),(.18,.18,.095))
# 颈盾在 YZ 平面展开，边缘具有骨刺。
verts=[];faces=[]
for layer in [0,1]:
    for r in [0,.5,1]:
        for i in range(48):
            a=i*2*pi/48;scallop=1+.055*cos(a*12)
            verts.append((base.x+.36+layer*.12-.12*r,base.y+cos(a)*.53*r*scallop,base.z+.12+sin(a)*.69*r*scallop))
for layer in [0,1]:
    for k in range(2):
        for i in range(48):a=layer*144+k*48+i;b=layer*144+k*48+(i+1)%48;faces.append((a,b,b+48,a+48))
for i in range(48):faces.append((96+i,96+(i+1)%48,240+(i+1)%48,240+i))
me=bpy.data.meshes.new('颈盾骨板');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('扇形角龙颈盾',me);COL.objects.link(o);me.materials.append(bone)
for i in range(14):
    a=i/14*2*pi
    tapered('颈盾边缘骨刺',[base+Vector((.32,cos(a)*.51,.12+sin(a)*.67)),base+Vector((.3,cos(a)*.62,.12+sin(a)*.80))],[.065,.003],bone)
for yy in [-.22,.22]:
    tapered('角龙眉角',[base+Vector((-.02,yy,.26)),base+Vector((-.35,yy,.62)),base+Vector((-.72,yy,.82))],[.14,.075,.001],bone)
tapered('角龙鼻角',[base+Vector((-.76,0,-.015)),base+Vector((-.89,0,.2)),base+Vector((-1.02,0,.31))],[.10,.06,.001],bone)
tapered('头骨下颌',[base+Vector((.10,-.04,-.25)),base+Vector((-.25,-.04,-.43)),base+Vector((-.77,-.04,-.37)),base+Vector((-1.12,-.04,-.24))],[.10,.075,.06,.028],bone)
for i in range(12):uv('角龙齿列',base+Vector((-.86+i*.06,-.21,-.30)),(.026,.026,.045),bone,12,8)
plaque(-.4,-.28,5.14,1.5,'TRICERATOPS • STUDY')
beam('研究室前护栏',(-2.4,-.43,5.91),(2,-.43,5.91),.022,gold)
for x in [-2.4,-1.65,-.9,-.15,.6,1.35,2]:beam('研究室护栏柱',(x,-.43,5.43),(x,-.43,5.94),.018,gold)

# 水晶洞。
group('06｜青蓝水晶岩洞')
for i in range(23):rock('水晶洞岩层',(random.uniform(2.5,5.3),random.uniform(.1,2.15),5.65+random.uniform(0,.35)),(random.uniform(.25,.65),random.uniform(.25,.5),random.uniform(.15,.5)))
for x,z in [(2.6,6.2),(5.1,6.5),(4.85,7.1),(5.15,7.75)]:rock('洞穴侧崖',(x,1.85,z),(.4,.6,.55))

def gem(loc,r,h,angle):
    verts=[]
    for zz,rr in [(0,r*.75),(h*.73,r),(h*.84,r*.83)]:
        for i in range(6):verts.append((rr*cos(i*pi/3),rr*sin(i*pi/3),zz))
    verts.append((0,0,h));faces=[tuple(reversed(range(6)))]
    for k in range(2):
        for i in range(6):faces.append((k*6+i,k*6+(i+1)%6,(k+1)*6+(i+1)%6,(k+1)*6+i))
    for i in range(6):faces.append((12+i,12+(i+1)%6,18))
    me=bpy.data.meshes.new('六方晶体');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('青蓝石英晶簇',me);COL.objects.link(o);me.materials.append(crystal);o.location=loc;o.rotation_euler=angle
for i in range(15):
    a=i*2.399;rr=.5*math.sqrt(i/15);gem((3.75+rr*cos(a),.75+rr*sin(a),5.98),random.uniform(.10,.20),1.65 if i==0 else random.uniform(.42,1.18),(sin(a)*.35,cos(a)*.35,a))
for i in range(8):fern(random.uniform(2.6,5.2),1.7,6.2,.35)
light('晶洞青光',(3.7,.6,6.9),(.19,.72,1),65,.55,kind='POINT')
plaque(3.92,-.24,5.15,1.4,'AZURE CRYSTALS')

# 右侧书房与顶层小藏品。
group('07｜书房与藏品')
shelf(3.88,2.3,2.22,2.75,2.04,3);shelf(5.13,.85,2.25,.4,1.9,3)
desk(3.8,.96,2.24,2.5);chair(4.55,.25,2.23);lantern(3.7,.91,3.5,.57)
for x in [-4.4,-.2,3.9]:shelf(x,1.85,9.52,3.0,1.55,2)
for x in [-5.7,-4.6,-3.5]:
    for z in [.85,2.05,3.25]:
        for j in range(3):jar(x-.3+j*.3,1.02,z,.13)
for x in [-4.9,-1.7,1.2,4.7]:lantern(x,.35,10.25,.47)

# 从地面到研究室的折返楼梯。
group('08｜木阶与黄铜楼梯')
def staircase(points,width=.69):
    for a,b in zip(points[:-1],points[1:]):
        a=Vector(a);b=Vector(b);d=b-a;flat=Vector((d.x,d.y,0)).normalized();side=Vector((-flat.y,flat.x,0)); steps=max(2,round(abs(d.z)/.19))
        for i in range(steps):
            t=(i+.5)/steps;p=a+d*t;depth=Vector((d.x,d.y,0)).length/steps+.06
            o=cube('独立木踏板',p,(width,depth,.105),wood_light,.02);o.rotation_euler.z=math.atan2(-flat.x,flat.y)
            beam('踏板黄铜鼻口',p-flat*depth*.43-side*width*.5+Vector((0,0,.06)),p-flat*depth*.43+side*width*.5+Vector((0,0,.06)),.012,gold)
        for sign in [-1,1]:
            p=a+side*width*.48;q=b+side*width*.48
            beam('斜向楼梯侧梁',p-Vector((0,0,.12)),q-Vector((0,0,.12)),.067,wood_edge)
            beam('楼梯黄铜扶手',p+Vector((0,0,.75)),q+Vector((0,0,.75)),.026,gold)
            beam('楼梯中横杆',p+Vector((0,0,.38)),q+Vector((0,0,.38)),.011,gold)
            for i in range(0,steps+1,2):
                r=p+(q-p)*i/steps;beam('楼梯栏杆',r,r+Vector((0,0,.77)),.015,gold);uv('楼梯栏杆节点',r+Vector((0,0,.65)),(.026,.026,.04),gold,12,8)
# 低层从右前方向柜体中部上升，上层向后折返至头骨展区。
staircase([(5.95,-3.28,.20),(5.65,-2.28,1.28),(4.22,-1.6,2.72),(2.46,-1.08,4.15),(2.39,.38,5.46)])
for p in [(5.65,-2.28,1.28),(4.22,-1.6,2.72),(2.46,-1.08,4.15)]:cube('楼梯转折踏台',p,(.77,.75,.12),wood_edge)
for x,y,z in [(5.83,-2.98,.17),(4.25,-1.6,2.7),(2.45,-1.08,4.13)]:
    beam('楼梯支撑柱',(x,y,.13),(x,y,z),.037,gold);cyl('楼梯铜脚',(x,y,.10),.16,.12,gold)

# 玻璃立柜、骨骼标本和大厅灯具。
group('09｜大厅标本柜与灯具')
x,y=7.0,-.12
cyl('圆形标本柜木座',(x,y,.48),.71,.85,wood_edge,12)
for z in [.08,.88,3.76]:cyl('标本柜铜环',(x,y,z),.73,.10,gold,48)
# 圆柱玻璃只保留侧壁。
verts=[];faces=[]
for z in [.93,3.73]:
    for i in range(64):verts.append((x+.67*cos(i*2*pi/64),y+.67*sin(i*2*pi/64),z))
for i in range(64):faces.append((i,(i+1)%64,64+(i+1)%64,64+i))
me=bpy.data.meshes.new('圆筒玻璃');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('标本柜透明玻璃',me);COL.objects.link(ob);me.materials.append(glass)
for a in [0,pi/2,pi,pi*1.5]:beam('玻璃柜铜立柱',(x+.68*cos(a),y+.68*sin(a),.9),(x+.68*cos(a),y+.68*sin(a),3.76),.035,gold)
bpy.ops.mesh.primitive_cone_add(vertices=48,radius1=.72,radius2=.16,depth=.35,location=(x,y,3.97));finish(bpy.context.object,'铜制标本柜顶',gold)
uv('柜顶铜钮',(x,y,4.19),(.08,.08,.10),gold)
for i in range(23):
    z=1.1+i*.1;xx=x+.17*sin(i*.12)
    uv('标本脊椎',(xx,y,z),(.09,.075,.05),bone,12,8)
    if i<17:
        for side in [-1,1]:tube('标本肋骨',[(xx,y,z),(xx+side*.22,y-.01,z-.04),(xx+side*.29,y-.15,z-.14)],.018,bone)
beam('标本支杆',(x,y+.1,.96),(x,y+.1,3.5),.022,gold)
light('标本柜内暖光',(x,y,3.55),(1,.65,.27),35,.3,kind='POINT')
for xx,yy,zz,s in [(-5.7,-1,10.6,1.3),(-3.1,-.5,11.3,1.0),(-7,-3.5,9.5,1)]:
    lantern(xx,yy,zz,s);beam('吊灯链',(xx,yy,zz+.55*s),(xx,yy,13),.019,gold)
# 左侧独立标本柜与前景栏杆。
cube('左侧标本台',(-7,-1,.53),(1.1,1.0,1.05),wood_edge)
for x in [-7.5,-6.5]:
    for y in [-1.4,-.6]:beam('标本台立柱',(x,y,1),(x,y,2.8),.038,gold)
trim(-7,-1,2.82,1.2,1.05)
for i in range(9):beam('左柜珊瑚枝',(-7,-1,1.1+i*.12),(-7+sin(i*2.4)*.32,-1+cos(i*2.4)*.28,1.45+i*.12),.025,bone,.006)
for xx in [-7.6,-5.8]:
    cube('前景栏杆柱',(xx,-6,.62),(.26,.3,1.24),wood_edge);uv('前景铜球',(xx,-6,1.35),(.15,.15,.16),gold)
for z in [.25,1.0]:cube('前景木扶手',(-6.7,-6,z),(2,.22,.16),wood_edge)
# 极少量垂藤。
for i in range(4):
    x=-7.9+i*.21;y=-.7
    tube('高窗垂藤',[(x,y,10.4),(x+.1,y,9.5),(x-.2,y,8.7),(x+.15,y,7.9)],.021,wood_edge)
    for j in range(15):ico('藤叶',(x+random.uniform(-.17,.17),y-.02,10.3-j*.16),(.105,.035,.085),random.choice(leafmats),1)

# 灯光、相机和输出。
group('10｜灯光与相机')
light('左窗漫射天光',(-6.9,-3,8),(.62,.76,1),1900,5,(0,0,4.5))
light('正面柔光',(1,-9,8),(1,.79,.55),1450,7,(0,0,4.8))
light('顶层暖反光',(0,-1,11.5),(1,.65,.33),850,5,(0,0,5))
light('山谷内部冷天光',(-.6,.5,4.25),(.52,.76,.87),320,3,(-.6,-1,1.5))
light('鹿箱顶部光',(-4.1,-.5,8.45),(1,.79,.46),220,2,(-4,-1,6))
light('头骨重点灯',(-.5,-.6,8.3),(1,.72,.39),210,1.8,(-.2,.4,7.1))
light('晶洞顶光',(4,.4,8.35),(.67,.85,1),160,1.4,(3.8,.8,6.1))
world=bpy.data.worlds.new('博物馆低亮环境');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.17,.20,1);world.node_tree.nodes['Background'].inputs[1].default_value=.22;bpy.context.scene.world=world
bpy.ops.object.camera_add(location=(12.8,-25.5,10.1));cam=finish(bpy.context.object,'原画匹配主相机');target=Vector((-.8,0,5.55));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=43
scene=bpy.context.scene;scene.camera=cam;scene.unit_settings.system='METRIC'
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.cycles.max_bounces=8;scene.cycles.transmission_bounces=6
# Metal 可用时使用，否则保留 CPU。
try:
    pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='METAL';pref.get_devices()
    usable=[d for d in pref.devices if d.type=='METAL']
    if usable:
        for d in pref.devices:d.use=d.type=='METAL'
        scene.cycles.device='GPU'
except Exception as e:print('Metal 未启用：',e)
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=60
scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(OUT,'museum_preview_v01.png')
# 光晕限制在灯芯和精灵光点。
nt=bpy.data.node_groups.new('博物馆柔光合成','CompositorNodeTree'); scene.compositing_node_group=nt; nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor'); rl=nt.nodes.new('CompositorNodeRLayers'); gl=nt.nodes.new('CompositorNodeGlare'); gl.inputs['Type'].default_value='Fog Glow'; gl.inputs['Quality'].default_value='High'; gl.inputs['Strength'].default_value=.25; comp=nt.nodes.new('NodeGroupOutput'); nt.links.new(rl.outputs['Image'],gl.inputs['Image']); nt.links.new(gl.outputs['Image'],comp.inputs['Image'])
# 保存原画为独立参考图像数据块，不参与场景渲染。
ref=os.path.abspath(os.path.join(OUT,'../../../../design/concept-art/magic-museum/revision-06/ig_0e67d2d915f89549016a26534d45fc819a80e6cad97938c924.png'))
if os.path.exists(ref):im=bpy.data.images.load(ref);im.name='原画参考｜不参与渲染';im.use_fake_user=True;im.pack()
scene['说明']='根据指定原画制作的巨型胡桃木博物柜场景；男孩角色未建模。制作记录见 museum_build.md。'
scene['随机种子']=2616
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'museum_scene.blend'))
stats={'对象数':len(scene.objects),'网格数':sum(o.type=='MESH' for o in scene.objects),'材质数':len(bpy.data.materials),'集合':[c.name for c in scene.collection.children],'渲染器':scene.render.engine,'Blender版本':bpy.app.version_string}
with open(os.path.join(OUT,'scene_inventory.json'),'w') as f:json.dump(stats,f,ensure_ascii=False,indent=2)
print('场景保存完成',stats)
bpy.ops.render.render(write_still=True)
