---
name: audit
description: >
  Performs a comprehensive health check of an Obsidian wiki — checking
  index integrity, broken links, consistency, and coverage gaps. This
  skill should be used when the user asks to "audit my vault", "check
  wiki consistency", "find broken links", "review knowledge base",
  "check for missing articles", or "validate wiki indexes". Read-only
  on wiki files; writes only the audit report to output/.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
---

# Audit

Perform a read-only review of the entire wiki and produce a comprehensive audit report. No wiki files are modified — the only file written is the output report.

## Vault Discovery

Before any operation, resolve the vault path:

1. Check env var `OBSIDIAN_VAULT_PATH`
2. Check if `wiki/_master-index.md` exists in the current working directory
3. If neither, ask the user with `AskUserQuestion`

See [vault-conventions.md](references/vault-conventions.md) for full vault structure and conventions.

## Audit Checks

### 1. Index Integrity

Verify `wiki/_master-index.md` and each topic's `_index.md` are in sync with actual files:

- **Missing from index**: Articles that exist on disk but are not listed in their topic's `_index.md`
- **Missing from master index**: Topic folders that exist but are not listed in `_master-index.md`
- **Ghost entries**: Index entries pointing to articles or topics that don't exist on disk
- **Alphabetical order**: Flag indexes that aren't sorted alphabetically

### 2. Broken Wiki Links

Scan all articles for `[[wiki links]]` and verify each target exists:

- Parse all `[[...]]` patterns from every `.md` file in `wiki/`
- Resolve each link to a file path (e.g., `[[topic/article]]` → `wiki/topic/article.md`)
- Report links whose targets don't exist
- Group broken links by source file for actionable output

### 3. Missing Cross-Links

Identify related articles that should link to each other but don't:

- Find articles that mention concepts covered by other articles without linking
- Use Grep to search for article title keywords across the wiki
- Report pairs of articles that likely should be cross-linked

### 4. Consistency and Contradictions

Read articles within the same topic and across related topics to find:

- Contradictory claims **within the same project** (e.g., different dates, numbers, or definitions for the same concept in articles sharing the same `project` value)
- Inconsistent terminology within the same project (same concept referred to by different names)
- Duplicate coverage within the same project (multiple articles covering the same ground)

**Cross-project differences are expected, not errors.** Different projects may legitimately have different conventions, architectures, or definitions. Report these separately as informational "Cross-Project Divergences" rather than issues

### 5. Article Quality

Check each article against the required format:

- Missing **Key Takeaways** section
- Missing **Related** section
- Using paragraphs where bullet points are expected
- Missing one-line summary (blockquote after title)
- Empty or stub articles (fewer than 5 content lines)

### 6. Coverage Gaps

Identify areas where the knowledge base is thin:

- Concepts mentioned in articles but lacking their own dedicated article
- Topics with only one article (potentially underdeveloped areas)
- Suggest 3-5 new articles that would strengthen the knowledge base based on patterns in existing content

### 7. Unprocessed Raw Files

Check `raw/` for files that haven't been compiled:

- Files without `processed: true` in frontmatter
- Files with no frontmatter at all
- Report count and filenames

## Output Report

Write the report to `output/audit-YYYY-MM-DD.md` using today's date.

### Report Format

```markdown
# Wiki Audit Report — YYYY-MM-DD

> Automated audit of the knowledge base.

## Summary

- **Topics**: X total
- **Articles**: Y total
- **Projects**: N distinct projects
- **Issues found**: Z
- **Unprocessed raw files**: N

## Index Integrity

### Missing from Indexes
- [list]

### Ghost Entries
- [list]

## Broken Wiki Links

| Source Article | Broken Link |
|---|---|
| path/to/article.md | [[missing-target]] |

## Missing Cross-Links

| Article A | Article B | Reason |
|---|---|---|
| path/a.md | path/b.md | A mentions concept covered in B |

## Consistency Issues (within same project)

- [list of contradictions or inconsistencies between articles sharing the same project value]

## Cross-Project Divergences (informational)

| Concept | Project A | Project B | Difference |
|---|---|---|---|
| order confirmation | backend: uses sync flow | driver: uses async events | Different architectural approaches |

## Article Quality Issues

| Article | Issue |
|---|---|
| path/to/article.md | Missing Key Takeaways section |

## Coverage Gaps

### Concepts Needing Articles
- [concept] — mentioned in [[source-article]]

### Suggested New Articles
1. **article-name** in topic/ — rationale
2. ...

## Unprocessed Raw Files

- raw/file1.md
- raw/file2.txt
```

## Execution Strategy

To audit efficiently:

1. **Build a file inventory** — Glob for all `.md` files in `wiki/` and `raw/`
2. **Parse indexes first** — Read `_master-index.md` and all `_index.md` files to build the expected structure
3. **Scan articles in batches** — Read articles by topic folder, checking format and extracting links
4. **Cross-reference** — Compare extracted links against the file inventory
5. **Write report** — Compile all findings into the output report
