# Worktree Init Script Environment Variables

## Available Variables

The `InitScriptService` provides a restricted set of environment variables to worktree init scripts. Only safe system variables and Automaker-specific variables are available — API keys and secrets are explicitly excluded.

### Automaker-Specific Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `AUTOMAKER_PROJECT_PATH` | Absolute path to the main project root (where `.automaker/` lives) | `/Users/dev/my-project` |
| `AUTOMAKER_WORKTREE_PATH` | Absolute path to the new worktree directory | `/Users/dev/my-project/.automaker/worktrees/feature-auth/worktree` |
| `AUTOMAKER_BRANCH` | Branch name of the new worktree | `feature/add-auth` |

### System Variables (Passed Through)

| Variable | Description |
|----------|-------------|
| `PATH` | System executable search path |
| `HOME` | User home directory |
| `USER` | Current username |
| `SHELL` | User's default shell |
| `TERM` | Terminal type |
| `LANG` | System locale |
| `TMPDIR` | System temporary directory |
| `XDG_*` | XDG Base Directory variables (if set) |

### Node.js / Tool Variables (Passed Through)

| Variable | Description |
|----------|-------------|
| `NODE_PATH` | Node.js module search path (if set) |
| `NVM_DIR` | nvm installation directory (if set) |
| `VOLTA_HOME` | Volta installation directory (if set) |
| `CARGO_HOME` | Rust cargo directory (if set) |
| `GOPATH` | Go workspace directory (if set) |
| `PYENV_ROOT` | pyenv root directory (if set) |

## Excluded Variables

The following are **explicitly stripped** from the script's environment for security:

| Variable | Reason |
|----------|--------|
| `ANTHROPIC_API_KEY` | API secret — must not leak to scripts |
| `OPENAI_API_KEY` | API secret |
| `GOOGLE_API_KEY` | API secret |
| `AWS_SECRET_ACCESS_KEY` | Cloud credential |
| `GITHUB_TOKEN` | Auth token |
| `NPM_TOKEN` | Registry auth token |
| Any `*_SECRET*` | Matched by pattern |
| Any `*_KEY` (except PATH-like) | Matched by pattern |
| Any `*_TOKEN` | Matched by pattern |
| Any `*_PASSWORD` | Matched by pattern |

## Using Variables in Scripts

### Always use Automaker variables for paths

```bash
# ✅ Correct — portable across machines
cd "$AUTOMAKER_WORKTREE_PATH"
cp "$AUTOMAKER_PROJECT_PATH/.env" .env

# ❌ Wrong — hardcoded paths break on other machines
cd /Users/dev/my-project/.automaker/worktrees/feature-auth/worktree
cp /Users/dev/my-project/.env .env
```

### Quote all variable references

```bash
# ✅ Correct — handles paths with spaces
cp "$AUTOMAKER_PROJECT_PATH/.env" "$AUTOMAKER_WORKTREE_PATH/.env"

# ❌ Wrong — breaks if path contains spaces
cp $AUTOMAKER_PROJECT_PATH/.env $AUTOMAKER_WORKTREE_PATH/.env
```

### Check for tool availability

```bash
# ✅ Correct — graceful fallback if tool not installed
if command -v pnpm &>/dev/null; then
  pnpm install --frozen-lockfile
elif command -v npm &>/dev/null; then
  npm ci
else
  echo "No package manager found"
  exit 1
fi
```

### Use branch name for conditional logic

```bash
# Set up differently based on branch type
case "$AUTOMAKER_BRANCH" in
  feature/*)
    echo "Feature branch setup..."
    ;;
  fix/*)
    echo "Bugfix branch setup..."
    ;;
  *)
    echo "Standard setup..."
    ;;
esac
```

## Security Considerations

- **Never echo secrets** — Even if a variable slips through, avoid `echo $VAR` for unknown variables
- **Never install from untrusted sources** — Only use `npm ci` (lockfile-based), not `npm install` with arbitrary packages
- **Never fetch remote scripts** — Do not `curl | bash` in init scripts; keep all logic local
- **Copy .env, don't symlink** — Symlinks could expose the main project's env to unintended modifications
- **Handle missing env files gracefully** — Use `cp ... 2>/dev/null || true` since .env files may not exist

## Script Execution Context

| Property | Value |
|----------|-------|
| Working directory | Set by `cd "$AUTOMAKER_WORKTREE_PATH"` at script start |
| Shell | `/bin/bash` |
| Timeout | Configured per project (default varies) |
| Output | Streamed to UI via WebSocket in real-time |
| Exit code | `0` = success, non-zero = failure (tracked in worktree metadata) |
| Re-runs | Can be triggered via `POST /api/worktree/run-init-script` |
