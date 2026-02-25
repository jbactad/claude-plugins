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

Add the marketplace and install the plugin:

```
/plugin marketplace add jbactad/claude-plugins
/plugin install automaker-skills@jbactad-claude-plugins
```

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
