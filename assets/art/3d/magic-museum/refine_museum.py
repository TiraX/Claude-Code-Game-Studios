"""第二轮原画对照调整；在首轮场景上运行一次。"""
import bpy, math, random, os, ast
from mathutils import Vector
from math import sin,cos,pi
OUT=os.path.dirname(os.path.abspath(__file__))
random.seed(2617)
# 复用几何函数，避免执行重置场景的构建代码。
source=ast.parse(open(os.path.join(OUT,'build_museum.py')).read())
COL=None
wood=bpy.data.materials['深胡桃木｜顺纹'];wood_edge=bpy.data.materials['雕花木｜磨亮边缘'];wood_light=bpy.data.materials['抽屉老木面'];gold=bpy.data.materials['黄铜｜陈旧金属'];stone=bpy.data.materials['博物馆暖灰石灰岩'];dark=bpy.data.materials['缝隙阴影'];bone=bpy.data.materials['古旧象牙骨质'];moss=bpy.data.materials['湿润苔藓'];rockmat=bpy.data.materials['峡谷岩石'];leafmats=[bpy.data.materials['蕨叶'+str(i)] for i in range(4)]
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<geometry_helpers>','exec'))
# 胡桃木整体压暗，同时降低过白的骨质和过亮的草绿。
for mat,factor in [(wood,.40),(wood_edge,.38),(wood_light,.42),(bone,.64),(moss,.58)]:
    for n in mat.node_tree.nodes:
        if n.type=='VALTORGB':
            for e in n.color_ramp.elements:e.color=tuple(v*factor for v in e.color[:3])+(1,)
for m in leafmats:
    p=m.node_tree.nodes.get('Principled BSDF'); c=p.inputs['Base Color'].default_value; p.inputs['Base Color'].default_value=tuple(v*.62 for v in c[:3])+(1,)
for name,factor in [('左窗漫射天光',.75),('正面柔光',.33),('顶层暖反光',.45),('头骨重点灯',.68),('鹿箱顶部光',.78)]:bpy.data.objects[name].data.energy*=factor
# 从较低机位接近柜体，画幅改为原画的 16:9。
s=bpy.context.scene;cam=s.camera;cam.location=(9.4,-22,7.6);target=Vector((-.45,-.1,5.0));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=46
# 场景使用者可以在图像编辑器直接找到原画；必须持久保留未链接图像。
ref=os.path.abspath(os.path.join(OUT,'../../../../design/concept-art/magic-museum/revision-06/ig_0e67d2d915f89549016a26534d45fc819a80e6cad97938c924.png'))
im=bpy.data.images.load(ref,check_existing=True);im.name='原画参考｜不参与渲染';im.use_fake_user=True;im.pack()
# 岩石增加小尺度不规则表面，消除干净的多面球轮廓。
tex=bpy.data.textures.new('岩石侵蚀纹理',type='CLOUDS');tex.noise_scale=.28;tex.noise_depth=2
for o in list(s.objects):
    if o.type=='MESH' and any(o.name.startswith(n) for n in ['山谷峭壁','洞穴侧崖','水晶洞岩层','远山','森林苔藓石','山谷苔藓石']):
        sub=o.modifiers.new('岩面细分','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=1
        dis=o.modifiers.new('风化岩面','DISPLACE');dis.texture=tex;dis.strength=.15;dis.texture_coords='LOCAL'
        for p in o.data.polygons:p.use_smooth=True
# 把几何树冠转换为高密度叶片簇，保留原分枝与分布。
COL=bpy.data.collections['04｜双鹿森林生态箱']
for old in list(s.objects):
    if not old.name.startswith('树冠叶团'):continue
    verts=[];faces=[];center=old.location.copy();scale=old.scale.copy();col=old.users_collection[0]
    for j in range(75):
        a=random.random()*2*pi; v=random.uniform(-1,1);rr=random.random()**.33
        pos=center+Vector((cos(a)*math.sqrt(1-v*v)*scale.x*rr,sin(a)*math.sqrt(1-v*v)*scale.y*rr,v*scale.z*rr))
        u=Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-.3,.5))).normalized()*.10
        v2=Vector((-u.y,u.x,.03))* .47
        k=len(verts);verts.extend([pos-u,pos-v2,pos+u,pos+v2,pos+Vector((0,0,.018))]);faces.extend([(k,k+1,k+4),(k+1,k+2,k+4),(k+2,k+3,k+4),(k+3,k,k+4)])
    me=bpy.data.meshes.new('树冠细叶');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('树冠细密叶簇',me);col.objects.link(ob);me.materials.append(random.choice(leafmats));bpy.data.objects.remove(old,do_unlink=True)
# 增加地被的轮廓复杂度，避开溪流与主要动物。
COL=bpy.data.collections['03｜恐龙山谷生态箱']
for i in range(32):
    x=random.uniform(-4.08,2.95);y=random.uniform(-3.07,1.3)
    if abs(x+.4)>.65:fern(x,y,1.65,random.uniform(.28,.52))
COL=bpy.data.collections['04｜双鹿森林生态箱']
for i in range(18):fern(random.uniform(-5.9,-2.35),random.uniform(-.4,1.15),5.86,random.uniform(.32,.58))
# 背景森林灌木与岩壁覆盖后板。
for i in range(16):
    x=random.uniform(-5.88,-2.4);z=random.uniform(6,8.2)
    rock('森林背景覆苔岩',(x,1.45,z),(random.uniform(.25,.5),.20,random.uniform(.25,.6)),moss if i%3 else rockmat)
# 小枝、碎石与恐龙皮肤鳞片提供近景尺度。
COL=bpy.data.collections['03｜恐龙山谷生态箱']
for i in range(45):
    x=random.uniform(-4,2.8);y=random.uniform(-3.15,1.4)
    rock('溪谷碎石',(x,y,1.57),(random.uniform(.035,.08),random.uniform(.035,.08),random.uniform(.02,.06)),rockmat)
# 柜体增加卷草、抽屉钉、角部铜件与雕刻纹路。
COL=bpy.data.collections['02｜巨型胡桃木收藏柜']
for x,y,z,w,h in [(-.65,-3.51,.84,7.7,.85),(-4.12,-2.7,5.05,3.85,.65),(-.15,-.24,4.96,4.6,.78),(3.93,-.24,4.96,3.15,.78),(-4.4,-.24,9.1,3.5,.74),(-.15,-.24,9.1,4.6,.74),(3.93,-.24,9.1,3.15,.74)]:
    for side in [-1,1]:
        cx=x+side*w*.43
        for dz in [-h*.31,h*.31]:uv('抽屉铜钉',(cx,y-.014,z+dz),(.022,.014,.022),gold,12,8)
        tube('抽屉角部卷草',[(cx-side*.22,y-.025,z-h*.25),(cx,y-.025,z-h*.25),(cx+side*.045,y-.025,z),(cx-side*.08,y-.025,z+h*.12),(cx-side*.16,y-.025,z+.025)],.012,gold)
for x in [-6.25,-2.6,2.25,5.55,6.25]:
    for z in [4.5,8.6,10.7]:
        for sign in [-1,1]:tube('柱头雕花',[(x,-.31,z-.12),(x+sign*.12,-.34,z-.2),(x+sign*.11,-.34,z-.4),(x+sign*.035,-.34,z-.49)],.019,gold)
# 增加侧墙石砌实体和拱顶肋，避免舞台布景式薄框。
COL=bpy.data.collections['01｜建筑与石砖']
for yy in [-5,-.7,3.6,7.9]:
    for iz in range(17):
        cube('窗间墙砌石',(-8.43,yy,.3+iz*.64),(.87,.91,.62),stone,.025)
for yy in [-2.85,1.45,5.75]:
    # 窗底与窗楣石砌填充。
    for zz in [4.65,4.98,10.68,11.02,11.36]:cube('窗楣砌石',(-8.48,yy,zz),(.8,3.32,.31),stone,.02)
    for bottom,height in [(5.35,5.1),(.25,4.2)]:
        coords=[]
        for j in range(21):
            u=-1.46+2.92*j/20; frac=abs(u)/1.46;zz=bottom+height*(.65+.35*cos(frac*pi/2));coords.append(Vector((-8.00,yy+u,zz)))
        for j,p in enumerate(coords):
            q=coords[min(j+1,20)]-coords[max(j-1,0)]
            ob=cube('尖拱楔形石',p,(.75,.29,.34),stone,.018);ob.rotation_euler.x=math.atan2(q.z,q.y)
for yy in [-3,1.3,5.6]:
    tube('大厅拱顶石肋',[(-8.0,yy,9.9),(-6.7,yy,11.7),(-4.9,yy,12.6),(-2.5,yy,13.2)],.20,stone)
    tube('大厅拱顶木肋',[(-7.85,yy+.05,10),(-6.55,yy+.05,11.8),(-4.8,yy+.05,12.7),(-2.4,yy+.05,13.3)],.08,wood_edge)
# 压暗头骨眼窝的内腔，仍保留已有真实布尔开孔。
COL=bpy.data.collections['05｜角龙头骨研究室']
uv('头骨眼窝深腔',(-.37,.41,7.23),(.155,.08,.14),dark)
uv('头骨鼻腔深处',(-.96,.37,7.03),(.13,.08,.065),dark)
# 将骨架灯芯过曝降到温暖点光。
for name in ['灯芯｜暖金','森林精灵光']:
    m=bpy.data.materials.get(name)
    if m:m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value*=.65
# 删除空的默认集合。
c=bpy.data.collections.get('Collection')
if c and not c.objects:bpy.data.collections.remove(c)
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=60;s.cycles.samples=48
s.render.filepath=os.path.join(OUT,'museum_preview_v02.png')
s['迭代版本']='第二轮：低机位、深木色、岩面与植物细化、建筑拱肋、柜体装饰'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'museum_scene.blend'))
print('第二轮保存完成',flush=True)
bpy.ops.render.render(write_still=True)
