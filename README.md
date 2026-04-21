# claude-plugins

A Claude Code plugin marketplace by [jbactad](https://github.com/jbactad).

## Plugins

| Plugin | Description |
|--------|-------------|
| [mission-control](./mission-control/) | Autonomous AI orchestration engine — decomposes goals into tasks, executes with specialized agents, learns from outcomes, and delivers results with minimal human intervention. |
| [essentials](./essentials/) | Essential skills and commands for everyday workflows — CLAUDE.md management, quality auditing, and session learning capture. |
| [obsidian-rag](./obsidian-rag/) | Obsidian vault knowledge base manager — compile sources into wiki articles, audit health, query with citations, auto-capture conversations to daily logs, and inject wiki context into every session. |

## Installation

Add this marketplace to Claude Code:

```
/plugin marketplace add jbactad/claude-plugins
```

Then install a plugin:

```
/plugin install mission-control@jbactad-claude-plugins
/plugin install essentials@jbactad-claude-plugins
/plugin install obsidian-rag@jbactad-claude-plugins
```

To install for a specific scope:

```
/plugin install mission-control@jbactad-claude-plugins --scope user      # personal (default)
/plugin install mission-control@jbactad-claude-plugins --scope project   # shared with team
/plugin install mission-control@jbactad-claude-plugins --scope local     # personal, gitignored
```

## License

MIT
