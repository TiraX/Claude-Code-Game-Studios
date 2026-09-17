"""重新打开最终 v2 后验证完整性、原始文件保护和改动关键结构。"""
import bpy,os,math,json,hashlib,struct
from collections import Counter
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene;OUT=os.path.dirname(os.path.abspath(__file__));BASE=os.path.dirname(OUT)
required=['01｜建筑与石砖','02｜巨型胡桃木收藏柜','03｜恐龙山谷生态箱','04｜双鹿森林生态箱','05｜角龙头骨研究室','06｜青蓝水晶岩洞','07｜书房与藏品','08｜木阶与黄铜楼梯','09｜大厅标本柜与灯具','10｜灯光与相机']
manifest=json.load(open(os.path.join(OUT,'baseline_manifest.json')))
unchanged={name:hashlib.sha256(open(os.path.join(BASE,name),'rb').read()).hexdigest()==digest for name,digest in manifest.items()}
missing=[n for n in required if not bpy.data.collections.get(n)]
invalid=[o.name for o in s.objects if not all(math.isfinite(v) for row in o.matrix_world for v in row)]
empty=[o.name for o in s.objects if o.type=='MESH' and not o.data.vertices]
external=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not os.path.exists(bpy.path.abspath(im.filepath))]
checks={
 '地形封边':any(o.name.startswith('v2山谷连续河床地层封边') for o in s.objects),
 '森林封边':any(o.name.startswith('v2森林腐殖地形地层封边') for o in s.objects),
 '真实起伏远峰':bool(bpy.data.objects.get('v2真实起伏远峰')),
 '羽状蕨叶':any(o.name.startswith('v2羽状蕨叶') for o in s.objects),
 '薄壳头骨':bool(bpy.data.objects.get('v2薄骨颈盾')),
 '辅助鹿眼异常已清理':not any('v2眼眶高光' in o.name for o in s.objects),
 '男孩缺席':not any('男孩' in o.name or 'boy' in o.name.lower() for o in s.objects),
 '参考图打包':any(im.packed_file for im in bpy.data.images if im.name.startswith('原画参考'))}
with open(os.path.join(OUT,'museum_final_v2.png'),'rb') as f:f.seek(16);dimensions=struct.unpack('>II',f.read(8))
marks={'主抽屉把手':(-.65,-3.55,.87),'头骨焦点':(.08,.4,7.28),'站鹿焦点':(-4.9,-1.1,6.9),'楼梯底端':(5.95,-3.28,.20)}
uv={k:[round(world_to_camera_view(s,s.camera,Vector(v)).x,4),round(1-world_to_camera_view(s,s.camera,Vector(v)).y,4)] for k,v in marks.items()}
report={'基础完整性通过':not(missing or invalid or empty or external) and all(unchanged.values()) and all(checks.values()) and bool(s.camera) and dimensions==(1920,1080),'原始文件未改变':unchanged,'缺失集合':missing,'无效变换':invalid,'空网格':empty,'缺失外部图像':external,'关键结构':checks,'对象类型统计':dict(Counter(o.type for o in s.objects)),'材质数':len(bpy.data.materials),'面数':sum(len(o.data.polygons) for o in s.objects if o.type=='MESH'),'最终PNG尺寸':dimensions,'渲染采样':s.cycles.samples,'相机':{'焦距':s.camera.data.lens,'垂直偏移':s.camera.data.shift_y},'最终构图标记':uv,'视觉限制':'结构检查不能证明与原画视觉一致；3%构图容差未作全面定量验收。'}
with open(os.path.join(OUT,'verification_v2.json'),'w') as f:json.dump(report,f,ensure_ascii=False,indent=2)
with open(os.path.join(OUT,'camera_landmarks.json'),'w') as f:json.dump({'说明':'最终保存相机；左上原点，归一化坐标；非原画误差测量','v2主视角':uv},f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False,indent=2))
if not report['基础完整性通过']:raise RuntimeError('v2结构检查失败')
