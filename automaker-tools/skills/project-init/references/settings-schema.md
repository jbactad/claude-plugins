# Project Settings Schema

## Location

Project settings are stored at `{projectRoot}/.automaker/settings.json`.

All fields except `version` are optional — missing values fall back to global settings configured in Automaker's settings UI.

## Full Schema

```typescript
interface ProjectSettings {
  /** Schema version (current: 2) */
  version: number;

  // === Theme ===
  /** Project theme override (e.g., "dark", "nord", "github") */
  theme?: ThemeMode;
  /** UI font family override */
  fontFamilySans?: string;
  /** Code font family override */
  fontFamilyMono?: string;

  // === Worktree Management ===
  /** Use git worktrees for feature branches (default: true) */
  useWorktrees?: boolean;
  /** Current active worktree */
  currentWorktree?: { path: string | null; branch: string };
  /** List of worktrees in this project */
  worktrees?: WorktreeInfo[];

  // === Board Customization ===
  /** Board background settings */
  boardBackground?: BoardBackgroundSettings;
  /** Custom project icon (path relative to .automaker/) */
  customIconPath?: string;

  // === UI Visibility ===
  /** Show worktree panel row (default: true) */
  worktreePanelVisible?: boolean;
  /** Show init script indicator (default: true) */
  showInitScriptIndicator?: boolean;

  // === Worktree Behavior ===
  /** Default "delete branch" checkbox state when deleting worktree (default: false) */
  defaultDeleteBranchWithWorktree?: boolean;
  /** Auto-dismiss init script indicator after completion (default: true) */
  autoDismissInitScriptIndicator?: boolean;

  // === Agent Configuration ===
  /** Auto-load CLAUDE.md via Claude Agent SDK settingSources */
  autoLoadClaudeMd?: boolean;
  /** Custom subagent definitions (merged with global, project takes precedence) */
  customSubagents?: Record<string, AgentDefinition>;

  // === Auto Mode ===
  /** Enable auto mode for this project */
  automodeEnabled?: boolean;
  /** Max concurrent agents (overrides global maxConcurrency) */
  maxConcurrentAgents?: number;

  // === Commands ===
  /** Custom test command (auto-detected if not set) */
  testCommand?: string;
  /** Custom dev server command (auto-detected if not set) */
  devCommand?: string;

  // === Model Configuration ===
  /** Default model for new feature cards */
  defaultFeatureModel?: { model: string; thinkingLevel?: ThinkingLevel };
  /** Override phase models for this project */
  phaseModelOverrides?: Partial<PhaseModelConfig>;

  // === Terminal ===
  /** Terminal configuration overrides */
  terminalConfig?: TerminalConfig;

  // === Session ===
  /** Last selected chat session ID */
  lastSelectedSessionId?: string;
}
```

## Common Configuration Examples

### Minimal (Recommended Starting Point)

```json
{
  "version": 2,
  "useWorktrees": true,
  "autoLoadClaudeMd": true
}
```

### Node.js Project

```json
{
  "version": 2,
  "useWorktrees": true,
  "autoLoadClaudeMd": true,
  "testCommand": "npm test",
  "devCommand": "npm run dev"
}
```

### Python Project

```json
{
  "version": 2,
  "useWorktrees": true,
  "autoLoadClaudeMd": true,
  "testCommand": "pytest",
  "devCommand": "uvicorn main:app --reload"
}
```

### Monorepo with Custom Model

```json
{
  "version": 2,
  "useWorktrees": true,
  "autoLoadClaudeMd": true,
  "testCommand": "npm run test:all",
  "devCommand": "npm run dev",
  "maxConcurrentAgents": 3,
  "defaultFeatureModel": {
    "model": "claude-opus",
    "thinkingLevel": "medium"
  }
}
```

### Performance-Optimized (Faster, Lower Cost)

```json
{
  "version": 2,
  "useWorktrees": true,
  "autoLoadClaudeMd": true,
  "defaultFeatureModel": {
    "model": "claude-sonnet"
  },
  "maxConcurrentAgents": 2
}
```

## Key Settings Explained

### useWorktrees

When `true` (recommended), Automaker creates an isolated git worktree for each feature branch. This prevents features from interfering with each other and protects the main branch during agent execution.

When `false`, all features execute in the current working directory. Use this only for simple projects or when git worktrees are not suitable.

### autoLoadClaudeMd

When `true`, the Claude Agent SDK automatically loads `CLAUDE.md` from the project root via `settingSources`. If the project already has a root-level `CLAUDE.md`, avoid duplicating its content in `.automaker/context/CLAUDE.md`.

### testCommand / devCommand

If not specified, Automaker auto-detects these based on project structure (checks `package.json` scripts, `Makefile`, etc.). Set explicitly when auto-detection picks the wrong command.

### maxConcurrentAgents

Limits how many AI agents run in parallel during auto-mode batch processing. Higher values process features faster but consume more API tokens simultaneously. Default depends on global settings (typically 3-5).

### defaultFeatureModel

Sets the default Claude model for new feature cards. Options:
- `"claude-opus"` — Most capable, best for complex features
- `"claude-sonnet"` — Good balance of speed and quality
- `"claude-haiku"` — Fastest, best for simple features

### ThinkingLevel

Extended thinking intensity for Claude models:

| Level | Token Budget | Use Case |
|-------|-------------|----------|
| `"none"` | 0 | Simple tasks, fast execution |
| `"low"` | 1,024 | Light reasoning |
| `"medium"` | 10,000 | Moderate complexity |
| `"high"` | 20,000 | Complex features |
| `"ultrathink"` | 30,000+ | Maximum reasoning depth |

### PlanningMode

Controls how much planning the agent does before implementing:

| Mode | Behavior |
|------|----------|
| `"skip"` | No planning, agent starts implementing immediately |
| `"lite"` | Quick task decomposition, no approval needed |
| `"spec"` | Generate a specification with tasks, optionally require approval |
| `"full"` | Full phased planning with task tracking and approval workflow |
