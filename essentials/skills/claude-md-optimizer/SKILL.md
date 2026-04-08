---
name: claude-md-optimizer
description: Optimize CLAUDE.md files using a 4-tier architecture for rules, examples, and workflows. Use when the user asks to optimize, refactor, or improve a CLAUDE.md file, reduce its token usage, improve sub-agent convention adherence, or create a more maintainable project documentation structure. Also use when analyzing existing CLAUDE.md files to identify optimization opportunities or when setting up new CLAUDE.md files following best practices.
---

# CLAUDE.md Optimizer

Optimize CLAUDE.md files using a 4-tier architecture that balances token efficiency with convention adherence, especially for sub-agents.

## Core Principle: 4-Tier Architecture

**Do NOT extract everything into skills.** Skills are demand-loaded (only when explicitly invoked), so conventions placed in skills won't be followed by sub-agents or during normal coding unless someone remembers to invoke the skill first.

Instead, use a **4-tier architecture**:

### Tier 1: CLAUDE.md (Always Active)
Critical rules, project structure, and commands. These are compact one-liners loaded into every context, including sub-agent contexts. Also includes a **Mandatory Rules** section for operational/safety rules that apply to the orchestrator and all agents.

**What goes here**: project overview, tech stack, directory structure, commands, compact critical rules (Code Standards), mandatory operational rules (tool usage, file safety), convention/skill navigation tables.

#### Tier 1 Variant: Subdirectory CLAUDE.md Files

Claude Code also loads `CLAUDE.md` files placed in subdirectories — scoped to that subdirectory. When working on files within a subdirectory, Claude sees both the root CLAUDE.md and the subdirectory's CLAUDE.md. This enables layer- or domain-specific instructions without bloating the root file.

**When to use subdirectory CLAUDE.md files**:
- **Architectural layers** with distinct rules — e.g., in hexagonal architecture: `domain/CLAUDE.md` (no infrastructure imports, pure business logic), `infrastructure/CLAUDE.md` (adapter patterns, repository implementations), `application/CLAUDE.md` (use case orchestration, DTO rules), `presentation/CLAUDE.md` (controller conventions, request validation)
- **Domain-specific directories** — e.g., Symfony bundles (`src/OrderBundle/CLAUDE.md`), Go packages (`pkg/auth/CLAUDE.md`), bounded contexts in DDD (`src/Billing/CLAUDE.md`)
- **Monorepo packages** with independent conventions — e.g., `packages/api/CLAUDE.md` vs `packages/web/CLAUDE.md`
- **Subdirectories with a different tech stack** — e.g., a Node.js service within a PHP project, a Python ML pipeline alongside a Go API

**When NOT to use**:
- Small projects where everything fits in the root CLAUDE.md
- Directories that share identical conventions with the root (don't duplicate)

**Keep subdirectory CLAUDE.md files compact** — same Tier 1 principles as root: purpose, key constraints, specific commands. Never duplicate root content; only add what is unique to that directory.

### Tier 1.5: Rules Files (Auto-Loaded Every Session)
Hard constraints stored in `.claude/rules/`. Claude Code automatically loads all `.md` files in this directory into every session — no explicit reading required. These are binary constraints (MUST/NEVER) that, if violated, produce incorrect or dangerous results.

**What goes here**: "Always X", "Never Y", "Must Z" rules. No code examples needed — just the constraint. Each rule file should end with a cross-reference to the corresponding examples file.

### Tier 2: Knowledge Skills (Auto-Triggered Reference)
Detailed patterns with code examples packaged as skills with `user-invocable: false`. Claude auto-triggers these based on description relevance — no explicit "read this file" instruction needed. Optionally scoped to specific file patterns using the `paths` frontmatter field.

**What goes here**: detailed code examples, full pattern descriptions, Good/Bad comparisons, API reference for project-specific helpers, anti-patterns with explanations.

**Frontmatter**:
```yaml
---
name: testing-patterns
description: Detailed testing patterns, mock strategies, FakerTrait API, and Good/Bad examples. Loaded when writing or reviewing tests.
user-invocable: false
paths:
  - "tests/**/*"
  - "**/*Test.php"
---
```

### Tier 3: Workflow Skills (On-Demand Workflows)
Interactive, step-by-step workflows invoked explicitly via slash commands. These are for *doing things*, not for *knowing things*.

**What goes here**: feature development workflow, code review checklist, deployment procedure, bug fix workflow, migration steps.

### Why This Matters

| Tier | Location | Loading | Sub-agent sees it? | Best for |
|------|----------|---------|-------------------|----------|
| 1 | CLAUDE.md | Always | Always | Project structure, commands, compact rules |
| 1 (sub) | `subdir/CLAUDE.md` | When in subdir | When in subdir | Directory-specific overrides/additions |
| 1.5 | `.claude/rules/` | Auto-loaded every session | Always | Hard constraints (MUST/NEVER) |
| 2 | Skills (`user-invocable: false`) | When Claude decides relevant | When invoked | Detailed patterns with code examples |
| 3 | Skills (default) | When invoked | When invoked | Interactive workflows |

**The key insight**: Claude Code auto-loads all `.md` files in `.claude/rules/`. This means rules placed there are visible to all agents every session without any explicit reading. This is distinct from example files that must be explicitly read. The old "conventions/" approach didn't distinguish between auto-loaded constraints and on-demand references.

### Hooks: Beyond the 4 Tiers

Hooks are a parallel enforcement mechanism — not a tier, but a complement to the architecture. Unlike CLAUDE.md instructions (honored ~70% of the time), hooks execute 100% of the time on their lifecycle event.

**Use hooks when**:
- A constraint must be enforced absolutely (security rules, file protection, blocking)
- You need to react to tool results regardless of Claude's behavior (logging, linting)
- You want to validate completeness before Claude stops (Stop hook)

**Do not put hook-worthy rules only in CLAUDE.md or rules files** — if a rule must never be violated, it belongs in a hook.

See [optimization-guide.md](references/optimization-guide.md) for the full list of hook types and lifecycle events.

**Benefits**:
- Hard constraints are always enforced (Tier 1 + 1.5)
- Detailed patterns available when needed without bloating context (Tier 2)
- Workflows remain interactive and structured (Tier 3)
- 50-70% token reduction on CLAUDE.md while improving convention adherence

## Parallelization Strategy

**CRITICAL**: Use sub-agents to parallelize independent analysis tasks for maximum efficiency.

### When to Parallelize

Launch multiple Task agents concurrently for:

1. **Project exploration** (Step 0):
   - Agent 1: Explore backend structure and patterns
   - Agent 2: Explore frontend structure and patterns
   - Agent 3: Explore test structure and conventions
   - Agent 4: Explore configuration and tooling

2. **Code analysis** (Step 2):
   - Agent 1: Analyze backend code conventions
   - Agent 2: Analyze frontend patterns
   - Agent 3: Analyze testing strategies
   - Agent 4: Analyze API/database patterns

3. **Skill creation** (Step 5):
   - Create multiple skills in parallel using skill-creator
   - Each skill creation is independent

### Sub-Agent Types to Use

**Explore agent** (thoroughness: "medium"):
- Finding files by pattern across the project
- Searching for specific code patterns
- Understanding directory organization
- Quick codebase reconnaissance

**General-purpose agent**:
- Deep analysis of specific areas (backend, frontend, tests)
- Reading and analyzing multiple files
- Extracting conventions and patterns
- Complex multi-step analysis

### Example Parallelization

```
Launch 4 Explore agents in parallel:
1. "Explore backend structure - find all backend code, identify framework, discover patterns"
2. "Explore frontend structure - find UI components, identify framework, discover patterns"
3. "Explore test structure - find test files, identify frameworks, discover organization"
4. "Explore configs - find all config files (package.json, pyproject.toml, etc.)"
```

**Result**: 4x faster than sequential analysis.

## Optimization Workflow

### 0. Scan the Project (REQUIRED FIRST STEP)

**CRITICAL**: Before optimizing or creating CLAUDE.md, scan the actual project to understand its structure and conventions.

**Use parallel Explore agents** for maximum efficiency:

```
Launch 4 Explore agents in parallel (thoroughness: "medium"):

Agent 1: "Explore backend - find all backend code files, identify framework used,
         discover code organization patterns, and identify key entry points"

Agent 2: "Explore frontend - find all UI components, identify framework/library used,
         discover component patterns, and identify styling approach"

Agent 3: "Explore tests - find all test files, identify testing frameworks,
         discover test organization, and identify testing patterns"

Agent 4: "Explore configs - find package.json, pyproject.toml, Makefile, docker-compose,
         and any other configuration files to identify tech stack and tooling"
```

**What to discover from parallel exploration**:

1. **Project structure**:
   - Backend: Framework, entry points, route/endpoint patterns
   - Frontend: Framework, component structure, state management
   - Tests: Frameworks, organization (unit/integration/e2e)
   - Configs: Dependencies, scripts, build tools

2. **Actual conventions**:
   - Code organization patterns (file structure, naming)
   - Import/export patterns
   - Type usage (TypeScript, JSDoc, Python type hints)
   - Testing approaches and patterns
   - API design patterns

3. **Project context**:
   - Purpose (from README or package description)
   - Technologies in active use
   - Development workflow (commands, tooling)
   - Existing documentation

**Do NOT create CLAUDE.md from templates alone**. The CLAUDE.md and extracted content must reflect the actual project, not generic examples.

### 1. Analyze Existing CLAUDE.md

For existing CLAUDE.md files, run the analysis script:

```bash
${CLAUDE_SKILL_DIR}/scripts/analyze_claude_md.py /path/to/CLAUDE.md
```

This generates an optimization report identifying:
- Content that should stay in CLAUDE.md (Tier 1)
- Operational rules for the Mandatory Rules section (Tier 1)
- Content that should move to rules files (Tier 1.5)
- Content that should move to examples files (Tier 2)
- Content that should become skills (Tier 3)
- Agent definition recommendations
- Estimated token savings
- Priority levels

If creating a new CLAUDE.md, skip to step 2 after completing the project scan (step 0).

### 2. Classify Content into Tiers

**After parallel exploration completes**, classify everything you found into tiers.

**Tier 1 — Keep in CLAUDE.md** (always loaded):
- Project name and one-line description
- Tech stack list (not usage patterns)
- Directory structure with brief annotations
- Commands to run/build/test
- MCP server installation commands
- **Mandatory Rules section** (operational/safety rules for all agents)
- **Critical code standards as compact one-liners** (naming, forbidden patterns, must-follow rules)
- Rules references (auto-loaded, no explicit reading needed)
- Examples references table (which files to read when)
- Skills matrix (which workflow skill to invoke when)
- Agents table (if project uses sub-agents)
- Delegation routing (if project uses orchestrator pattern)
- Document references

**Tier 1.5 — Move to rules files** (auto-loaded every session):
- Binary constraints: "Always X", "Never Y", "Must Z"
- Hard rules that produce incorrect code if ignored
- Import ordering rules
- Testing constraints (forbidden patterns, required patterns)
- Database constraints
- Bundle/module dependency rules
- Each file ends with: `## Reference\nFor detailed patterns: .claude/examples/{topic}.md`

**Tier 2 — Move to examples files** (read before writing code):
- Code conventions with detailed examples
- Testing strategies and patterns with code examples
- API design patterns with examples
- Database patterns and queries
- Frontend component patterns
- Logging configuration and patterns
- Security practices with examples
- Anti-patterns with explanations

**Tier 3 — Create as skills** (invoked for workflows):
- Feature development workflow
- Code review procedure
- Bug fix workflow
- Deployment procedure
- Migration procedure
- Release process

**Hook candidates — flag for hook implementation, not rules files**:
- Security constraints that must never be violated (e.g., never write to `.env`)
- Bash commands that must be blocked absolutely (e.g., `rm -rf`)
- Completion validation that must always run before Claude stops
- Any rule where "Claude might ignore it" is unacceptable

**DELETE (do not redistribute into tiers)**:
- Generic advice ("write clean code", "follow best practices") — Claude follows these without being told
- Rules Claude already follows correctly without being told
- Full README or architecture doc content — reference with `@docs/file.md` instead
- Execution plans or running checklists (too volatile to maintain)

**The key distinctions**:
- Rules files store *hard constraints* (binary, auto-loaded).
- Examples files store *patterns with code* (detailed, on-demand).
- Skills store *procedures* (step-by-step workflows with actions to take).

**Optional: Use parallel general-purpose agents for deep analysis**:

If the exploration revealed complex areas needing detailed analysis:

```
Launch multiple general-purpose agents in parallel:

Agent 1: "Analyze backend code conventions - read 3-5 backend files, identify
         patterns for imports, error handling, API structure, and database usage"

Agent 2: "Analyze frontend conventions - read 3-5 component files, identify
         patterns for component structure, state management, styling, and props"

Agent 3: "Analyze testing strategy - read test files, identify testing patterns,
         coverage approach, mocking strategy, and test organization"
```

See [extraction-guide.md](references/extraction-guide.md) for detailed extraction rules.

### 3. Promote Critical Rules to CLAUDE.md (Tier 1)

**This step is essential for sub-agent adherence.** Sub-agents receive CLAUDE.md in their context but won't read examples files unless explicitly told to. Promote the most critical rules as compact one-liners.

**What to promote** (condense to single lines):
- Naming conventions: `Entity → {Name}Entity, Service → {Domain}Service`
- Forbidden patterns: `Never mock entities, use FakerTrait instead`
- Mandatory patterns: `declare(strict_types=1) in every PHP file`
- Import rules: `Always use ClassName::class, never string literals for FQCNs`
- Testing rules: `Test naming: test_{method}_{scenario}_{expected}()`

**Format for CLAUDE.md**:
```markdown
### Code Standards (always active)

**Naming**: Entity → `{Name}Entity`, Service → `{Domain}Service`, Repository → `{Entity}Repository`

**Code rules**:
- `declare(strict_types=1)` in every file
- Constructor injection with `private readonly`
- Always use `ClassName::class`, never string literals

**Testing rules**:
- Never mock entities, use FakerTrait: `$this->fake()->entity()`
- Test method naming: `test_{method}_{scenario}_{expected}()`
```

**Rule of thumb**: If a sub-agent ignoring this rule would produce incorrect code, it belongs in CLAUDE.md.

**Also add a Mandatory Rules section** for operational/safety rules:
```markdown
## MANDATORY RULES (ALL AGENTS MUST FOLLOW)

**These rules are NON-NEGOTIABLE. Violation = immediate stop.**

### Tool Usage
- [Tool restrictions that apply to orchestrator + all agents]

### File Safety
- [File protection rules — what to never delete/modify]
- [Blocking policy — what to do when tool calls are denied]
```

These are distinct from Code Standards. Code Standards are coding conventions. Mandatory Rules are operational rules about *how agents should behave* (tool usage, file safety, blocking policies). Use ALL-CAPS headers and severity language ("Violation = immediate stop") to signal their importance.

### 4. Create Rules Files (Tier 1.5)

Create `.claude/rules/` directory with hard constraint files. Claude Code auto-loads all `.md` files in this directory every session.

**Rules file naming**:
- `code.md` or `php-code.md` — Language/framework hard rules
- `testing.md` — Testing constraints
- `database.md` — Database access constraints
- `security.md` — Security constraints

**Rules file structure**:
```markdown
# [Area] Rules

## Hard Rules

- `declare(strict_types=1)` in every PHP file
- PSR-12 coding standard
- `final` classes by default
- Constructor injection with `private readonly`
- Never use generic `\Exception`

## [Category]

[More binary constraints...]

## Reference

For detailed patterns and examples: `.claude/examples/{topic}.md`
```

**Optional: Scope rules to specific paths** using YAML frontmatter:
```markdown
---
paths:
  - "src/api/**/*.ts"
  - "tests/**/*"
---
# Testing Rules
...
```
Rules with `paths` only load when Claude is working with matching files.

**Key characteristics**:
- Binary constraints only: MUST/NEVER/ALWAYS
- No code examples (those go in knowledge skills)
- Compact — each rule fits on one line
- Auto-loaded — no explicit reading needed
- Cross-reference to the corresponding knowledge skill at bottom

### 5. Create Knowledge Skills (Tier 2)

Create skills with `user-invocable: false` to hold detailed patterns and code examples. Claude auto-triggers these based on description relevance — no explicit "read before writing code" instruction needed.

**Knowledge skill naming**:
- `[project]-code-patterns` — Language/framework code patterns
- `[project]-testing-patterns` — Testing strategies and patterns
- `[project]-database-patterns` — Database access and query patterns
- `[project]-api-patterns` — API design patterns
- `[project]-frontend-patterns` — Frontend component patterns
- `[project]-anti-patterns` — Common mistakes to avoid

**Knowledge skill frontmatter**:
```yaml
---
name: testing-patterns
description: Detailed testing patterns, mock strategies, FakerTrait API, and Good/Bad code examples for this project. Loaded when writing or reviewing tests.
user-invocable: false
paths:
  - "tests/**/*"
  - "**/*Test.php"
---
```

- Use `paths` to scope loading to specific file patterns (optional but recommended)
- Write description so Claude recognizes when the skill is relevant
- Omit `paths` for skills that are broadly relevant across the project

**Knowledge skill body structure**:
```markdown
# [Area] Patterns

## [Pattern Category]

### Rule
[Clear statement of the rule]

### Why
[Brief explanation]

### Example
```[lang]
// Good
[correct code]

// Bad
[incorrect code]
```

## References
- [Link to helper files or API references]
```

**Key characteristics**:
- Detailed code examples with Good/Bad comparisons
- Auto-triggered by Claude (no explicit reading instruction needed)
- `user-invocable: false` — hidden from `/` menu, used by Claude only
- Base on actual project code, not generic examples

**Add rules listing to CLAUDE.md** (knowledge skills don't need listing — Claude finds them automatically):
```markdown
## Rules (auto-loaded)

Hard constraints loaded every session. No explicit reading needed:

- `.claude/rules/code.md` — Language/framework constraints
- `.claude/rules/testing.md` — Testing constraints
- `.claude/rules/database.md` — Database constraints
```

### 6. Create Agent Definitions (if applicable)

If the project uses sub-agents (Task/Agent tool), create `.claude/agents/` with agent definition files.

**When to create agents**:
- Project uses an orchestrator pattern (main conversation delegates)
- Multiple distinct task types (code writing, review, testing, research)
- Need for specialized tools/permissions per task type

**Agent frontmatter template**:
```markdown
---
name: task-executor
description: >
  Execute ad-hoc tasks using TDD. Use for bug fixes, small features,
  test fixes, and refactoring.

  <example>
  Context: User wants a small refactoring done
  user: "Rename the getOrder method to findOrderById"
  </example>
model: sonnet
color: cyan
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---
```

**CRITICAL**: Always use `description: >` (YAML folded block scalar) when the description contains `<example>` tags. Bare YAML values with angle brackets break frontmatter parsing and the agent won't be detected.

**Agent structure**:
```markdown
# [Agent Name]

[One-line purpose]

## Mandatory Rules

[Duplicate critical safety rules here — agents don't reliably read external files]

## Scope

[What this agent does and doesn't do]

## Process

[Step-by-step process for the agent]

## Constraints

[Hard limits — what the agent must never do]

## Output Format

[What the agent returns when done]
```

**Guardrail embedding pattern**: Every code-writing agent must have safety rules duplicated directly in its prompt. Do not rely on agents reading external rule files for critical safety constraints. Read-only advisor agents (tools restricted to Read, Grep, Glob, Bash) need fewer guardrails since they can't modify code.

**Register agents in CLAUDE.md**:
```markdown
### Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| task-executor | sonnet | Ad-hoc tasks (small features, refactoring) |
| code-reviewer | haiku | Fast conventions linter |
| architecture-reviewer | sonnet | Deep design/risk review |
```

### 7. Create Delegation Architecture (if applicable)

If the project uses an orchestrator pattern, add delegation guidance to CLAUDE.md.

**Orchestrator-only pattern**:
```markdown
## Delegation

Main conversation = orchestrator ONLY. NEVER use Edit/Write on `src/` or `tests/` files. Delegate to sub-agents:

- Feature implementation → feature-workflow skill
- Bug fixes → bug-workflow skill
- Small tasks → task-executor agent
- Code review → code-reviewer + architecture-reviewer agents
- Codebase exploration → Explore agent
```

**Agent selection decision tree** (for a delegation-rules skill):
```
Is this a feature with multiple slices?
  YES → /feature-workflow
  NO  → Is this a bug fix?
          YES → /bug-workflow
          NO  → Is this a code review?
                  YES → code-reviewer + architecture-reviewer (parallel)
                  NO  → Is this a small, well-defined task?
                          YES → task-executor agent
                          NO  → Is this research/exploration?
                                  YES → Explore agent
                                  NO  → Handle in main conversation
```

**Create a delegation-rules skill** that documents:
- Agent routing matrix (task type → agent/skill)
- Sub-agent prompt template (context to provide)
- Permission requirements (mode: "dontAsk" for implementation agents)
- Guardrail cross-references

### 8. Create Workflow Skills (Tier 3)

**IMPORTANT**: Use the `skill-creator` skill to create workflow skills.

**Only create workflow skills for interactive procedures**, not for reference material. Workflow skills guide Claude through a multi-step process. Reference material belongs in knowledge skills (Tier 2, `user-invocable: false`).

**Skills can be created in parallel** since they're independent:

```
If creating 3 skills, invoke skill-creator 3 times in parallel:

1. "Use /skill-creator to create a feature development workflow skill"
2. "Use /skill-creator to create a code review workflow skill"
3. "Use /skill-creator to create a deployment procedure skill"
```

**Skill naming convention** (workflows, not conventions):
- `[project]-feature-dev` — Feature development workflow
- `[project]-code-review` — Code review checklist and procedure
- `[project]-bugfix` — Bug investigation and fix workflow
- `[project]-deployment` — Deployment procedure
- `[project]-migration` — Database migration steps

**DO NOT create workflow skills for**:
- Code constraints (use rules files in `.claude/rules/`)
- Code patterns with examples (use knowledge skills with `user-invocable: false`)
- Naming rules (promote to CLAUDE.md)
- Anything that must be active in every session (use CLAUDE.md or rules files)

**Skills matrix in CLAUDE.md**:
```markdown
## Skills

| Skill | When to Invoke |
|-------|---------------|
| [project]-feature-dev | Starting a new feature |
| [project]-code-review | Reviewing a PR or code changes |
| [project]-bugfix | Investigating and fixing a bug |
```

### 9. Create Subdirectory CLAUDE.md Files (if applicable)

During the project scan (Step 0), identify subdirectories that warrant their own CLAUDE.md. Look for:

- **Architectural layers**: `domain/`, `application/`, `infrastructure/`, `presentation/` in hexagonal/clean architecture — each layer has distinct dependency rules and conventions
- **Domain boundaries**: Symfony bundles, Go packages, DDD bounded contexts — self-contained areas with their own conventions
- **Monorepo packages**: Independent packages with their own tech stack, build commands, or testing setup
- **Mixed tech stacks**: A subdirectory using a different language or framework than the root project

**Subdirectory CLAUDE.md structure** (keep compact):
```markdown
# [Directory Name]

> [One-line purpose/role in the architecture]

## Constraints
- [Layer-specific rules, e.g., "No imports from infrastructure/ — this is the domain layer"]
- [Directory-specific conventions]

## Commands
```bash
[Directory-specific build/test commands if different from root]
```
```

**Do NOT create subdirectory CLAUDE.md files** for directories that follow the same conventions as the root — it only adds duplication.

### 10. Add Cross-References

Standardize cross-references across all files (including subdirectory CLAUDE.md files if created):

**Rules files** end with:
```markdown
## Reference

For detailed patterns and examples: `.claude/examples/{topic}.md`
```

**Agent prompts** include:
```markdown
Before writing ANY code, read these files:
- `.claude/examples/code.md`
- `.claude/examples/testing.md`
```

**CLAUDE.md** includes at bottom:
```markdown
## Reference Documentation

- `.claude/rules/` — Hard constraints (auto-loaded every session)
- `.claude/examples/` — Detailed patterns with examples (on-demand)
- `.claude/agents/` — Agent definitions (if using sub-agents)
```

### 11. Add MEMORY.md Guidance (optional)

If the project will have long-lived usage, set up auto-memory:

**MEMORY.md organization**:
- 200-line budget (lines after 200 are truncated in context)
- Section structure with topic headers and dates
- Scannable bullet format for quick reference
- Operational gotchas and tool quirks

**Migration path**:
- If a memory entry is a hard constraint → migrate to `.claude/rules/`
- If a memory entry is a pattern with examples → migrate to `.claude/examples/`
- Keep only operational learnings and tool-specific gotchas in MEMORY.md

### 12. Verify Optimization

Check that CLAUDE.md:
- Is under 200 lines (target: compact but complete)
- Contains a **Mandatory Rules** section for operational/safety rules
- Contains a **Code Standards** section with compact one-liners
- Has Rules listing pointing to `.claude/rules/` (auto-loaded)
- Has Examples References table pointing to `.claude/examples/` (on-demand)
- Has a Skills matrix for workflow skills only (not conventions)
- Contains no multi-line code examples (those belong in examples files)
- Contains no generic advice Claude already follows without being told
- All rules are concrete and verifiable ("Use 2-space indentation", not "Format code properly")
- Sub-agents would produce correct code from CLAUDE.md + rules alone for basic cases

Check that `.claude/rules/` files:
- Contain only binary constraints (MUST/NEVER/ALWAYS)
- Have no detailed code examples (those belong in examples files)
- End with cross-reference to corresponding examples file
- Are auto-loaded (no explicit reading needed)

Check that knowledge skills (`user-invocable: false`) files:
- Contain detailed patterns with Good/Bad code comparisons
- Use `paths` frontmatter to scope loading where appropriate
- Have descriptions that clearly signal when Claude should load them
- Complement (not duplicate) the rules files

Check for hook candidates:
- Any rule in CLAUDE.md or rules files that must be enforced 100% → implement as a hook instead
- Security/file-protection rules are the most common hook candidates
- If hooks are needed, invoke `plugin-dev:hook-development` for implementation guidance

Check subdirectory CLAUDE.md files (if created):
- Are compact (purpose, constraints, commands only)
- Do not duplicate content from the root CLAUDE.md
- Each serves a directory with genuinely distinct conventions or architectural role

Check that agent files (if applicable):
- Have embedded guardrails (safety rules duplicated in the agent prompt)
- Use `description: >` block scalar for descriptions with `<example>` tags
- Read-only agents have restricted tool lists
- Are registered in CLAUDE.md's Agents table

## Template Structure

See [template.md](references/template.md) for the complete canonical structure.

**Key sections**:
1. **Project header**: Name and one-line description
2. **Tech Stack**: Technology list with brief annotations
3. **Mandatory Rules**: Operational/safety rules for all agents
4. **Project Structure**: Directory tree with `.claude/` subdirectories
5. **Code Standards (always active)**: Compact critical rules (Tier 1)
6. **Commands**: How to run things
7. **MCP Servers**: Available servers and their purposes
8. **Skills & Agents**: Skills matrix + Agents table (Tier 3)
9. **Delegation**: Agent routing (if using orchestrator pattern)
10. **Reference Documentation**: Pointers to rules, examples, and other docs

## Rules vs Knowledge Skills: When to Split

### Rules (Tier 1.5 — Auto-Loaded)
Hard constraints that Claude Code loads automatically every session. All agents see these without explicit reading.

```markdown
## Rules (auto-loaded)

- `.claude/rules/code.md` — Language hard constraints
- `.claude/rules/testing.md` — Testing constraints
- `.claude/rules/database.md` — Database constraints
```

No "when to read" needed — they're always loaded. Can optionally use `paths` frontmatter to scope to specific file patterns.

### Knowledge Skills (Tier 2 — Auto-Triggered)
Detailed patterns packaged as skills with `user-invocable: false`. Claude auto-triggers them based on description relevance — no explicit listing needed in CLAUDE.md.

```yaml
---
name: testing-patterns
description: Detailed testing patterns, FakerTrait API, mock strategies, and Good/Bad examples. Loaded when writing or reviewing tests.
user-invocable: false
paths:
  - "tests/**/*"
---
```

**The key difference from rules**: Rules are binary constraints (MUST/NEVER). Knowledge skills contain detailed patterns with code examples — the "how", not just the "what".

### Common Mistake

Do NOT put conventions in the workflow Skills matrix. If a trigger says "when writing tests" and the content is patterns/examples, it's a knowledge skill (`user-invocable: false`), not a workflow skill. Workflow skills should have triggers like "when starting a new feature" that imply a multi-step interactive procedure.

## Example Transformation

**Before** (verbose CLAUDE.md, ~1500 tokens):
```markdown
# Project

## Code Conventions
### Backend
- Use Pydantic for schemas
- Always use Depends() for DB sessions
[30 more lines...]

### Frontend
- Feature-based folders
- TanStack Query for API calls
[25 more lines...]

## Testing
- 70% unit tests
- 20% integration tests
[40 more lines...]

## API Design
- RESTful endpoints
- Return 201 for POST
[20 more lines...]
```

**After** (optimized CLAUDE.md with 4-tier approach, ~600 tokens):
```markdown
# Project

> E-commerce platform backend

**Stack**: Python 3.11+ | FastAPI | SQLAlchemy | SQLite | React 18 | Vite | Tailwind

---

## MANDATORY RULES (ALL AGENTS MUST FOLLOW)

### Tool Usage
- NEVER add `description` parameter to Bash tool calls

### File Safety
- NEVER delete/modify `.env` files
- If ANY tool call is denied, STOP and report

---

### Code Standards (always active)

**Naming**: Schema → `{Name}Create/Update/Response`, Route → `{resource}_router`

**Python rules**:
- Pydantic models for all request/response schemas
- `Depends()` for database sessions, never manual session management

**Testing rules**:
- Test method naming: `test_{method}_{scenario}_{expected}()`
- Use factory fixtures, never raw object construction

## Commands
```bash
cd backend && uv run uvicorn app.main:app --reload
uv run pytest tests/
```

## Skills & Agents

### Skills
| Skill | When to Invoke |
|-------|---------------|
| project-feature-dev | Starting a new feature |

### Agents
| Agent | Model | Purpose |
|-------|-------|---------|
| task-executor | sonnet | Ad-hoc tasks |

## Delegation

Main conversation = orchestrator ONLY. Delegate to sub-agents:
- Features → /feature-workflow
- Small tasks → task-executor agent

## Reference Documentation

- `.claude/rules/` — Hard constraints (auto-loaded every session)
- `.claude/examples/` — Detailed patterns with code examples (on-demand)
```

**Rules files created** (in `.claude/rules/`):
- `code.md` — Python hard constraints (strict types, imports, naming)
- `testing.md` — Testing constraints (forbidden patterns, required structure)

**Knowledge skills created** (`user-invocable: false`):
- `code-patterns` — Python/FastAPI patterns with Good/Bad examples (auto-triggers when writing Python)
- `testing-patterns` — Testing patterns, mocking strategy, fixtures API (auto-triggers when writing tests)
- `anti-patterns` — Common mistakes to avoid (auto-triggers on relevant code)

**Result**: 60% token reduction. Hard constraints always enforced via auto-loaded rules. Detailed patterns auto-triggered by Claude when relevant. Sub-agents follow naming and testing rules even without reading examples files.

## Complete Parallelization Workflow

**Phase 1: Initial Project Scan (4 parallel Explore agents)**
```
Agent 1: Backend exploration
Agent 2: Frontend exploration
Agent 3: Test exploration
Agent 4: Config/tooling exploration
```
**Time**: ~30-60 seconds (vs 2-4 minutes sequential)

**Phase 2: Deep Analysis (optional, 3 parallel general-purpose agents)**
```
Agent 1: Backend convention analysis
Agent 2: Frontend convention analysis
Agent 3: Testing strategy analysis
```
**Time**: ~45-90 seconds (vs 3-5 minutes sequential)

**Phase 3: Skill Creation (N parallel skill-creator invocations)**
```
Create all extracted skills simultaneously:
- Knowledge skills (user-invocable: false) for patterns and examples
- Workflow skills for interactive procedures
```
**Time**: ~2-3 minutes per skill (all parallel)

**Total Time Savings**:
- Sequential: 8-12 minutes
- Parallel: 3-5 minutes
- **Speedup: 2-3x faster**

## Project Scanning Checklist

**USE PARALLEL EXPLORE AGENTS** to gather this information efficiently:

**Tech Stack Discovery** (from config agent):
- [ ] Check package.json, pyproject.toml, Gemfile, etc. for dependencies
- [ ] Identify frontend framework (React, Vue, Svelte, vanilla JS)
- [ ] Identify backend framework (FastAPI, Express, Rails, Django)
- [ ] Check for testing frameworks (pytest, Jest, Vitest, Playwright)
- [ ] Look for build tools (Vite, Webpack, Rollup, esbuild)

**Project Structure** (from all 4 agents):
- [ ] List main directories (src/, lib/, app/, components/, etc.)
- [ ] Identify configuration files location
- [ ] Find test directories
- [ ] Locate documentation directories

**Actual Conventions** (from domain-specific agents):
- [ ] Read 2-3 sample code files to identify patterns
- [ ] Check import/export patterns
- [ ] Look for type annotations or JSDoc
- [ ] Identify naming conventions (camelCase, snake_case, kebab-case)
- [ ] Check for linter/formatter configs (.eslintrc, .prettierrc, pyproject.toml)

**Commands** (from config agent):
- [ ] Check package.json scripts or Makefile
- [ ] Identify dev server command
- [ ] Identify test command
- [ ] Check for build/deployment commands

**Development Setup** (from config agent):
- [ ] Check for Docker/docker-compose
- [ ] Look for environment variable examples (.env.example)
- [ ] Identify database setup (if any)
- [ ] Check for MCP servers or other tools

**Always use parallel Explore agents for maximum efficiency. Do NOT explore sequentially.**

## Quick Reference

**Step 0 — Scan**: Launch 4 parallel Explore agents (backend, frontend, tests, configs)

**Step 1 — Analyze**: `${CLAUDE_SKILL_DIR}/scripts/analyze_claude_md.py /path/to/CLAUDE.md`

**Step 2 — Classify**: Sort content into Tier 1 (CLAUDE.md) / Tier 1.5 (rules) / Tier 2 (examples) / Tier 3 (skills)

**Step 3 — Promote**: Extract critical rules as compact one-liners for CLAUDE.md "Code Standards" + "Mandatory Rules" sections

**Step 4 — Rules files**: Create `.claude/rules/` with binary constraints (auto-loaded)

**Step 5 — Knowledge skills**: Create skills with `user-invocable: false` + `paths` for detailed patterns and code examples

**Step 6 — Agent definitions**: Create `.claude/agents/` with embedded guardrails (if project uses sub-agents)

**Step 7 — Delegation**: Add delegation routing to CLAUDE.md (if project uses orchestrator pattern)

**Step 8 — Workflow skills**: Use `/skill-creator` for interactive workflow skills only

**Step 9 — Subdirectory CLAUDE.md**: Create `subdir/CLAUDE.md` for architectural layers, domain boundaries, monorepo packages, or mixed tech stacks (only if applicable)

**Step 10 — Cross-references**: Rules → examples, agents → rules + examples, CLAUDE.md → all

**Step 11 — Memory**: Set up MEMORY.md with 200-line budget (optional)

**Step 12 — Verify**: Check all tiers are populated, cross-referenced, and consistent

**Parallelization**: Use Task tool with Explore/general-purpose agents for 2-3x speedup

**Size target**: 50–200 lines for project CLAUDE.md, 20–50 lines for global `~/.claude/CLAUDE.md`

**Key rule**: Hard constraints → rules/. Patterns with examples → knowledge skills (`user-invocable: false`). Workflows → workflow skills. Critical rules + operational rules → CLAUDE.md.

**REMEMBER**: Always scan the actual project first with parallel agents!

## Additional Reference

See [optimization-guide.md](references/optimization-guide.md) for broader Claude Code optimization topics: memory hierarchy, context management, hooks, thinking/effort levels, the decision framework for what goes where, and the quick start checklist.
