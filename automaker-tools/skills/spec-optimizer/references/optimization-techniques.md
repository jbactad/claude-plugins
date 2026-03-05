# Spec Optimization Techniques

## Before/After Examples

### Example 1: Vague Overview to Precise Overview

**Before (poor):**
```xml
<overview>
  An app for managing tasks with AI.
</overview>
```

**After (optimized):**
```xml
<overview>
  TaskFlow is a project management platform that uses AI-powered agents to automatically implement, test, and deploy software features. Product managers define features through a Kanban board interface, and autonomous Claude-powered agents execute the implementation in isolated git worktrees. The system targets engineering teams of 5-50 developers who want to accelerate feature delivery while maintaining code quality through automated verification.
</overview>
```

**Why it matters:** The feature generation model uses the overview to understand scope and target audience. A vague overview produces generic features; a precise one produces features tailored to the actual use case.

---

### Example 2: Weak Capabilities to Strong Capabilities

**Before (poor):**
```xml
<core_capabilities>
  <capability>User management</capability>
  <capability>Dashboard</capability>
  <capability>Reports</capability>
  <capability>Settings</capability>
</core_capabilities>
```

**After (optimized):**
```xml
<core_capabilities>
  <capability>User authentication and authorization with email/password login, OAuth2 social providers (Google, GitHub), role-based access control (admin, editor, viewer), and session management via HTTP-only JWT cookies.</capability>
  <capability>Interactive dashboard displaying real-time project metrics: feature velocity chart, agent utilization heatmap, build success rate trend, and active worktree count. All widgets support date range filtering and CSV export.</capability>
  <capability>Automated report generation producing weekly sprint summaries, feature completion forecasts, and code quality scorecards. Reports render as PDF via Puppeteer and distribute via email through SendGrid integration.</capability>
  <capability>Project settings panel with theme selection (light/dark/system), notification preferences per event type, API key management with masked display, and model configuration for each AI phase (spec generation, feature generation, implementation).</capability>
</core_capabilities>
```

**Why it matters:** Each optimized capability contains enough detail for the feature generation model to produce 3-5 distinct features. "User management" could mean anything; the optimized version specifies authentication methods, authorization model, and session strategy.

---

### Example 3: Missing Tech Stack to Complete Tech Stack

**Before (poor):**
```xml
<technology_stack>
  <technology>React</technology>
  <technology>Node</technology>
  <technology>Database</technology>
</technology_stack>
```

**After (optimized):**
```xml
<technology_stack>
  <technology>React 19 - UI component framework with Server Components support</technology>
  <technology>TypeScript 5.9 - Primary language for frontend and backend</technology>
  <technology>Vite 7 - Build tool, dev server, and HMR</technology>
  <technology>Express 5 - HTTP server with async middleware support</technology>
  <technology>PostgreSQL 16 - Primary relational database</technology>
  <technology>Drizzle ORM 0.38 - Type-safe SQL query builder and migrations</technology>
  <technology>Tailwind CSS 4 - Utility-first CSS framework</technology>
  <technology>Zustand 5 - Lightweight state management</technology>
  <technology>TanStack Router - Type-safe file-based routing</technology>
  <technology>Playwright 1.49 - E2E browser testing</technology>
  <technology>Vitest 4.0 - Unit and integration testing</technology>
  <technology>ws 8 - WebSocket server for real-time events</technology>
</technology_stack>
```

**Why it matters:** Agents choose APIs based on the tech stack. Without "Drizzle ORM," an agent might use raw SQL or pick Prisma. Without "Zustand," it might create a React Context or import Redux.

---

### Example 4: Stale Implemented Features to Curated Ones

**Before (stale):**
```xml
<implemented_features>
  <feature>
    <name>Basic UI</name>
    <description>Added some UI components</description>
  </feature>
  <feature>
    <name>Basic UI Setup</name>
    <description>Set up the basic UI framework</description>
  </feature>
  <feature>
    <name>Login Page</name>
    <description>Will add login functionality</description>
  </feature>
</implemented_features>
```

**After (curated):**
```xml
<implemented_features>
  <feature>
    <name>Component Library Foundation</name>
    <description>Established shadcn/ui component library with Button, Input, Card, Dialog, and DropdownMenu primitives. All components support dark mode and follow the design token system in tailwind.config.ts.</description>
    <file_locations>
      <location>src/components/ui/</location>
      <location>tailwind.config.ts</location>
    </file_locations>
  </feature>
  <feature>
    <name>Authentication Flow</name>
    <description>Implemented email/password authentication with bcrypt hashing, JWT session tokens stored in HTTP-only cookies, and a login/register page with form validation.</description>
    <file_locations>
      <location>src/routes/auth/login.tsx</location>
      <location>src/routes/auth/register.tsx</location>
      <location>src/server/auth.ts</location>
    </file_locations>
  </feature>
</implemented_features>
```

**Issues fixed:**
- Merged "Basic UI" and "Basic UI Setup" (semantic duplicates)
- Changed "Login Page" description from future tense ("will add") to past tense (what was actually built)
- Added `file_locations` to anchor features to code
- Used descriptive names instead of generic ones

---

## Common Anti-Patterns

### 1. The Wishlist Spec

**Problem:** Mixing aspirational features with actual capabilities.

```xml
<core_capabilities>
  <capability>AI-powered everything</capability>
  <capability>Blockchain integration</capability>
  <capability>AR/VR support</capability>
  <capability>Quantum computing optimization</capability>
</core_capabilities>
```

**Fix:** Only include capabilities that are planned for the current development cycle. Move future ideas to a separate planning document outside the spec.

### 2. The Kitchen Sink

**Problem:** Listing 50+ micro-capabilities that should be sub-features.

```xml
<core_capabilities>
  <capability>Login button</capability>
  <capability>Login form validation</capability>
  <capability>Login error messages</capability>
  <capability>Password reset link</capability>
  <capability>Password reset form</capability>
  <capability>Password reset email</capability>
  <!-- 44 more entries -->
</core_capabilities>
```

**Fix:** Consolidate into 8-15 high-level capabilities. Each capability should represent a functional area, not a UI element. Let the feature generation model handle decomposition.

### 3. The Ghost Town

**Problem:** Empty or near-empty optional sections that add noise without value.

```xml
<additional_requirements>
</additional_requirements>
<development_guidelines>
</development_guidelines>
<implementation_roadmap>
</implementation_roadmap>
```

**Fix:** Omit optional sections entirely if there is nothing meaningful to include. The schema marks them as optional for this reason.

### 4. The Copy-Paste Spec

**Problem:** Implemented features that are verbatim copies of core capabilities.

```xml
<core_capabilities>
  <capability>User authentication with JWT tokens</capability>
</core_capabilities>
<implemented_features>
  <feature>
    <name>User authentication with JWT tokens</name>
    <description>User authentication with JWT tokens</description>
  </feature>
</implemented_features>
```

**Fix:** Remove implemented items from `core_capabilities`. The `implemented_features` description should detail what was actually built, not repeat the capability statement. Move the capability to `implemented_features` only after it is fully built.

### 5. The Version Amnesia

**Problem:** Tech stack without versions, causing agents to guess.

**Fix:** Always include version numbers. Run `npm list --depth=0` or check `package.json` to get exact versions. Even approximate versions ("React 18+" ) are better than none.

### 6. The Monolith Capability

**Problem:** A single capability that encompasses the entire application.

```xml
<core_capabilities>
  <capability>Full-featured project management system with user auth, dashboards, reports, settings, API, notifications, integrations, and admin panel</capability>
</core_capabilities>
```

**Fix:** Break it into distinct functional areas. Each capability should be independently describable and decomposable into features.

---

## Feature Generation Tips

### Write Capabilities That Decompose Well

A well-written capability naturally breaks into 2-5 features:

```xml
<capability>Real-time notification system with in-app toast notifications for agent events, persistent notification center with read/unread state, email digest configuration for daily/weekly summaries, and webhook integration for external alerting services.</capability>
```

This decomposes into:
1. Toast notification component for agent events
2. Notification center with read/unread tracking
3. Email digest configuration and scheduling
4. Webhook integration for external alerts

### Include Dependency Hints

State dependencies explicitly in capability descriptions:

```xml
<capability>Report generation using data from the dashboard metrics system (capability 2). Produces PDF summaries via Puppeteer with charts rendered from the same D3.js visualizations used in the dashboard.</capability>
```

### Order Capabilities by Implementation Priority

The feature generation model respects the ordering of capabilities. Place foundational capabilities first:

1. Data model and database schema
2. Authentication and authorization
3. Core CRUD operations
4. Real-time features (WebSocket, events)
5. Advanced features (AI integration, reporting)
6. Polish (themes, accessibility, performance)

### Specify Interaction Patterns

Instead of "search functionality," specify:

```xml
<capability>Full-text search across features, agents, and logs with debounced input (300ms), highlighted result snippets, faceted filtering by status/date/category, and keyboard navigation (arrow keys to browse, Enter to select, Escape to close).</capability>
```

---

## Maintaining Spec Currency

### After Feature Batch Completion

1. Run `POST /api/spec-regeneration/sync` to auto-merge completed features and update the tech stack.
2. Review the auto-appended `<implemented_features>` entries for accuracy.
3. Remove any `core_capabilities` entries that are now fully covered by implemented features.
4. Update `implementation_roadmap` phase statuses if the sync endpoint did not advance them automatically.

### After Major Codebase Changes

1. Regenerate the full spec with `POST /api/spec-regeneration/generate` and `analyzeProject: true`.
2. Compare the new spec against the previous version.
3. Manually merge sections where the AI-generated spec missed nuances the previous version captured.
4. Validate the XML structure: single root element, proper nesting, escaped special characters.

### Periodic Review Cadence

- **Weekly:** Run sync to capture completed features and tech stack changes.
- **Per sprint/milestone:** Review `core_capabilities` for accuracy and reorder by current priority.
- **Per major release:** Full regeneration with codebase analysis, followed by manual review and merge.

---

## Multi-Project Patterns

### Web Application Template

Focus the spec on:
- Route structure and navigation patterns
- State management approach and store organization
- API layer design (REST endpoints, request/response shapes)
- Authentication/authorization model
- Component library and design system

### API Service Template

Focus the spec on:
- Endpoint catalog with request/response schemas
- Authentication mechanisms (API keys, OAuth, JWT)
- Rate limiting and error handling patterns
- Database schema and migration strategy
- Integration points with external services

### Monorepo Template

Focus the spec on:
- Package boundary definitions and dependency rules
- Shared type definitions and contracts between packages
- Build order and dependency chain
- Per-package testing strategy
- Cross-package import conventions

### CLI Tool Template

Focus the spec on:
- Command hierarchy and argument parsing
- Configuration file format and precedence
- Output formatting (JSON, table, plain text)
- Error messages and exit codes
- Shell completion and help text generation
