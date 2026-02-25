# automaker-skills

Claude Code plugin providing specialized skills for working with [Automaker](https://github.com/AutoMaker-Org/automaker) projects.

## Skills

| Skill | Purpose |
|-------|---------|
| **automaker-project-init** | Bootstrap `.automaker/` directory structure and configuration for any codebase |
| **automaker-context-optimizer** | Create and optimize `.automaker/context/` files (CLAUDE.md, context-metadata.json) |
| **automaker-feature-optimizer** | Create and optimize feature cards for better AI agent execution |
| **automaker-memory-manager** | Manage `.automaker/memory/` files — create, update, and organize agent learnings |
| **automaker-spec-optimizer** | Optimize `app_spec.txt` and `spec.md` for better AI comprehension |
| **automaker-worktree-init** | Create optimized `.automaker/worktree-init.sh` bootstrap scripts |

## Installation

Use the `--plugin-dir` flag to load the plugin:

```bash
claude --plugin-dir /path/to/automaker-skills
```

Or add it to your Claude Code settings for persistent use.

## Usage

Each skill triggers automatically when you ask relevant questions. Examples:

- "Initialize Automaker for this project"
- "Create context files for Automaker"
- "Create a feature to add user authentication"
- "Add a learning about our database patterns"
- "Optimize the project spec"
- "Create a worktree init script"

## Prerequisites

- Claude Code CLI
- An existing codebase (skills analyze your project to generate Automaker configuration)
