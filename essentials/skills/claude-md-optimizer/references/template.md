# CLAUDE.md Template

This is the canonical structure for an optimized CLAUDE.md file using the 4-tier architecture.

**Tier 1** (this file): compact critical rules, mandatory operational rules, navigation tables.
**Tier 1.5** (rules files): hard constraints in `.claude/rules/` (auto-loaded every session).
**Tier 2** (examples files): detailed patterns with code examples in `.claude/examples/`.
**Tier 3** (skills): interactive workflow procedures in `.claude/skills/`.

---

# [Project Name]

> [One-sentence project description]

**Stack**: [Tech] | [Tech] | [Tech] | [Tech]

---

## MANDATORY RULES (ALL AGENTS MUST FOLLOW)

**These rules are NON-NEGOTIABLE. Violation = immediate stop.**

### Tool Usage
- [Tool restrictions, e.g., "NEVER add description parameter to Bash tool calls"]
- [Path conventions, e.g., "ALWAYS use relative paths in Bash commands"]

### File Safety
- [File protection, e.g., "NEVER delete, overwrite, or modify .env files"]
- [Deletion policy, e.g., "NEVER delete files unless the plan explicitly names them AND user confirms"]

### Sub-Agent Blocking Policy
- [Test restrictions, e.g., "ONLY run unit tests. NEVER run integration tests"]
- [Blocking behavior, e.g., "If ANY tool call is denied, STOP and report"]
- [Error handling, e.g., "If unexpected errors, STOP and report. Do NOT retry destructive operations"]

---

## Project Structure

```
project-root/
├── [key-dirs]/          # [Brief annotation]
├── [key-dirs]/          # [Brief annotation]
└── .claude/
    ├── rules/           # Tier 1.5: hard constraints (auto-loaded)
    │   ├── code.md
    │   ├── testing.md
    │   └── database.md
    ├── examples/        # Tier 2: detailed patterns (on-demand)
    │   ├── code.md
    │   ├── testing.md
    │   └── anti-patterns.md
    ├── agents/          # Agent definitions (if using sub-agents)
    │   ├── task-executor.md
    │   └── code-reviewer.md
    └── skills/          # Tier 3: workflow procedures
        ├── [project]-feature-dev/
        └── [project]-code-review/
```

### Code Standards (always active)

**Naming**: [Pattern] → `{Template}`, [Pattern] → `{Template}`

**[Language] rules**:
- [Critical rule as one-liner]
- [Critical rule as one-liner]
- [Forbidden pattern as one-liner]

**Testing rules**:
- [Critical testing rule as one-liner]
- [Critical testing rule as one-liner]

**Database rules**:
- [Critical database rule as one-liner]

## Commands

```bash
# [Category]
[command]  # [Description]
```

## MCP Servers

**[Server Name]** - [Purpose]:
```bash
claude mcp add [name] [command]
```

Use for: [bullet list]

## Skills & Agents

### Workflow Skills

| Skill | When to Invoke |
|-------|---------------|
| [project]-feature-dev | Starting a new feature from scratch |
| [project]-code-review | Reviewing a PR or code changes |
| [project]-bugfix | Investigating and fixing a reported bug |

### Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| task-executor | sonnet | Ad-hoc tasks (small features, refactoring, test fixes) |
| code-reviewer | haiku | Fast conventions linter (naming, imports, patterns) |
| architecture-reviewer | sonnet | Deep review: architecture, complexity, risk |

## Delegation

Main conversation = orchestrator ONLY. NEVER use Edit/Write on `src/` or `tests/` files. Delegate to sub-agents:

- Feature implementation → feature-workflow skill
- Bug fixes → bug-workflow skill
- Small tasks → task-executor agent
- Code review → code-reviewer + architecture-reviewer agents (parallel)
- Codebase exploration → Explore agent

## Reference Documentation

- `.claude/rules/` — Hard constraints (auto-loaded every session)
- `.claude/examples/` — Detailed patterns with code examples (on-demand)
- `.claude/agents/` — Agent definitions
- `.claude/docs/` — Domain documentation

---

### Subdirectory CLAUDE.md Files (Tier 1 Variant)

For projects with architectural layers, domain boundaries, monorepo packages, or mixed tech stacks, create scoped CLAUDE.md files in subdirectories. Claude Code loads these automatically when working on files within that subdirectory, alongside the root CLAUDE.md.

**Template for subdirectory CLAUDE.md**:
```markdown
# [Directory Name]

> [One-line purpose/architectural role]

## Constraints
- [Layer-specific dependency rules, e.g., "No imports from infrastructure/"]
- [Directory-specific conventions not in root CLAUDE.md]

## Commands
```bash
[Directory-specific commands if different from root]
```
```

**Examples of good candidates**:
- Hexagonal architecture layers: `domain/CLAUDE.md` ("Pure business logic, no framework imports"), `infrastructure/CLAUDE.md` ("Adapter implementations, repository patterns")
- Symfony bundles: `src/OrderBundle/CLAUDE.md` (bundle-specific entity conventions, service naming)
- Go packages: `pkg/auth/CLAUDE.md` (package-specific interfaces, testing approach)
- DDD bounded contexts: `src/Billing/CLAUDE.md` (aggregate rules, event naming)
- Monorepo packages: `packages/api/CLAUDE.md` vs `packages/web/CLAUDE.md`
- Mixed tech stacks: Node.js service directory within a PHP project

**Rules**: Keep compact. Never duplicate root CLAUDE.md content. Only add what is unique to that directory.

---

## Template Guidance

### What to KEEP in CLAUDE.md (Tier 1)

- **Project overview**: Name, one-line description, tech stack
- **Mandatory Rules**: Operational/safety rules for all agents (tool usage, file safety, blocking policy)
- **Project structure**: Directory tree with `.claude/` subdirectories
- **Code Standards**: Critical rules as compact one-liners
- **Commands**: How to run, build, test (not the patterns to test)
- **MCP servers**: Available servers and their purposes
- **Skills & Agents**: Skills matrix + Agents table
- **Delegation**: Agent routing (if using orchestrator pattern)
- **Reference Documentation**: Pointers to rules, examples, and other docs

### What to put in Rules Files (Tier 1.5)

- **Binary constraints**: MUST/NEVER/ALWAYS rules
- **Import ordering**: Required import group order
- **Testing constraints**: Forbidden mock patterns, required test structure
- **Database constraints**: No migrations, use repositories only
- **Bundle dependencies**: Allowed/forbidden cross-module imports
- **Cross-reference**: Each file ends with pointer to corresponding examples file

### What to put in Examples Files (Tier 2)

- **Code patterns**: Language-specific patterns with Good/Bad examples
- **Testing strategies**: What to test, how to organize tests, helper APIs
- **API design patterns**: REST conventions, error handling examples
- **Database patterns**: Query patterns, repository patterns
- **Frontend patterns**: Component structure, state management
- **Anti-patterns**: Common mistakes with explanations

### What to create as Skills (Tier 3)

- **Feature development**: Step-by-step workflow for new features
- **Code review**: Review checklist and procedure
- **Bug fix**: Investigation and fix workflow
- **Deployment**: CI/CD and release procedure
- **Migration**: Database or framework migration steps

### Mandatory Rules Section

The Mandatory Rules section is distinct from Code Standards:
- **Code Standards** = coding conventions (naming, imports, patterns)
- **Mandatory Rules** = operational rules (tool usage, file safety, blocking behavior)

Mandatory Rules apply to the orchestrator AND all agents. Use ALL-CAPS headers and severity language to signal importance.

### Promoting Rules to CLAUDE.md

The "Code Standards (always active)" section is key. These rules are always visible, including to sub-agents.

**Promote when**: ignoring the rule would produce incorrect code.
**Format**: one-liner per rule, no code blocks, no multi-line explanations.
**Detailed version**: keep in the corresponding examples file.

### Sub-Agent Considerations

Sub-agents see CLAUDE.md + rules files by default (both auto-loaded). To ensure they also follow detailed patterns:

1. **Critical rules in Code Standards + Rules files**: Always visible, no action needed.
2. **Examples file references**: Add delegation instructions or agent prompts telling sub-agents to read examples files before writing code.

Example in agent definition:
```
Before writing ANY code, read these files:
- `.claude/examples/code.md`
- `.claude/examples/testing.md`
```

### Agent Definitions

If the project uses sub-agents, create `.claude/agents/` with:
- **Frontmatter**: name, description (use `>` block scalar), model, tools
- **Embedded guardrails**: Duplicate critical safety rules in each code-writing agent
- **Read-only advisors**: Restrict tools to Read, Grep, Glob, Bash
- **Registration**: Add to Agents table in CLAUDE.md

### Cross-Reference Pattern

Standardize cross-references across all files:
- **Rules files** end with: `## Reference\nFor detailed patterns: .claude/examples/{topic}.md`
- **Agent prompts** include: `Before writing ANY code, read: [list of examples files]`
- **CLAUDE.md** includes: `## Reference Documentation` section at bottom
