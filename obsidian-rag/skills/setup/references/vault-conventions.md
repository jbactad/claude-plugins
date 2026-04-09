# Vault Structure and Conventions

## Directory Layout

```
vault/
├── raw/          — inbox for source material (user drops files here)
├── daily/        — auto-captured conversation logs (YYYY-MM-DD.md)
├── wiki/         — LLM-maintained knowledge base
│   ├── _master-index.md   — entry point, lists all topics
│   ├── index.md           — article catalog table (used by SessionStart hook)
│   ├── log.md             — append-only build log
│   ├── connections/       — cross-cutting articles spanning multiple topics
│   ├── qa/                — question-answer articles (filed by /query --file-back)
│   └── <topic>/           — one subfolder per topic (kebab-case)
│       ├── _index.md      — lists all articles in this topic
│       └── <article>.md   — individual articles (kebab-case)
└── output/       — audit reports and query exports
```

## Vault Discovery

Every operation must resolve the vault path before proceeding. Check in order:

1. If env var `OBSIDIAN_VAULT_PATH` is set, use that path
2. If `wiki/_master-index.md` exists in the current working directory, the vault is `.`
3. Otherwise, ask the user for the vault path using `AskUserQuestion`

Once resolved, verify the vault has the expected subdirectories (`raw/`, `daily/`, `wiki/`, `wiki/connections/`, `wiki/qa/`, `output/`). Create any missing directories silently.

## Naming Conventions

- **Topic folders**: lowercase kebab-case (e.g., `machine-learning/`, `distributed-systems/`)
- **Article files**: lowercase kebab-case with `.md` extension (e.g., `retrieval-augmented-generation.md`)
- **Index files**: always prefixed with underscore (`_master-index.md`, `_index.md`)
- **Raw files**: timestamped prefix recommended (`2026-04-08-topic-name.md`)
- **Output files**: descriptive name with date (`audit-2026-04-08.md`, `query-result-2026-04-08.md`)

## Project Attribution

Vaults that hold knowledge from multiple projects use a `project` frontmatter field to track provenance.

### On Raw Files

```yaml
---
captured: 2026-04-08
project: backend
---
```

### On Wiki Articles

```yaml
---
project: backend
---
```

- Single project: `project: backend`
- Multiple projects: `project: [backend, driver]` (list format)
- If a raw file has no `project` field and the source project is ambiguous, ask the user

The `project` field is optional for single-project vaults. For multi-project vaults it is required on every raw file and wiki article.

### Project-Scoped Behavior

- **Compile**: when a topic already has an article on the same concept from a different project, create a separate article (e.g., `order-confirmation-flow-driver.md`) rather than merging
- **Query**: when the user specifies a project context, prioritize articles matching that project. Show cross-project results separately
- **Audit**: only flag contradictions between articles that share the same `project` value. Cross-project differences go in an informational "Cross-Project Divergences" section

## Wiki Article Format

Every wiki article must follow this structure:

```markdown
---
project: <source project, if applicable>
title: "Article Title"
aliases: []
tags: []
sources:
  - "raw/source.md"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Article Title

> One-line summary of the concept.

## Key Takeaways

- Bullet point 1 (quick-scan bullets)
- Bullet point 2
- Bullet point 3

## Details

Deeper encyclopedia-style explanation. Use paragraphs for nuance, context, and relationships that don't fit in bullets. Include specific facts, numbers, and definitions.

## Content

- Use bullets for enumerable items, lists, and comparisons
- Organize with subheadings as needed
- Use [[wiki links]] to connect related concepts across topics

## Related

- [[topic/article-name]] — brief description of relationship
- [[other-topic/other-article]] — brief description of relationship

## Sources

- [[daily/YYYY-MM-DD]] — initial discovery
- [[daily/YYYY-MM-DD]] — updated with new information
```

### Required Sections

- **Key Takeaways**: 3-7 bullet points summarizing the most important insights
- **Details**: Encyclopedia-style paragraphs for deeper explanation (omit only if the article is purely a reference list)
- **Related**: Links to related articles using `[[wiki links]]` format
- **Sources**: Links back to originating daily logs or raw files (`[[daily/YYYY-MM-DD]]` or `[[raw/filename]]`)

### Wiki Link Format

Use double-bracket Obsidian links: `[[topic-folder/article-name]]`

- Link to the file path relative to `wiki/` without the `.md` extension
- Example: `[[machine-learning/transformer-architecture]]`
- When referencing a concept that should have its own article but doesn't yet, still use wiki link syntax — this creates a discoverable "wanted" article

## Connection Article Format

Articles in `wiki/connections/` capture cross-cutting insights linking 2+ concepts. Create one when a source or conversation reveals a non-obvious relationship between topics.

```markdown
---
project: <source project, if applicable>
title: "Connection: X and Y"
connects:
  - "topic-a/article-x"
  - "topic-b/article-y"
sources:
  - "daily/YYYY-MM-DD"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# Connection: X and Y

> One-line summary of the relationship.

## The Connection

[What links these concepts — the shared pattern, mechanism, or constraint]

## Key Insight

[The non-obvious relationship — why this connection matters]

## Evidence

[Specific examples from conversations or source material]

## Related

- [[topic-a/article-x]]
- [[topic-b/article-y]]

## Sources

- [[daily/YYYY-MM-DD]] — session where this connection was discovered
```

## Q&A Article Format

Articles in `wiki/qa/` file answers to queries for future reuse. Created by the query skill with `--file-back`.

```markdown
---
project: <source project, if applicable>
title: "Q: Original Question"
question: "The exact question asked"
consulted:
  - "topic/article-1"
  - "topic/article-2"
filed: YYYY-MM-DD
---

# Q: Original Question

## Answer

[The synthesized answer with [[wikilinks]] to sources]

## Sources Consulted

- [[topic/article-1]] — relevant because...
- [[topic/article-2]] — provided context on...

## Follow-Up Questions

- What about edge case X?
- How does this interact with Y?
```

## Operational File Formats

### wiki/index.md (article catalog)

Used by the SessionStart hook to inject context into every session.

```markdown
# Knowledge Base Article Catalog

> Table of all articles. Used by the SessionStart hook to inject context into sessions.

| Article | Summary | Source | Updated |
|---------|---------|--------|---------|
| [[topic/article-name]] | one-line summary | raw/source.md | 2026-04-08 |
| [[connections/cross-topic]] | one-line summary | daily/2026-04-08.md | 2026-04-08 |
```

Every compile/query operation that creates or updates articles must append new rows to this table.

### wiki/log.md (build log)

Append-only log of all compile, query, and audit operations.

```markdown
# Build Log

> Append-only record of all compile, query, and audit operations.

## [2026-04-08T12:00:00] compile | source.md
- Source: raw/source.md
- Articles created: [[topic/article]], ...
- Articles updated: [[topic/article]], ... (if any)

## [2026-04-08T12:00:00] compile-daily | 2026-04-08.md
- Source: daily/2026-04-08.md
- Articles created: [[connections/cross-topic]], ...

## [2026-04-08T12:00:00] query (filed) | question text here
- Filed to: [[qa/slug]]
```

### daily/YYYY-MM-DD.md (conversation log)

Auto-captured by the SessionEnd/PreCompact hooks. Each session appends a new entry.

```markdown
## [HH:MM] Session — one-line summary of the session

### Context
- Brief description of what was being worked on

### Key Exchanges
- Q: question asked
- A: key point from the answer

### Decisions Made
- Decision and rationale

### Lessons Learned
- Insight or lesson

### Action Items
- [ ] Outstanding task or follow-up
```

## Index File Formats

### _master-index.md

```markdown
# Knowledge Base Index

> Master index of all topics in the wiki.

## Topics

- [[topic-name/_index|Topic Display Name]] — one-line description
- [[another-topic/_index|Another Topic]] — one-line description
```

Sort topics alphabetically.

### _index.md (per topic)

```markdown
# Topic Display Name

> One-line description of this topic area.

## Articles

- [[topic-name/article-one]] — one-line description
- [[topic-name/article-two]] — one-line description
```

Sort articles alphabetically within each topic index.

## Cross-Linking Guidelines

- Link to related concepts whenever they are mentioned in article content
- If an article spans multiple topics, create entries in each relevant topic's `_index.md`
- Prefer specific links (`[[ml/attention-mechanism]]`) over vague ones (`[[ml/_index]]`)
- When a linked target doesn't exist yet, keep the link — it flags a coverage gap for auditing
