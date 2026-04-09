#!/usr/bin/env python3
"""
Query the knowledge base using index-guided retrieval (no RAG).

The LLM reads the article catalog, picks relevant articles, synthesizes
an answer, and optionally files the answer back as a Q&A article.

Usage:
    python query.py "How does order confirmation work?"
    python query.py "What is the auth strategy?" --file-back
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import OUTPUT_DIR, QA_DIR, SCRIPTS_DIR, WIKI_DIR, now_iso, today_iso
from utils import load_state, read_all_wiki_content, save_state, slugify


async def run_query(question: str, file_back: bool = False, project: str | None = None) -> str:
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )

    wiki_content = read_all_wiki_content()

    tools = ["Read", "Glob", "Grep"]
    if file_back:
        tools.extend(["Write", "Edit"])

    project_filter = ""
    if project:
        project_filter = f"\nPrioritize articles with `project: {project}` in frontmatter. Label cross-project results clearly."

    file_back_instructions = ""
    if file_back:
        slug = slugify(question)[:60]
        qa_path = QA_DIR / f"{slug}.md"
        timestamp = now_iso()
        file_back_instructions = f"""

After answering, file the answer back:
1. Create `{qa_path}` using this frontmatter:
   ```yaml
   ---
   title: "Q: {question}"
   question: "{question}"
   filed: {today_iso()}
   ---
   ```
2. Add a row to `wiki/index.md`: `| [[qa/{slug}]] | {question[:60]} | query | {today_iso()} |`
3. Append to `wiki/log.md`:
   ```
   ## [{timestamp}] query (filed) | {question[:60]}
   - Filed to: [[qa/{slug}]]
   ```
"""

    prompt = f"""You are a knowledge base query engine. Answer the question by consulting
the knowledge base below.

## How to Answer

1. Read the INDEX section — it lists every article with a one-line summary
2. Identify relevant articles (3-10 max)
3. Synthesize a clear, direct answer
4. Cite sources using [[wikilinks]]
5. If the knowledge base has no relevant information, say so explicitly
{project_filter}

## Knowledge Base

{wiki_content}

## Question

{question}
{file_back_instructions}"""

    answer = ""
    cost = 0.0

    try:
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                cwd=str(WIKI_DIR.parent),
                system_prompt={"type": "preset", "preset": "claude_code"},
                allowed_tools=tools,
                permission_mode="acceptEdits",
                max_turns=15,
            ),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        answer += block.text
            elif isinstance(message, ResultMessage):
                cost = message.total_cost_usd or 0.0
    except Exception as e:
        answer = f"Error querying knowledge base: {e}"

    state = load_state()
    state["query_count"] = state.get("query_count", 0) + 1
    state["total_cost"] = state.get("total_cost", 0.0) + cost
    save_state(state)

    return answer


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the knowledge base")
    parser.add_argument("question", help="Question to ask")
    parser.add_argument("--file-back", action="store_true",
                        help="File answer back as a Q&A wiki article")
    parser.add_argument("--project", help="Filter results to a specific project")
    args = parser.parse_args()

    print(f"Question: {args.question}")
    if args.project:
        print(f"Project: {args.project}")
    print("-" * 60)

    answer = asyncio.run(run_query(args.question, args.file_back, args.project))
    print(answer)


if __name__ == "__main__":
    main()
