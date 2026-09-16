"""成图检查后的最终小幅修正：取景下移、颈盾朝向、皮肤凹凸。"""
import bpy,os,math
from mathutils import Matrix,Vector
s=bpy.context.scene;out=os.path.dirname(os.path.abspath(__file__))
s.camera.data.shift_y=-.035
pivot=Vector((.26,.38,7.25));transform=Matrix.Translation(pivot) @ Matrix.Rotation(-math.pi/3,4,'Z') @ Matrix.Translation(-pivot)
for o in s.objects:
    if o.name.startswith('扇形角龙颈盾') or o.name.startswith('颈盾边缘骨刺'):o.matrix_world=transform @ o.matrix_world
for n in bpy.data.materials['恐龙皮肤'].node_tree.nodes:
    if n.type=='BUMP':n.inputs['Strength'].default_value=.18;n.inputs['Distance'].default_value=.014
s['迭代版本']='最终：下移取景保留柜脚；调整颈盾朝向；降低恐龙皮肤凹凸'
s.render.filepath=os.path.join(out,'museum_final.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out,'museum_scene.blend'))
bpy.ops.render.render(write_still=True)
