---
name: compile
description: >
  Processes unprocessed source material from an Obsidian vault's raw/
  directory into structured, interlinked wiki articles. This skill should
  be used when the user asks to "compile my vault", "process raw files",
  "ingest sources", "build wiki articles", "update the knowledge base",
  "compile notes", or has new files in raw/ that need processing.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# Compile

Process unprocessed source material into structured, interlinked wiki articles. Backed by `${CLAUDE_SKILL_DIR}/scripts/compile.py` — run directly for automation or CI use.

Two source modes:
- `raw/` (default) — user-dropped source files
- `daily/` — auto-captured conversation logs from SessionEnd/PreCompact hooks
- `all` — both sources

## Vault Discovery

Before any operation, resolve the vault path:

1. Check env var `OBSIDIAN_VAULT_PATH`
2. Check if `wiki/_master-index.md` exists in the current working directory
3. If neither, ask the user with `AskUserQuestion`

Create any missing directories silently. If `wiki/_master-index.md` does not exist, create it before processing. See [vault-conventions.md](references/vault-conventions.md) for full vault structure, naming rules, and article format.

## Workflow

### 1. Determine Source and Discover Files

**Source: raw/** (default)

Glob for files in `raw/`:

```
raw/**/*.md
raw/**/*.txt
raw/**/*.pdf
```

A file is unprocessed if it lacks `processed: true` in its YAML frontmatter.

If the user says "recompile", "force compile", or "compile everything", treat all files as unprocessed.

**Source: daily/**

Glob for `daily/YYYY-MM-DD.md` files. These are auto-captured conversation logs. A daily file is processed if its SHA-256 hash matches the value stored in `output/state.json` under key `daily/YYYY-MM-DD.md`.

**Source: all** — process both raw/ and daily/.

### 2. Process Each File

For each unprocessed file:

1. **Read the file** and identify its core topic(s)
2. **Read the `project` field** from the raw file's frontmatter. If absent and the vault contains articles from multiple projects, ask the user with `AskUserQuestion`
3. **Determine topic folder(s)** — map to existing topics in `wiki/` or create new ones. For cross-cutting insights spanning multiple topics, use `wiki/connections/`. For daily logs, also consider `wiki/connections/` for cross-cutting insights. For each new topic:
   - Create the folder `wiki/<topic-name>/` (lowercase kebab-case)
   - Create `wiki/<topic-name>/_index.md` using the `_index.md` format from [vault-conventions.md](references/vault-conventions.md)
4. **Write the wiki article** following the article format in [vault-conventions.md](references/vault-conventions.md):
   - YAML frontmatter with `project` field carried from the raw file
   - Title derived from the source content
   - One-line summary
   - **Key Takeaways** section with 3-7 bullet points
   - Content using bullet points over paragraphs
   - Mermaid diagram(s) where the content warrants it (see Mermaid Guidelines below)
   - `[[wiki links]]` to related concepts across topics
   - **Related** section at the bottom
5. **Update the topic's `_index.md`** — add the new article entry alphabetically using the format `- [[topic-name/article-name]] — one-line description`
6. **Update `wiki/_master-index.md`**:
   - If the topic is new, add `- [[topic-name/_index|Topic Display Name]] — one-line description` alphabetically
7. **Update `wiki/index.md`** — append a new row: `| [[path/article]] | one-line summary | source/file.md | YYYY-MM-DD |`
8. **Append to `wiki/log.md`** — one entry per compile operation (see format in [vault-conventions.md](references/vault-conventions.md))
9. **Mark raw files as processed** — add `processed: true` and `processed_date: YYYY-MM-DD` to frontmatter (raw/ only, not daily/)

### 3. Handle Multi-Topic Sources

When a source file spans multiple topics:

- Create a primary article in the most relevant topic
- Create shorter summary articles in secondary topics that link back to the primary
- Update all affected `_index.md` files
- Cross-link between the primary and summary articles

### 4. Cross-Link with Existing Articles

After writing each article:

- Scan existing articles in related topics for mentions of the new concept
- Add `[[wiki links]]` to existing articles where the new concept is mentioned
- Add links from the new article to existing related articles
- Update the **Related** section of both new and existing articles

### 5. Report Results

After processing all files, print a summary:

```
Compiled X files:
- [raw] source-1.md → topic-a/article-1.md, topic-b/article-2.md
- [daily] 2026-04-08.md → connections/cross-topic.md
- Updated indexes: wiki/index.md, wiki/log.md, _master-index.md, topic-a/_index.md
- Cross-linked: 3 existing articles updated
- Skipped: Y files (already processed)
```

## Edge Cases

- **Empty raw/**: Report "No unprocessed files found in raw/" and exit
- **Duplicate content (same project)**: If a raw file covers a topic that already has an article from the same project, merge new information into the existing article rather than creating a duplicate. Add the new source as a reference
- **Duplicate content (different project)**: If the topic already has an article from a different project, create a separate article with a project-disambiguated filename (e.g., `order-confirmation-flow-driver.md`). Do not merge cross-project content
- **Unrecognizable content**: If a file cannot be meaningfully categorized, ask the user for guidance with `AskUserQuestion`
- **Binary/non-text files**: Skip with a warning

## Mermaid Guidelines

Add a Mermaid diagram when the source material describes something inherently structural or sequential that a diagram communicates better than bullets. Use judgment — not every article needs one.

### When to add a diagram

- **Flows and processes** — multi-step sequences, request/response cycles, user journeys → `flowchart`
- **State machines** — entities with discrete states and transitions → `stateDiagram-v2`
- **System architecture** — components and their relationships → `flowchart` or `graph`
- **Timelines and sequences** — interactions between actors over time → `sequenceDiagram`
- **Hierarchies** — parent/child relationships, taxonomies → `flowchart TD`

### When NOT to add a diagram

- Simple lists or enumerations (bullets are clearer)
- Concepts with no inherent structure (definitions, explanations)
- When the diagram would just restate the bullet points without adding clarity

### Placement

Place the diagram immediately after the section it illustrates, not at the top or bottom of the article. Use a subheading to introduce it:

```markdown
## Order State Machine

\`\`\`mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Confirmed
    Confirmed --> Shipped
    Shipped --> Delivered
    Delivered --> [*]
    Pending --> Cancelled
    Confirmed --> Cancelled
\`\`\`
```

### Quality rules

- Keep diagrams simple — if it needs more than ~15 nodes, split the article instead
- Use descriptive node labels, not abbreviations
- Prefer `stateDiagram-v2` over `stateDiagram`
- Prefer `flowchart` over `graph` for compatibility

## Article Quality Guidelines

- Prefer specific, actionable bullet points over vague summaries
- Extract concrete facts, numbers, and definitions
- Preserve technical accuracy — do not paraphrase in ways that lose precision
- When the source contradicts existing wiki content, note the contradiction and link both perspectives
- Attribute claims to their source when the raw file includes provenance information
