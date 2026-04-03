---
name: midjourney
description: "通过 Discord Bot API 调用 Midjourney 生成游戏美术资产（角色立绘、场景、UI 素材等），并将生成结果保存到项目资产目录。"
argument-hint: "[asset-type] [description] -- 例如：character '武士少女，红色战甲，赛博朋克风格'"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion
---

## 前置要求

在首次使用前，需要配置 Discord 凭据。Skill 会自动检测配置文件是否存在。

**需要的凭据**（保存在 `.env` 文件中，已 gitignore）：
- `DISCORD_TOKEN` — Discord 用户 Token（Settings → Advanced → Enable Developer Mode，然后从请求头中获取）
- `DISCORD_CHANNEL_ID` — 已加入 Midjourney Bot 的 Discord 频道 ID
- `DISCORD_GUILD_ID` — Discord 服务器 ID

> ⚠️ 使用 Self-bot（用户 Token）违反 Discord ToS，风险自负。
> 推荐使用专为此用途创建的小号，不要使用主账号。

---

## 执行流程

### Step 1 — 读取项目上下文

读取以下文件，理解美术风格要求：
- `design/gdd/game-concept.md`（如存在）
- `docs/art-bible.md` 或 `design/art-bible.md`（如存在）
- `CLAUDE.md` 中的技术偏好

### Step 2 — 解析参数

从调用参数中提取：
- **资产类型**：`character`（角色）/ `scene`（场景）/ `ui`（UI）/ `item`（道具）/ `concept`（概念图）
- **描述**：图像内容的自然语言描述

如果参数不完整，使用 `AskUserQuestion` 询问：
1. 资产类型
2. 图像描述
3. 是否有风格参考（可选）

### Step 3 — 构建 Midjourney Prompt

根据资产类型和项目美术风格，构建优化的 MJ V7 prompt。

**Prompt 结构**：
```
[主体描述], [环境/场景], [风格], [情绪/光线], [参数]
```

**编写技巧**：
- 使用**英文**描述，主体放最前面（权重最高）
- 风格词放后段（如 `cinematic`, `oil painting`, `anime style`）
- 用 `::` 控制权重，如 `cat::2 dog::1`
- 使用 `--no text, watermark, blurry` 排除不需要的元素

**按资产类型的推荐参数（默认使用 V7）**：

| 资产类型 | 推荐参数 | 示例风格词 |
|---------|---------|-----------|
| `character` | `--ar 2:3 --draft --v 7` | `character design sheet, full body, clean white background, front view + 3/4 view side by side, game asset` |
| `scene` | `--ar 16:9 --draft --v 7` | `environment concept art, game background, detailed` |
| `ui` | `--ar 1:1 --v 7` | `game UI element, flat design, icon, clean` |
| `item` | `--ar 1:1 --v 7` | `game item, isolated on white, detailed texture` |
| `concept` | `--ar 16:9 --draft --v 7` | `concept art, game art style, detailed illustration` |

> 💡 `--draft` 模式速度 2 倍、资源消耗 50%，适合快速迭代——满意后可在 Discord 中点击 Upscale 升级高清。

### ⚠️ 角色资产背景规则（强制）

**`character` 类型必须使用简洁背景，角色是绝对主体。**

- ✅ **强制**：`clean white background` 或 `simple gradient background`——背景不能有叙事元素、场景细节或复杂环境
- ✅ **强制**：角色主体占画面面积 ≥ 70%
- ✅ **推荐**：`character design sheet` 格式，包含 `front view + 3/4 view side by side`（正面+四分之三并排），便于美术参考
- ❌ **禁止**：复杂场景背景（门廊、森林、室内等环境）出现在角色立绘中
- ❌ **禁止**：环境道具（食物、植物、家具等）出现在角色设计图中

**`character` 类型 Prompt 结构模板**：
```
character design sheet, [角色物种/职业/外观详细描述], [服装装备描述], [姿态/表情], [风格关键词], front view + 3/4 view side by side, [光线], clean white background, [渲染质量词] --ar 2:3 --draft --v 7
```

**参考示例（Zootopia 风格）**：
```
character design sheet, anthropomorphic spectacled langur male senior lawyer, tall lean angular build, dark charcoal-black fur, striking white circular eye-ring markings, perfectly tailored three-piece charcoal grey suit, minimal expression commanding presence, Disney Zootopia 3D animation style, front view + 3/4 view side by side, cool dramatic side lighting, clean white background, vibrant saturated colors, Pixar render quality --ar 2:3 --draft --v 7
```

**V7 进阶参数**（可选，询问用户是否需要）：

| 参数 | 说明 | 适用场景 |
|------|------|---------|
| `--stylize 0-1000` | 风格化强度（默认100，越高越艺术） | 需要强烈画风时 |
| `--chaos 0-100` | 变化程度，越高结果越多样 | 探索多种可能时 |
| `--seed [数字]` | 固定种子，便于复现结果 | 需要一致性时 |
| `--sref [URL]` | 风格参考图 | 有参考图时 |
| `--sw 0-100` | 风格参考权重 | 配合 `--sref` |
| `--cref [URL]` | 角色参考图（保持人物一致） | 角色立绘系列 |
| `--cw 0-100` | 角色权重（低=只看脸，高=含服装） | 配合 `--cref` |
| `--ow 0-1000` | Omni-Reference 权重（V7 新增） | 全向参考时 |
| `--style raw` | 减少 AI 自动美化，更贴近原始提示 | 需要精确控制时 |

向用户展示构建好的 prompt，**等待确认或修改后再继续**。

### Step 3.5 — 请求发送权限确认

展示完 Prompt 后，**必须**使用 `AskUserQuestion` 向用户请求权限，提供以下三个选项：

```
问题：「确认发送这条 Midjourney 生成请求？」

选项：
1. 同意本次 — 仅授权当前这一条请求，下次仍需确认
2. 本 Session 内全部同意 — 当前会话内所有后续 Midjourney 请求自动发送，无需再次确认
3. 不同意 — 取消本次发送，可修改 Prompt 后重试
```

- 若用户选择 **「本 Session 内全部同意」**，在当前会话剩余时间内跳过此步骤，直接发送后续请求
- 若用户选择 **「不同意」**，停止流程并提示用户可以修改 Prompt 或取消任务
- 会话级授权状态仅存在于当前 Claude Code session 内，**不写入任何文件**，下次启动 session 重置为需要确认

### Step 4 — 检查配置

```bash
# 检查 .env 文件
if [ ! -f .env ]; then
  echo "未找到 .env 文件，请先配置 Discord 凭据"
  exit 1
fi

# 检查必要的变量
source .env
if [ -z "$DISCORD_TOKEN" ] || [ -z "$DISCORD_CHANNEL_ID" ]; then
  echo "缺少 DISCORD_TOKEN 或 DISCORD_CHANNEL_ID"
  exit 1
fi
```

如果配置缺失，输出配置指引（见下方"配置指引"章节），然后停止。

### Step 5 — 发送生成请求

**必须使用 Discord Interactions API**（而非普通消息），Midjourney Bot 只响应斜杠命令交互。

先从 Guild 获取 `/imagine` 命令 ID（每个服务器固定，可缓存）：

```bash
source .env

# 获取 /imagine 命令 ID
curl -s \
  "https://discord.com/api/v10/guilds/${DISCORD_GUILD_ID}/application-command-index" \
  -H "Authorization: ${DISCORD_TOKEN}" \
  | python3 -c "
import sys, json
raw = sys.stdin.buffer.read().decode('utf-8', errors='replace')
cmds = json.loads(raw).get('application_commands', [])
for cmd in cmds:
    if cmd.get('name') == 'imagine' and cmd.get('application_id') == '936929561302675456':
        print(cmd['id'], cmd['version'])
        break
"
```

发送 `/imagine` 交互请求：

```bash
source .env

PROMPT="$1"
COMMAND_ID="938956540159881230"        # Midjourney /imagine 命令 ID（固定值）
APPLICATION_ID="936929561302675456"    # Midjourney Bot 应用 ID（固定值）
COMMAND_VERSION="$2"                   # 从上面查询获取

PAYLOAD=$(python3 -c "
import json, sys
payload = {
  'type': 2,
  'application_id': '${APPLICATION_ID}',
  'guild_id': '${DISCORD_GUILD_ID}',
  'channel_id': '${DISCORD_CHANNEL_ID}',
  'session_id': 'skill_session_001',
  'data': {
    'version': '${COMMAND_VERSION}',
    'id': '${COMMAND_ID}',
    'name': 'imagine',
    'type': 1,
    'options': [{'type': 3, 'name': 'prompt', 'value': sys.argv[1]}],
    'application_command': {
      'id': '${COMMAND_ID}',
      'application_id': '${APPLICATION_ID}',
      'version': '${COMMAND_VERSION}',
      'name': 'imagine',
      'description': 'Create images with Midjourney',
      'type': 1,
      'options': [{'type': 3, 'name': 'prompt', 'description': 'The prompt to imagine', 'required': True}]
    }
  }
}
print(json.dumps(payload))
" "${PROMPT}")

HTTP_STATUS=$(curl -s -o /dev/null -w '%{http_code}' -X POST \
  "https://discord.com/api/v10/interactions" \
  -H "Authorization: ${DISCORD_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

echo "HTTP 状态: $HTTP_STATUS"
# 204 = 成功，无响应体
```

> ✅ HTTP 204 表示请求成功，Midjourney Bot 已接收并开始生成。

### Step 6 — 提示用户前往查看

请求发送成功（HTTP 204）后，**直接跳过等待**，立即输出以下提示：

```
✅ 已成功发送生成请求！

👉 请前往 Discord 频道查看生成结果（draft 模式约 15-30 秒完成）
   生成完成后可在 Discord 中点击：
   - U1～U4：放大单格为高清大图
   - V1～V4：对单格生成变体
   - 🔄：重新生成全部四格
```

> 不轮询等待结果。MJ 生成完成后结果在 Discord 频道可见，Upscale 也需要在 Discord 手动操作，轮询无法代替这一步骤。

### Step 7 — 更新资产登记

生成完成后，在 `assets/art/generated/MANIFEST.md` 中追加记录（不存在则创建）：

```markdown
| 类型 | 描述 | 完整 Prompt | 生成时间 |
|------|------|------------|---------|
| [类型] | [描述] | [使用的 Prompt] | [时间戳] |
```

### Step 8 — 输出结果摘要

向用户报告：
- ✅ 生成成功（或 ❌ 失败原因）
- 使用的完整 Prompt
- 提示用户**前往 Discord 频道查看图片**，可在 Discord 中执行 Upscale（U1-U4）放大单格
- 下一步操作建议（如继续生成变体，或用 `--sref` / `--cref` 保持风格/角色一致性）

---

## 四格图与 Upscale

Midjourney V7 默认输出 2×2 四格图，所有后续操作（Upscale、Vary、Re-roll）均在 **Discord 频道内** 手动完成：

- **U1～U4** — 放大单格为高清大图
- **V1～V4** — 对单格生成变体
- **🔄** — 重新生成全部四格

> Skill 只负责发送生成指令和报告完成状态，**不下载图片**。请前往 Discord 频道查看和操作生成结果。

---

## 批量生成模式

如果调用参数以 `batch:` 开头，则读取一个 JSON 文件，批量生成一组资产：

```bash
# 用法：/midjourney batch:assets/art/generated/batch-request.json
```

批量文件格式：
```json
[
  { "type": "character", "description": "...", "style_suffix": "..." },
  { "type": "scene", "description": "...", "style_suffix": "..." }
]
```

批量模式下，每张图之间等待 30 秒以避免触发速率限制。

---

## 配置指引

首次使用时，如果未找到配置，输出以下内容：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Midjourney Skill — 首次配置指引
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 在项目根目录创建 .env 文件（已在 .gitignore 中）：

   DISCORD_TOKEN=你的Discord用户Token
   DISCORD_CHANNEL_ID=Midjourney频道ID
   DISCORD_GUILD_ID=Discord服务器ID

2. 如何获取 Discord Token：
   - 打开 Discord 网页版，按 F12 打开开发者工具
   - 进入 Network 标签，随便点一个频道
   - 搜索请求头中的 "authorization" 字段
   - 该值即为你的 Token

3. 如何获取频道/服务器 ID：
   - 在 Discord 设置 → 高级 → 启用开发者模式
   - 右键频道 → 复制频道 ID
   - 右键服务器图标 → 复制服务器 ID

4. 确认 Midjourney Bot 已加入该频道，且你有发送消息的权限

5. 确保 .env 已加入 .gitignore，运行：
   echo '.env' >> .gitignore
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 错误处理

| 错误情况 | 处理方式 |
|---------|---------|
| 401 Unauthorized | Token 无效或过期，提示重新从浏览器 Network 请求头获取 |
| 403 Forbidden | 频道权限不足，检查是否有发消息权限 |
| 204 但长时间无回复 | Midjourney 队列拥堵，提示前往 Discord 确认是否接收到任务 |
| 超时未检测到 Bot 消息 | 提示手动前往 Discord 频道查看，生成可能已完成 |
| `.env` 缺失 | 输出配置指引（见上方） |

---

## 目录结构

生成的资产保存在：

```
assets/art/generated/
├── MANIFEST.md          # 所有生成资产的登记表
├── character/           # 角色立绘
├── scene/               # 场景背景
├── ui/                  # UI 素材
├── item/                # 道具图标
└── concept/             # 概念图
```
