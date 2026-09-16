"""使用 Blender 后台重新打开场景后，验证交付文件的基本完整性。"""
import bpy, os, math, json
from collections import Counter
s=bpy.context.scene
out=os.path.dirname(bpy.data.filepath)
required=['01｜建筑与石砖','02｜巨型胡桃木收藏柜','03｜恐龙山谷生态箱','04｜双鹿森林生态箱','05｜角龙头骨研究室','06｜青蓝水晶岩洞','07｜书房与藏品','08｜木阶与黄铜楼梯','09｜大厅标本柜与灯具','10｜灯光与相机']
missing=[name for name in required if not bpy.data.collections.get(name)]
invalid=[o.name for o in s.objects if not all(math.isfinite(v) for row in o.matrix_world for v in row)]
empty=[o.name for o in s.objects if o.type=='MESH' and len(o.data.vertices)==0]
external=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not os.path.exists(bpy.path.abspath(im.filepath))]
report={'场景文件':bpy.data.filepath,'Blender版本':bpy.app.version_string,'对象类型统计':dict(Counter(o.type for o in s.objects)),'集合对象数':{n:len(bpy.data.collections[n].all_objects) for n in required if bpy.data.collections.get(n)},'缺失集合':missing,'无效变换':invalid,'空网格':empty,'丢失外部图像':external,'相机':s.camera.name if s.camera else None,'男孩对象':[o.name for o in s.objects if '男孩' in o.name or 'boy' in o.name.lower()],'参考图已打包':any(im.packed_file for im in bpy.data.images if im.name.startswith('原画参考')),'渲染分辨率':[s.render.resolution_x,s.render.resolution_y],'渲染采样':s.cycles.samples}
report['基础完整性通过']=not(missing or invalid or empty or external) and bool(s.camera) and report['参考图已打包'] and not report['男孩对象']
with open(os.path.join(out,'verification.json'),'w') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False,indent=2))
if not report['基础完整性通过']:raise RuntimeError('场景完整性检查失败')
