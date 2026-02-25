---
name: context-optimizer
description: This skill should be used when the user asks to "create context files", "optimize CLAUDE.md for Automaker", "set up .automaker/context", "improve AI agent context", "create context-metadata.json", or wants to optimize how AI agents understand their project in Automaker. Also use when discussing context file best practices or agent prompt customization for Automaker projects.
---

# Automaker Context Optimizer

Create and optimize `.automaker/context/` files so Automaker's AI agents have high-quality project knowledge injected into every prompt.

## How Context Loading Works

Automaker's `loadContextFiles()` reads all `.md` and `.txt` files from `.automaker/context/` and prepends them to every agent prompt — both interactive chat and auto-mode feature execution. Files are prefixed with: "You MUST follow the rules and conventions defined in these context files."

Descriptions from `context-metadata.json` are included alongside each file. When `autoLoadClaudeMd=true` in settings, the SDK also loads CLAUDE.md via `settingSources` — avoid duplicating content already in the project-root CLAUDE.md.

## Context Optimization Workflow

### 1. Analyze the Project

Before writing context files, gather:

- **Tech stack** — Read `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, etc.
- **Directory structure** — Identify src layout, module boundaries, shared packages
- **Existing patterns** — Scan for error handling, logging, API response shapes, naming conventions
- **Build/test commands** — Extract from `package.json` scripts, `Makefile`, CI configs
- **Critical constraints** — Ports in use, protected files, deployment targets

### 2. Create CLAUDE.md (Primary Context File)

Create `.automaker/context/CLAUDE.md` with these sections:

```markdown
# Project Context

## Overview
[One paragraph: what the project does, who it's for, current state]

## Tech Stack
[Exact frameworks, versions, key dependencies]

## Directory Structure
[Key directories and their purposes — not exhaustive, focus on what agents need]

## Commands
[Build, test, lint, dev server — exact commands]

## Coding Conventions
[Import patterns, naming, file organization, error handling]

## Critical Rules
[NEVER do X, ALWAYS do Y — use imperative language]
```

### 3. Create Supplementary Context Files

Split concerns into focused files when CLAUDE.md exceeds 2500 words:

| File | Purpose |
|------|---------|
| `CODE_QUALITY.md` | Linting rules, formatting, type strictness |
| `API_CONVENTIONS.md` | Route patterns, response shapes, error codes |
| `TESTING.md` | Test framework, fixture patterns, coverage rules |
| `SECURITY.md` | Auth patterns, input validation, secret handling |
| `ARCHITECTURE.md` | Module boundaries, dependency rules, data flow |

### 4. Create context-metadata.json

Create `.automaker/context/context-metadata.json`:

```json
{
  "files": {
    "CLAUDE.md": {
      "description": "Primary project instructions, tech stack, and coding conventions"
    },
    "CODE_QUALITY.md": {
      "description": "Code quality standards, linting rules, and formatting requirements"
    }
  }
}
```

Write descriptions that help agents understand each file's relevance before loading it.

### 5. Optimize Content

Apply these optimization techniques:

- **Be specific** — Include file paths (`src/lib/logger.ts`), not vague references
- **Use imperative language** — "Use `createLogger()` from `@pkg/utils`" not "You should use..."
- **Include anti-patterns** — "NEVER use `console.log` — use `createLogger()` instead"
- **Keep files under 3000 words** — Split large files into focused ones
- **Avoid duplication** — If `autoLoadClaudeMd=true`, do not repeat project-root CLAUDE.md content
- **Reference real code** — "Follow the pattern in `src/routes/auth.ts` for new endpoints"
- **Prioritize non-obvious information** — Agents can read code; tell them what code alone doesn't convey

## Quick Reference: Content Priorities

**High value (always include):**
- Import conventions and package boundaries
- Build/test/lint commands
- NEVER rules (ports, protected files, deprecated patterns)
- Error handling and logging patterns

**Medium value (include for complex projects):**
- API response shapes and error codes
- Database access patterns
- State management conventions
- Git workflow and PR conventions

**Low value (agents can discover from code):**
- Obvious type definitions
- Standard framework usage
- File-by-file descriptions

## Additional Resources

### Reference Files

- **`references/context-patterns.md`** — Detailed templates for React, Express, monorepo, Python, and other project types with complete CLAUDE.md examples
- **`references/metadata-format.md`** — Full `context-metadata.json` schema and description writing guide
