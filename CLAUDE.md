# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Claude Code Game Studios — Game Studio Agent Architecture

Indie game development managed through 48 coordinated Claude Code subagents.
Each agent owns a specific domain, enforcing separation of concerns and quality.

## Commands

```bash
# Start the studio (first session or after /clear)
claude                          # Launch Claude Code in this directory

# Run hooks manually (bash required; on Windows use Git Bash)
bash .claude/hooks/session-start.sh
bash .claude/hooks/pre-commit.sh

# Validate JSON files (e.g. settings, sprint data)
python -m json.tool <file.json>

# Run Python-based tests
pytest tests/

# Engine-specific test runners (configure after /setup-engine)
# Godot:  godot --headless --script tests/gdunit4_runner.gd
# Unreal: headless runner with -nullrhi flag
```

> **First session?** Run `/start` to begin guided onboarding (engine choice, game concept, initial GDD).

## Architecture

### Three-Tier Agent Hierarchy

All work flows through a tiered delegation model — never skip a tier:

| Tier | Roles | Model | Responsibility |
|------|-------|-------|----------------|
| **1 — Directors** | `creative-director`, `technical-director`, `producer` | Opus | Vision, architecture, production coordination |
| **2 — Department Leads** | e.g. `game-designer`, `lead-programmer`, `qa-lead` | Sonnet | Domain ownership, design/code authority |
| **3 — Specialists** | e.g. `godot-gdscript-specialist`, `ui-programmer` | Sonnet/Haiku | Implementation, file-level changes |

Agent definitions: `.claude/agents/<name>.md`

### Skills (Slash Commands)

37+ skills in `.claude/skills/<skill-name>/SKILL.md`. Key categories:

- **Onboarding**: `/start`, `/setup-engine`, `/onboard`
- **Design**: `/new-gdd`, `/design-review`, `/review-all-gdds`
- **Architecture**: `/architecture-decision`, `/architecture-review`
- **Development**: `/dev-story`, `/code-review`, `/team-gameplay`, `/team-ui`
- **QA / Release**: `/qa-story`, `/story-done`, `/gate-check`, `/release`
- **Production**: `/sprint-plan`, `/sprint-status`, `/story-readiness`

### Hooks (Lifecycle Automation)

12 bash scripts in `.claude/hooks/` wired to Claude Code lifecycle events via `.claude/settings.json`:

| Event | Hook | Purpose |
|-------|------|---------|
| Session start | `session-start.sh` | Previews `production/session-state/active.md` |
| Session stop | `session-stop.sh` | Appends session log |
| Pre-commit | `pre-commit.sh` | Lint, JSON validation, doc-comment check |
| Post-commit | `post-commit.sh` | Updates session state |
| Pre-push | `pre-push.sh` | Blocks force-push to main |
| Asset write | `on-asset-write.sh` | Enforces asset pipeline rules |
| Compaction | `on-compaction.sh` | Preserves key context in summary |

### Path-Scoped Rules

11 markdown rules in `.claude/rules/` automatically applied based on which files are being edited:

- `src/gameplay/**` → gameplay coding standards
- `src/core/**` → engine/core standards
- `design/gdd/**` → GDD 8-section requirement enforcement
- `docs/architecture/**` → ADR format enforcement
- `production/**` → sprint/milestone format rules

### Traceability Chain

`design/gdd/` → `docs/architecture/tr-registry.yaml` → stories → `docs/architecture/control-manifest.md`

Every story must reference a GDD and ADR. `/story-done` checks manifest version for staleness.

## Technology Stack

- **Engine**: [CHOOSE: Godot 4 / Unity / Unreal Engine 5]
- **Language**: [CHOOSE: GDScript / C# / C++ / Blueprint]
- **Version Control**: Git with trunk-based development
- **Build System**: [SPECIFY after choosing engine]
- **Asset Pipeline**: [SPECIFY after choosing engine]

> **Note**: Engine-specialist agents exist for Godot, Unity, and Unreal with
> dedicated sub-specialists. Use the set matching your engine.

## Project Structure

@.claude/docs/directory-structure.md

## Engine Version Reference

@docs/engine-reference/godot/VERSION.md

## Technical Preferences

@.claude/docs/technical-preferences.md

## Coordination Rules

@.claude/docs/coordination-rules.md

## Collaboration Protocol

**User-driven collaboration, not autonomous execution.**
Every task follows: **Question -> Options -> Decision -> Draft -> Approval**

- Agents MUST ask "May I write this to [filepath]?" before using Write/Edit tools
- Agents MUST show drafts or summaries before requesting approval
- Multi-file changes require explicit approval for the full changeset
- No commits without user instruction

See `docs/COLLABORATIVE-DESIGN-PRINCIPLE.md` for full protocol and examples.

## Coding Standards

@.claude/docs/coding-standards.md

## Context Management

@.claude/docs/context-management.md

## Language Preference

所有与用户的交互一律使用**中文**。
