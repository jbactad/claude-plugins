# essentials

Essential Claude Code skills and commands for everyday workflows.

## Skills

| Skill | Purpose |
|-------|---------|
| **claude-md-optimizer** | Optimize CLAUDE.md files using a 4-tier architecture (CLAUDE.md, rules, examples, skills). Analyzes existing files, classifies content into tiers, and restructures for token efficiency and sub-agent convention adherence. |

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

- "Optimize my CLAUDE.md"
- "Improve CLAUDE.md for sub-agent adherence"
- "Set up CLAUDE.md for this project"
- "Reduce CLAUDE.md token usage"

Use the command at the end of a session:

```
/revise-claude-md
```

## Prerequisites

- Claude Code CLI
