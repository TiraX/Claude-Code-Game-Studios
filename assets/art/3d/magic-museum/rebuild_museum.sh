#!/bin/zsh
# 从空场景按顺序重建，每个阶段失败时立即停止。
set -eu
MUSEUM_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
MUSEUM_BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
"$MUSEUM_BLENDER" --background --python-exit-code 1 --python "$MUSEUM_DIR/build_museum.py"
for MUSEUM_STAGE in refine_museum finalize_museum polish_museum verify_museum; do
  "$MUSEUM_BLENDER" --background "$MUSEUM_DIR/museum_scene.blend" --python-exit-code 1 --python "$MUSEUM_DIR/$MUSEUM_STAGE.py"
done
