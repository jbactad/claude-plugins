# SpecOutput Schema Reference

## Complete TypeScript Interface

```typescript
interface SpecOutput {
  project_name: string;
  overview: string;
  technology_stack: string[];
  core_capabilities: string[];
  implemented_features: Array<{
    name: string;
    description: string;
    file_locations?: string[];
  }>;
  additional_requirements?: string[];
  development_guidelines?: string[];
  implementation_roadmap?: Array<{
    phase: string;
    status: 'completed' | 'in_progress' | 'pending';
    description: string;
  }>;
}
```

**Required fields:** `project_name`, `overview`, `technology_stack`, `core_capabilities`, `implemented_features`

**Optional fields:** `additional_requirements`, `development_guidelines`, `implementation_roadmap`

The schema enforces `additionalProperties: false`, so no extra fields are permitted.

---

## Field-by-Field Guide

### project_name

**Type:** `string` (required)

The canonical name of the project. Use the exact name from `package.json`, the repository, or the primary brand name.

**Good:**
```
"Automaker"
```

**Bad:**
```
"My Cool Project v2.0 (WIP)"
```

Avoid version numbers, status indicators, or decorative text. The name serves as an identifier, not a tagline.

---

### overview

**Type:** `string` (required)

A comprehensive description of the project's purpose, target users, and primary goals. Aim for 3-5 sentences.

**Good:**
```
"Automaker is an autonomous AI development studio that manages software features through a Kanban-based workflow. AI agents powered by Claude implement features in isolated git worktrees, ensuring the main branch remains stable. The system supports automatic feature generation from project specifications, parallel agent execution, and automated verification."
```

**Bad:**
```
"A really cool app that does a lot of things with AI."
```

The overview sets the context for every capability and feature that follows. Vague overviews produce vague features.

---

### technology_stack

**Type:** `string[]` (required)

Each entry is a single string describing one technology, framework, or tool. Include versions when known.

**Good:**
```json
[
  "React 19 - UI framework",
  "Vite 7 - Build tool and dev server",
  "Express 5 - HTTP server framework",
  "TypeScript 5.9 - Primary language",
  "Tailwind CSS 4 - Utility-first styling",
  "Zustand 5 - State management",
  "Playwright - E2E testing",
  "Vitest - Unit testing"
]
```

**Bad:**
```json
[
  "JavaScript",
  "Some CSS framework",
  "Backend stuff"
]
```

Specificity matters. When agents see "React 19" they use React 19 APIs. When they see "JavaScript" they have no framework context and may generate vanilla JS or pick an arbitrary framework.

---

### core_capabilities

**Type:** `string[]` (required)

Each entry is a sentence or short paragraph describing a major functional area that the project provides or needs to provide.

**Good:**
```json
[
  "Feature board with drag-and-drop Kanban columns supporting backlog, in-progress, review, and completed states. Each card displays title, priority badge, and assigned agent status.",
  "AI agent orchestration that spawns Claude-powered agents in isolated git worktrees. Agents execute feature implementation autonomously with real-time progress streaming via WebSocket.",
  "Project specification management with structured XML format, AI-powered generation from project overviews, and automatic sync of completed features back to the spec."
]
```

**Bad:**
```json
[
  "Board",
  "AI stuff",
  "Manage specs and things"
]
```

Each capability should be self-contained enough that a feature generation model can decompose it into 2-5 individual feature cards without needing additional context.

---

### implemented_features

**Type:** `Array<{ name: string; description: string; file_locations?: string[] }>` (required)

Features that have already been built and verified. This section is auto-populated by `syncFeatureToAppSpec()` when features reach `verified` or `completed` status, but manual curation is encouraged.

**Good:**
```json
[
  {
    "name": "WebSocket Event Streaming",
    "description": "Real-time event streaming from server to UI via WebSocket. Supports agent progress, terminal output, and feature status change events.",
    "file_locations": [
      "apps/server/src/lib/events.ts",
      "apps/ui/src/hooks/use-websocket.ts"
    ]
  },
  {
    "name": "Git Worktree Isolation",
    "description": "Each AI agent operates in a dedicated git worktree, preventing concurrent agents from conflicting on the main branch.",
    "file_locations": [
      "libs/git-utils/src/worktree.ts"
    ]
  }
]
```

**Bad:**
```json
[
  {
    "name": "Feature 1",
    "description": "Did some work on the thing"
  }
]
```

Include `file_locations` whenever possible. This anchors the feature to specific code and helps agents understand project structure. Descriptions should state what was built, not what was planned.

---

### additional_requirements (optional)

**Type:** `string[]`

Non-functional requirements, constraints, and cross-cutting concerns.

**Good:**
```json
[
  "All API endpoints must return responses within 500ms for non-AI operations",
  "Support Chromium-based browsers and Safari 17+",
  "Maintain WCAG 2.1 AA accessibility compliance for all interactive elements",
  "All file operations must use the secure-fs wrapper to enforce path restrictions"
]
```

**Bad:**
```json
[
  "Be fast",
  "Work on browsers",
  "Be accessible"
]
```

Quantify where possible. "Be fast" gives agents no target; "respond within 500ms" gives them a testable criterion.

---

### development_guidelines (optional)

**Type:** `string[]`

Coding standards, architectural patterns, and conventions that agents must follow.

**Good:**
```json
[
  "Import shared packages using @automaker/* aliases, never relative paths across package boundaries",
  "Create loggers via createLogger('ModuleName') from @automaker/utils for consistent log formatting",
  "Follow the route handler factory pattern: export a createXxxHandler(deps) function that returns an Express handler",
  "Use atomic JSON writes via atomicWriteJson() for all feature.json file operations to prevent corruption"
]
```

**Bad:**
```json
[
  "Write clean code",
  "Follow best practices",
  "Use TypeScript"
]
```

Reference specific functions, modules, and patterns from the codebase. Agents follow concrete instructions; they interpret vague ones unpredictably.

---

### implementation_roadmap (optional)

**Type:** `Array<{ phase: string; status: 'completed' | 'in_progress' | 'pending'; description: string }>`

Phased delivery plan with current status tracking.

**Good:**
```json
[
  {
    "phase": "Core Infrastructure",
    "status": "completed",
    "description": "Express server, WebSocket events, secure file system, git worktree management, and feature data model."
  },
  {
    "phase": "AI Agent Integration",
    "status": "in_progress",
    "description": "Claude Agent SDK integration, agent spawning in worktrees, real-time progress streaming, and auto-mode orchestration."
  },
  {
    "phase": "Advanced Workflows",
    "status": "pending",
    "description": "Feature dependency resolution, parallel agent execution, automated verification pipelines, and spec-to-feature feedback loops."
  }
]
```

**Bad:**
```json
[
  {
    "phase": "Phase 1",
    "status": "pending",
    "description": "Do stuff"
  }
]
```

Use descriptive phase names that correspond to capability groups. The sync endpoint updates statuses automatically based on completed features matching phase names.

---

## XML Representation

Automaker stores the spec as XML in `app_spec.txt`. The `specToXml()` function converts `SpecOutput` to this format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project_specification>
  <project_name>Project Name</project_name>

  <overview>
    Project overview text here.
  </overview>

  <technology_stack>
    <technology>React 19 - UI framework</technology>
    <technology>Express 5 - HTTP server</technology>
  </technology_stack>

  <core_capabilities>
    <capability>Description of capability 1.</capability>
    <capability>Description of capability 2.</capability>
  </core_capabilities>

  <implemented_features>
    <feature>
      <name>Feature Name</name>
      <description>What was built.</description>
      <file_locations>
        <location>src/path/to/file.ts</location>
      </file_locations>
    </feature>
  </implemented_features>

  <additional_requirements>
    <requirement>Requirement text.</requirement>
  </additional_requirements>

  <development_guidelines>
    <guideline>Guideline text.</guideline>
  </development_guidelines>

  <implementation_roadmap>
    <phase>
      <name>Phase Name</name>
      <status>in_progress</status>
      <description>Phase description.</description>
    </phase>
  </implementation_roadmap>
</project_specification>
```

Special characters must be XML-escaped: `<` as `&lt;`, `>` as `&gt;`, `&` as `&amp;`, `"` as `&quot;`, `'` as `&apos;`.

---

## JSON Schema (for Structured Output)

The JSON schema used with Claude's structured output feature:

```json
{
  "type": "object",
  "properties": {
    "project_name": {
      "type": "string",
      "description": "The name of the project"
    },
    "overview": {
      "type": "string",
      "description": "A comprehensive description of what the project does, its purpose, and key goals"
    },
    "technology_stack": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of all technologies, frameworks, libraries, and tools used"
    },
    "core_capabilities": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of main features and capabilities the project provides"
    },
    "implemented_features": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "description": { "type": "string" },
          "file_locations": {
            "type": "array",
            "items": { "type": "string" }
          }
        },
        "required": ["name", "description"]
      },
      "description": "Features that have been implemented based on code analysis"
    },
    "additional_requirements": {
      "type": "array",
      "items": { "type": "string" }
    },
    "development_guidelines": {
      "type": "array",
      "items": { "type": "string" }
    },
    "implementation_roadmap": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "phase": { "type": "string" },
          "status": {
            "type": "string",
            "enum": ["completed", "in_progress", "pending"]
          },
          "description": { "type": "string" }
        },
        "required": ["phase", "status", "description"]
      }
    }
  },
  "required": ["project_name", "overview", "technology_stack", "core_capabilities", "implemented_features"],
  "additionalProperties": false
}
```
