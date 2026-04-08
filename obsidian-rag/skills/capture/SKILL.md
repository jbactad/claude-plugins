---
name: capture
description: >
  Quickly saves information to an Obsidian vault's raw/ directory for
  later processing by the compile skill. This skill should be used when
  the user asks to "capture a note", "save this to my vault", "add to
  raw", "jot this down", "save for later", "capture this link", or
  "add a source".
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash
  - AskUserQuestion
---

# Capture

Quickly save information to the vault's `raw/` directory for later processing by the compile skill. Designed for fast capture of notes, links, quotes, ideas, and research findings without going through the full compile workflow.

## Vault Discovery

Before any operation, resolve the vault path:

1. Check env var `OBSIDIAN_VAULT_PATH`
2. Check if `wiki/_master-index.md` exists in the current working directory
3. If neither, ask the user with `AskUserQuestion`

Create `raw/` if it doesn't exist.

See [vault-conventions.md](references/vault-conventions.md) for vault structure and naming conventions.

## Capture Workflow

### 1. Gather Content

Accept content from one of these sources:

- **Inline content** — the user provides text directly in their message
- **Interactive** — if no content provided, ask with `AskUserQuestion`: "What would you like to capture?"
- **File reference** — the user points to a file to read and capture

### 2. Detect Project

Determine which project this capture belongs to:

1. If the user explicitly names a project, use that
2. Otherwise, infer the project name from the current working directory name (e.g., cwd `/workspace/acme/backend` → `project: backend`)
3. If the cwd is the vault root itself and the project is ambiguous, ask with `AskUserQuestion`

### 3. Gather Metadata (Optional)

If the user provides metadata, include it. Do not prompt for metadata unless the user's message suggests they want to add some. Common metadata fields:

- **source**: URL or reference where the information came from
- **tags**: Comma-separated topic tags
- **context**: Why this is being captured or how it relates to other work

### 4. Create the Raw File

Write a timestamped file to `raw/`:

**Filename format**: `raw/YYYY-MM-DD-topic-slug.md`

- Use today's date as the prefix
- Derive the slug from the content's main topic (kebab-case, 2-4 words)
- If multiple captures happen on the same day with the same topic, append a counter: `raw/2026-04-08-topic-slug-2.md`

**File format**:

```markdown
---
captured: YYYY-MM-DD
project: <project name, if detected>
source: <url or reference, if provided>
tags: <comma-separated tags, if provided>
context: <user-provided context, if any>
---

# <Descriptive Title>

<captured content>
```

### 5. Confirm

After writing the file, print:

```
Captured to raw/YYYY-MM-DD-topic-slug.md
Run /compile when ready to process into wiki articles.
```

## Examples

### Quick note capture (inside a project directory)

User says from `/workspace/acme/backend`: "Capture this — transformer models use self-attention to weigh input tokens against each other"

Result:
```markdown
---
captured: 2026-04-08
project: backend
---

# Transformer Self-Attention

- Transformer models use self-attention to weigh input tokens against each other
```

### Link with context

User says: "Save this link for later: https://example.com/paper.pdf — it's about retrieval-augmented generation for domain-specific tasks"

Result:
```markdown
---
captured: 2026-04-08
source: https://example.com/paper.pdf
tags: rag, retrieval-augmented-generation
---

# Retrieval-Augmented Generation for Domain-Specific Tasks

- Source paper on retrieval-augmented generation (RAG) applied to domain-specific tasks
- URL: https://example.com/paper.pdf
```

## Edge Cases

- **No vault found**: After vault discovery fails, ask the user for the path. If they want to create a new vault, create the `raw/`, `wiki/`, and `output/` directories
- **Very long content**: Accept it all — raw files have no length limit. The compile skill handles splitting into multiple articles if needed
- **Multiple items in one message**: Create separate raw files for each distinct item if the user provides multiple unrelated pieces of information
