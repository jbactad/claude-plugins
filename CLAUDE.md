# claude-plugins

Claude Code plugin marketplace by jbactad. Hosts reusable plugins with skills, commands, agents, and hooks.

## Structure

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json       # Marketplace manifest — lists all plugins
├── automaker-skills/          # Plugin: Automaker project optimization skills
│   ├── .claude-plugin/plugin.json
│   └── skills/                # 6 skills, each with SKILL.md + references/
├── mission-control/           # Plugin: Autonomous AI orchestration engine
│   ├── .claude-plugin/plugin.json
│   ├── skills/                # 3 skills (orchestrate, playbook, mission-memory)
│   ├── commands/              # 4 commands (mission, checkpoint, debrief, playbook)
│   ├── agents/                # 5 agents (mission-planner, researcher, implementer, reviewer, retrospective)
│   ├── hooks/hooks.json       # 3 hooks (SessionStart, Stop, PreToolUse)
│   └── scripts/               # Hook scripts
└── mission-control-plan.md    # Implementation plan (reference only)
```

## Plugin Conventions

**Manifest**: Every plugin has `.claude-plugin/plugin.json` with `name`, `version`, `description`, `author`

**Skills**: `skills/{name}/SKILL.md` with YAML frontmatter + `references/` directory for supporting docs
- User-invocable skills: omit `disable-model-invocation` or set `user-invocable: true`
- Knowledge-only skills: set `user-invocable: false` (loaded as context by other skills)

**Commands**: `commands/{name}/SKILL.md` with `disable-model-invocation: true`

**Agents**: `agents/{name}.md` with YAML frontmatter — must include `name`, `description`, `tools`, `model`, `color`, `maxTurns`
- Read-only agents: add `disallowedTools: Edit, Write`
- Isolated agents: add `isolation: worktree`

**Hooks**: `hooks/hooks.json` — use `${CLAUDE_PLUGIN_ROOT}` for portable script paths

**Naming**: Lowercase kebab-case for all directory and file names. No plugin-name prefix on skill directories.

## Adding a Plugin

1. Create `{plugin-name}/.claude-plugin/plugin.json`
2. Add components (skills/, commands/, agents/, hooks/)
3. Register in root `.claude-plugin/marketplace.json` under `plugins[]`
4. Add to the table in `README.md`

## Marketplace Install

```
/plugin marketplace add github:jbactad/claude-plugins
/plugin add {plugin-name}
```
