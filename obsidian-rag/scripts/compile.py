#!/usr/bin/env python3
"""
Compile source files into structured wiki articles using the Claude Agent SDK.

Two source modes:
  --source raw    (default) Process unprocessed files in raw/ → wiki articles
  --source daily  Process daily conversation logs in daily/ → wiki articles
  --source all    Process both raw/ and daily/

Usage:
    python compile.py                        # compile new raw/ files
    python compile.py --source daily         # compile new daily logs
    python compile.py --source all           # compile both
    python compile.py --all                  # force recompile all sources
    python compile.py --dry-run              # show what would be compiled
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    CONVENTIONS_FILE,
    DAILY_DIR,
    RAW_DIR,
    SCRIPTS_DIR,
    WIKI_DIR,
    now_iso,
    today_iso,
)
from utils import (
    file_hash,
    list_daily_logs,
    list_raw_files,
    load_state,
    read_master_index,
    read_wiki_index,
    save_state,
)

ROOT_DIR = SCRIPTS_DIR.parent


async def compile_source(source_path: Path, source_type: str, state: dict) -> float:
    """Compile a single source file into wiki articles. Returns API cost."""
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )

    source_content = source_path.read_text(encoding="utf-8")
    conventions = CONVENTIONS_FILE.read_text(encoding="utf-8") if CONVENTIONS_FILE.exists() else ""
    master_index = read_master_index()
    article_index = read_wiki_index()
    timestamp = now_iso()

    if source_type == "raw":
        task_description = f"""Process this raw source file and compile it into structured wiki articles.

Follow the vault conventions exactly (article format, naming, indexes, cross-links).

After writing articles, update:
1. Each affected topic's `_index.md` (add new article entries alphabetically)
2. `wiki/_master-index.md` (add new topics if created)
3. `wiki/index.md` (add new rows to the table: `| [[path]] | summary | {source_path.name} | {today_iso()} |`)
4. Append to `wiki/log.md`:
   ```
   ## [{timestamp}] compile | {source_path.name}
   - Source: raw/{source_path.name}
   - Articles created: [[topic/article]], ...
   - Articles updated: [[topic/article]], ... (if any)
   ```
5. Mark the raw file as processed by adding to its YAML frontmatter:
   ```
   processed: true
   processed_date: {today_iso()}
   ```"""
    else:  # daily
        task_description = f"""Process this daily conversation log and compile knowledge into wiki articles.

Extract concepts, decisions, lessons, and insights. Create articles in the most
relevant topic folders. For cross-cutting insights that span multiple topics,
create articles in `wiki/connections/`.

After writing articles, update:
1. Each affected topic's `_index.md` (add new article entries alphabetically)
2. `wiki/_master-index.md` (add new topics if created)
3. `wiki/index.md` (add new rows: `| [[path]] | summary | daily/{source_path.name} | {today_iso()} |`)
4. Append to `wiki/log.md`:
   ```
   ## [{timestamp}] compile-daily | {source_path.name}
   - Source: daily/{source_path.name}
   - Articles created: [[topic/article]], ...
   - Articles updated: [[topic/article]], ... (if any)
   ```"""

    prompt = f"""You are a knowledge compiler for an Obsidian vault.

## Vault Conventions

{conventions}

## Current Topic Index (wiki/_master-index.md)

{master_index}

## Current Article Catalog (wiki/index.md)

{article_index}

## Source File: {source_path.name}

{source_content}

## Task

{task_description}

Write all files directly. Use the tool to read existing articles before updating them.
Vault root: {WIKI_DIR.parent}
"""

    cost = 0.0
    try:
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                cwd=str(WIKI_DIR.parent),
                system_prompt={"type": "preset", "preset": "claude_code"},
                allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
                permission_mode="acceptEdits",
                max_turns=30,
            ),
        ):
            if isinstance(message, ResultMessage):
                cost = message.total_cost_usd or 0.0
    except Exception as e:
        print(f"  Error: {e}")
        return 0.0

    # Update state
    rel_key = f"{source_type}/{source_path.name}"
    state.setdefault("ingested", {})[rel_key] = {
        "hash": file_hash(source_path),
        "compiled_at": now_iso(),
        "cost_usd": cost,
    }
    state["total_cost"] = state.get("total_cost", 0.0) + cost
    save_state(state)

    return cost


def get_pending(source_type: str, force: bool, state: dict) -> list[tuple[Path, str]]:
    """Return list of (path, type) tuples that need compiling."""
    pending = []

    if source_type in ("raw", "all"):
        for path in list_raw_files():
            key = f"raw/{path.name}"
            prev = state.get("ingested", {}).get(key, {})
            if force or not prev or prev.get("hash") != file_hash(path):
                pending.append((path, "raw"))

    if source_type in ("daily", "all"):
        for path in list_daily_logs():
            key = f"daily/{path.name}"
            prev = state.get("ingested", {}).get(key, {})
            if force or not prev or prev.get("hash") != file_hash(path):
                pending.append((path, "daily"))

    return pending


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile sources into wiki articles")
    parser.add_argument("--source", choices=["raw", "daily", "all"], default="raw")
    parser.add_argument("--all", action="store_true", help="Force recompile all")
    parser.add_argument("--file", help="Compile a specific file (path relative to vault root, e.g. raw/source.md or daily/2026-04-01.md)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    state = load_state()

    if args.file:
        file_path = ROOT_DIR / args.file
        if not file_path.exists():
            print(f"File not found: {file_path}")
            sys.exit(1)
        stype = "daily" if args.file.startswith("daily/") else "raw"
        pending = [(file_path, stype)]
    else:
        pending = get_pending(args.source, args.all, state)

    if not pending:
        print("Nothing to compile — all sources are up to date.")
        return

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Files to compile ({len(pending)}):")
    for path, stype in pending:
        print(f"  [{stype}] {path.name}")

    if args.dry_run:
        return

    total_cost = 0.0
    for i, (path, stype) in enumerate(pending, 1):
        print(f"\n[{i}/{len(pending)}] Compiling [{stype}] {path.name}...")
        cost = asyncio.run(compile_source(path, stype, state))
        total_cost += cost
        print(f"  Done. Cost: ${cost:.4f}")

    print(f"\nComplete. Total cost: ${total_cost:.4f}")


if __name__ == "__main__":
    main()
