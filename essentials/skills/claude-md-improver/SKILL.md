---
name: claude-md-improver
description: This skill should be used when the user asks to "audit CLAUDE.md", "check CLAUDE.md quality", "improve CLAUDE.md", "fix CLAUDE.md", "review my CLAUDE.md", "grade my CLAUDE.md", "write a CLAUDE.md", "set up CLAUDE.md for this project", or mentions "CLAUDE.md best practices", "CLAUDE.md maintenance", or "project memory optimization". Scans all CLAUDE.md files in the repository, evaluates quality against a scoring rubric, outputs a scored quality report, then proposes targeted updates with diffs.
---

# CLAUDE.md Improver

Audit, evaluate, and improve CLAUDE.md files across a codebase to ensure Claude Code has optimal project context.

**This skill can write to CLAUDE.md files.** After presenting a quality report and getting user approval, it updates CLAUDE.md files with targeted improvements.

## Workflow

### Phase 1: Discovery

Find all CLAUDE.md files in the repository:

```bash
find . \( -name "CLAUDE.md" -o -name "CLAUDE.local.md" \) 2>/dev/null | head -50
find .claude/rules -name "*.md" 2>/dev/null
```

**File Types & Locations:**

| Type | Location | Purpose |
|------|----------|---------|
| Project root | `./CLAUDE.md` | Primary project context (checked into git, shared with team) |
| Alternative location | `./.claude/CLAUDE.md` | Equivalent to project root CLAUDE.md |
| Local overrides | `./CLAUDE.local.md` | Personal/local settings (auto-gitignored, not shared) |
| Global defaults | `~/.claude/CLAUDE.md` | User-wide defaults across all projects |
| Package-specific | `./packages/*/CLAUDE.md` | Module-level context in monorepos |
| Subdirectory | Any nested location | Feature/domain-specific context |
| Rules (global) | `./.claude/rules/*.md` | Always loaded at launch (no `paths` frontmatter) |
| Rules (path-scoped) | `./.claude/rules/*.md` | Loaded only when Claude reads files matching `paths` frontmatter globs |

**Note:** Claude walks up the directory tree from the current working directory, loading CLAUDE.md and CLAUDE.local.md at each level. Subdirectory CLAUDE.md files load on-demand when those directories are accessed.

**Import syntax:** CLAUDE.md files support `@path/to/file` imports to pull in external files. Imported files can chain imports up to 5 hops deep.

**If no CLAUDE.md files are found**, skip to Phase 2b to create one from scratch.

### Phase 2a: Quality Assessment (Existing Projects)

For each CLAUDE.md file, evaluate against quality criteria. See [references/quality-criteria.md](references/quality-criteria.md) for detailed rubrics.

**Quick Assessment Checklist:**

| Criterion | Weight | Check |
|-----------|--------|-------|
| Commands/workflows documented | High | Are build/test/deploy commands present? |
| Architecture clarity | High | Can Claude understand the codebase structure? |
| Non-obvious patterns | Medium | Are gotchas and quirks documented? |
| Conciseness | Medium | No verbose explanations or obvious info? |
| Currency | High | Does it reflect current codebase state? |
| Actionability | High | Are instructions executable, not vague? |

**Size guideline:** Target under 200 lines per CLAUDE.md file. Bloated files cause Claude to ignore instructions. If a file exceeds this, recommend splitting into `.claude/rules/*.md` or using `@path` imports.

**Quality Scores:**
- **A (90-100)**: Comprehensive, current, actionable
- **B (70-89)**: Good coverage, minor gaps
- **C (50-69)**: Basic info, missing key sections
- **D (30-49)**: Sparse or outdated
- **F (0-29)**: Missing or severely outdated

### Phase 2b: Bootstrap (New Projects)

When no CLAUDE.md exists, analyze the codebase to generate one:

1. **Scan the project** — identify package manager, build system, test framework, directory structure, and entry points
2. **Select a template** from [references/templates.md](references/templates.md) matching the project type (minimal, comprehensive, monorepo, or package)
3. **Fill the template** with real commands, paths, and patterns discovered from the codebase
4. **Present the draft** to the user for review before writing

After user approval, create `./CLAUDE.md` using the Write tool. Then proceed to Phase 3 to output a quality report on the newly created file.

### Phase 3: Quality Report Output

**ALWAYS output the quality report BEFORE making any updates.**

Format:

```
## CLAUDE.md Quality Report

### Summary
- Files found: X
- Average score: X/100
- Files needing update: X

### File-by-File Assessment

#### 1. ./CLAUDE.md (Project Root)
**Score: XX/100 (Grade: X)**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Commands/workflows | X/20 | ... |
| Architecture clarity | X/20 | ... |
| Non-obvious patterns | X/15 | ... |
| Conciseness | X/15 | ... |
| Currency | X/15 | ... |
| Actionability | X/15 | ... |

**Issues:**
- [List specific problems]

**Recommended additions:**
- [List what should be added]

#### 2. ./packages/api/CLAUDE.md (Package-specific)
...
```

### Phase 4: Targeted Updates

After outputting the quality report, ask user for confirmation before updating. See [references/update-guidelines.md](references/update-guidelines.md) for detailed guidance on what to add and what to avoid.

**Update Guidelines (Critical):**

1. **Propose targeted additions only** - Focus on genuinely useful info:
   - Commands or workflows discovered during analysis
   - Gotchas or non-obvious patterns found in code
   - Package relationships that weren't clear
   - Testing approaches that work
   - Configuration quirks

2. **Keep it minimal** - Avoid:
   - Restating what's obvious from the code
   - Generic best practices already covered
   - One-off fixes unlikely to recur
   - Verbose explanations when a one-liner suffices

3. **Show diffs** - For each change, show:
   - Which CLAUDE.md file to update
   - The specific addition (as a diff or quoted block)
   - Brief explanation of why this helps future sessions

**Diff Format:**

```markdown
### Update: ./CLAUDE.md

**Why:** Build command was missing, causing confusion about how to run the project.

```diff
+ ## Quick Start
+
+ ```bash
+ npm install
+ npm run dev  # Start development server on port 3000
+ ```
```
```

### Phase 5: Apply Updates

After user approval, apply changes using the Edit tool. Preserve existing content structure.

## Templates

See [references/templates.md](references/templates.md) for CLAUDE.md templates by project type.

## Common Issues to Flag

1. **Stale commands**: Build commands that no longer work
2. **Missing dependencies**: Required tools not mentioned
3. **Outdated architecture**: File structure that's changed
4. **Missing environment setup**: Required env vars or config
5. **Broken test commands**: Test scripts that have changed
6. **Undocumented gotchas**: Non-obvious patterns not captured

## User Tips to Share

When presenting recommendations, remind users:

- **Keep it concise**: CLAUDE.md should be human-readable; dense is better than verbose
- **Actionable commands**: All documented commands should be copy-paste ready
- **Use `CLAUDE.local.md`**: For personal preferences not shared with team (auto-gitignored)
- **Global defaults**: Put user-wide preferences in `~/.claude/CLAUDE.md`

## What Makes a Great CLAUDE.md

See [references/templates.md](references/templates.md) for key principles, recommended sections, and templates by project type.
