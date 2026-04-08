# Extraction Guide

This guide helps classify content from CLAUDE.md into the correct tier of the 4-tier architecture.

## The 4-Tier Architecture

1. **Tier 1: CLAUDE.md** — Always-active compact rules + mandatory operational rules. Loaded into every context including sub-agents.
2. **Tier 1.5: Rules files** — Hard constraints (MUST/NEVER/ALWAYS) in `.claude/rules/`. Auto-loaded every session by Claude Code. Optionally scoped to file patterns via `paths` frontmatter.
3. **Tier 2: Knowledge Skills** — Detailed patterns with code examples packaged as skills with `user-invocable: false`. Claude auto-triggers based on description relevance. Optionally scoped via `paths` frontmatter.
4. **Tier 3: Workflow Skills** — Interactive step-by-step procedures invoked on demand via slash commands.

## Classification Decision Tree

Ask these questions about each piece of content:

```
Is this generic advice Claude follows without being told (e.g., "write clean code")?
  YES → DELETE — do not redistribute into any tier
  NO  → Is this a step-by-step procedure or workflow?
          YES → Tier 3 (Workflow Skill)
          NO  → Is this a rule that, if ignored, would produce incorrect code?
                  YES → Must this be enforced 100% of the time (security, file safety, blocking)?
                          YES → Hook (PreToolUse to block, Stop to validate, SessionStart to set context)
                          NO  → Is it a binary constraint (MUST/NEVER/ALWAYS)?
                                  YES → Compact version → Tier 1 (CLAUDE.md Code Standards)
                                        Full version → Tier 1.5 (rules/)
                                  NO  → Is it a pattern with code examples?
                                          YES → Compact version → Tier 1, detailed → Tier 2 (Knowledge Skill, user-invocable: false)
                                          NO  → Tier 1 (CLAUDE.md Code Standards)
                  NO  → Is this a pattern with examples or detailed explanation?
                          YES → Tier 2 (Knowledge Skill, user-invocable: false)
                          NO  → Is this an operational/safety rule (tool usage, file protection)?
                                  YES → Must it be enforced 100%?
                                          YES → Hook
                                          NO  → Tier 1 (CLAUDE.md Mandatory Rules section)
                                  NO  → Keep in CLAUDE.md as structural info
```

## Tier 1: Keep in CLAUDE.md

### Structural Content (always keep)

- Project name and one-line description
- Technology list (not usage patterns)
- Directory tree with brief file descriptions
- Commands to run/build/test
- MCP server installation commands
- Rules listing (auto-loaded, no "when to read" needed)
- Skills matrix (workflow skills only; knowledge skills don't need listing — Claude finds them automatically)
- Agents table (if using sub-agents)
- Delegation routing (if using orchestrator pattern)
- Document reference table

### Mandatory Rules (operational/safety rules)

These go in a dedicated **MANDATORY RULES** section in CLAUDE.md, distinct from Code Standards:

- **Tool usage restrictions**: "NEVER add description parameter to Bash tool calls"
- **File safety rules**: "NEVER delete/modify .env files"
- **Blocking policies**: "If ANY tool call is denied, STOP and report"
- **Sub-agent constraints**: "ONLY run unit tests. NEVER run integration tests"
- **Error handling**: "If unexpected errors, STOP and report. Do NOT retry destructive operations"

**Key characteristics**:
- Apply to the orchestrator AND all agents (not just coding rules)
- Use ALL-CAPS headers and severity language ("Violation = immediate stop")
- Separate from Code Standards (which are coding conventions)
- Compact — each rule fits on one line

### Promoted Rules (extract from rules/examples, compact to one-liners)

**Promote when**: a sub-agent ignoring this rule would produce incorrect code.

Look for these patterns and condense them:

#### Naming conventions
```
Before (in rules/examples file, 10 lines with examples):
  "Entities should be named with the Entity suffix..."
  [examples, explanations]

After (in CLAUDE.md, 1 line):
  **Naming**: Entity → `{Name}Entity`, Service → `{Domain}Service`, Repository → `{Entity}Repository`
```

#### Forbidden patterns
```
Before (in rules/examples file, 15 lines):
  "Never mock entities directly because..."
  [explanation, examples of what to do instead]

After (in CLAUDE.md, 1 line):
  - Never mock entities, use FakerTrait: `$this->fake()->entity()`
```

#### Mandatory patterns
```
Before (in rules/examples file, 5 lines):
  "All PHP files must declare strict types..."
  [example, explanation]

After (in CLAUDE.md, 1 line):
  - `declare(strict_types=1)` in every PHP file
```

**Rule of thumb**: If you can't condense it to one line, keep the full version in rules/examples files and put only the condensed version in CLAUDE.md.

## Tier 1.5: Move to Rules Files

### What Goes in Rules Files

Rules files store *hard constraints*: binary rules that produce incorrect or dangerous results if violated. They are auto-loaded by Claude Code every session — no explicit reading needed.

Place in `.claude/rules/` when you see:

- "Always X" / "Never Y" / "Must Z" patterns
- Binary constraints with no nuance
- Forbidden patterns (things that must never appear in code)
- Required patterns (things that must always appear)
- Dependency rules (module A must never import from module B)
- Import ordering requirements

### Rules vs Knowledge Skills: The Split

| Characteristic | Rules (`rules/`) | Knowledge Skills (`user-invocable: false`) |
|---|---|---|
| Content type | Binary constraints | Patterns with code examples |
| Format | One-liner per rule | Good/Bad code comparisons |
| Loading | Auto-loaded every session | Auto-triggered by Claude when relevant |
| Purpose | What NOT to do / What MUST be done | How to do it correctly |
| Code examples | None (or minimal) | Detailed, with explanations |
| Path scoping | Optional (`paths` frontmatter) | Optional (`paths` frontmatter) |

**Example split for testing**:

Rules file (`rules/testing.md`):
```markdown
- NEVER mock entities — use FakerTrait
- NEVER use `markTestSkipped()`
- Test naming: `test_{method}_{scenario}_{expected}()`
- Mock properties MUST have `MockObject|Type` union types
```

Knowledge skill (`skills/testing-patterns/SKILL.md`):
```yaml
---
name: testing-patterns
description: Mock patterns, FakerTrait API, fixture workflow, and Good/Bad examples for tests.
user-invocable: false
paths:
  - "tests/**/*"
  - "**/*Test.php"
---
```
```markdown
## Mock Patterns

### Rule
Define mocks as class properties, configure in setUp()

### Example
```php
// Good
private MockObject|OrderRepository $orderRepository;

protected function setUp(): void
{
    $this->orderRepository = $this->createMock(OrderRepository::class);
}

// Bad — local variable mock
public function testSomething(): void
{
    $repo = $this->createMock(OrderRepository::class); // NO!
}
```
```

### Rules File Structure

```markdown
# [Area] Rules

## [Category]

- [Binary constraint as one-liner]
- [Binary constraint as one-liner]

## [Category]

- [Binary constraint as one-liner]

## Reference

For detailed patterns and examples: `.claude/examples/{topic}.md`
```

### Rules File Naming

- `code.md` or `php-code.md` — Language/framework constraints
- `testing.md` — Testing constraints
- `database.md` — Database access constraints
- `security.md` — Security constraints

### Cross-References

Every rules file SHOULD end with a `## Reference` section pointing to its corresponding knowledge skill. This creates a two-way link: rules say what, knowledge skills show how.

## Tier 2: Create Knowledge Skills

### What Goes in Knowledge Skills

Knowledge skills store *patterns with code*: detailed conventions showing how to implement things correctly, with Good/Bad comparisons. They are packaged as skills with `user-invocable: false` — Claude auto-triggers them based on description relevance.

Create knowledge skills when you see:

#### Code Patterns → skill `[project]-code-patterns`

- "Use X pattern for Y" with code examples
- Naming conventions with multiple examples
- File organization rules with directory examples
- Import/export patterns with code
- Class/function structure requirements with templates
- Error handling patterns with code examples

#### Testing Patterns → skill `[project]-testing-patterns`

- Testing pyramid ratios with examples
- What to test at each level with code
- Test organization patterns
- Mocking strategies with code examples
- Coverage requirements
- Helper trait/utility documentation (FakerTrait API, etc.)

#### Database Patterns → skill `[project]-database-patterns`

- Connection setup details
- Query patterns with code examples
- Transaction handling patterns
- Repository patterns with code
- Performance guidelines (indexes, eager loading)

#### API Design → skill `[project]-api-patterns`

- Endpoint patterns with code examples
- HTTP status codes to use
- Error handling conventions with code
- Request/response formats with examples
- Authentication patterns

#### Frontend Patterns → skill `[project]-frontend-patterns`

- Component organization with code examples
- State management patterns
- Styling conventions
- Form handling patterns
- API call patterns

#### Anti-Patterns → skill `[project]-anti-patterns`

- Common mistakes with explanations
- What NOT to do with code examples
- Past bugs and their root causes

### Knowledge Skill Structure

Each knowledge skill lives in `.claude/skills/[name]/SKILL.md`:

```yaml
---
name: [project]-testing-patterns
description: Detailed testing patterns, mock strategies, FakerTrait API, and Good/Bad examples. Loaded when writing or reviewing tests.
user-invocable: false
paths:
  - "tests/**/*"
  - "**/*Test.php"
---
```

Body structure:

```markdown
# [Area] Patterns

## [Pattern Category]

### Rule
[Clear statement of the rule]

### Why
[Brief explanation — important for buy-in]

### Example
```[lang]
// Good
[correct code]

// Bad — [why it's bad]
[incorrect code]
```

## References
- [Link to helper files, API references, etc.]
```

### Knowledge Skill Naming

Use project-prefixed kebab-case names:
- `[project]-code-patterns` — General code patterns (language/framework)
- `[project]-testing-patterns` — Testing strategies and patterns
- `[project]-database-patterns` — Database access and query patterns
- `[project]-api-patterns` — API design patterns
- `[project]-frontend-patterns` — Frontend component patterns
- `[project]-anti-patterns` — Common mistakes to avoid

### Grouping Rules

- Group related patterns together (don't create micro-skills)
- Create separate skills when content exceeds 200 lines or concerns a distinct area
- A project typically needs 3-5 knowledge skills
- Use `paths` to scope skills to relevant directories when possible — reduces noise
- Include reference material (API docs, helper references) within the skill body or its references/ directory

## Tier 3: Create Workflow Skills

### What Goes in Workflow Skills

Workflow skills store *procedures*: step-by-step workflows that guide Claude through a multi-step process. They are interactive tools, not reference material. Unlike knowledge skills, these are user-invoked (default behavior).

Create skills when you see:

#### Feature Development → `skills/[project]-feature-dev/`

- Step-by-step process for creating a new feature
- File creation order and checklist
- Testing requirements for the feature
- PR/review process

#### Code Review → `skills/[project]-code-review/`

- Checklist of things to verify
- Common issues to look for
- Conventions to check against
- Review comment templates

#### Bug Fix → `skills/[project]-bugfix/`

- Investigation procedure
- Debugging steps
- Fix verification process
- Regression test requirements

#### Deployment → `skills/[project]-deployment/`

- Pre-deployment checks
- Deployment steps
- Post-deployment verification
- Rollback procedure

### Distinguishing Rules, Knowledge Skills, and Workflow Skills

| Content Type | Rules File | Knowledge Skill | Workflow Skill |
|---|---|---|---|
| "Never mock entities" | Yes | No | No |
| "Here's how to use FakerTrait [code]" | No | Yes | No |
| "Step 1: Create entity, Step 2: Create repo..." | No | No | Yes |
| "Test naming: test_{method}_{scenario}" | Yes | No | No |
| "Mock pattern with Good/Bad code examples" | No | Yes | No |
| "When fixing a bug: 1. Reproduce, 2. Write test..." | No | No | Yes |

**Simple test**:
- Binary constraint → rules file
- Pattern with code examples → knowledge skill (`user-invocable: false`)
- Multi-step procedure → workflow skill

## Agent Definitions

### When to Create Agents

Create `.claude/agents/` definitions when the project:
- Uses an orchestrator pattern (main conversation delegates work)
- Has multiple distinct task types (code writing, review, testing, research)
- Needs specialized tools/permissions per task type
- Benefits from read-only advisors (analysis without code modification)

### Agent Content Classification

| Content | Goes In |
|---|---|
| Agent name, description, model, tools | Agent frontmatter |
| Safety rules the agent must follow | Embedded in agent body (duplicated from rules) |
| Step-by-step process for the agent | Agent body |
| What the agent can/cannot do | Agent body (Scope + Constraints sections) |
| Output format expectations | Agent body |

### Agent Frontmatter Template

```markdown
---
name: agent-name
description: >
  One-line purpose of the agent. Use YAML folded block scalar (>)
  when description contains <example> tags.

  <example>
  Context: When this agent should be used
  user: "Example trigger phrase"
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

**CRITICAL**: Always use `description: >` (YAML folded block scalar) for descriptions containing `<example>` tags. Bare YAML values with angle brackets break frontmatter parsing.

### Agent Types

**Code-writing agents** (full tool access):
- Need embedded guardrails (safety rules duplicated in the agent prompt)
- Include: "Before writing ANY code, read these files: [list]"
- Tools: Read, Write, Edit, Glob, Grep, Bash

**Read-only advisors** (restricted tools):
- Analyze and recommend, but never modify code
- Fewer guardrails needed since they can't cause damage
- Tools: Read, Grep, Glob, Bash

### Guardrail Embedding

Every code-writing agent must have safety rules duplicated directly in its prompt:

```markdown
## Mandatory Rules

- NEVER delete, overwrite, or modify `.env` files
- ONLY run unit tests via `paratest`. NEVER run integration tests
- If ANY tool call is denied, STOP and report
```

Do NOT rely on agents reading external rule files for critical safety constraints. The agent prompt is the only guaranteed context.

## Mandatory Rules Section

### What Goes in Mandatory Rules

Operational/safety rules that belong in CLAUDE.md's **MANDATORY RULES** section:

- **Tool usage restrictions**: How agents should use tools (e.g., no description on Bash, relative paths only)
- **File safety rules**: What files to never touch (e.g., .env, dotfiles)
- **Blocking policies**: What to do when tool calls are denied or errors occur
- **Sub-agent constraints**: What sub-agents can/cannot do (e.g., only unit tests)
- **Completion criteria**: When a task is considered "done" (tests green, committed, no diagnostics)

### Mandatory Rules vs Code Standards

| Mandatory Rules | Code Standards |
|---|---|
| How agents should *behave* | How code should *look* |
| Tool usage, file safety, blocking | Naming, imports, patterns |
| Operational constraints | Coding conventions |
| ALL-CAPS headers, severity language | Compact one-liners |
| Apply to orchestrator + all agents | Apply to code-writing agents |

### Mandatory Rules Format

```markdown
## MANDATORY RULES (ALL AGENTS MUST FOLLOW)

**These rules are NON-NEGOTIABLE. Violation = immediate stop.**

### Tool Usage
- NEVER add `description` parameter to Bash tool calls
- ALWAYS use relative paths in Bash commands

### File Safety
- NEVER delete, overwrite, or modify `.env` files
- NEVER delete files unless the plan explicitly names them AND user confirms

### Sub-Agent Blocking Policy
- ONLY run unit tests. NEVER run integration tests
- If ANY tool call is denied, STOP and report
```

## Common Mistakes

### Mistake 1: Putting conventions in workflow skills
**Problem**: Workflow skills are user-invoked. If naming conventions are in a workflow skill, sub-agents won't follow them unless someone invokes the skill.
**Fix**: Move hard constraints to rules files. Move patterns with examples to knowledge skills (`user-invocable: false`). Promote critical rules to CLAUDE.md.

### Mistake 2: Not promoting critical rules to CLAUDE.md
**Problem**: Even rules files auto-load, but examples files don't. And rules files may be too terse for sub-agents to fully understand.
**Fix**: Promote the most critical rules as compact one-liners in CLAUDE.md's "Code Standards" section.

### Mistake 3: Verbose rules in CLAUDE.md
**Problem**: Multi-line explanations and code examples in CLAUDE.md waste tokens on every request.
**Fix**: Keep CLAUDE.md rules to one line each. Put detailed explanations in examples files. Put binary constraints in rules files.

### Mistake 4: Not splitting rules from patterns
**Problem**: Putting binary constraints and detailed code examples in the same place. If in `rules/`, the code examples bloat every session. If only in a workflow skill, the constraints aren't enforced.
**Fix**: Split into `rules/{topic}.md` (binary constraints, auto-loaded) and a knowledge skill `user-invocable: false` (patterns with code, auto-triggered). Cross-reference between them.

### Mistake 5: Creating too many files
**Problem**: 10+ small files are harder to maintain and reference.
**Fix**: Group related patterns. Most projects need 3-5 rules files and 3-5 examples files.

### Mistake 6: Not embedding guardrails in agents
**Problem**: Agent definitions that say "read rules/testing.md before starting" — agents may skip this.
**Fix**: Duplicate critical safety rules directly in the agent prompt. Reference external files for non-critical patterns only.

### Mistake 7: Missing cross-references
**Problem**: Rules files exist but nothing points to them. Examples files exist but agents don't know to read them.
**Fix**: Rules files end with `## Reference` pointing to examples. Agent prompts include "Before writing ANY code, read: [list]". CLAUDE.md has a Reference Documentation section.

### Mistake 8: No Mandatory Rules section
**Problem**: Operational rules (tool usage, file safety) mixed in with coding conventions, or missing entirely.
**Fix**: Create a dedicated MANDATORY RULES section in CLAUDE.md with ALL-CAPS headers and severity language. These are distinct from Code Standards.

### Mistake 9: Putting critical safety rules only in CLAUDE.md or rules files
**Problem**: Rules like "never modify .env" or "never run rm -rf" placed only in CLAUDE.md or rules files are honored ~70% of the time. Subagents and edge cases can still violate them.
**Fix**: Implement critical safety and security rules as hooks (PreToolUse to block, Stop to validate). Keep the rule in CLAUDE.md for visibility, but the hook is the enforcement mechanism.

### Mistake 10: Keeping generic advice and rules Claude already follows
**Problem**: CLAUDE.md contains rules like "write clean code", "handle errors properly", or "test your changes" — advice Claude follows by default. These waste tokens without improving behavior.
**Fix**: Delete them. Only write rules that are (a) specific enough to verify and (b) Claude would not follow without being told. If you can't verify compliance by reading the code, the rule is too vague.
