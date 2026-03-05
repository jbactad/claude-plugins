# Complete .automaker/ Directory Structure

## Full Directory Tree

```
.automaker/
├── context/                        # AI agent context files
│   ├── CLAUDE.md                   # Primary project instructions (tech stack, conventions, rules)
│   ├── context-metadata.json       # Descriptions for each context file
│   ├── CODE_QUALITY.md             # (optional) Linting, formatting, type strictness rules
│   ├── API_CONVENTIONS.md          # (optional) Route patterns, response shapes, error codes
│   ├── TESTING.md                  # (optional) Test framework, fixtures, coverage rules
│   ├── SECURITY.md                 # (optional) Auth patterns, input validation
│   └── ARCHITECTURE.md             # (optional) Module boundaries, dependency rules
│
├── features/                       # Feature JSON files (Kanban board data)
│   └── {featureId}/                # Per-feature directory
│       ├── feature.json            # Feature definition (title, description, status, etc.)
│       ├── agent-output.md         # Agent's implementation summary
│       └── images/                 # Feature-specific screenshots/mockups
│           └── {imageId}.{ext}     # Referenced in feature.json imagePaths
│
├── memory/                         # Agent learning files
│   ├── _index.md                   # Project overview (excluded from agent loading — documentation only)
│   ├── api-patterns.md             # API conventions learned from implementations
│   ├── database-patterns.md        # Database access patterns
│   ├── testing-patterns.md         # Test writing patterns
│   └── debugging-notes.md          # Common debugging issues and solutions
│
├── worktrees/                      # Runtime worktree metadata (gitignored)
│   └── {branchName}/
│       └── worktree.json           # Worktree status, init script result
│
├── ideation/                       # Ideation system data (gitignored)
│   ├── ideas/                      # Idea entries
│   │   └── {ideaId}/
│   │       ├── idea.json           # Idea metadata
│   │       └── attachments/        # Idea images/files
│   ├── sessions/                   # Brainstorming conversation history
│   │   └── {sessionId}.json
│   ├── drafts/                     # Unsaved conversation drafts
│   └── analysis.json               # Project analysis for ideation
│
├── validations/                    # GitHub issue validation results
│   └── {issueNumber}/
│       └── validation.json         # Verdict, analysis, metadata
│
├── events/                         # Event history (gitignored)
│   ├── index.json                  # Event index for quick listing
│   └── {eventId}.json              # Individual event records
│
├── board/                          # Board customization (gitignored)
│   └── (background images, etc.)
│
├── images/                         # Project-level shared images (gitignored)
│
├── categories.json                 # Board column definitions (JSON array of strings)
├── settings.json                   # Project-specific settings (overrides global)
├── app_spec.txt                    # Structured XML specification (parsed by Automaker)
├── spec.md                         # Markdown specification (supplementary)
├── analysis.json                   # Project structure analysis cache
├── worktree-init.sh                # Worktree bootstrap script (runs on worktree creation)
├── execution-state.json            # Auto-mode execution state for recovery (gitignored)
├── active-branches.json            # Active git branch tracking (gitignored)
└── notifications.json              # Project notification queue (gitignored)
```

## File Categories

### Must Commit to Git

These files should be tracked in version control — they represent shared project configuration:

| File | Purpose |
|------|---------|
| `context/CLAUDE.md` | AI agent instructions shared across team |
| `context/context-metadata.json` | File descriptions for context loading |
| `context/*.md` (other) | Additional context files |
| `features/` (entire tree) | Feature definitions are project data |
| `categories.json` | Board column structure |
| `settings.json` | Project configuration |
| `app_spec.txt` | Structured project specification |
| `spec.md` | Supplementary specification |
| `worktree-init.sh` | Worktree bootstrap script |
| `memory/` (entire tree) | Agent learnings (team knowledge base) |

### Should Gitignore

These files are runtime-generated, machine-specific, or ephemeral:

| File/Directory | Reason |
|----------------|--------|
| `worktrees/` | Runtime worktree metadata, machine-specific paths |
| `execution-state.json` | Auto-mode recovery state, session-specific |
| `active-branches.json` | Branch tracking, machine-specific |
| `notifications.json` | Transient notification queue |
| `events/` | Event history for debugging, can be large |
| `ideation/` | Brainstorming sessions, personal to user |
| `board/` | Board UI customization, personal preference |
| `images/` | Project-level images, often large binaries |
| `analysis.json` | Cached project analysis, regeneratable |

### Created by Automaker at Runtime

These files are created automatically during normal Automaker operation:

| File | Created When |
|------|-------------|
| `features/{id}/feature.json` | User creates a feature card |
| `features/{id}/agent-output.md` | Agent completes feature implementation |
| `worktrees/{branch}/worktree.json` | Git worktree is created for a feature |
| `execution-state.json` | Auto-mode starts processing features |
| `active-branches.json` | Branch tracking updates |
| `notifications.json` | Feature status changes |
| `events/` | Any operation that emits events |
| `analysis.json` | Project analysis is triggered |

### Created by User/Skill

These files should be created manually or via skills for best results:

| File | Recommended Creation Method |
|------|----------------------------|
| `context/CLAUDE.md` | `automaker-context-optimizer` skill |
| `context/context-metadata.json` | `automaker-context-optimizer` skill |
| `worktree-init.sh` | `automaker-worktree-init` skill |
| `app_spec.txt` | Automaker spec editor UI or `automaker-spec-optimizer` skill |
| `spec.md` | `automaker-spec-optimizer` skill |
| `memory/*.md` | `automaker-memory-manager` skill |
| `settings.json` | `automaker-project-init` skill or Automaker settings UI |
| `categories.json` | `automaker-project-init` skill |

## Recommended .gitignore Entries

```gitignore
# Automaker - runtime and machine-specific files
.automaker/worktrees/
.automaker/execution-state.json
.automaker/active-branches.json
.automaker/notifications.json
.automaker/events/
.automaker/ideation/
.automaker/board/
.automaker/images/
.automaker/analysis.json
```
