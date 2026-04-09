---
name: query
description: >
  Answers questions by navigating an Obsidian wiki's index hierarchy and
  synthesizing information with [[wiki link]] citations. This skill should
  be used when the user asks to "query my vault", "search the knowledge
  base", "find information about", "what does my wiki say about", "answer
  from my notes", or "look up in my vault".
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
  - AskUserQuestion
  - mcp__qmd__query
  - mcp__qmd__get
  - mcp__qmd__multi_get
---

# Query

Answer questions by retrieving relevant wiki articles and synthesizing them with `[[wiki link]]` citations. Uses qmd hybrid search when available (BM25 + semantic + reranking), falls back to index-guided retrieval otherwise. Backed by `${CLAUDE_SKILL_DIR}/scripts/query.py` — run directly for automation or batch use.

```bash
uv run python ${CLAUDE_SKILL_DIR}/scripts/query.py "How does X work?"
uv run python ${CLAUDE_SKILL_DIR}/scripts/query.py "What is Y?" --file-back   # file answer to wiki/qa/
uv run python ${CLAUDE_SKILL_DIR}/scripts/query.py "What about Z?" --project backend
```

## Vault Discovery

Before any operation, resolve the vault path:

1. Check env var `OBSIDIAN_VAULT_PATH`
2. Check if `wiki/master-index.md` exists in the current working directory
3. If neither, ask the user with `AskUserQuestion`

See [vault-conventions.md](references/vault-conventions.md) for vault structure and wiki link format.

## Query Workflow

### 1. Understand the Question

Parse the user's question to identify:

- **Key concepts** — the main topics or terms to search for
- **Question type** — factual lookup, comparison, synthesis, or exploration
- **Scope** — specific topic or cross-cutting across the knowledge base
- **Project context** — if the user mentions a project name (e.g., "in backend", "for the driver app"), note it as a filter. If the current working directory is inside a project directory, use that as the default project context

### 2. Retrieve Relevant Articles

**If `mcp__qmd__query` is available (qmd plugin installed) — preferred:**

Use hybrid search for precise, scalable retrieval:

```json
{
  "searches": [
    { "type": "lex", "query": "<2–4 key terms from the question>" },
    { "type": "vec", "query": "<full natural language question>" }
  ],
  "collections": ["vault"],
  "limit": 10
}
```

- First search gets 2× weight in fusion — put the strongest query first
- Add `"intent": "<disambiguation hint>"` when the query terms are ambiguous
- Use `mcp__qmd__get` to retrieve full article content by path or `#docid`
- Skip step 3 — qmd's hybrid retrieval covers keyword and semantic matching

**If qmd is not available — index-guided fallback:**

1. **Read `wiki/index.md`** — one-line catalog of every article; use it to identify relevant articles without reading them all. If `index.md` has no article rows (empty table), skip to step 2
2. **Read `wiki/master-index.md`** — for topic-level orientation
3. **Read targeted articles** — only articles identified as plausibly relevant

### 3. Search for Additional Hits (index-guided fallback only)

When qmd is not available, supplement index navigation with Grep:

- Search for key terms from the question across `wiki/**/*.md`
- Check results for articles not already identified via the index
- Read any additional relevant articles

### 4. Synthesize the Answer

Compose a response that:

- **Directly answers the question** — lead with the answer, not the process
- **Uses bullet points** for multi-part answers
- **Cites sources** — every factual claim includes a `[[wiki link]]` to the article it came from
- **Notes gaps** — if the wiki doesn't fully cover the question, say so explicitly
- **Flags contradictions** — if different articles disagree, present both perspectives with citations
- **Respects project scope** — if a project context was identified in step 1:
  - Prioritize articles whose `project` frontmatter matches the target project
  - If cross-project articles are included, label them clearly (e.g., "From driver project:" or "(cross-project)")
  - If no project-matching articles exist, fall back to all articles and note the mismatch

### 5. File Back (optional)

If the user says "save this answer", "file it back", or passes `--file-back`:

1. Create `wiki/qa/<slug>.md` following the Q&A article format in [vault-conventions.md](references/vault-conventions.md): frontmatter with `title`, `question`, `consulted` (list of articles read), and `filed` date; `## Answer`, `## Sources Consulted`, and `## Follow-Up Questions` sections
2. Append a row to `wiki/index.md`: `| [[qa/slug]] | question summary | query | YYYY-MM-DD |`
3. Append to `wiki/log.md`: `## [timestamp] query (filed) | question`

For plain report output (not filed to wiki), write to `output/query-<topic>-YYYY-MM-DD.md`.

## Citation Format

Inline citations use wiki link syntax:

```markdown
Transformers use self-attention to process input sequences in parallel
([[machine-learning/transformer-architecture]]).
```

For report output, include a sources section:

```markdown
## Sources

- [[machine-learning/transformer-architecture]] — core architecture details
- [[machine-learning/attention-mechanism]] — attention mechanism explanation
- [[nlp/sequence-to-sequence]] — historical context
```

## Answer Quality Guidelines

- Prefer specific facts from articles over general knowledge
- When the wiki contains the answer, use wiki content — do not supplement with external knowledge unless the wiki is silent on a point
- If the wiki has no relevant content, state clearly: "The knowledge base does not contain information about [topic]"
- When synthesizing across multiple articles, clearly attribute which article contributes which point
- For comparison questions, use a structured format (table or side-by-side bullets)

## Edge Cases

- **Empty wiki**: Report "The wiki contains no articles yet. Run /compile to process raw files."
- **No relevant articles**: State what was searched and that no matches were found. Suggest topics the user could add
- **Ambiguous question**: Ask the user to clarify using `AskUserQuestion` rather than guessing
- **Very broad question**: Provide a high-level overview with pointers to specific topic indexes, rather than reading every article
