# Init Script Patterns by Project Type

## Node.js (npm)

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Node.js Project Init ==="
echo "Installing dependencies..."
npm ci

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true
cp "$AUTOMAKER_PROJECT_PATH/.env.local" .env.local 2>/dev/null || true

echo "=== Init complete ==="
```

## Node.js (yarn)

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Yarn Project Init ==="
echo "Installing dependencies..."
yarn install --frozen-lockfile

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true

echo "=== Init complete ==="
```

## Node.js (pnpm)

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== pnpm Project Init ==="
echo "Installing dependencies..."
pnpm install --frozen-lockfile

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true

echo "=== Init complete ==="
```

## Node.js (bun)

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Bun Project Init ==="
echo "Installing dependencies..."
bun install --frozen-lockfile

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true

echo "=== Init complete ==="
```

## Monorepo (npm workspaces)

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Monorepo Init ==="
echo "Installing all workspace dependencies..."
npm ci

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true
# Copy app-specific env files
for envfile in $(find "$AUTOMAKER_PROJECT_PATH/apps" -maxdepth 2 -name ".env*" -not -name ".env.example"); do
  relative="${envfile#$AUTOMAKER_PROJECT_PATH/}"
  mkdir -p "$(dirname "$relative")"
  cp "$envfile" "$relative" 2>/dev/null || true
done

echo "Building shared packages..."
npm run build:packages

echo "=== Init complete ==="
```

## Monorepo (Turborepo)

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Turborepo Init ==="
echo "Installing dependencies..."
npm ci

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true

echo "Building dependencies..."
npx turbo run build --filter='./packages/*'

echo "=== Init complete ==="
```

## Python (pip + venv)

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Python Project Init ==="
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt 2>/dev/null || true

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true

echo "=== Init complete ==="
```

## Python (uv)

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Python (uv) Project Init ==="
echo "Syncing dependencies..."
uv sync

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true

echo "=== Init complete ==="
```

## Python (Poetry)

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Poetry Project Init ==="
echo "Installing dependencies..."
poetry install

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true

echo "=== Init complete ==="
```

## Full-Stack with Prisma

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Full-Stack + Prisma Init ==="
echo "Installing dependencies..."
npm ci

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true
cp "$AUTOMAKER_PROJECT_PATH/.env.local" .env.local 2>/dev/null || true

echo "Generating Prisma client..."
npx prisma generate

echo "Running migrations (if database available)..."
npx prisma migrate dev --skip-generate 2>/dev/null || echo "Skipping migrations (database not available)"

echo "=== Init complete ==="
```

## Full-Stack with Drizzle

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Full-Stack + Drizzle Init ==="
echo "Installing dependencies..."
npm ci

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true

echo "Pushing schema (if database available)..."
npx drizzle-kit push 2>/dev/null || echo "Skipping schema push (database not available)"

echo "=== Init complete ==="
```

## Go Project

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Go Project Init ==="
echo "Downloading modules..."
go mod download

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true

echo "Building..."
go build ./... 2>/dev/null || echo "Build skipped (optional)"

echo "=== Init complete ==="
```

## Rust Project

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Rust Project Init ==="
echo "Fetching dependencies..."
cargo fetch

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true

echo "=== Init complete ==="
```

## Ruby on Rails

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Rails Project Init ==="
echo "Installing gems..."
bundle install

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true

echo "Setting up database..."
bin/rails db:prepare 2>/dev/null || echo "Database setup skipped"

echo "=== Init complete ==="
```

## Docker-Based Project

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Docker Project Init ==="
echo "Starting services..."
docker compose up -d

echo "Installing dependencies..."
npm ci

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true

echo "Waiting for services..."
sleep 5

echo "Running migrations..."
npm run migrate 2>/dev/null || true

echo "=== Init complete ==="
```

## Java / Gradle

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Gradle Project Init ==="
echo "Building project..."
./gradlew build -x test

echo "Copying environment files..."
cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true

echo "=== Init complete ==="
```

## Advanced Patterns

### Conditional Package Manager Detection

```bash
#!/bin/bash
set -e
cd "$AUTOMAKER_WORKTREE_PATH"

echo "=== Auto-Detect Init ==="

# Detect and install with the right package manager
if [ -f "bun.lockb" ]; then
  echo "Detected bun..."
  bun install --frozen-lockfile
elif [ -f "pnpm-lock.yaml" ]; then
  echo "Detected pnpm..."
  pnpm install --frozen-lockfile
elif [ -f "yarn.lock" ]; then
  echo "Detected yarn..."
  yarn install --frozen-lockfile
elif [ -f "package-lock.json" ]; then
  echo "Detected npm..."
  npm ci
fi

# Copy all env files from project root
echo "Copying environment files..."
for envfile in "$AUTOMAKER_PROJECT_PATH"/.env*; do
  [ -f "$envfile" ] || continue
  filename=$(basename "$envfile")
  [ "$filename" = ".env.example" ] && continue
  cp "$envfile" "$AUTOMAKER_WORKTREE_PATH/$filename" 2>/dev/null || true
done

echo "=== Init complete ==="
```

### Git Hooks Setup

```bash
# Add after dependency installation if using Husky
echo "Setting up git hooks..."
npx husky install 2>/dev/null || true
```

### Parallel Operations

```bash
# Run independent operations in parallel for speed
echo "Running parallel setup..."
npm ci &
PID_NPM=$!

cp "$AUTOMAKER_PROJECT_PATH/.env" .env 2>/dev/null || true &
PID_ENV=$!

wait $PID_NPM
wait $PID_ENV
echo "Parallel setup complete"
```
