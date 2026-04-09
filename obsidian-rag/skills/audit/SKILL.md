---
name: audit
description: >
  Performs a comprehensive health check of an Obsidian wiki — checking
  broken links, orphan pages, uncompiled sources, stale articles, missing
  backlinks, sparse articles, and cross-article contradictions. This skill
  should be used when the user asks to "audit my vault", "check wiki health",
  "find broken links", "review knowledge base", "lint my wiki", or "validate
  wiki indexes". Backed by lint.py. Read-only on wiki files; writes report
  to output/.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
---

# Audit

Perform a comprehensive health check of the wiki and produce an audit report. Backed by `${CLAUDE_SKILL_DIR}/scripts/lint.py` — run directly for automation or CI use.

```bash
uv run python ${CLAUDE_SKILL_DIR}/scripts/lint.py                     # all checks
uv run python ${CLAUDE_SKILL_DIR}/scripts/lint.py --structural-only   # skip LLM contradiction check
uv run python ${CLAUDE_SKILL_DIR}/scripts/lint.py --project backend   # scope contradictions to one project
```

## Vault Discovery

Before any operation, resolve the vault path:

1. Check env var `OBSIDIAN_VAULT_PATH`
2. Check if `wiki/master-index.md` exists in the current working directory
3. If neither, ask the user with `AskUserQuestion`

See [vault-conventions.md](references/vault-conventions.md) for full vault structure and conventions.

## Checks

Run all 7 checks. Each issue is tagged with severity: `error`, `warning`, or `suggestion`.

### 1. Broken Links (error)

Scan all articles in `wiki/` for `[[wikilinks]]` and verify each target exists:
- Parse all `[[...]]` patterns from every `.md` file in `wiki/`
- Resolve to file path (e.g., `[[topic/article]]` → `wiki/topic/article.md`)
- Skip links prefixed with `daily/` or `raw/` (these are cross-references, not articles)
- Report links whose targets don't exist on disk

### 2. Orphan Pages (warning)

Articles with zero inbound links:
- For each article, count how many other articles link to it via `[[wikilink]]`
- Report articles with 0 inbound links
- Skip `master-index.md`, `index.md`, and `log.md` files

### 3. Orphan Sources (warning)

Source files that haven't been compiled yet:
- Check `raw/**/*.md` and `daily/YYYY-MM-DD.md` files against `output/state.json`
- Report files not recorded in `state["ingested"]`
- Suggest: `run /compile` for raw files, `run /compile --source daily` for daily logs

### 4. Stale Articles (warning)

Source files that changed since last compilation:
- Compare SHA-256 hash of each raw/ and daily/ file against the stored hash in `output/state.json`
- Report files where current hash ≠ stored hash
- Suggest recompile

### 5. Missing Backlinks (suggestion, auto-fixable)

One-directional links that should be bidirectional:
- If article A links to article B, check whether B links back to A
- Report pairs where the return link is missing
- Tag as `auto_fixable: true`

### 6. Sparse Articles (suggestion)

Articles under 200 words:
- Count words in each article (excluding frontmatter and headings)
- Report articles below the threshold

### 7. Contradictions (warning, LLM check)

Conflicting claims across articles in the same project:
- Uses Claude Agent SDK to read all wiki content and identify contradictions
- Only flags contradictions **within the same project** (same `project` frontmatter value)
- Cross-project differences are expected — report them separately as "Cross-Project Divergences"
- Skip with `--structural-only` flag to avoid LLM cost
- Scope to one project with `--project <name>`

## Output Report

Write report to `output/audit-YYYY-MM-DD.md`. Format:

```markdown
# Audit Report — YYYY-MM-DD

**Total issues:** N
- Errors: X
- Warnings: Y
- Suggestions: Z

## Errors

- **[x]** `topic/article.md` — Broken link [[missing-target]] — target does not exist

## Warnings

- **[!]** `topic/article.md` — Orphan page — no other articles link to [[topic/article]]
- **[!]** `raw/source.md` — Uncompiled raw file — run /compile to process
- **[!]** `raw/source.md` — Source changed since last compilation — recompile to update
- **[!]** (cross-article) — CONTRADICTION: [file1] vs [file2] - description

## Suggestions

- **[?]** `topic/article.md` — [[topic/article]] links to [[other]] but not vice versa (auto-fixable)
- **[?]** `topic/sparse.md` — Sparse article — 87 words (min recommended: 200)
```

After writing the report, print the path and a brief summary of counts.
