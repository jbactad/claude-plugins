"""Path constants and configuration for obsidian-rag scripts."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path


# ── Plugin directory ───────────────────────────────────────────────────────────
SCRIPTS_DIR = Path(__file__).resolve().parent
PLUGIN_DIR = SCRIPTS_DIR.parent


# ── Vault resolution ───────────────────────────────────────────────────────────

def resolve_vault() -> Path:
    """Resolve vault root from OBSIDIAN_VAULT_PATH env var or cwd."""
    env_path = os.environ.get("OBSIDIAN_VAULT_PATH")
    if env_path:
        return Path(env_path).resolve()

    # Check if cwd looks like a vault
    cwd = Path.cwd()
    if (cwd / "wiki" / "master-index.md").exists():
        return cwd

    raise RuntimeError(
        "Cannot resolve vault path. "
        "Set OBSIDIAN_VAULT_PATH env var or run from the vault directory."
    )


VAULT_DIR = resolve_vault()


# ── Vault directories ──────────────────────────────────────────────────────────
RAW_DIR = VAULT_DIR / "raw"
DAILY_DIR = VAULT_DIR / "daily"
WIKI_DIR = VAULT_DIR / "wiki"
OUTPUT_DIR = VAULT_DIR / "output"

# ── Wiki structure ─────────────────────────────────────────────────────────────
CONNECTIONS_DIR = WIKI_DIR / "connections"    # cross-cutting insight articles
QA_DIR = WIKI_DIR / "qa"                     # filed query answers

MASTER_INDEX_FILE = WIKI_DIR / "master-index.md"   # topic list (skill-compatible)
INDEX_FILE = WIKI_DIR / "index.md"                   # table catalog (used by session-start)
LOG_FILE = WIKI_DIR / "log.md"                       # build log

# ── References ─────────────────────────────────────────────────────────────────
CONVENTIONS_FILE = PLUGIN_DIR / "skills" / "compile" / "references" / "vault-conventions.md"

# ── Plugin state (stored alongside scripts, not in the vault) ──────────────────
STATE_FILE = SCRIPTS_DIR / "state.json"
LAST_FLUSH_FILE = SCRIPTS_DIR / "last-flush.json"


# ── Time helpers ───────────────────────────────────────────────────────────────

def now_iso() -> str:
    """Current datetime in ISO 8601 format."""
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def today_iso() -> str:
    """Current date in YYYY-MM-DD format."""
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
