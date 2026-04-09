---
name: setup
description: >
  Initializes a new Obsidian vault or upgrades an existing one to work
  with the obsidian-rag plugin. This skill should be used when the user
  asks to "set up my vault", "initialize obsidian-rag", "upgrade my vault",
  "update the setup", "set up the knowledge base", or is configuring the
  plugin for the first time.
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
2. Check if `wiki/index.md` exists in the current working directory
3. Otherwise ask the user with `AskUserQuestion`: "What is the path to the vault you want to set up?"

## Step 2: Detect Mode

Inspect the vault to determine what's missing:

- `raw/`, `wiki/`, `output/`, `daily/` — base directories
- `wiki/connections/`, `wiki/qa/` — article type directories
- `wiki/index.md` — merged topic navigator + article catalog (used by SessionStart hook)
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

**`wiki/index.md`** — if missing:
```markdown
# Knowledge Base Index

> Topics and articles in this vault.

## Topics

## Articles

| Article | Summary | Source | Updated |
|---------|---------|--------|---------|
```

**`wiki/log.md`** — if missing:
```markdown
# Build Log

> Append-only record of all compile, query, and audit operations.

```

**`CLAUDE.md`** — if missing, create with full vault structure and skills table (see [vault-conventions.md](references/vault-conventions.md) for canonical content). If it exists, read it and check for completeness against the expected content:

- Vault structure section lists all directories: `raw/`, `daily/`, `wiki/`, `output/`
- Wiki structure mentions: `wiki/index.md`, `wiki/log.md`, `wiki/connections/`, `wiki/qa/`
- Skills table includes all five skills: `compile`, `audit`, `query`, `capture`, `setup`

If anything is missing or outdated, ask the user: "Your CLAUDE.md is missing some sections added in the latest version. Update it?" — then apply only the missing additions without rewriting existing content.

**`.claude/rules/wiki-conventions.md`** — if missing, create with standard wiki constraints (article format, index sync rules, raw file protection). See [vault-conventions.md](references/vault-conventions.md) for the canonical rules content.

## Step 5: Configure qmd (Optional)

qmd provides hybrid search (BM25 + semantic + LLM reranking) that makes the query skill scale past ~500 articles. It's a separate plugin from `tobi/qmd`.

Check if qmd is installed:

```bash
qmd status 2>/dev/null && echo "installed" || echo "not installed"
```

**If installed**, register the vault's wiki as a collection and generate embeddings:

```bash
qmd collection add <vault_path>/wiki --name vault
qmd context add qmd://vault "Knowledge base wiki articles"
qmd embed
```

After each `/compile` run, keep the index current:

```bash
qmd update && qmd embed
```

**If not installed**, note it in the report as an optional next step.

## Step 6: Report

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
  · wiki/index.md
  · CLAUDE.md
  · output/

Next steps:
  1. Set OBSIDIAN_VAULT_PATH=/path/to/vault in your shell profile
  2. Drop source files in raw/ and run /compile
  3. The SessionStart hook injects the wiki index into every session automatically
  4. (Optional) Enable hybrid search at scale:
       /plugin marketplace add tobi/qmd
       /plugin install qmd@qmd
       qmd collection add wiki/ --name vault && qmd embed
```
