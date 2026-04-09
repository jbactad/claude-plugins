# obsidian-rag

General-purpose Obsidian vault manager for Claude Code. Turns Claude into a librarian that compiles your source material into structured wiki articles, keeps the knowledge base consistent, answers questions from it with citations, and automatically captures what you learn in conversations.

## Features

- **5 skills**: compile, audit, query, capture, setup
- **3 lifecycle hooks**: automatic session capture and wiki context injection
- **Index-guided retrieval**: reads article catalog to answer questions without loading the full wiki
- **qmd integration**: optional hybrid search (BM25 + semantic + reranking) for vaults with 500+ articles
- **Project-scoped articles**: multi-project vaults supported via `project:` frontmatter
- **Incremental compilation**: SHA-256 hash tracking — only reprocesses changed files

## Vault Structure

```
vault/
├── raw/          — inbox: drop source files here
├── daily/        — auto-captured conversation logs (YYYY-MM-DD.md)
├── wiki/         — LLM-maintained knowledge base
│   ├── master-index.md    — topic navigator
│   ├── index.md           — article catalog (injected at session start)
│   ├── log.md             — append-only build log
│   ├── connections/       — cross-cutting articles spanning multiple topics
│   ├── qa/                — filed query answers
│   └── <topic>/           — one subfolder per topic
│       └── <article>.md
└── output/       — audit reports and query exports
```

## Skills

| Skill | Triggers |
|-------|----------|
| `compile` | "compile my vault", "process raw files", "ingest sources", new files in `raw/` |
| `audit` | "audit my vault", "check wiki health", "find broken links", "lint my wiki" |
| `query` | "query my vault", "what does my wiki say about", "find information about" |
| `capture` | "capture a note", "save this to my vault", "jot this down" |
| `setup` | "set up my vault", "initialize obsidian-rag", "upgrade my vault", "update the setup" |

### compile

Processes source files from `raw/` (or `daily/`) into structured, interlinked wiki articles. Each article gets rich frontmatter (`title`, `aliases`, `tags`, `sources`, `created`, `updated`), a **Key Takeaways** section, a **Details** section, wiki links to related concepts, and a **Sources** section linking back to originating files.

Detects unprocessed files via SHA-256 hash tracking in `output/state.json`. Marks raw files with `processed: true` as a human-readable secondary marker.

```bash
uv run python scripts/compile.py                        # compile new raw/ files
uv run python scripts/compile.py --source daily         # compile daily logs
uv run python scripts/compile.py --source all           # both
uv run python scripts/compile.py --all                  # force recompile everything
uv run python scripts/compile.py --file raw/source.md   # compile a specific file
uv run python scripts/compile.py --dry-run
```

### audit

Seven health checks against the wiki. Writes a report to `output/audit-YYYY-MM-DD.md`.

| Check | Severity |
|-------|----------|
| Broken `[[wikilinks]]` | error |
| Orphan pages (zero inbound links) | warning |
| Orphan sources (uncompiled files) | warning |
| Stale articles (source changed since last compile) | warning |
| Missing backlinks (A→B but B↛A) | suggestion (auto-fixable) |
| Sparse articles (under 200 words) | suggestion |
| Contradictions across articles (LLM check) | warning |

```bash
uv run python scripts/lint.py                    # all checks
uv run python scripts/lint.py --structural-only  # skip LLM contradiction check (free)
uv run python scripts/lint.py --project backend  # scope contradictions to one project
```

### query

Answers questions by retrieving relevant articles and synthesizing them with `[[wiki link]]` citations.

**With qmd installed** (recommended for large vaults): uses hybrid BM25 + semantic search via the `mcp__qmd__query` tool for precise retrieval that scales to any vault size.

**Without qmd**: reads `wiki/index.md` to identify relevant articles without loading the full wiki, then greps for additional matches.

Supports `--file-back` to file the answer permanently as a Q&A article in `wiki/qa/`.

### capture

Quick-save notes, links, quotes, and ideas to `raw/` for later compilation. Writes timestamped files (`YYYY-MM-DD-topic-slug.md`) with frontmatter for `project`, `source`, `tags`, and `context`.

### setup

Initializes or upgrades a vault. Creates missing directories and files, checks `CLAUDE.md` completeness against the current plugin version, and optionally configures a qmd collection.

## Hooks

Hooks are installed at **user scope** and fire across all Claude Code sessions. They exit silently when no vault is configured, so non-vault projects are unaffected.

| Hook | Behavior |
|------|----------|
| `SessionStart` | Injects `wiki/index.md` and the most recent daily log into every session as context |
| `SessionEnd` | Captures the conversation transcript; spawns a background flush process to extract learnings into `daily/YYYY-MM-DD.md` |
| `PreCompact` | Same as SessionEnd — fires before auto-compaction to preserve context that summarization would discard |

The flush process uses the Claude Agent SDK to decide what's worth saving, then appends a structured entry to the daily log. After 6 PM local time, it also triggers `compile.py --source daily` as a detached background process if today's log has changed since last compilation.

## Installation

```
/plugin marketplace add jbactad/claude-plugins
/plugin install obsidian-rag@jbactad-claude-plugins
```

## Quick Start

```bash
# 1. Set vault path in your shell profile
export OBSIDIAN_VAULT_PATH=~/path/to/your/vault

# 2. Initialize the vault
# "set up my vault at ~/path/to/your/vault"

# 3. Drop source files and compile
# → copy files to raw/
# "compile my vault"

# 4. Query the knowledge base
# "what does my wiki say about X?"
```

## Configuration

Set `OBSIDIAN_VAULT_PATH` in your shell profile (`~/.zshrc` or `~/.bashrc`) to point to your vault root. Without this, the hooks fall back to checking whether the current working directory contains a `wiki/` folder.

```bash
export OBSIDIAN_VAULT_PATH=~/Documents/my-vault
```

## Optional: qmd Hybrid Search

For vaults with 500+ articles, install the [qmd plugin](https://github.com/tobi/qmd) to enable hybrid BM25 + semantic + LLM reranking search. The query skill automatically detects and uses it when available.

```bash
/plugin marketplace add tobi/qmd
/plugin install qmd@qmd

# Register your wiki as a collection
qmd collection add $OBSIDIAN_VAULT_PATH/wiki --name vault
qmd context add qmd://vault "Knowledge base wiki articles"
qmd embed

# Keep current after each compile
qmd update && qmd embed
```

## Requirements

- [uv](https://docs.astral.sh/uv/) — Python package manager used by all scripts and hooks
- Python 3.12+
- Claude Code CLI
- (Optional) [qmd](https://github.com/tobi/qmd) for hybrid search at scale

## License

MIT
