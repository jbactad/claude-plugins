# Vault Structure and Conventions

## Directory Layout

```
vault/
├── raw/          — inbox for source material (user drops files here)
├── wiki/         — LLM-maintained knowledge base
│   ├── _master-index.md   — entry point, lists all topics
│   └── <topic>/           — one subfolder per topic (kebab-case)
│       ├── _index.md      — lists all articles in this topic
│       └── <article>.md   — individual articles (kebab-case)
└── output/       — query results and generated reports
```

## Vault Discovery

Every operation must resolve the vault path before proceeding. Check in order:

1. If env var `OBSIDIAN_VAULT_PATH` is set, use that path
2. If `wiki/_master-index.md` exists in the current working directory, the vault is `.`
3. Otherwise, ask the user for the vault path using `AskUserQuestion`

Once resolved, verify the vault has the expected subdirectories (`raw/`, `wiki/`, `output/`). Create any missing directories silently.

## Naming Conventions

- **Topic folders**: lowercase kebab-case (e.g., `machine-learning/`, `distributed-systems/`)
- **Article files**: lowercase kebab-case with `.md` extension (e.g., `retrieval-augmented-generation.md`)
- **Index files**: always prefixed with underscore (`_master-index.md`, `_index.md`)
- **Raw files**: timestamped prefix recommended (`2026-04-08-topic-name.md`)
- **Output files**: descriptive name with date (`audit-2026-04-08.md`, `query-result-2026-04-08.md`)

## Wiki Article Format

Every wiki article must follow this structure:

```markdown
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
