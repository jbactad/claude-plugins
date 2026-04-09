# Vault Structure and Conventions

## Directory Layout

```
vault/
├── raw/          — inbox for source material (user drops files here)
├── daily/        — auto-captured conversation logs (YYYY-MM-DD.md)
├── wiki/         — LLM-maintained knowledge base
│   ├── index.md           — topic navigator + article catalog (used by SessionStart hook)
│   ├── log.md             — append-only build log
│   ├── connections/       — cross-cutting articles spanning multiple topics
│   ├── qa/                — question-answer articles (filed by /query --file-back)
│   └── <topic>/           — one subfolder per topic (kebab-case)
│       ├── index.md       — lists all articles in this topic
│       └── <article>.md   — individual articles (kebab-case)
└── output/       — audit reports and query exports
```

## Vault Discovery

Every operation must resolve the vault path before proceeding. Check in order:

1. If env var `OBSIDIAN_VAULT_PATH` is set, use that path
2. If `wiki/index.md` exists in the current working directory, the vault is `.`
3. Otherwise, ask the user for the vault path using `AskUserQuestion`

Once resolved, verify the vault has the expected subdirectories (`raw/`, `daily/`, `wiki/`, `wiki/connections/`, `wiki/qa/`, `output/`). Create any missing directories silently.

## Naming Conventions

- **Topic folders**: lowercase kebab-case (e.g., `machine-learning/`, `distributed-systems/`)
- **Article files**: lowercase kebab-case with `.md` extension (e.g., `retrieval-augmented-generation.md`)
- **Index files**: `wiki/index.md` (top-level), `wiki/<topic>/index.md` (per-topic)
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
---

# Article Title

> One-line summary of the concept.

## Key Takeaways

- Bullet point 1
- Bullet point 2
- Bullet point 3

## Content

- Use bullet points over paragraphs
- Organize with subheadings as needed
- Use [[wiki links]] to connect related concepts across topics
- Include specific facts, not vague summaries

## Related

- [[topic/article-name]] — brief description of relationship
- [[other-topic/other-article]] — brief description of relationship
```

### Required Sections

- **Key Takeaways**: 3-7 bullet points summarizing the most important insights
- **Related**: Links to related articles using `[[wiki links]]` format

### Wiki Link Format

Use double-bracket Obsidian links: `[[topic-folder/article-name]]`

- Link to the file path relative to `wiki/` without the `.md` extension
- Example: `[[machine-learning/transformer-architecture]]`
- When referencing a concept that should have its own article but doesn't yet, still use wiki link syntax — this creates a discoverable "wanted" article

## Operational File Formats

### wiki/index.md (top-level index)

Merged topic navigator and article catalog. Used by the SessionStart hook to inject context into every session.

```markdown
# Knowledge Base Index

> Topics and articles in this vault.

## Topics

- **Topic Display Name** (`topic-name/`) — one-line description
- **Another Topic** (`another-topic/`) — one-line description

## Articles

| Article | Summary | Source | Updated |
|---------|---------|--------|---------|
| [[topic/article-name]] | one-line summary | raw/source.md | 2026-04-08 |
| [[connections/cross-topic]] | one-line summary | daily/2026-04-08.md | 2026-04-08 |
```

Sort topics alphabetically. Append article rows in chronological order.

### wiki/<topic>/index.md (per-topic index)

Lists all articles within a topic. Created when a new topic folder is created.

```markdown
# Topic Display Name

> One-line description of this topic area.

## Articles

- [[topic-name/article-one]] — one-line description
- [[topic-name/article-two]] — one-line description
```

Sort articles alphabetically.

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

## Cross-Linking Guidelines

- Link to related concepts whenever they are mentioned in article content
- If an article spans multiple topics, create entries in each relevant topic's `index.md`
- Prefer specific links (`[[ml/attention-mechanism]]`) over broad topic references
- When a linked target doesn't exist yet, keep the link — it flags a coverage gap for auditing
