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
---

# Query

Answer questions by navigating the wiki's hierarchical structure and synthesizing information from relevant articles. Provide citations using `[[wiki links]]` so the user can trace claims back to source articles.

## Vault Discovery

Before any operation, resolve the vault path:

1. Check env var `OBSIDIAN_VAULT_PATH`
2. Check if `wiki/_master-index.md` exists in the current working directory
3. If neither, ask the user with `AskUserQuestion`

See [vault-conventions.md](references/vault-conventions.md) for vault structure and wiki link format.

## Query Workflow

### 1. Understand the Question

Parse the user's question to identify:

- **Key concepts** — the main topics or terms to search for
- **Question type** — factual lookup, comparison, synthesis, or exploration
- **Scope** — specific topic or cross-cutting across the knowledge base
- **Project context** — if the user mentions a project name (e.g., "in backend", "for the driver app"), note it as a filter. If the current working directory is inside a project directory, use that as the default project context

### 2. Navigate the Index Hierarchy

Start broad and narrow down:

1. **Read `wiki/_master-index.md`** — identify which topics are relevant to the question
2. **Read relevant `_index.md` files** — find specific articles that likely contain the answer
3. **Read targeted articles** — extract the information needed

This top-down approach avoids reading the entire wiki. Only read articles that are plausibly relevant.

### 3. Search for Additional Hits

After index-guided navigation, use Grep to find mentions the index might miss:

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

### 5. Handle "Report" Requests

If the user asks for a report or persistent output:

- Write the answer to `output/` with a descriptive filename (e.g., `output/query-topic-YYYY-MM-DD.md`)
- Use the same citation format in the report
- Include a **Sources** section at the bottom listing all referenced articles

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
