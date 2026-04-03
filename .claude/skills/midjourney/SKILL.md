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

根据资产类型和项目美术风格，构建优化的 MJ prompt：

**Prompt 结构**：
```
[主体描述], [风格关键词], [技术参数], [质量参数]
```

**按资产类型的推荐参数**：

| 资产类型 | 推荐参数 | 示例风格词 |
|---------|---------|-----------|
| `character` | `--ar 2:3 --q 2` | `character design, full body, white background, game asset` |
| `scene` | `--ar 16:9 --q 2` | `environment concept art, game background, detailed` |
| `ui` | `--ar 1:1 --q 2` | `game UI element, flat design, icon, clean` |
| `item` | `--ar 1:1 --q 2` | `game item, isolated on white, detailed texture` |
| `concept` | `--ar 16:9 --q 2` | `concept art, game art style, detailed illustration` |

向用户展示构建好的 prompt，**等待确认或修改后再继续**。

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

通过 Discord API 向 Midjourney Bot 发送 `/imagine` 命令：

```bash
#!/bin/bash
# 读取环境变量
source .env

PROMPT="$1"
FULL_PROMPT="/imagine prompt: ${PROMPT}"

# 发送消息到 Discord 频道
RESPONSE=$(curl -s -X POST \
  "https://discord.com/api/v10/channels/${DISCORD_CHANNEL_ID}/messages" \
  -H "Authorization: ${DISCORD_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"${FULL_PROMPT}\",
    \"tts\": false
  }")

echo "请求已发送，响应："
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

# 提取消息 ID 用于后续轮询
MESSAGE_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null)
echo "MESSAGE_ID=${MESSAGE_ID}"
```

### Step 6 — 等待并获取生成结果

Midjourney 生成需要约 30-90 秒。通过轮询频道消息来检测结果：

```bash
#!/bin/bash
source .env

WAIT_SECONDS=90
POLL_INTERVAL=10
ELAPSED=0

echo "等待 Midjourney 生成结果（最多 ${WAIT_SECONDS} 秒）..."

while [ $ELAPSED -lt $WAIT_SECONDS ]; do
  sleep $POLL_INTERVAL
  ELAPSED=$((ELAPSED + POLL_INTERVAL))
  
  # 获取频道最新消息，查找 Midjourney Bot 的回复
  MESSAGES=$(curl -s \
    "https://discord.com/api/v10/channels/${DISCORD_CHANNEL_ID}/messages?limit=5" \
    -H "Authorization: ${DISCORD_TOKEN}")
  
  # 查找包含图片附件的 Midjourney Bot 消息（Bot ID: 936929561302675456）
  IMAGE_URL=$(echo "$MESSAGES" | python3 -c "
import sys, json
msgs = json.load(sys.stdin)
for msg in msgs:
    if msg.get('author', {}).get('id') == '936929561302675456':
        attachments = msg.get('attachments', [])
        if attachments and attachments[0].get('url', '').endswith(('.png', '.jpg', '.webp')):
            print(attachments[0]['url'])
            break
" 2>/dev/null)
  
  if [ -n "$IMAGE_URL" ]; then
    echo "找到生成结果：$IMAGE_URL"
    echo "$IMAGE_URL"
    exit 0
  fi
  
  echo "  已等待 ${ELAPSED}s，继续等待..."
done

echo "超时：未在 ${WAIT_SECONDS} 秒内找到生成结果"
exit 1
```

> ⚠️ 注意：此轮询方式依赖于频道中最新的 MJ Bot 消息，在高并发频道中可能出现误匹配。
> 推荐使用私有服务器的专用频道以减少干扰。

### Step 7 — 下载并保存资产

```bash
#!/bin/bash
# 参数：IMAGE_URL ASSET_TYPE DESCRIPTION
IMAGE_URL="$1"
ASSET_TYPE="$2"
DESCRIPTION="$3"

# 生成文件名：类型_日期时间_描述摘要
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
# 将描述转为 snake_case，最多 30 个字符
SLUG=$(echo "$DESCRIPTION" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -cd '[:alnum:]_' | cut -c1-30)
FILENAME="${ASSET_TYPE}_${TIMESTAMP}_${SLUG}.png"

# 确定保存目录
SAVE_DIR="assets/art/generated/${ASSET_TYPE}"
mkdir -p "$SAVE_DIR"

# 下载图片
curl -s -L "$IMAGE_URL" -o "${SAVE_DIR}/${FILENAME}"

if [ $? -eq 0 ]; then
  echo "已保存到：${SAVE_DIR}/${FILENAME}"
else
  echo "下载失败"
  exit 1
fi
```

### Step 8 — 更新资产登记

在 `assets/art/generated/MANIFEST.md` 中追加记录（如不存在则创建）：

```markdown
| 文件名 | 类型 | 描述 | Prompt | 生成时间 |
|--------|------|------|--------|---------|
| [文件名] | [类型] | [描述] | [使用的 Prompt] | [时间戳] |
```

### Step 9 — 输出结果摘要

向用户报告：
- ✅ 生成成功 / ❌ 失败原因
- 保存路径
- 使用的完整 Prompt
- 下一步操作建议（使用 `/asset-audit` 检查命名规范，或继续生成更多变体）

---

## 四格图处理

Midjourney 默认输出 2×2 四格图。Skill 会提示用户选择：
- **全部保存** — 保存完整四格图（文件名加 `_grid` 后缀）
- **选择单格** — 回复 `U1`~`U4` 触发放大，再获取单图（需要额外一轮轮询）

使用 `AskUserQuestion` 询问用户偏好。

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
| 401 Unauthorized | Token 无效或过期，提示重新获取 |
| 403 Forbidden | 频道权限不足，检查 Bot 权限设置 |
| 超时未返回结果 | 提示手动检查 Discord 频道，提供频道链接 |
| 图片下载失败 | 输出原始 URL，提示手动下载 |
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
