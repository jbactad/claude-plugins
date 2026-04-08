---
description: Rules for developing plugin components
paths:
  - "**/.claude-plugin/**"
  - "**/skills/**"
  - "**/commands/**"
  - "**/agents/**"
  - "**/hooks/**"
---

## Skill Bundled Resources

- Reference files: use markdown links — `see [references/file.md](references/file.md)`, not backtick notation
- Scripts: use `${CLAUDE_SKILL_DIR}` — e.g., `${CLAUDE_SKILL_DIR}/scripts/helper.py` (ensure scripts have shebang + execute permission)
- `${CLAUDE_PLUGIN_ROOT}` is NOT available in SKILL.md — only in hooks, MCP servers, and hook scripts
