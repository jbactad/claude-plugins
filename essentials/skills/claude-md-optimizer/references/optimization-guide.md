# Claude Code Optimization Guide

Personal reference for getting the most out of Claude Code's memory, context, and extensibility systems.

Last updated: March 2026

## The Memory Hierarchy

Claude Code loads configuration in layers. More specific layers take precedence over broader ones.

### Layer 1: Global (personal, all projects)

Location: `~/.claude/`

```
~/.claude/
├── CLAUDE.md           # Personal preferences, loaded every session
├── rules/              # Global rules (always loaded, or glob-scoped)
├── skills/             # Global skills (progressive disclosure)
├── agents/             # Global subagents
└── settings.json       # Tool permissions, model config, hooks
```

`~/.claude/CLAUDE.md` is for personal preferences that apply everywhere: response style, favorite tools, language preferences, engineering principles you always want enforced.

### Layer 2: Project (team, shared via git)

Location: `<project-root>/`

```
<project-root>/
├── CLAUDE.md           # Project instructions, loaded at startup
├── CLAUDE.local.md     # Personal overrides, gitignored
└── .claude/
    ├── rules/          # Modular rules (always or glob-scoped)
    ├── skills/         # Project skills
    ├── agents/         # Project subagents
    ├── commands/       # Slash commands (merged with skills now)
    └── settings.json   # Project settings
```

### Layer 3: Subdirectory (lazy loaded)

Location: `<project-root>/subdir/CLAUDE.md`

Only loads when Claude reads files in that directory. Siblings never load (working in `frontend/` won't load `backend/CLAUDE.md`). Useful for monorepos.

### Layer 4: Auto Memory

Location: `~/.claude/projects/<project-hash>/memory/MEMORY.md`

Managed by Claude when you say "remember X". Accumulates cruft over time. Prune manually via `/memory` every ~10 sessions. Limited to 200 lines in the system prompt.


## Writing Effective CLAUDE.md Files

### Size targets

- Global `~/.claude/CLAUDE.md`: 20 to 50 lines
- Project `CLAUDE.md`: 50 to 200 lines
- Beyond 200 lines: split into `.claude/rules/` files

### What to include

- Tech stack and key dependencies
- Coding conventions that are specific and verifiable
- Architecture at a glance (a few bullets, not a full doc)
- Immutable rules (things that must never be violated)
- References to docs (`@docs/architecture.md`) rather than duplicating content

### What NOT to include

- Generic advice ("write clean code", "follow best practices")
- Things Claude already does correctly without being told
- Execution plans or running checklists (these change too often)
- Anything longer than a few lines that could live in `docs/` instead
- Full README or architecture doc content (reference it, don't duplicate)

### Writing style

Be concrete enough to verify. Examples:

- Good: "Use 2-space indentation"
- Bad: "Format code properly"
- Good: "Run `npm test` before committing"
- Bad: "Test your changes"
- Good: "Always validate inputs with Zod"
- Bad: "Handle validation"


## Rules (`.claude/rules/`)

Rules are markdown files that load into context. Two modes:

### Always-on rules (no frontmatter)

```markdown
<!-- .claude/rules/git-workflow.md -->
# Git Workflow
- Use conventional commits format
- Never force push to main
- Squash merge feature branches
```

Loads every session. Functionally equivalent to splitting CLAUDE.md into separate files. Useful for organization but does not save tokens.

### Conditional rules (with glob frontmatter)

```markdown
<!-- .claude/rules/api-security.md -->
---
globs: ["src/api/**/*.ts", "src/routes/**/*.ts"]
---
# API Security
- Always validate JWT tokens
- Rate limiting on all endpoints
- Parameterized queries only, no string concatenation
```

Only loads when Claude works on files matching the glob pattern. This is where you get actual token savings.

### When to use rules vs other mechanisms

- Rules: invariants that must always hold. Coding standards, security constraints, naming conventions.
- If Claude already follows a rule without being told: delete it.
- If a rule must be enforced 100% of the time: use a hook instead (rules are honored ~70% of the time, hooks are 100%).


## Skills (`.claude/skills/`)

Skills are the most powerful extension mechanism. They use progressive disclosure across three levels:

1. **Metadata** (loaded at startup): name + description from frontmatter. ~100 tokens per skill. Negligible overhead even with dozens of skills.
2. **Body** (loaded on invocation): full SKILL.md content, up to ~5,000 tokens. Only enters context when Claude determines the skill is relevant.
3. **Referenced files** (loaded on demand): additional markdown, scripts, resources in the skill directory. Only read when the body references them and the task needs them.

### Skill structure

```
.claude/skills/my-skill/
├── SKILL.md            # Main instructions (<500 lines)
├── resources/          # Additional docs loaded on demand
│   ├── patterns.md
│   └── examples.md
└── scripts/            # Executable scripts (output enters context, not code)
    └── analyze.py
```

### Frontmatter options

```yaml
---
name: my-skill
description: What this does and when to use it (max 1024 chars)
disable-model-invocation: true   # Only manual /my-skill, no auto-trigger
user-invocable: true             # Can be called as /my-skill
allowed-tools: Read, Grep, Glob  # Restrict tool access
model: opus                      # Override model
context: fork                    # Run in isolated context (subagent)
agent: Explore                   # Subagent type
---
```

### Key decisions

- `disable-model-invocation: true`: use when you want explicit control (deployments, destructive actions)
- `context: fork`: runs in a subagent with its own context window, keeps main context clean
- No frontmatter restrictions: Claude auto-invokes when it detects relevance from conversation context

### Reliability caveat

Vercel's evals found skills weren't auto-invoked in 56% of their test cases. If you need guaranteed activation, use rules or hooks instead. For important skills, you can also manually invoke with `/skill-name`.


## Subagents (`.claude/agents/`)

Subagents get their own context window. This is the key benefit: they don't pollute your main conversation.

### When to use subagents

- Deep exploration that would fill your main context
- Parallel analysis (up to 10 concurrent subagents)
- Tasks requiring restricted tool access (e.g., read-only code review)
- Research tasks where you only need the summary, not the full exploration

### Subagent file format

```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
maxTurns: 10
---

You are a senior security engineer. Review code for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication and authorization flaws
- Secrets or credentials in code

Provide specific line references and suggested fixes.
```

### Triggering subagents

- Explicit: "Use the security-reviewer subagent on this file"
- General: "Use subagents to review this" or "Use a subagent to research X"
- From skills: set `context: fork` in skill frontmatter
- Claude can auto-delegate based on agent descriptions

### Subagent tips

- Give each subagent one clear goal, input format, output format, and handoff rule
- Scope tools per agent (reviewers get read-only, implementers get write)
- Use Explore type subagents for research to keep main context clean
- Subagents inherit project context (skills, CLAUDE.md, rules) but have their own conversation window


## Hooks

Hooks are deterministic. Unlike CLAUDE.md instructions which Claude follows ~70% of the time, hooks execute 100% of the time on their lifecycle event.

### Four handler types

1. **Command hooks** (`type: "command"`): shell commands, receive JSON via stdin, return results via exit codes
2. **HTTP hooks** (`type: "http"`): POST JSON to a URL endpoint — useful for external integrations and logging
3. **Prompt hooks** (`type: "prompt"`): single-turn LLM evaluation using `$ARGUMENTS`
4. **Agent hooks** (`type: "agent"`): spawn subagents with tool access for deep verification

### Key lifecycle events

- **PreToolUse**: fires before any tool execution, can approve/deny/modify the action. Most powerful hook.
- **PostToolUse**: fires after tool succeeds. Good for formatting, linting, logging.
- **PostToolUseFailure**: fires after a tool fails. Good for error handling and recovery.
- **Stop**: fires when Claude finishes responding.
- **StopFailure**: fires when a turn ends due to an API error.
- **SubagentStart** / **SubagentStop**: fire when subagents are spawned and complete.
- **TaskCreated** / **TaskCompleted**: fire on task lifecycle events.
- **UserPromptSubmit**: fires when the user submits a prompt, before processing.
- **PermissionRequest**: fires when a permission dialog appears.
- **SessionStart** / **SessionEnd**: fire at session boundaries. SessionStart supports `$CLAUDE_ENV_FILE` for persisting env vars.
- **CwdChanged**: fires when working directory changes. Also supports `$CLAUDE_ENV_FILE`.
- **FileChanged**: fires when a watched file changes. Also supports `$CLAUDE_ENV_FILE`.
- **PreCompact** / **PostCompact**: fire before and after context compaction.
- **Notification**: fires when Claude sends notifications.
- **Elicitation** / **ElicitationResult**: fire during MCP user input handling.

### Configuration

Hooks are configured in `settings.json` (project or user level), not in CLAUDE.md. To disable all hooks temporarily, set `"disableAllHooks": true` in settings.

### When to use hooks vs rules

- "Never run `rm -rf`" in CLAUDE.md: honored ~70% of the time
- Same rule as a PreToolUse hook blocking the command: 100% enforcement
- For security rules, always prefer hooks over CLAUDE.md instructions


## Commands (`.claude/commands/`)

Commands and skills have been merged. A file at `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy`. Existing command files keep working.

Use commands (with `disable-model-invocation: true`) for workflows you explicitly trigger: deployments, PR creation, test runs, code reviews.

### The `$ARGUMENTS` placeholder

```markdown
---
name: fix-issue
description: Fix a GitHub issue by number
disable-model-invocation: true
---
Fix GitHub issue #$ARGUMENTS following our coding standards.
```

Running `/fix-issue 423` replaces `$ARGUMENTS` with `423`.

### Dynamic context with shell commands

```markdown
---
name: pr-summary
description: Summarize the current PR
context: fork
---
## Current PR
!`gh pr view --json title,body,files`

Summarize the changes above.
```

The `!` backtick syntax runs the shell command and injects its output before sending to Claude.


## Context Management

### The context window

- Default: 200K tokens (~50 complete exchanges before saturation)
- 1M tokens available on Max, Team, and Enterprise plans (as of March 2026, no pricing premium)
- A 500-line TypeScript file consumes ~4,000 tokens
- A detailed Claude response consumes 1,500 to 3,000 tokens
- System buffer reserved: ~33K tokens (down from 45K in earlier versions)

### Key commands

- `/context`: see current context usage and what's loaded
- `/cost`: see token costs for the session
- `/memory`: see all loaded CLAUDE.md and rules files, toggle auto memory
- `/clear`: reset context completely, start fresh
- `/compact`: summarize current session to free context (lossy, slow)
- `/effort`: set thinking effort level (low/medium/high)

### When to /clear vs /compact

**Prefer /clear in most cases.** Use it when:
- Switching to a different task
- Finishing a task and starting fresh
- Context is cluttered with exploration you no longer need

**Use /compact only when:**
- You genuinely need prior context from this session
- You're hitting the ~83% threshold and can't start fresh
- Note: compaction is slow (can take over a minute) and lossy

### Session handoff pattern

Before `/clear`, create a handoff file:

```markdown
<!-- .claude/session-handoff.md -->
## Session State, March 19 2026

### Decisions made
- Architecture: JWT with refresh tokens
- Database: PostgreSQL 16 with Drizzle ORM

### Modified files
- src/auth/login.ts (validation added)
- src/middleware/jwt.ts (new file)

### Next steps
- Write tests for login.ts
- Implement the /refresh endpoint
```

Reference it in the next session with `@.claude/session-handoff.md`.

### The docs/ folder as external memory

Instead of cramming everything into CLAUDE.md, store detailed knowledge in `docs/`:

```
docs/
├── architecture.md
├── api-patterns.md
├── deployment.md
└── decisions/
    └── 2026-03-auth-approach.md
```

Reference on demand with `@docs/architecture.md`. This replaces the "memory bank" concept from Cline. Simpler and more predictable.

### Task tracking with checkboxes

Instead of complex memory systems, use markdown checkboxes:

```markdown
<!-- docs/plan.md -->
## Feature: User Authentication
- [x] Set up JWT middleware
- [x] Implement login endpoint
- [ ] Write tests for login
- [ ] Implement refresh token endpoint
- [ ] Add rate limiting
```

Claude can check off boxes as it completes work. Reference with `@docs/plan.md`.


## Thinking and Effort Levels

### Extended thinking keywords (Claude Code only, not web/API)

- `think`: standard extended thinking
- `megathink`: deeper analysis
- `ultrathink`: maximum thinking budget (31,999 tokens). Reintroduced in v2.1.68.

As of v2.0.0, only `ultrathink` triggers extended thinking. Previous keywords like "think hard" have been disabled.

### When to use ultrathink

- Complex architectural decisions
- Performance optimization analysis
- Debugging difficult issues in unfamiliar code
- System design planning

Don't use it for routine edits, renames, or simple tasks. It wastes time and tokens.

### /effort command (v2.1.76)

Set persistent effort level: low, medium, high. Opus 4.6 defaults to medium for Max and Team subscribers. Use ultrathink for one-off high effort on specific prompts.

### Plan Mode (Shift+Tab twice)

Separates thinking from execution. Claude analyzes and proposes strategy without making changes. Use it for:
- Complex refactoring (3+ files)
- Exploring unfamiliar codebases
- Validating approach before executing
- Saves ~40% tokens compared to direct exploratory approach


## Decision Framework: What Goes Where

```
Need it enforced 100%?
├── YES → Use a Hook (deterministic, can't be skipped)
└── NO → Is it an invariant/standard?
    ├── YES → Use a Rule (.claude/rules/)
    └── NO → Is it domain expertise?
        ├── YES → Use a Skill (auto-invoked, progressive disclosure)
        └── NO → Is it a workflow you trigger manually?
            ├── YES → Use a Command/Skill with disable-model-invocation
            └── NO → Does it need isolated context?
                ├── YES → Use a Subagent
                └── NO → Just prompt directly
```

### Common mistakes

- **Bloated CLAUDE.md**: instructions Claude already follows, generic advice, full architecture docs. Keep it lean.
- **Rules without globs**: same as putting it in CLAUDE.md, no token savings. Add globs to scope them.
- **Skills that should be rules**: if it's a constraint, not expertise, use a rule.
- **Commands that should be skills**: if you keep forgetting to invoke `/fastapi` when touching API code, convert it to an auto-invoked skill.
- **Everything in one context**: use subagents for exploration and research to keep main context clean.
- **Over-engineering upfront**: start with a lean CLAUDE.md and 2 to 3 rules. Add skills and subagents only when you identify repeated friction.


## Plugins

Run `/plugin` to browse the marketplace. Plugins bundle skills, hooks, subagents, and MCP servers into a single installable unit. If you work with a typed language, install a code intelligence plugin for precise symbol navigation.


## Quick Start Checklist

1. Create `~/.claude/CLAUDE.md` with personal preferences (20 to 50 lines)
2. Create 2 to 3 global rules in `~/.claude/rules/` for universal standards
3. For each project, create a lean `<root>/CLAUDE.md` (50 to 80 lines)
4. Add glob-scoped rules in `<root>/.claude/rules/` for domain-specific conventions
5. Set up a `docs/` folder for detailed knowledge, reference with `@docs/filename.md`
6. Periodically prune auto memory via `/memory`
7. Use `/clear` between tasks, not `/compact`
8. Use Plan Mode for complex work, ultrathink for hard problems
9. Add skills and subagents as you identify repeated friction points
10. Use hooks for anything that must be enforced 100%
