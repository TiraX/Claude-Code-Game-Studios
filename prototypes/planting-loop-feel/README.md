# PROTOTYPE - NOT FOR PRODUCTION
# 生态种植核心循环——催芽手感验证
# Created: 2026-03-30

## 核心问题

> 不依赖任何奖励系统，单纯的「种植 → 催芽 → 破土动画 → 里虹嗅一嗅」30 秒循环，本身是否令人愉悦？

## 文件结构

```
planting-loop-feel/
├── README.md                   ← 本文件
├── REPORT.md                   ← 原型报告（测试后填写结论）
├── Source/
│   ├── ProtoConstants.h        ← 所有硬编码数值（数据配置库存根）
│   ├── ProtoPlant.h/.cpp       ← 🔴 必建：生态种植系统
│   ├── ProtoSpells.h           ← 🔴 必建：精灵魔法系统（催芽+灵雨）
│   │                              🟡 存根：魔力值系统、土地感知系统、资源材料系统
│   ├── ProtoLihong.h/.cpp      ← 🔴 必建：里虹伴侣AI
│   └── BLUEPRINT_SETUP.md      ← Blueprint 搭建说明（粒子、动画、关卡）
└── Test/
    └── PLAYTEST_SCRIPT.md      ← 结构化测试脚本（4个区块，调参测试）
```

## 实现范围（系统索引对应）

| 系统（systems-index.md） | 原型角色 | 实现位置 |
|--------------------------|---------|---------|
| 生态种植系统 | 🔴 必建 | `ProtoPlant.h/.cpp` |
| 精灵魔法系统 | 🔴 必建 | `ProtoSpells.h` (UProtoSpellCaster) |
| 里虹伴侣AI | 🔴 必建 | `ProtoLihong.h/.cpp` |
| 魔力值系统 | 🟡 存根 | `ProtoSpells.h` (UProtoManaStub) |
| 岛屿生机度系统 | 🟡 存根 | `ProtoPlant.cpp` (GEngine debug msg) |
| 土地感知系统 | 🟡 存根 | `ProtoSpells.h` (ULandSenseStub) |
| 资源与材料系统 | 🟡 存根 | `ProtoConstants.h` (STARTING_* consts) |
| 游戏数据配置库 | 🟡 存根 | `ProtoConstants.h` (全部 constexpr) |
| 其余 29 个系统 | ⚪ 跳过 | — |

## 关键调参变量

在 `ProtoConstants.h` 修改，或直接在 BP_ProtoLihong 实例的 Details 面板调整：

| 变量 | 默认值 | 要测试的问题 |
|------|--------|------------|
| `LIHONG_NOTICE_DELAY_SEC` | 0.6s | 停顿越短越像机器人，越长越自然？ |
| `BASE_GROWTH_SEC` | 8s | 等待的满足感临界点 |
| `CATALYZE_MULT` | 3× | 施法的爽感是否可感知？ |
| `LIHONG_SNIFF_DURATION` | 2.5s | 嗅探时长 |

## 搭建顺序

1. 将 Source/*.h/.cpp 添加到 UE5 项目（或新建空白 UE5 C++ 项目）
2. 按 `BLUEPRINT_SETUP.md` 说明创建 Blueprint 子类和粒子系统
3. 按 `BLUEPRINT_SETUP.md` 搭建关卡
4. 运行游戏，完成自检（无蓝图编译错误，里虹能走到植物旁边）
5. 按 `Test/PLAYTEST_SCRIPT.md` 进行 2–3 次测试
6. 填写 `REPORT.md` 结论

## 重要约束

- 原型代码 **绝对不能** import 或依赖 `src/` 下的任何生产代码
- 生产代码 **绝对不能** import 原型目录
- 如果建议 PROCEED，生产实现必须从头重写——原型代码不重构进生产
