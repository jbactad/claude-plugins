# claude-plugins

Claude Code plugin marketplace by jbactad. Hosts reusable plugins with skills, commands, agents, and hooks.

## Structure

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json       # Marketplace manifest — lists all plugins
├── automaker-tools/          # Plugin: Automaker project optimization skills
│   ├── .claude-plugin/plugin.json
│   └── skills/                # 6 skills, each with SKILL.md + references/
├── mission-control/           # Plugin: Autonomous AI orchestration engine
│   ├── .claude-plugin/plugin.json
│   ├── skills/                # 3 skills (orchestrate, playbook, mission-memory)
│   ├── commands/              # 4 commands (mission, checkpoint, debrief, playbook)
│   ├── agents/                # 5 agents (mission-planner, researcher, implementer, reviewer, retrospective)
│   ├── hooks/hooks.json       # 3 hooks (SessionStart, Stop, PreToolUse)
│   └── scripts/               # Hook scripts
├── essentials/                # Plugin: Essential everyday workflows
│   ├── .claude-plugin/plugin.json
│   ├── skills/                # 1 skill (claude-md-improver)
│   └── commands/              # 1 command (revise-claude-md)
├── obsidian-rag/              # Plugin: Obsidian vault knowledge base manager
│   ├── .claude-plugin/plugin.json
│   └── skills/                # 4 skills (compile, audit, query, capture)
└── mission-control-plan.md    # Implementation plan (reference only)
```

## Development Guidelines

Always consult the available `plugin-dev` skills before developing or modifying any plugin component. If a skill is not available, use the `claude-code-guide` agent as a fallback.

- **Skills** → invoke `plugin-dev:skill-development`
- **Commands** → invoke `plugin-dev:command-development`
- **Agents** → invoke `plugin-dev:agent-development`
- **Hooks** → invoke `plugin-dev:hook-development`
- **Plugin structure / scaffolding** → invoke `plugin-dev:plugin-structure`
- **Plugin settings** → invoke `plugin-dev:plugin-settings`
- **MCP integration** → invoke `plugin-dev:mcp-integration`

## Plugin Conventions

**Manifest**: Every plugin has `.claude-plugin/plugin.json` with `name`, `version`, `description`, `author`

**Skills**: `skills/{name}/SKILL.md` with YAML frontmatter + `references/` directory for supporting docs
- Valid frontmatter: `name`, `description`, `argument-hint`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `context`, `agent`, `hooks`
- `tools` is NOT a valid field — use `allowed-tools` instead
- User-invocable skills: omit `disable-model-invocation` or set `user-invocable: true`
- Knowledge-only skills: set `user-invocable: false` (loaded as context by other skills)

**Commands**: `commands/{name}.md` with `disable-model-invocation: true`
- Same frontmatter fields as skills. Commands are flat `.md` files, not directories.

**Agents**: `agents/{name}.md` with YAML frontmatter — must include `name`, `description`, `tools`, `model`, `color`, `maxTurns`
- Read-only agents: add `disallowedTools: Edit, Write`
- Isolated agents: add `isolation: worktree`

**Hooks**: `hooks/hooks.json` — use `${CLAUDE_PLUGIN_ROOT}` for portable script paths

**Naming**: Lowercase kebab-case for all directory and file names. No plugin-name prefix on skill directories.

**Versioning**: Bump the plugin version in `.claude-plugin/plugin.json` whenever any plugin component is modified. Use semver patch increments (`0.1.0` → `0.1.1`) for fixes and improvements, minor increments (`0.1.0` → `0.2.0`) for new components.

## Adding a Plugin

1. Create `{plugin-name}/.claude-plugin/plugin.json`
2. Add components (skills/, commands/, agents/, hooks/)
3. Register in root `.claude-plugin/marketplace.json` under `plugins[]`
4. Add to the table in `README.md`

## Gotchas

- Always verify skill content against official Claude Code docs using the `claude-code-guide` agent — even official marketplace plugins can have inaccuracies
- Valid CLAUDE.md variants: `CLAUDE.md`, `CLAUDE.local.md` (auto-gitignored), `.claude/CLAUDE.md`, `~/.claude/CLAUDE.md`, `.claude/rules/*.md`. There is NO `.claude.md` or `.claude.local.md`
- CLAUDE.md supports `@path/to/file` import syntax (max 5 hops)
- Target under 200 lines per CLAUDE.md file — bloated files cause Claude to ignore instructions

## Marketplace Install

```
/plugin marketplace add jbactad/claude-plugins
/plugin install {plugin-name}@jbactad-claude-plugins
```
