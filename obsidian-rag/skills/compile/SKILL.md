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

Process unprocessed source material from the vault's `raw/` directory into structured, interlinked wiki articles in `wiki/`.

## Vault Discovery

Before any operation, resolve the vault path:

1. Check env var `OBSIDIAN_VAULT_PATH`
2. Check if `wiki/_master-index.md` exists in the current working directory
3. If neither, ask the user with `AskUserQuestion`

Create any missing directories (`raw/`, `wiki/`, `output/`) silently.

See [vault-conventions.md](references/vault-conventions.md) for full vault structure, naming rules, and article format.

## Workflow

### 1. Discover Unprocessed Files

Glob for all files in `raw/`:

```
raw/**/*.md
raw/**/*.txt
raw/**/*.pdf
```

To determine if a file has already been processed, check for a `processed: true` line in the file's YAML frontmatter (if any). Files without frontmatter or without `processed: true` are unprocessed.

### 2. Process Each File

For each unprocessed file:

1. **Read the file** and identify its core topic(s)
2. **Determine topic folder(s)** — map to existing topics in `wiki/` or create new ones
3. **Write the wiki article** following the article format in [vault-conventions.md](references/vault-conventions.md):
   - Title derived from the source content
   - One-line summary
   - **Key Takeaways** section with 3-7 bullet points
   - Content using bullet points over paragraphs
   - `[[wiki links]]` to related concepts across topics
   - **Related** section at the bottom
4. **Update the topic's `_index.md`** — add the new article entry alphabetically
5. **Update `wiki/_master-index.md`** — add the topic if new, keep alphabetical order
6. **Mark the raw file as processed** — add or update YAML frontmatter with `processed: true` and `processed_date: YYYY-MM-DD`

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
Compiled X files from raw/:
- Created: article-1.md (topic-a), article-2.md (topic-b)
- Updated indexes: topic-a/_index.md, topic-b/_index.md, _master-index.md
- Cross-linked: 3 existing articles updated
- Skipped: Y files (already processed)
```

## Edge Cases

- **Empty raw/**: Report "No unprocessed files found in raw/" and exit
- **Duplicate content**: If a raw file covers a topic that already has an article, merge new information into the existing article rather than creating a duplicate. Add the new source as a reference
- **Unrecognizable content**: If a file cannot be meaningfully categorized, ask the user for guidance with `AskUserQuestion`
- **Binary/non-text files**: Skip with a warning

## Article Quality Guidelines

- Prefer specific, actionable bullet points over vague summaries
- Extract concrete facts, numbers, and definitions
- Preserve technical accuracy — do not paraphrase in ways that lose precision
- When the source contradicts existing wiki content, note the contradiction and link both perspectives
- Attribute claims to their source when the raw file includes provenance information
