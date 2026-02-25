# Feature Schema Reference

## Core Feature Interface

```typescript
interface Feature {
  // === Identity ===
  id: string;                    // Unique identifier (UUID or custom)
  title?: string;                // Short display name for the board
  titleGenerating?: boolean;     // True while title is being AI-generated
  category: string;              // Board column (e.g., "backlog", "in_progress", "done")

  // === Description ===
  description: string;           // Full implementation instructions for the AI agent
  descriptionHistory?: DescriptionHistoryEntry[];  // Version history of description changes

  // === Execution Config ===
  model?: string;                // Claude model override (e.g., "claude-opus")
  thinkingLevel?: ThinkingLevel; // Extended thinking: "none"|"low"|"medium"|"high"|"ultrathink"
  reasoningEffort?: ReasoningEffort;  // For non-Claude models
  planningMode?: PlanningMode;   // Planning approach: "skip"|"lite"|"spec"|"full"
  requirePlanApproval?: boolean; // Require human review before execution

  // === Pipeline ===
  skipTests?: boolean;           // Skip test generation step
  excludedPipelineSteps?: string[];  // Array of pipeline step IDs to skip

  // === Dependencies ===
  dependencies?: string[];       // Feature IDs this depends on
  priority?: number;             // Sort order within category

  // === Status (managed by Automaker) ===
  status?: string;               // "pending"|"running"|"completed"|"failed"|"verified"
  passes?: boolean;              // Whether verification passed
  error?: string;                // Error message if failed
  summary?: string;              // Agent's implementation summary
  startedAt?: string;            // ISO timestamp when execution started

  // === Branch & Worktree ===
  branchName?: string;           // Git branch name (undefined = use current worktree)

  // === Attachments ===
  imagePaths?: Array<string | FeatureImagePath>;  // Screenshots, mockups
  textFilePaths?: FeatureTextFilePath[];           // Reference text files

  // === Planning State ===
  planSpec?: PlanSpec;           // Plan/spec state for spec/full modes

  // === Extensibility ===
  spec?: string;                 // Legacy spec field
  [key: string]: unknown;        // Catch-all for custom fields
}
```

## Supporting Types

### DescriptionHistoryEntry

Tracks description changes over time:

```typescript
interface DescriptionHistoryEntry {
  description: string;        // The description text at this point
  timestamp: string;          // ISO date string
  source: 'initial' | 'enhance' | 'edit';  // What triggered this version
  enhancementMode?: 'improve' | 'technical' | 'simplify' | 'acceptance' | 'ux-reviewer';
}
```

### PlanSpec

Tracks planning state for `spec` and `full` planning modes:

```typescript
interface PlanSpec {
  status: 'pending' | 'generating' | 'generated' | 'approved' | 'rejected';
  content?: string;           // The plan/spec markdown content
  version: number;            // Plan revision number
  generatedAt?: string;       // ISO timestamp
  approvedAt?: string;        // ISO timestamp (only if approved)
  reviewedByUser: boolean;    // Whether user has reviewed
  tasksCompleted?: number;    // Number of completed tasks
  tasksTotal?: number;        // Total tasks in the plan
  currentTaskId?: string;     // Currently executing task ID
  tasks?: ParsedTask[];       // Parsed task list from plan content
}
```

### ParsedTask

Individual tasks extracted from a plan:

```typescript
interface ParsedTask {
  id: string;                 // e.g., "T001"
  description: string;        // e.g., "Create user model"
  filePath?: string;          // e.g., "src/models/user.ts"
  phase?: string;             // e.g., "Phase 1: Foundation" (full mode only)
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
}
```

### FeatureImagePath

```typescript
interface FeatureImagePath {
  id: string;
  path: string;              // Path to image file
  filename: string;
  mimeType: string;          // e.g., "image/png"
}
```

### FeatureTextFilePath

```typescript
interface FeatureTextFilePath {
  id: string;
  path: string;
  filename: string;
  mimeType: string;
  content: string;           // Full text content of the file
}
```

## Feature Statuses

| Status | Meaning | Transitions To |
|--------|---------|---------------|
| `pending` | Waiting to be executed | `running` |
| `running` | AI agent is actively implementing | `completed`, `failed` |
| `completed` | Agent finished implementation | `verified`, `running` (re-run) |
| `failed` | Agent encountered an error | `running` (retry) |
| `verified` | Implementation verified (tests pass, manual review) | — |

## Feature Export/Import

Features can be exported and imported between projects:

```typescript
interface FeatureExport {
  version: string;            // Export format version
  feature: Feature;           // The feature data
  exportedAt: string;         // ISO date
  exportedBy?: string;        // Who/what exported
  metadata?: {
    projectName?: string;
    projectPath?: string;
    branch?: string;
  };
}

interface FeatureImport {
  data: Feature | FeatureExport;
  overwrite?: boolean;        // Replace existing feature with same ID
  preserveBranchInfo?: boolean;
  newId?: string;             // Assign new ID on import
  targetCategory?: string;    // Place in different category
}
```

## Minimal Valid Feature

```json
{
  "id": "auth-middleware",
  "category": "backlog",
  "description": "Add JWT authentication middleware to Express API routes."
}
```

## Fully Configured Feature

```json
{
  "id": "auth-middleware",
  "title": "JWT Auth Middleware",
  "category": "backlog",
  "description": "Add JWT authentication middleware to the Express API.\n\nCreate src/middleware/auth.ts that extracts Bearer tokens, verifies with jsonwebtoken, and attaches decoded payload to req.user.\n\nApply to all routes except /api/auth/login, /api/auth/register, and /api/health.\n\nFollow error handling pattern in src/middleware/error-handler.ts.\nAdd tests in src/middleware/__tests__/auth.test.ts.",
  "priority": 1,
  "dependencies": ["user-model", "error-handler"],
  "model": "claude-opus",
  "thinkingLevel": "medium",
  "planningMode": "spec",
  "requirePlanApproval": true,
  "skipTests": false,
  "imagePaths": [],
  "textFilePaths": []
}
```
