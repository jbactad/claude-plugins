---
name: setup
description: >
  Initializes a new Obsidian vault or upgrades an existing one to work
  with the obsidian-rag plugin. This skill should be used when the user
  asks to "set up my vault", "initialize obsidian-rag", "upgrade my vault",
  "set up the knowledge base", or is configuring the plugin for the first time.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash
  - AskUserQuestion
---

# Setup

Initialize a new Obsidian vault or upgrade an existing one to work with obsidian-rag. Safe to run on existing vaults — only creates what's missing, never overwrites.

## Step 1: Resolve Vault Path

1. Check env var `OBSIDIAN_VAULT_PATH`
2. Check if `wiki/` exists in the current working directory
3. Otherwise ask the user with `AskUserQuestion`: "What is the path to the vault you want to set up?"

## Step 2: Detect Mode

Inspect the vault to determine what's missing:

- `raw/`, `wiki/`, `output/`, `daily/` — base directories
- `wiki/connections/`, `wiki/qa/` — article type directories
- `wiki/_master-index.md` — topic list index
- `wiki/index.md` — article catalog table (used by SessionStart hook)
- `wiki/log.md` — build log
- `CLAUDE.md` — vault instructions
- `.claude/rules/wiki-conventions.md` — auto-loaded constraints

## Step 3: Create Missing Directories

Create any that don't exist (silently):

- `raw/`
- `wiki/`
- `wiki/connections/`
- `wiki/qa/`
- `daily/`
- `output/`
- `.claude/rules/`

## Step 4: Initialize Missing Files

See [vault-conventions.md](references/vault-conventions.md) for all file formats.

**`wiki/_master-index.md`** — if missing:
```markdown
# Knowledge Base Index

> Master index of all topics in the wiki.

## Topics

```

**`wiki/index.md`** — if missing:
```markdown
# Knowledge Base Article Catalog

> Table of all articles. Used by the SessionStart hook to inject context into sessions.

| Article | Summary | Source | Updated |
|---------|---------|--------|---------|
```

**`wiki/log.md`** — if missing:
```markdown
# Build Log

> Append-only record of all compile, query, and audit operations.

```

**`CLAUDE.md`** — if missing, create with vault structure and skills table. If it exists, check whether it mentions obsidian-rag skills — if not, ask the user if they want the skills table added.

**`.claude/rules/wiki-conventions.md`** — if missing, create with standard wiki constraints (article format, index sync rules, raw file protection). See [vault-conventions.md](references/vault-conventions.md) for the canonical rules content.

## Step 5: Report

Print a summary of what was created vs what already existed:

```
Vault setup complete: /path/to/vault

Created:
  ✓ daily/
  ✓ wiki/connections/
  ✓ wiki/qa/
  ✓ wiki/index.md
  ✓ wiki/log.md

Already existed (unchanged):
  · raw/
  · wiki/
  · wiki/_master-index.md
  · CLAUDE.md
  · output/

Next steps:
  1. Set OBSIDIAN_VAULT_PATH=/path/to/vault in your shell profile
  2. Drop source files in raw/ and run /compile
  3. The SessionStart hook injects the wiki index into every session automatically
```
