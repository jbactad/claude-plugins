---
name: spec-optimizer
description: This skill should be used when the user asks to "optimize the spec", "improve app_spec.txt", "update spec.md", "optimize project specification", "improve feature generation from spec", or wants to restructure their Automaker project specification for better AI comprehension. Also use when discussing spec.md structure, app_spec.txt format, or how to write specs that generate better features.
---

# Automaker Spec Optimizer

## Overview

Optimize Automaker project specifications to produce higher-quality AI-generated features. Automaker uses two spec-related files that drive its autonomous development workflow. Understanding their roles, structure, and interaction is essential for maximizing feature generation quality.

## The Two Spec Files

### app_spec.txt (Primary Specification)

- **Location:** `.automaker/app_spec.txt`
- **Format:** XML following the `<project_specification>` schema
- **Purpose:** Serve as the structured source of truth for the project. The spec generation model reads this file when generating features via `POST /api/spec-regeneration/generate-features`.
- **Creation:** Generate through the Automaker UI or via `POST /api/spec-regeneration/generate` (AI-powered) or `POST /api/spec-regeneration/create` (from a project overview).
- **Auto-updates:** When features reach `verified` or `completed` status, `syncFeatureToAppSpec()` in `FeatureLoader` appends them to the `<implemented_features>` section automatically.

### spec.md (Human-Readable Specification)

- **Location:** `.automaker/spec.md`
- **Format:** Markdown
- **Purpose:** Provide a human-readable project specification that can be manually authored or AI-generated. Serves as supplementary documentation alongside `app_spec.txt`.

Both files live in the `.automaker/` directory at the project root. The `app_spec.txt` XML file is the one Automaker's backend actively parses and uses for feature generation.

## The SpecOutput Schema

Automaker's structured output uses the `SpecOutput` interface. Refer to [references/spec-schema.md](references/spec-schema.md) for the complete schema definition with field-by-field guidance.

**Required fields:** `project_name`, `overview`, `technology_stack`, `core_capabilities`, `implemented_features`

**Optional fields:** `additional_requirements`, `development_guidelines`, `implementation_roadmap`

The spec generation model (default: Opus) produces a `SpecOutput` JSON object via structured output, which Automaker then converts to XML via `specToXml()` and saves as `app_spec.txt`.

## Optimizing the Spec Structure

### Project Name and Overview

- Write the project name exactly as it appears in `package.json` or the repository.
- Keep the overview to one focused paragraph (3-5 sentences).
- State the problem being solved, the target users, and the primary value proposition.
- Avoid aspirational language; describe what the project does or will do concretely.

### Technology Stack

- List every technology, framework, and tool with its version when known.
- Format each entry as a single descriptive string (e.g., "React 19 - UI framework").
- Include build tools, testing frameworks, databases, and deployment targets.
- Agents use this list to make correct import and API decisions -- omitting a technology leads to agents guessing or choosing defaults.

### Core Capabilities

- Write each capability as a single, clear sentence describing a functional area.
- Limit to 2-3 sentences per capability. The first sentence names the capability; subsequent sentences add acceptance criteria.
- Number capabilities in priority order. The feature generation model respects this ordering.
- Separate what exists from what needs to be built. Use `implemented_features` for completed work and `core_capabilities` for planned work.
- Target 8-15 capabilities. Fewer than 5 produces overly broad features; more than 20 produces fragmented ones.

### Implemented Features

- Each entry needs a `name` and `description`. Optionally include `file_locations` to anchor the feature to specific code paths.
- Keep descriptions factual: describe what was built, not what was planned.
- Automaker auto-populates this section via `syncFeatureToAppSpec()`, but manual curation improves accuracy.
- Deduplicate entries that describe the same functionality with different names.
- Remove entries for features that were reverted or abandoned.

### Additional Requirements

- List non-functional requirements: performance targets, security constraints, accessibility standards, browser support.
- Keep each requirement to one sentence.

### Development Guidelines

- State coding standards, architectural patterns, and conventions agents must follow.
- Reference existing patterns in the codebase by file path (e.g., "Follow the route handler pattern in `apps/server/src/routes/`").
- Include naming conventions, error handling strategies, and testing requirements.

### Implementation Roadmap

- Define phases with a `phase` name, `status` (`completed`, `in_progress`, or `pending`), and `description`.
- Reference `core_capabilities` by topic alignment so agents understand what work belongs to each phase.
- The sync endpoint (`POST /api/spec-regeneration/sync`) automatically updates phase statuses based on completed features.

## Optimization Techniques

Refer to [references/optimization-techniques.md](references/optimization-techniques.md) for detailed before/after examples and anti-pattern catalog.

### Write for AI Comprehension

- Use precise, unambiguous language. Replace "handle user stuff" with "Authenticate users via JWT tokens and manage session lifecycle."
- Specify file paths and module boundaries. An agent reading "implement the dashboard" has no context; "implement the dashboard view in `apps/ui/src/components/views/dashboard-view.tsx` using the existing Zustand store pattern" gives it a clear target.
- Include acceptance criteria inline. Instead of "Add search functionality," write "Add full-text search across feature titles and descriptions, with debounced input and result highlighting."

### Structure for Decomposition

- Write capabilities that map to 2-5 individual features each. A capability that maps to 1 feature is too granular for the spec level; one that maps to 20+ is too broad.
- Include dependency hints in capability descriptions. If capability 5 depends on capability 2, state it: "Requires the authentication system from capability 2."
- Group related capabilities sequentially so the feature generation model produces features in a logical implementation order.

### Maintain Spec Currency

- Run `POST /api/spec-regeneration/sync` periodically to synchronize completed features, update the tech stack via codebase analysis, and advance roadmap phases.
- Review auto-appended `implemented_features` entries for accuracy after each batch of feature completions.
- Update `core_capabilities` to remove items that have been fully implemented and moved to `implemented_features`.
- Regenerate the full spec via `POST /api/spec-regeneration/generate` with `analyzeProject: true` when the codebase has diverged significantly from the spec.

### Optimize the app_spec.txt XML

- Validate the XML structure: ensure a single `<project_specification>` root element, proper tag nesting, and XML-escaped special characters.
- Keep the XML well-indented with 2-space indentation for readability.
- Verify that every `<feature>` in `<implemented_features>` has both `<name>` and `<description>` child elements.
- Remove duplicate `<feature>` entries (Automaker checks for duplicates by name, case-insensitive, but manual review catches semantic duplicates with different names).

## Spec-to-Feature Generation Workflow

1. **Spec creation:** `POST /api/spec-regeneration/generate` sends the project overview to the spec generation model (configurable via `phaseModels.specGenerationModel`, defaults to Opus). When `analyzeProject` is true, the model uses `Read`, `Glob`, and `Grep` tools to inspect the actual codebase.

2. **Structured output:** The model returns a `SpecOutput` JSON object via Claude's structured output. Automaker converts it to XML via `specToXml()` and writes it to `.automaker/app_spec.txt`.

3. **Feature generation:** `POST /api/spec-regeneration/generate-features` reads the saved `app_spec.txt`, loads existing features to prevent duplicates, and sends both to the feature generation model (configurable via `phaseModels.featureGenerationModel`, defaults to Sonnet).

4. **Feature output:** The model returns a JSON array of features, each with `id`, `title`, `description`, and optional `category`, `priority`, `complexity`, and `dependencies`. Automaker creates feature cards from these on the Kanban board.

5. **Spec sync:** As features reach `verified`/`completed`, `syncFeatureToAppSpec()` appends them to `<implemented_features>`. The sync endpoint performs a full reconciliation: merging completed features, analyzing the tech stack, and updating roadmap phases.

## Key Principles

- **Specificity over brevity:** A longer, precise capability description produces better features than a short, vague one.
- **Separation of concerns:** Keep "what exists" in `implemented_features` and "what to build" in `core_capabilities`. Mixing them causes duplicate feature generation.
- **Incremental refinement:** Optimize the spec iteratively. Generate features, review their quality, adjust the spec, and regenerate.
- **Schema compliance:** Always ensure the spec conforms to the `SpecOutput` schema. Invalid or missing fields cause silent failures in feature generation.
- **Codebase anchoring:** Reference actual file paths, module names, and patterns. Agents perform better when given concrete starting points rather than abstract descriptions.
