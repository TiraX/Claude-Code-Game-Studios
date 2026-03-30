---
name: map-systems
description: "Decompose a game concept into individual systems, map dependencies, prioritize design order, and create the systems index."
argument-hint: "[optional: 'next' to pick highest-priority undesigned system, or a system name to hand off to /design-system]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, TodoWrite
---

When this skill is invoked:

## 1. Parse Arguments

Two modes:

- **No argument**: `/map-systems` — Run the full decomposition workflow (Phases 1-5)
  to create or update the systems index.
- **`next`**: `/map-systems next` — Pick the highest-priority undesigned system
  from the index and hand off to `/design-system` (Phase 6).

---

## 2. Phase 1: Read Concept (Required Context)

Read the game concept and any existing design work. This provides the raw material
for systems decomposition.

**Required:**
- Read `design/gdd/game-concept.md` — **fail with a clear message if missing**:
  > "No game concept found at `design/gdd/game-concept.md`. Run `/brainstorm` first
  > to create one, then come back to decompose it into systems."

**Optional (read if they exist):**
- Read `design/gdd/game-pillars.md` — pillars constrain priority and scope
- Read `design/gdd/systems-index.md` — if exists, **resume** from where it left off
  (update, don't recreate from scratch)
- Glob `design/gdd/*.md` — check which system GDDs already exist

**If the systems index already exists:**
- Read it and present current status to the user
- Use `AskUserQuestion` to ask:
  "The systems index already exists with [N] systems ([M] designed, [K] not started).
  What would you like to do?"
  - Options: "Update the index with new systems", "Design the next undesigned system",
    "Review and revise priorities"

---

## 3. Phase 2: Systems Enumeration (Collaborative)

Extract and identify all systems the game needs. This is the creative core of the
skill — it requires human judgment because concept docs rarely enumerate every
system explicitly.

### Step 2a: Extract Explicit Systems

Scan the game concept for directly mentioned systems and mechanics:
- Core Mechanics section (most explicit)
- Core Loop section (implies what systems drive each loop tier)
- Technical Considerations section (networking, procedural generation, etc.)
- MVP Definition section (required features = required systems)

### Step 2b: Identify Implicit Systems

For each explicit system, identify the **hidden systems** it implies. Games always
need more systems than the concept doc mentions. Use this inference pattern:

- "Inventory" implies: item database, equipment slots, weight/capacity rules,
  inventory UI, item serialization for save/load
- "Combat" implies: damage calculation, health system, hit detection, status effects,
  enemy AI, combat UI (health bars, damage numbers), death/respawn
- "Open world" implies: streaming/chunking, LOD system, fast travel, map/minimap,
  point of interest tracking, world state persistence
- "Multiplayer" implies: networking layer, lobby/matchmaking, state synchronization,
  anti-cheat, network UI (ping, player list)
- "Crafting" implies: recipe database, ingredient gathering, crafting UI,
  success/failure mechanics, recipe discovery/learning
- "Dialogue" implies: dialogue tree system, dialogue UI, choice tracking, NPC
  state management, localization hooks
- "Progression" implies: XP system, level-up mechanics, skill tree, unlock
  tracking, progression UI, progression save data

Explain in conversation text why each implicit system is needed (with examples).

### Step 2c: Apply Two-Level Category Hierarchy

Systems must be organized using a **two-level (大类 → 小类) hierarchy** to prevent
a flat list from becoming unnavigable as system count grows.

**Rule: When a top-level category contains 4 or more systems, introduce sub-categories.**

**How to define sub-categories:**
- Group systems by shared *function* or *domain focus*, not just by who builds them
- Sub-category names should reflect what the player experiences, not implementation
  details (e.g., "生态种植" not "植物模块")
- Each sub-category should contain 2–5 systems; if a sub-category would have only
  1 system, fold it into a sibling sub-category or leave as standalone
- A system that is a clear singleton in a category may remain without a sub-category
  label (use "—" as sub-category)

**Common sub-category patterns by top-level category:**
- **Core** → Foundation (zero-dep infra), Control & Camera, World Management
- **Gameplay** → per-mechanic pillar (e.g., Planting, Magic, Building, Animal, Island)
- **Economy** → Resources, Vitality/Progress, Relationship/Bond
- **UI** → HUD/Feedback, Interaction Panels, Journal/Log
- **Narrative** → Dialogue, Events/Story, Records/Lore

**Presentation format for enumeration:**
Show systems grouped visually by 大类, then 小类, in a two-column grouping table.
Include a `大类` column and a `小类` column in the enumeration table. Example:

| # | 系统名 | 大类 | 小类 | 优先级 | 状态 | 设计文档 | 依赖系统 |
|---|--------|------|------|--------|------|----------|----------|
| 1 | 输入系统 | Core | 基础框架 | MVP | 未开始 | — | — |
| 2 | 精灵角色控制器 | Core | 控制与视角 | MVP | 未开始 | — | 输入系统 |

### Step 2d: User Review

Present the enumeration organized by 大类 and 小类. For each system, show:
- Name, 大类, 小类
- Brief description (1 sentence)
- Whether it was explicit (from concept) or implicit (inferred)

Then use `AskUserQuestion` to capture feedback:
- "Are there systems missing from this list?"
- "Should any of these be combined or split?"
- "Are there systems listed that this game does NOT need?"
- "Do the sub-category groupings make sense? Any that should be renamed or merged?"

Iterate until the user approves the enumeration.

---

## 4. Phase 3: Dependency Mapping (Collaborative)

For each system, determine what it depends on. A system "depends on" another if
it cannot function without that other system existing first.

### Step 3a: Map Dependencies

For each system, list its dependencies. Use these dependency heuristics:
- **Input/output dependencies**: System A produces data System B needs
- **Structural dependencies**: System A provides the framework System B plugs into
- **UI dependencies**: Every gameplay system has a corresponding UI system that
  depends on it (but UI is designed after the gameplay system)

### Step 3b: Sort by Dependency Order

Arrange systems into layers:
1. **Foundation**: Systems with zero dependencies (designed and built first)
2. **Core**: Systems depending only on Foundation systems
3. **Feature**: Systems depending on Core systems
4. **Presentation**: UI and feedback systems that wrap gameplay systems
5. **Polish**: Meta-systems, tutorials, analytics, accessibility

### Step 3c: Detect Circular Dependencies

Check for cycles in the dependency graph. If found:
- Highlight them to the user
- Propose resolutions (interface abstraction, simultaneous design, breaking the
  cycle by defining a contract between the two systems)

### Step 3d: Present to User

Show the dependency map as a layered list. Highlight:
- Any circular dependencies
- Any "bottleneck" systems (many others depend on them — these are high-risk)
- Any systems with no dependents (leaf nodes — lower risk, can be designed late)

Use `AskUserQuestion` to ask: "Does this dependency ordering look right? Any
dependencies I'm missing or that should be removed?"

---

## 5. Phase 4: Priority Assignment (Collaborative)

Assign each system to a priority tier based on what milestone it's needed for.

### Step 4a: Auto-Assign Based on Concept

Use these heuristics for initial assignment:
- **MVP**: Systems mentioned in the concept's "Required for MVP" section, plus their
  Foundation-layer dependencies
- **Vertical Slice**: Systems needed for a complete experience in one area
- **Alpha**: All remaining gameplay systems
- **Full Vision**: Polish, meta, and nice-to-have systems

### Step 4b: User Review

Present the priority assignments in a table. For each tier, explain why systems
were placed there.

Use `AskUserQuestion` to ask: "Do these priority assignments match your vision?
Which systems should be higher or lower priority?"

Explain reasoning in conversation: "I placed [system] in MVP because the core loop
requires it — without [system], the 30-second loop can't function."

### Step 4c: Determine Design Order

Combine dependency sort + priority tier to produce the final design order:
1. MVP Foundation systems first
2. MVP Core systems second
3. MVP Feature systems third
4. Vertical Slice Foundation/Core systems
5. ...and so on

This is the order the team should write GDDs in.

---

## 6. Phase 5: Create Systems Index (Write)

### Step 5a: Draft the Document

Using the template at `.claude/docs/templates/systems-index.md`, populate the
systems index with all data from Phases 2-4:
- Fill the enumeration table
- Fill the dependency map
- Fill the recommended design order
- Fill the high-risk systems
- Fill progress tracker (all systems "Not Started" initially, unless GDDs already exist)

### Step 5a-2: Derive Minimum Prototype System Set

After producing the full systems list, identify the **最小原型系统集** — the
smallest possible subset of systems needed to answer the game's most critical
unknown (usually "does the core gameplay loop feel good?").

This is separate from the MVP list. Apply the following rules:

1. **Identify the core question**: What is the single most important gameplay
   hypothesis to validate? (e.g., "Does planting → magic → animal attraction
   feel satisfying as a feedback loop?")
2. **Tag each system** with one of three roles for the prototype:
   - 🔴 **必建** — the system whose behavior is the hypothesis; must be built
   - 🟡 **存根** — required by 必建 systems to compile or run; stub/hardcode in ≤ 30 lines
   - ⚪ **跳过** — everything else (all UI systems, audio, persistence, progression,
     meta, analytics, systems beyond vertical-slice priority)
3. **Scope constraint**: The 必建 set should contain **no more than 3–5 systems**.
   If more are required, the prototype question is too broad — split it into
   two smaller experiments.
4. **Add a "最小原型系统集" section** to the systems index document:

```markdown
## 最小原型系统集

> 目的：验证「[core question]」
> 原则：原型 ≠ MVP。本集合仅需能运行出「感受」，不需要完整数值平衡、存档或UI。

| 系统 | 原型角色 | 实现建议 |
|------|---------|---------|
| [系统名] | 🔴 必建 | 完整实现最小可测版本 |
| [系统名] | 🟡 存根 | 硬编码单一数值即可（如 `const MANA = 50`）|
| [系统名] | ⚪ 跳过 | 不需要，用占位数据代替 |

**验证时长目标**：1–3天等效工作量
**验证结论输出**：运行 `/prototype [描述]` 开始原型
```

5. Present this section to the user for review before writing.


### Step 5b: Approval

Present a summary of the document:
- Total systems count by category
- MVP system count
- First 3 systems in the design order
- Any high-risk items

Ask: "May I write the systems index to `design/gdd/systems-index.md`?"

Wait for approval. Write the file only after "yes."

### Step 5c: Update Session State

After writing, update `production/session-state/active.md` with:
- Task: Systems decomposition
- Status: Systems index created
- File: design/gdd/systems-index.md
- Next: Design individual system GDDs

---

## 7. Phase 6: Design Individual Systems (Handoff to /design-system)

This phase is entered when:
- The user says "yes" to designing systems after creating the index
- The user invokes `/map-systems [system-name]`
- The user invokes `/map-systems next`

### Step 6a: Select the System

- If a system name was provided, find it in the systems index
- If `next` was used, pick the highest-priority undesigned system (by design order)
- If the user just finished the index, ask:
  "Would you like to start designing individual systems now? The first system in
  the design order is [name]. Or would you prefer to stop here and come back later?"

Use `AskUserQuestion` for: "Start designing [system-name] now, pick a different
system, or stop here?"

### Step 6b: Hand Off to /design-system

Once a system is selected, invoke the `/design-system [system-name]` skill.

The `/design-system` skill handles the full GDD authoring process:
- Gathers context from game concept, systems index, and dependency GDDs
- Creates a file skeleton immediately
- Walks through all 8 required sections one at a time (collaborative, incremental)
- Cross-references existing docs to prevent contradictions
- Routes to specialist agents for domain expertise
- Writes each section to file as soon as it's approved
- Runs `/design-review` when complete
- Updates the systems index

**Do not duplicate the /design-system workflow here.** This skill owns the systems
*index*; `/design-system` owns individual system *GDDs*.

### Step 6c: Loop or Stop

After `/design-system` completes, use `AskUserQuestion`:
- "Continue to the next system ([next system name])?"
- "Pick a different system?"
- "Stop here for this session?"

If continuing, return to Step 6a.

---

## 8. Phase 7: Suggest Next Steps

After the systems index is created (or after designing some systems), suggest
the appropriate next actions:

- "Run `/design-system [system-name]` to write the next system's GDD"
- "Run `/design-review [path]` on each completed GDD to validate quality"
- "Run `/gate-check pre-production` to check if you're ready to start building"
- "Prototype the highest-risk system with `/prototype [system]`"
- "Plan the first implementation sprint with `/sprint-plan new`"

---

## Collaborative Protocol

This skill follows the collaborative design principle at every phase:

1. **Question -> Options -> Decision -> Draft -> Approval** at every step
2. **AskUserQuestion** at every decision point (Explain -> Capture pattern):
   - Phase 2: "Missing systems? Combine or split?"
   - Phase 3: "Dependency ordering correct?"
   - Phase 4: "Priority assignments match your vision?"
   - Phase 5: "May I write the systems index?"
   - Phase 6: "Start designing, pick different, or stop?" then hand off to `/design-system`
3. **"May I write to [filepath]?"** before every file write
4. **Incremental writing**: Update the systems index after each system is designed
5. **Handoff**: Individual GDD authoring is owned by `/design-system`, which handles
   incremental section writing, cross-referencing, design review, and index updates
6. **Session state updates**: Write to `production/session-state/active.md` after
   each milestone (index created, system designed, priorities changed)

**Never** auto-generate the full systems list and write it without review.
**Never** start designing a system without user confirmation.
**Always** show the enumeration, dependencies, and priorities for user validation.
