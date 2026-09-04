---
name: map-systems
description: "Decompose a game concept into individual systems, map dependencies, prioritize design order, and create the systems index."
argument-hint: "[next | system-name] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, TodoWrite, Task
---

When this skill is invoked:

## Parse Arguments

Two modes:

- **No argument**: `/map-systems` — Run the full decomposition workflow (Phases 1-5)
  to create or update the systems index.
- **`next`**: `/map-systems next` — Pick the highest-priority undesigned system
  from the index and hand off to `/design-system` (Phase 6).

Also resolve the review mode (once, store for all gate spawns this run):
1. If `--review [full|lean|solo]` was passed → use that
2. Else read `production/review-mode.txt` → use that value
3. Else → default to `lean`

See `.claude/docs/director-gates.md` for the full check pattern.

---

## Phase 1: Read Concept (Required Context)

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

## Phase 2: Systems Enumeration (Collaborative)

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

## Phase 3: Dependency Mapping (Collaborative)

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

**Review mode check** — apply before spawning TD-SYSTEM-BOUNDARY:
- `solo` → skip. Note: "TD-SYSTEM-BOUNDARY skipped — Solo mode." Proceed to priority assignment.
- `lean` → skip (not a PHASE-GATE). Note: "TD-SYSTEM-BOUNDARY skipped — Lean mode." Proceed to priority assignment.
- `full` → spawn as normal.

**After dependency mapping is approved, spawn `technical-director` via Task using gate TD-SYSTEM-BOUNDARY (`.claude/docs/director-gates.md`) before proceeding to priority assignment.**

Pass: the dependency map summary, layer assignments, bottleneck systems list, any circular dependency resolutions.

Present the assessment. If REJECT, revise the system boundaries with the user before moving to priority assignment. If CONCERNS, note them inline in the systems index and continue.

---

## Phase 4: Priority Assignment (Collaborative)

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

**"Why" column guidance**: When explaining why each system was placed in a priority tier, mix technical necessity with player-experience reasoning. Do not use purely technical justifications like "Combat needs damage math" — connect to player experience where relevant. Examples of good "Why" entries:
- "Required for the core loop — without it, placement decisions have no consequence (Pillar 2: Placement is the Puzzle)"
- "Ballista's punch-through identity is established here — this stat definition is what makes it feel different from Archer"
- "Foundation for all economy decisions — players must understand upgrade costs to make meaningful placement choices"

Pure technical necessity ("X depends on Y") is insufficient alone when the system directly shapes player experience.

**Review mode check** — apply before spawning PR-SCOPE:
- `solo` → skip. Note: "PR-SCOPE skipped — Solo mode." Proceed to writing the systems index.
- `lean` → skip (not a PHASE-GATE). Note: "PR-SCOPE skipped — Lean mode." Proceed to writing the systems index.
- `full` → spawn as normal.

**After priorities are approved, spawn `producer` via Task using gate PR-SCOPE (`.claude/docs/director-gates.md`) before writing the index.**

Pass: total system count per milestone tier, estimated implementation volume per tier (system count × average complexity), team size, stated project timeline.

Present the assessment. If UNREALISTIC, offer to revise priority tier assignments before writing the index. If CONCERNS, note them and continue.

### Step 4c: Determine Design Order

Combine dependency sort + priority tier to produce the final design order:
1. MVP Foundation systems first
2. MVP Core systems second
3. MVP Feature systems third
4. Vertical Slice Foundation/Core systems
5. ...and so on

This is the order the team should write GDDs in.

---

## Phase 5: Create Systems Index (Write)

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

**Review mode check** — apply before spawning CD-SYSTEMS:
- `solo` → skip. Note: "CD-SYSTEMS skipped — Solo mode." Proceed to Phase 7 next steps.
- `lean` → skip (not a PHASE-GATE). Note: "CD-SYSTEMS skipped — Lean mode." Proceed to Phase 7 next steps.
- `full` → spawn as normal.

**After the systems index is written, spawn `creative-director` via Task using gate CD-SYSTEMS (`.claude/docs/director-gates.md`).**

Pass: systems index path, game pillars and core fantasy (from `design/gdd/game-concept.md`), MVP priority tier system list.

Present the assessment. If REJECT, revise the system set with the user before GDD authoring begins. If CONCERNS, record them in the systems index as a `> **Creative Director Note**` at the top of the relevant tier section.

### Step 5c: Update Session State

After writing, create `production/session-state/active.md` if it does not exist, then update it with:
- Task: Systems decomposition
- Status: Systems index created
- File: design/gdd/systems-index.md
- Next: Design individual system GDDs

**Verdict: COMPLETE** — systems index written to `design/gdd/systems-index.md`.
If the user declined: **Verdict: BLOCKED** — user did not approve the write.

---

## Phase 6: Design Individual Systems (Handoff to /design-system)

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

## Phase 7: Suggest Next Steps

After the systems index is created (or after designing some systems), present next actions using `AskUserQuestion`:

- "Systems index is written. What would you like to do next?"
  - [A] Start designing GDDs — run `/design-system [first-system-in-order]`
  - [B] Ask a director to review the index first — ask `creative-director` or `technical-director` to validate the system set before committing to 10+ GDD sessions
  - [C] Stop here for this session

**The director review option ([B]) is worth highlighting**: having a Creative Director or Technical Director review the completed systems index before starting GDD authoring catches scope issues, missing systems, and boundary problems before they're locked in across many documents. It is optional but recommended for new projects.

After any individual GDD is completed:
- "Run `/design-review design/gdd/[system].md` in a fresh session to validate quality"
- "Run `/gate-check systems-design` when all MVP GDDs are complete"

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

## Context Window Awareness

If context reaches or exceeds 70% at any point, append this notice:

> **Context is approaching the limit (≥70%).** The systems index is saved to
> `design/gdd/systems-index.md`. Open a fresh Claude Code session to continue
> designing individual GDDs — run `/map-systems next` to pick up where you left off.

---

## Recommended Next Steps

- Run `/design-system [first-system-in-order]` to author the first GDD (use design order from the index)
- Run `/map-systems next` to always pick the highest-priority undesigned system automatically
- Run `/design-review design/gdd/[system].md` in a fresh session after each GDD is authored
- Run `/gate-check pre-production` when all MVP GDDs are authored and reviewed
