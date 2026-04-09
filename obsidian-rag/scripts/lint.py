#!/usr/bin/env python3
"""
Lint the wiki knowledge base for structural and semantic health.

Runs 7 checks:
  1. Broken links       — [[wikilinks]] pointing to non-existent articles
  2. Orphan pages       — articles with zero inbound links
  3. Orphan sources     — raw/ files not yet compiled
  4. Stale articles     — source files changed since last compilation
  5. Missing backlinks  — A links to B but B doesn't link back to A
  6. Sparse articles    — articles under 200 words
  7. Contradictions     — conflicting claims (LLM check)

Usage:
    python lint.py                    # all checks
    python lint.py --structural-only  # skip LLM contradiction check (free)
    python lint.py --project backend  # scope contradiction check to one project
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import OUTPUT_DIR, SCRIPTS_DIR, WIKI_DIR, today_iso, now_iso
from utils import (
    count_inbound_links,
    extract_wikilinks,
    file_hash,
    get_article_word_count,
    list_daily_logs,
    list_raw_files,
    list_wiki_articles,
    load_state,
    read_all_wiki_content,
    save_state,
    wiki_article_exists,
)


def check_broken_links() -> list[dict]:
    issues = []
    for article in list_wiki_articles():
        content = article.read_text(encoding="utf-8")
        rel = article.relative_to(WIKI_DIR)
        for link in extract_wikilinks(content):
            if link.startswith("daily/") or link.startswith("raw/"):
                continue
            if not wiki_article_exists(link):
                issues.append({
                    "severity": "error",
                    "check": "broken_link",
                    "file": str(rel),
                    "detail": f"Broken link [[{link}]] — target does not exist",
                })
    return issues


def check_orphan_pages() -> list[dict]:
    issues = []
    for article in list_wiki_articles():
        rel = article.relative_to(WIKI_DIR)
        link_target = str(rel).replace(".md", "").replace("\\", "/")
        if count_inbound_links(link_target) == 0:
            issues.append({
                "severity": "warning",
                "check": "orphan_page",
                "file": str(rel),
                "detail": f"Orphan page — no other articles link to [[{link_target}]]",
            })
    return issues


def check_orphan_sources() -> list[dict]:
    state = load_state()
    ingested = state.get("ingested", {})
    issues = []
    for path in list_raw_files():
        if f"raw/{path.name}" not in ingested:
            issues.append({
                "severity": "warning",
                "check": "orphan_source",
                "file": f"raw/{path.name}",
                "detail": f"Uncompiled raw file — run /compile to process",
            })
    for path in list_daily_logs():
        if f"daily/{path.name}" not in ingested:
            issues.append({
                "severity": "warning",
                "check": "orphan_source",
                "file": f"daily/{path.name}",
                "detail": f"Uncompiled daily log — run /compile --source daily",
            })
    return issues


def check_stale_articles() -> list[dict]:
    state = load_state()
    ingested = state.get("ingested", {})
    issues = []
    for path in list_raw_files():
        key = f"raw/{path.name}"
        if key in ingested and ingested[key].get("hash") != file_hash(path):
            issues.append({
                "severity": "warning",
                "check": "stale_article",
                "file": key,
                "detail": f"Source changed since last compilation — recompile to update",
            })
    for path in list_daily_logs():
        key = f"daily/{path.name}"
        if key in ingested and ingested[key].get("hash") != file_hash(path):
            issues.append({
                "severity": "warning",
                "check": "stale_article",
                "file": key,
                "detail": f"Daily log changed since last compilation — recompile to update",
            })
    return issues


def check_missing_backlinks() -> list[dict]:
    issues = []
    for article in list_wiki_articles():
        content = article.read_text(encoding="utf-8")
        rel = article.relative_to(WIKI_DIR)
        source_link = str(rel).replace(".md", "").replace("\\", "/")

        for link in extract_wikilinks(content):
            if link.startswith("daily/") or link.startswith("raw/"):
                continue
            target_path = WIKI_DIR / f"{link}.md"
            if target_path.exists():
                target_content = target_path.read_text(encoding="utf-8")
                if f"[[{source_link}]]" not in target_content:
                    issues.append({
                        "severity": "suggestion",
                        "check": "missing_backlink",
                        "file": str(rel),
                        "detail": f"[[{source_link}]] links to [[{link}]] but not vice versa",
                        "auto_fixable": True,
                    })
    return issues


def check_sparse_articles() -> list[dict]:
    issues = []
    for article in list_wiki_articles():
        word_count = get_article_word_count(article)
        if word_count < 200:
            rel = article.relative_to(WIKI_DIR)
            issues.append({
                "severity": "suggestion",
                "check": "sparse_article",
                "file": str(rel),
                "detail": f"Sparse article — {word_count} words (min recommended: 200)",
            })
    return issues


async def check_contradictions(project: str | None = None) -> list[dict]:
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )

    wiki_content = read_all_wiki_content()

    project_scope = (
        f"\nOnly check articles with `project: {project}` in frontmatter. "
        "Cross-project differences are expected — do NOT flag them."
        if project else
        "\nNote: articles from different projects may intentionally differ — "
        "only flag contradictions within the same project."
    )

    prompt = f"""Review this knowledge base for contradictions and inconsistencies.
{project_scope}

## Knowledge Base

{wiki_content}

## Instructions

Look for:
- Direct contradictions (article A says X, article B says not-X, same project)
- Inconsistent terminology within the same project
- Outdated information conflicting with newer entries

For each issue, output EXACTLY one line:
CONTRADICTION: [file1] vs [file2] - description
INCONSISTENCY: [file] - description

If no issues: output exactly: NO_ISSUES
No preamble, no explanation — only the formatted lines."""

    response = ""
    try:
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                allowed_tools=[],
                max_turns=2,
            ),
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response += block.text
    except Exception as e:
        return [{"severity": "error", "check": "contradiction", "file": "(system)",
                 "detail": f"LLM check failed: {e}"}]

    issues = []
    if "NO_ISSUES" not in response:
        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith(("CONTRADICTION:", "INCONSISTENCY:")):
                issues.append({
                    "severity": "warning",
                    "check": "contradiction",
                    "file": "(cross-article)",
                    "detail": line,
                })
    return issues


def generate_report(all_issues: list[dict]) -> str:
    errors = [i for i in all_issues if i["severity"] == "error"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]
    suggestions = [i for i in all_issues if i["severity"] == "suggestion"]

    lines = [
        f"# Audit Report — {today_iso()}",
        "",
        f"**Total issues:** {len(all_issues)}",
        f"- Errors: {len(errors)}",
        f"- Warnings: {len(warnings)}",
        f"- Suggestions: {len(suggestions)}",
        "",
    ]

    for label, issues, marker in [
        ("Errors", errors, "x"),
        ("Warnings", warnings, "!"),
        ("Suggestions", suggestions, "?"),
    ]:
        if issues:
            lines.append(f"## {label}")
            lines.append("")
            for issue in issues:
                fixable = " (auto-fixable)" if issue.get("auto_fixable") else ""
                lines.append(f"- **[{marker}]** `{issue['file']}` — {issue['detail']}{fixable}")
            lines.append("")

    if not all_issues:
        lines.append("All checks passed. Knowledge base is healthy.")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit the knowledge base")
    parser.add_argument("--structural-only", action="store_true",
                        help="Skip LLM contradiction check (faster, no cost)")
    parser.add_argument("--project", help="Scope contradiction check to a specific project")
    args = parser.parse_args()

    print("Running knowledge base audit...")
    all_issues: list[dict] = []

    structural_checks = [
        ("Broken links", check_broken_links),
        ("Orphan pages", check_orphan_pages),
        ("Orphan sources", check_orphan_sources),
        ("Stale articles", check_stale_articles),
        ("Missing backlinks", check_missing_backlinks),
        ("Sparse articles", check_sparse_articles),
    ]

    for name, check_fn in structural_checks:
        print(f"  {name}...", end=" ", flush=True)
        issues = check_fn()
        all_issues.extend(issues)
        print(f"{len(issues)} issue(s)")

    if not args.structural_only:
        print(f"  Contradictions (LLM)...", end=" ", flush=True)
        issues = asyncio.run(check_contradictions(args.project))
        all_issues.extend(issues)
        print(f"{len(issues)} issue(s)")
    else:
        print("  Contradictions (skipped — structural-only mode)")

    report = generate_report(all_issues)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"audit-{today_iso()}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\nReport saved to: {report_path.relative_to(WIKI_DIR.parent)}")

    state = load_state()
    state["last_lint"] = now_iso()
    save_state(state)

    errors = sum(1 for i in all_issues if i["severity"] == "error")
    warnings = sum(1 for i in all_issues if i["severity"] == "warning")
    suggestions = sum(1 for i in all_issues if i["severity"] == "suggestion")
    print(f"Results: {errors} errors, {warnings} warnings, {suggestions} suggestions")


if __name__ == "__main__":
    main()
