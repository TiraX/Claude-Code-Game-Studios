#!/bin/zsh
# 从 v1 基线构建 v2，逐步渲染并完成只读验收。
set -eu
MUSEUM_V2_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
MUSEUM_BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
"$MUSEUM_BLENDER" --background --python-exit-code 1 --python "$MUSEUM_V2_DIR/build_v2.py"
for MUSEUM_STAGE in refine_v2 finish_v2 polish_v2 correct_background_v2 verify_v2 inspect_v2; do
  "$MUSEUM_BLENDER" --background "$MUSEUM_V2_DIR/museum_scene_v2.blend" --python-exit-code 1 --python "$MUSEUM_V2_DIR/$MUSEUM_STAGE.py"
done
