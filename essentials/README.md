# essentials

Essential Claude Code skills and commands for everyday workflows.

## Skills

| Skill | Purpose |
|-------|---------|
| **claude-md-improver** | Audit, evaluate, and improve CLAUDE.md files across a codebase. Scores quality against a rubric, outputs a report, and proposes targeted updates. Also bootstraps CLAUDE.md for new projects. |

## Commands

| Command | Description |
|---------|-------------|
| `/revise-claude-md` | Capture learnings from the current session into CLAUDE.md. Reviews what context was missing and proposes concise additions. |

## Installation

Add the marketplace and install the plugin:

```
/plugin marketplace add jbactad/claude-plugins
/plugin install essentials@jbactad-claude-plugins
```

## Usage

Skills trigger automatically when you ask relevant questions. Examples:

- "Audit my CLAUDE.md files"
- "Check CLAUDE.md quality"
- "Set up CLAUDE.md for this project"
- "Grade my CLAUDE.md"

Use the command at the end of a session:

```
/revise-claude-md
```

## Prerequisites

- Claude Code CLI
