---
name: prototype
description: "Rapid prototyping workflow. Skips normal standards to quickly validate a game concept or mechanic. Produces throwaway code and a structured prototype report."
argument-hint: "[concept-description]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
---

When this skill is invoked:

1. **Read the concept description** from the argument. Identify the core
   question this prototype must answer. If the concept is vague, state the
   question explicitly before proceeding.

2. **Read CLAUDE.md** for project context and the current tech stack. Understand
   what engine, language, and frameworks are in use so the prototype is built
   with compatible tooling.

2b. **Identify the minimum system set** (if a systems index exists):

   - Check for `design/gdd/systems-index.md`. If it exists, read it.
   - Classify every system in the index into one of three buckets:

     | Bucket | Definition | Prototype treatment |
     |--------|-----------|---------------------|
     | **核心假设系统** | The system whose *feel or behavior* is the hypothesis being tested — removing it makes the prototype pointless | Build a real (but minimal) version |
     | **脚手架系统** | Required for core systems to run, but their own design is not being tested | Hardcode or stub in ≤ 30 lines |
     | **跳过系统** | Everything else: UI polish, audio, persistence, analytics, meta-systems, systems in later priority tiers | Do not build — use placeholder data or omit entirely |

   - **Prototype ≠ MVP**: The MVP system list is what the game needs to *ship a
     playable build*. The prototype only needs enough systems to answer the core
     question. Many MVP systems can be:
     - Replaced by hardcoded constants (e.g., game data config → `const MANA_COST = 10`)
     - Replaced by a single integer counter (e.g., resource system → `int mana = 50`)
     - Omitted entirely (e.g., save system, all UI systems, all audio systems)
     - Merged into one throwaway script

   - Present the classification to the user as a table before writing any code:
     ```
     核心假设系统 (build): [list]
     脚手架存根   (stub):  [list]
     跳过         (skip):  [list]
     ```
   - Wait for the user to confirm or adjust before proceeding.

   - If no systems index exists, state the assumption: "No systems index found —
     proceeding without scope reduction analysis. Consider running `/map-systems`
     first to make the prototype scope explicit."

3. **Create a prototype plan**: Define in 3-5 bullet points what the minimum
   viable prototype looks like. What is the core question? What is the absolute
   minimum code needed to answer it? What can be skipped?

4. **Create the prototype directory**: `prototypes/[concept-name]/` where
   `[concept-name]` is a short, kebab-case identifier derived from the concept.

5. **Implement the prototype** in the isolated directory. Every file must begin
   with:
   ```
   // PROTOTYPE - NOT FOR PRODUCTION
   // Question: [Core question being tested]
   // Date: [Current date]
   ```
   Standards are intentionally relaxed:
   - Hardcode values freely
   - Use placeholder assets
   - Skip error handling
   - Use the simplest approach that works
   - Copy code rather than importing from production

6. **Test the concept**: Run the prototype. Observe behavior. Collect any
   measurable data (frame times, interaction counts, feel assessments).

7. **Generate the Prototype Report** and save it to
   `prototypes/[concept-name]/REPORT.md`:

```markdown
## Prototype Report: [Concept Name]

### Hypothesis
[What we expected to be true -- the question we set out to answer]

### Approach
[What we built, how long it took, what shortcuts we took]

### Result
[What actually happened -- specific observations, not opinions]

### Metrics
[Any measurable data collected during testing]
- Frame time: [if relevant]
- Feel assessment: [subjective but specific -- "response felt sluggish at
  200ms delay" not "felt bad"]
- Player action counts: [if relevant]
- Iteration count: [how many attempts to get it working]

### Recommendation: [PROCEED / PIVOT / KILL]

[One paragraph explaining the recommendation with evidence]

### If Proceeding
[What needs to change for a production-quality implementation]
- Architecture requirements
- Performance targets
- Scope adjustments from the original design
- Estimated production effort

### If Pivoting
[What alternative direction the results suggest]

### If Killing
[Why this concept does not work and what we should do instead]

### Lessons Learned
[Discoveries that affect other systems or future work]
```

8. **Output a summary** to the user with: the core question, the result, and
   the recommendation. Link to the full report at
   `prototypes/[concept-name]/REPORT.md`.

### Important Constraints

- Prototype code must NEVER import from production source files
- Production code must NEVER import from prototype directories
- If the recommendation is PROCEED, the production implementation must be
  written from scratch -- prototype code is not refactored into production
- Total prototype effort should be timeboxed to 1-3 days equivalent of work
- If the prototype scope starts growing, stop and reassess whether the
  question can be simplified
