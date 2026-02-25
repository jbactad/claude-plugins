---
name: project-init
description: This skill should be used when the user asks to "initialize Automaker for a project", "set up .automaker directory", "bootstrap Automaker", "configure a new Automaker project", "create .automaker structure", or wants to prepare any codebase for use with Automaker. Also use when discussing .automaker/ directory layout, project settings, .gitignore for Automaker, or first-time Automaker setup.
---

# Automaker Project Initializer

Bootstrap the `.automaker/` directory structure and essential configuration files so any codebase is ready for AI-driven feature development with Automaker.

## How Project Initialization Works

Automaker stores all project-specific data under `{projectRoot}/.automaker/`. When a project is opened in Automaker for the first time, the UI runs `initializeProject()` which creates the minimum required directories (`.automaker/`, `.automaker/context/`, `.automaker/features/`, `.automaker/images/`) and a `categories.json` file. However, many optional but valuable files are not created automatically — the user must set them up manually for optimal AI agent performance.

This skill bridges that gap by creating a fully optimized `.automaker/` setup from the start.

## Initialization Workflow

### 1. Analyze the Project

Before creating any files, detect the project's characteristics:

- **Git status** — Verify `.git/` exists; if not, `git init` is needed first
- **Tech stack** — Read `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, `Gemfile`, `build.gradle`
- **Package manager** — Detect via lockfiles: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `bun.lockb`
- **Environment files** — Check for `.env`, `.env.local`, `.env.development`
- **Database** — Look for `prisma/`, `drizzle/`, `alembic/`, `db/migrate/`
- **Existing `.automaker/`** — If already present, offer to augment rather than overwrite
- **Monorepo** — Check for `workspaces` in `package.json`, `turbo.json`, `nx.json`, `lerna.json`

### 2. Create the Directory Structure

Create the complete `.automaker/` directory tree:

```
.automaker/
├── context/               # AI agent context files
│   ├── CLAUDE.md          # Primary project instructions
│   └── context-metadata.json  # File descriptions
├── features/              # Feature JSON files (Kanban board data)
├── images/                # Project-level images
├── memory/                # Agent learning files
├── categories.json        # Board column categories
├── settings.json          # Project-specific settings
└── worktree-init.sh       # Worktree bootstrap script (optional)
```

### 3. Create Essential Files

#### categories.json

Define board columns. Default categories:

```json
["backlog", "in_progress", "done"]
```

Custom categories map to the Kanban board columns in the UI. Features are organized into these categories.

#### settings.json

Create with project-appropriate defaults:

```json
{
  "version": 2,
  "useWorktrees": true,
  "autoLoadClaudeMd": true
}
```

Key project settings to consider:

| Setting | Type | Purpose |
|---------|------|---------|
| `useWorktrees` | `boolean` | Isolate feature branches in git worktrees (recommended: `true`) |
| `autoLoadClaudeMd` | `boolean` | Auto-load CLAUDE.md via Claude Agent SDK |
| `testCommand` | `string` | Custom test command (e.g., `"npm test"`, `"pytest"`) |
| `devCommand` | `string` | Custom dev server command (e.g., `"npm run dev"`) |
| `maxConcurrentAgents` | `number` | Limit parallel agents in auto-mode |
| `defaultFeatureModel` | `object` | Default model for new features (e.g., `{ "model": "claude-opus" }`) |

#### context/CLAUDE.md

Generate using the **automaker-context-optimizer** skill workflow — analyze the project and write tech stack, directory structure, commands, conventions, and critical rules.

#### context/context-metadata.json

```json
{
  "files": {
    "CLAUDE.md": {
      "description": "Primary project instructions including tech stack, directory structure, commands, conventions, and critical rules"
    }
  }
}
```

#### worktree-init.sh (if applicable)

Generate using the **automaker-worktree-init** skill workflow — detect package manager, env files, build steps, and create an optimized bootstrap script.

### 4. Configure .gitignore

Add Automaker-specific entries to `.gitignore`:

```gitignore
# Automaker
.automaker/worktrees/
.automaker/execution-state.json
.automaker/active-branches.json
.automaker/notifications.json
.automaker/events/
.automaker/ideation/
.automaker/board/
.automaker/images/
.automaker/analysis.json
```

Files to **keep tracked** in git (commit these):
- `.automaker/context/` — AI context is shared across team
- `.automaker/features/` — Feature definitions are project data
- `.automaker/categories.json` — Board structure
- `.automaker/settings.json` — Project config
- `.automaker/worktree-init.sh` — Bootstrap script
- `.automaker/spec.md` — Project specification
- `.automaker/app_spec.txt` — Structured specification

### 5. Initialize Memory (Optional)

Create `.automaker/memory/_index.md` with project overview:

```markdown
---
tags: ["project-overview", "architecture"]
relevantTo: ["all", "onboarding"]
summary: "Project overview and key architectural decisions"
importance: 0.9
relatedFiles: []
usageStats:
  loaded: 0
  referenced: 0
  successfulFeatures: 0
---

# Project Overview

[Brief project description and key decisions]
```

Note: `_index.md` is excluded from agent memory loading — it serves as human-readable documentation only. Use `gotchas.md` with `importance: 0.9` for critical warnings that must always reach agents.

### 6. Verify Initialization

After creating all files, verify:
- All required directories exist
- `categories.json` is valid JSON array
- `settings.json` has `version` field
- `context/CLAUDE.md` is non-empty and specific to the project
- `context/context-metadata.json` references all context files
- `.gitignore` includes Automaker entries
- `worktree-init.sh` is executable (`chmod +x`) if created

## Quick Reference: Minimum vs Full Setup

| Component | Minimum | Full |
|-----------|---------|------|
| `.automaker/` directory | Required | Required |
| `features/` | Required | Required |
| `context/` | Required | Required |
| `categories.json` | Required | Required |
| `context/CLAUDE.md` | Highly recommended | Required |
| `settings.json` | Optional | Recommended |
| `worktree-init.sh` | Optional | Recommended |
| `memory/` | Optional | Recommended |
| `spec.md` | Optional | For spec-driven workflows |
| `.gitignore` entries | Recommended | Required |

## Additional Resources

### Reference Files

- **`references/directory-structure.md`** — Complete `.automaker/` directory tree with every file and subdirectory documented, including runtime-generated files
- **`references/settings-schema.md`** — Full `ProjectSettings` interface documentation with all fields, types, defaults, and usage examples
