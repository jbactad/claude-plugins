---
name: worktree-init
description: This skill should be used when the user asks to "create a worktree init script", "set up worktree-init.sh", "optimize worktree initialization", "configure worktree setup", or wants to automate worktree environment setup in Automaker projects. Also use when discussing .automaker/worktree-init.sh, worktree bootstrapping, or post-worktree-creation hooks.
---

# Automaker Worktree Init Script Generator

Create optimized `.automaker/worktree-init.sh` scripts that automatically set up the development environment when Automaker creates a new git worktree for feature isolation.

## How Init Scripts Work

Automaker creates isolated git worktrees for each feature branch. After `git worktree add`, the `InitScriptService` automatically runs `.automaker/worktree-init.sh` in the new worktree directory. The script runs once per branch (unless force-re-run via API), streams output to the UI via WebSocket, and its status is tracked in `.automaker/worktrees/{branch}/worktree.json`.

**Security model:** The script runs with a restricted environment — `ANTHROPIC_API_KEY` and other secrets are explicitly excluded. Only safe system variables and Automaker-specific variables are available.

## Init Script Creation Workflow

### 1. Analyze the Project

Before writing the init script, detect:

- **Package manager** — `package-lock.json` (npm), `yarn.lock` (yarn), `pnpm-lock.yaml` (pnpm), `bun.lockb` (bun)
- **Language runtime** — Node.js, Python, Go, Rust, Ruby, Java
- **Environment files** — `.env`, `.env.local`, `.env.development`
- **Database** — Prisma, Drizzle, SQLAlchemy, ActiveRecord migrations
- **Monorepo tools** — npm workspaces, Turborepo, Nx, Lerna
- **Build requirements** — Shared packages that need pre-building
- **Git hooks** — Husky, lint-staged, pre-commit

### 2. Write the Script

Create `.automaker/worktree-init.sh` following this structure:

```bash
#!/bin/bash
set -e

echo "=== Automaker Worktree Init ==="
echo "Project: $AUTOMAKER_PROJECT_PATH"
echo "Worktree: $AUTOMAKER_WORKTREE_PATH"
echo "Branch: $AUTOMAKER_BRANCH"

# 1. Install dependencies
echo "Installing dependencies..."
<package-manager-install-command>

# 2. Copy environment files (never committed to git)
echo "Setting up environment..."
cp "$AUTOMAKER_PROJECT_PATH/.env" "$AUTOMAKER_WORKTREE_PATH/.env" 2>/dev/null || true

# 3. Build prerequisites (monorepos)
echo "Building shared packages..."
<build-command>

# 4. Database setup (if applicable)
echo "Running migrations..."
<migration-command>

echo "=== Init complete ==="
```

### 3. Apply Best Practices

- **Start with `set -e`** — Fail fast on errors; do not let broken state persist
- **Use `2>/dev/null || true`** for optional steps (missing .env files, optional migrations)
- **Add echo statements** — Output streams to the UI; users see progress in real-time
- **Make it idempotent** — Safe to re-run without side effects
- **Keep it fast** — The AI agent may start working before the script completes
- **Use Automaker env vars** — Reference `$AUTOMAKER_PROJECT_PATH` for the main project root
- **Never hardcode paths** — Use the provided environment variables
- **Handle missing tools gracefully** — Check `command -v` before running optional tools

### 4. Common Patterns

| Project Type | Key Steps |
|-------------|-----------|
| Node.js | `npm ci` (or yarn/pnpm/bun install) |
| Monorepo | Install + `npm run build:packages` |
| Python | Create venv + `pip install -r requirements.txt` |
| Full-stack + DB | Install + copy .env + run migrations |
| Docker-based | `docker compose up -d` + install |
| Rust | `cargo build` (optional, agent may do this) |
| Go | `go mod download` |

### 5. Available Environment Variables

| Variable | Description |
|----------|-------------|
| `AUTOMAKER_PROJECT_PATH` | Absolute path to the main project root |
| `AUTOMAKER_WORKTREE_PATH` | Absolute path to the new worktree directory |
| `AUTOMAKER_BRANCH` | Branch name of the new worktree |
| `PATH`, `HOME`, `USER`, `SHELL`, `TERM`, `LANG` | Standard system variables |

**Excluded:** `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and other API secrets.

### 6. Managing Init Scripts via API

| Endpoint | Purpose |
|----------|---------|
| `GET /api/worktree/init-script` | Read current script content |
| `PUT /api/worktree/init-script` | Save script (max 1MB) |
| `DELETE /api/worktree/init-script` | Delete script |
| `POST /api/worktree/run-init-script` | Force re-run on existing worktree |

## Additional Resources

### Reference Files

- **`references/init-script-patterns.md`** — Complete script templates for Node.js, Python, Go, Rust, Ruby, Docker, and monorepo projects
- **`references/environment-variables.md`** — Full documentation of available and excluded environment variables with security considerations
