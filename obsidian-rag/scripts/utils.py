"""Shared utilities for obsidian-rag scripts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from config import (
    CONNECTIONS_DIR,
    INDEX_FILE,
    LOG_FILE,
    QA_DIR,
    RAW_DIR,
    DAILY_DIR,
    STATE_FILE,
    WIKI_DIR,
)


# ── State management ───────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"ingested": {}, "query_count": 0, "last_lint": None, "total_cost": 0.0}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ── File hashing ───────────────────────────────────────────────────────────────

def file_hash(path: Path) -> str:
    """SHA-256 hash of a file (first 16 hex chars)."""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


# ── Slug / naming ──────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


# ── Wikilink helpers ───────────────────────────────────────────────────────────

def extract_wikilinks(content: str) -> list[str]:
    """Extract all [[wikilinks]] from markdown content, stripping display text."""
    raw = re.findall(r"\[\[([^\]]+)\]\]", content)
    # Strip display text: [[path|Display]] → path
    return [link.split("|")[0].strip() for link in raw]


def wiki_article_exists(link: str) -> bool:
    """Check if a wikilinked article exists on disk."""
    path = WIKI_DIR / f"{link}.md"
    return path.exists()


# ── File listing ───────────────────────────────────────────────────────────────

def list_raw_files() -> list[Path]:
    """List all unprocessed-candidate files in raw/."""
    if not RAW_DIR.exists():
        return []
    files = []
    for ext in ("*.md", "*.txt"):
        files.extend(RAW_DIR.glob(ext))
    return sorted(files)


def list_daily_logs() -> list[Path]:
    """List all daily log files in daily/."""
    if not DAILY_DIR.exists():
        return []
    return sorted(DAILY_DIR.glob("*.md"))


def list_wiki_articles() -> list[Path]:
    """List all wiki article files, excluding index and log files."""
    articles = []
    skip = {
        WIKI_DIR / "index.md",
        WIKI_DIR / "log.md",
    }
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file in skip:
            continue
        if md_file.name == "index.md":
            continue  # skip per-topic index.md files
        articles.append(md_file)
    return sorted(articles)


# ── Index helpers ──────────────────────────────────────────────────────────────

def read_wiki_index() -> str:
    """Read the merged topic navigator + article catalog."""
    if INDEX_FILE.exists():
        return INDEX_FILE.read_text(encoding="utf-8")
    return (
        "# Knowledge Base Index\n\n"
        "## Topics\n\n"
        "## Articles\n\n"
        "| Article | Summary | Source | Updated |\n"
        "|---------|---------|--------|---------|"
    )


def read_all_wiki_content() -> str:
    """Read index + all wiki articles into a single string for context."""
    parts = [f"## INDEX\n\n{read_wiki_index()}"]

    for article_path in list_wiki_articles():
        rel = article_path.relative_to(WIKI_DIR)
        content = article_path.read_text(encoding="utf-8")
        parts.append(f"## {rel}\n\n{content}")

    return "\n\n---\n\n".join(parts)


# ── Inbound link counting ──────────────────────────────────────────────────────

def count_inbound_links(target: str) -> int:
    """Count how many wiki articles link to a given target."""
    count = 0
    for article in list_wiki_articles():
        content = article.read_text(encoding="utf-8")
        if f"[[{target}]]" in content or f"[[{target}|" in content:
            count += 1
    return count


# ── Article helpers ────────────────────────────────────────────────────────────

def get_article_word_count(path: Path) -> int:
    """Count words in an article, excluding YAML frontmatter."""
    content = path.read_text(encoding="utf-8")
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:]
    return len(content.split())
