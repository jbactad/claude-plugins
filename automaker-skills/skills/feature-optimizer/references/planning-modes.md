# Planning Modes Guide

## Overview

Planning modes control how much upfront planning the AI agent does before implementing a feature. The right mode depends on feature complexity, risk, and desired control.

## Mode Comparison

### skip — No Planning

```
Description → Implement → Done
```

- Agent reads the description and starts coding immediately
- No task decomposition, no spec generation
- Fastest execution, lowest token usage
- Best for: bug fixes, typos, config changes, one-file modifications

**When to use skip:**
- Feature touches 1 file
- Description is under 50 words
- Implementation path is obvious
- Low risk of breaking existing functionality

**Example feature for skip:**
```json
{
  "description": "Fix the typo in src/components/Header.tsx: change 'Welcom' to 'Welcome' on line 42.",
  "planningMode": "skip"
}
```

### lite — Quick Decomposition

```
Description → Quick task list → Implement all tasks → Done
```

- Agent creates a brief task list (not a full spec)
- No approval step — proceeds directly to implementation
- Moderate token usage overhead
- Best for: small features, 2-3 file changes, well-defined scope

**When to use lite:**
- Feature touches 2-3 files
- Description is 50-150 words
- Implementation has a few clear steps
- Changes are straightforward additions

**Example feature for lite:**
```json
{
  "description": "Add a 'Copy to clipboard' button to the CodeBlock component.\n\nModify src/components/CodeBlock.tsx to add a copy button in the top-right corner.\nUse the existing Button component from src/components/ui/Button.tsx.\nAdd a toast notification on successful copy using the existing toast utility.",
  "planningMode": "lite"
}
```

### spec — Specification with Tasks

```
Description → Generate spec → [Optional: User approval] → Execute tasks → Done
```

- Agent generates a detailed specification with numbered tasks
- Each task has a description and optionally a file path
- Tracks task completion progress (tasksCompleted/tasksTotal)
- Set `requirePlanApproval: true` to review before execution
- Best for: medium features, multi-file changes, new components

**When to use spec:**
- Feature touches 4+ files
- Description is 150-300 words
- Implementation requires new patterns or components
- You want visibility into the agent's plan

**Spec mode task tracking:**
```
T001: Create data model        [completed]
T002: Add API endpoint         [in_progress]
T003: Create UI component      [pending]
T004: Add routing              [pending]
T005: Write tests              [pending]
```

**Example feature for spec:**
```json
{
  "description": "Add user profile page with avatar upload, name editing, and email change functionality.\n\nCreate a new route at /profile.\nBuild ProfilePage component with three sections.\nAdd avatar upload using existing FileUpload component.\nConnect to existing user API endpoints.\nAdd form validation using Zod schemas.",
  "planningMode": "spec",
  "requirePlanApproval": true
}
```

### full — Phased Planning

```
Description → Full phased plan → User approval → Execute phases → Done
```

- Agent generates a comprehensive multi-phase implementation plan
- Phases group related tasks (e.g., "Phase 1: Foundation", "Phase 2: API", "Phase 3: UI")
- Full task tracking with phase awareness
- Always recommended to use with `requirePlanApproval: true`
- Highest token usage but most structured execution
- Best for: complex features, architectural changes, large refactors

**When to use full:**
- Feature is a major new capability
- Description is 300+ words
- Implementation spans many files and concerns
- Multiple phases needed (data layer → API → UI)
- High risk or high complexity

**Full mode phase tracking:**
```
Phase 1: Data Foundation
  T001: Create database schema  [completed]
  T002: Generate migrations     [completed]

Phase 2: API Layer
  T003: Add CRUD endpoints      [in_progress]
  T004: Add validation          [pending]

Phase 3: Frontend
  T005: Create list view        [pending]
  T006: Create detail view      [pending]
  T007: Add routing             [pending]
```

**Example feature for full:**
```json
{
  "description": "Implement a complete notification system with real-time delivery.\n\nPhase 1 - Data: Create notification model with types (info, warning, error, success), read/unread status, and user association. Add database migration.\n\nPhase 2 - Backend: Create notification service with CRUD operations, WebSocket broadcasting to connected clients, and notification preferences per user.\n\nPhase 3 - Frontend: Add notification bell icon in header with unread count badge, dropdown panel showing recent notifications, mark-as-read on click, and 'Mark all read' button.\n\nPhase 4 - Polish: Add notification sound toggle, browser push notification support (optional), and notification grouping by type.",
  "planningMode": "full",
  "requirePlanApproval": true,
  "model": "claude-opus",
  "thinkingLevel": "high"
}
```

## Decision Flowchart

```
Is the feature a simple fix (typo, config, one-line change)?
  └─ YES → skip
  └─ NO ↓

Does the feature touch 3 or fewer files?
  └─ YES → lite
  └─ NO ↓

Does the feature introduce new patterns or components?
  └─ NO → spec
  └─ YES ↓

Is this an architectural change or major new capability?
  └─ NO → spec (with requirePlanApproval: true)
  └─ YES → full (with requirePlanApproval: true)
```

## Token Usage Estimates

Approximate additional tokens consumed by planning overhead:

| Mode | Planning Overhead | Total for Medium Feature |
|------|------------------|-------------------------|
| `skip` | ~0 tokens | ~5,000-15,000 |
| `lite` | ~500-1,000 tokens | ~6,000-18,000 |
| `spec` | ~2,000-5,000 tokens | ~10,000-30,000 |
| `full` | ~5,000-15,000 tokens | ~20,000-60,000 |

These are rough estimates — actual usage depends on feature complexity, model choice, and thinking level.

## Combining with Thinking Levels

Planning modes and thinking levels are complementary:

| Combination | Use Case |
|-------------|----------|
| `skip` + `none` | Trivial fixes, maximum speed |
| `lite` + `low` | Simple features, fast turnaround |
| `spec` + `medium` | Standard features, balanced |
| `full` + `high` | Complex features, maximum quality |
| `full` + `ultrathink` | Architecture-level changes, mission-critical |

Avoid wasteful combinations:
- `skip` + `ultrathink` — Planning would capture the thinking benefit better
- `full` + `none` — Full planning needs reasoning to produce quality plans

## Plan Approval Workflow

When `requirePlanApproval: true`:

1. Agent generates plan → `planSpec.status = "generated"`
2. Plan appears in Automaker UI for review
3. User reviews tasks, file paths, and approach
4. User approves → `planSpec.status = "approved"` → agent proceeds
5. User rejects → `planSpec.status = "rejected"` → agent generates revised plan

This checkpoint prevents wasted execution when the agent's approach doesn't match expectations.
