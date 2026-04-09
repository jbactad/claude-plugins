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
    if (cwd / "wiki" / "index.md").exists():
        return cwd

    raise RuntimeError(
        "Cannot resolve vault path. "
        "Set OBSIDIAN_VAULT_PATH env var or run from the vault directory."
    )


def _make_vault_dirs(vault: Path) -> dict:
    wiki = vault / "wiki"
    return dict(
        VAULT_DIR=vault,
        RAW_DIR=vault / "raw",
        DAILY_DIR=vault / "daily",
        WIKI_DIR=wiki,
        OUTPUT_DIR=vault / "output",
        CONNECTIONS_DIR=wiki / "connections",
        QA_DIR=wiki / "qa",
        INDEX_FILE=wiki / "index.md",
        LOG_FILE=wiki / "log.md",
    )


try:
    _vault = resolve_vault()
    _dirs = _make_vault_dirs(_vault)
    VAULT_DIR: Path = _dirs["VAULT_DIR"]
    RAW_DIR: Path = _dirs["RAW_DIR"]
    DAILY_DIR: Path = _dirs["DAILY_DIR"]
    WIKI_DIR: Path = _dirs["WIKI_DIR"]
    OUTPUT_DIR: Path = _dirs["OUTPUT_DIR"]
    CONNECTIONS_DIR: Path = _dirs["CONNECTIONS_DIR"]
    QA_DIR: Path = _dirs["QA_DIR"]
    INDEX_FILE: Path = _dirs["INDEX_FILE"]
    LOG_FILE: Path = _dirs["LOG_FILE"]
    VAULT_CONFIGURED = True
except RuntimeError:
    VAULT_CONFIGURED = False
    # Provide dummy paths so imports don't fail — callers must check VAULT_CONFIGURED
    VAULT_DIR = DAILY_DIR = RAW_DIR = WIKI_DIR = OUTPUT_DIR = Path("/dev/null")
    CONNECTIONS_DIR = QA_DIR = VAULT_DIR
    INDEX_FILE = LOG_FILE = VAULT_DIR

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
