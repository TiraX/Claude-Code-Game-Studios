# Codex Game Studios -- Game Studio Agent Architecture

Indie game development managed through coordinated Codex-capable agents and skills.
Each agent owns a specific domain, enforcing separation of concerns and quality.

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

> Historical source docs still live under `.claude/docs/`. Codex-facing skills
> have been imported under `.codex/skills/`.

## Engine Version Reference

@docs/engine-reference/godot/VERSION.md

## Technical Preferences

@.claude/docs/technical-preferences.md

## Coordination Rules

@.claude/docs/coordination-rules.md

## Collaboration Protocol

**User-driven collaboration with explicit assumptions and scoped execution.**
For substantial design or implementation work, prefer:
**Question -> Options -> Decision -> Draft -> Approval** when the goal is unclear.

- Codex should state assumptions before significant edits.
- If multiple interpretations exist, present them rather than choosing silently.
- Keep changes surgical and trace every changed line to the user's request.
- For multi-file design changes, summarize the intended changeset before editing when practical.
- No commits without user instruction

See `docs/COLLABORATIVE-DESIGN-PRINCIPLE.md` for full protocol and examples.

> **First session?** If the project has no engine configured and no game concept,
> run `/start` to begin the guided onboarding flow.

## Codex Operating Guidelines

- Think before coding: state assumptions, surface tradeoffs, and ask when the request is genuinely unclear.
- Simplicity first: write the minimum code or design text that solves the request; avoid speculative abstractions and extra features.
- Surgical changes: touch only what the task requires, match existing style, and clean up only unused code created by the current change.
- Goal-driven execution: define verifiable success criteria, then loop until the change is checked.

## Communication Language

- **All communication with the user MUST be in Chinese (中文).** This applies to
  conversational replies, clarification questions, status updates, and
  explanations.
- **Code, file paths, technical identifiers, command names, and document section
  headers remain in English** unless the user explicitly requests otherwise.
- **Design documents and in-game text** follow the project's localization
  configuration (see `/setup-localization` once configured), not this rule.
- This rule applies to all Codex agents and imported skills used in this project.

## Coding Standards

@.claude/docs/coding-standards.md

## Context Management

@.claude/docs/context-management.md
