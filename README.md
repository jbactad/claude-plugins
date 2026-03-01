# claude-plugins

A Claude Code plugin marketplace by [jbactad](https://github.com/jbactad).

## Plugins

| Plugin | Description |
|--------|-------------|
| [automaker-skills](./automaker-skills/) | Skills for working with Automaker projects — context optimization, feature management, memory, specs, worktrees, and project initialization. |
| [mission-control](./mission-control/) | Autonomous AI orchestration engine — decomposes goals into tasks, executes with specialized agents, learns from outcomes, and delivers results with minimal human intervention. |
| [essentials](./essentials/) | Essential skills and commands for everyday workflows — CLAUDE.md management, quality auditing, and session learning capture. |

## Installation

Add this marketplace to Claude Code:

```
/plugin marketplace add jbactad/claude-plugins
```

Then install a plugin:

```
/plugin install automaker-skills@jbactad-claude-plugins
/plugin install mission-control@jbactad-claude-plugins
```

To install for a specific scope:

```
/plugin install automaker-skills@jbactad-claude-plugins --scope user      # personal (default)
/plugin install automaker-skills@jbactad-claude-plugins --scope project   # shared with team
/plugin install automaker-skills@jbactad-claude-plugins --scope local     # personal, gitignored
```

## License

MIT
