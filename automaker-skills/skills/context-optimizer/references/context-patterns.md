# Context File Patterns by Project Type

## React / Next.js Project

```markdown
# Project Context

## Overview
[App name] is a React [18/19] application built with [Next.js 14/15 / Vite / CRA].
State management uses [Zustand/Redux/Context]. Styling via [Tailwind/CSS Modules/styled-components].

## Tech Stack
- React 19, TypeScript 5.x
- Next.js 15 (App Router)
- Tailwind CSS 4 with CSS variables
- Zustand 5 for state management
- TanStack Query for server state
- shadcn/ui components (New York style)

## Directory Structure
- `src/app/` — Next.js App Router pages and layouts
- `src/components/` — Reusable React components
- `src/components/ui/` — shadcn/ui primitives (do not modify directly)
- `src/hooks/` — Custom React hooks
- `src/lib/` — Utilities, API client, constants
- `src/store/` — Zustand stores

## Commands
- `npm run dev` — Development server (port 3000)
- `npm run build` — Production build
- `npm run lint` — ESLint
- `npm run test` — Vitest

## Coding Conventions
- Use functional components with hooks, never class components
- Prefix custom hooks with `use`
- Co-locate component tests: `Component.test.tsx` next to `Component.tsx`
- Import UI primitives from `@/components/ui/`, never from `@radix-ui` directly
- Use `cn()` from `@/lib/utils` for conditional class merging

## Critical Rules
- NEVER modify files in `src/components/ui/` — these are shadcn/ui generated
- NEVER use `any` type — use `unknown` and narrow with type guards
- NEVER import from `next/router` — use `next/navigation` (App Router)
- ALWAYS use server components by default; add `'use client'` only when needed
```

## Express / API Project

```markdown
# Project Context

## Overview
[Service name] is a REST API built with Express 5 and TypeScript.
Database: [PostgreSQL via Prisma / MongoDB via Mongoose].

## Tech Stack
- Express 5, TypeScript 5.x
- Prisma ORM with PostgreSQL
- Zod for request validation
- Winston for logging
- Jest for testing

## Directory Structure
- `src/routes/` — Express route handlers organized by resource
- `src/services/` — Business logic (no HTTP awareness)
- `src/middleware/` — Auth, validation, error handling middleware
- `src/lib/` — Database client, logger, utilities
- `src/types/` — Shared TypeScript definitions
- `prisma/` — Schema and migrations

## Commands
- `npm run dev` — Development server with nodemon (port 3008)
- `npm run build` — TypeScript compilation
- `npm run test` — Jest with coverage
- `npx prisma migrate dev` — Run migrations
- `npx prisma generate` — Regenerate client

## Coding Conventions
- Route handlers call services, never contain business logic
- Validate all request bodies with Zod schemas
- Use `createLogger('context')` from `src/lib/logger.ts`, never `console.log`
- Return `{ success: true, ...data }` for success, `{ success: false, error }` for errors
- Use `asyncHandler()` wrapper on all async route handlers

## Critical Rules
- NEVER put business logic in route handlers — extract to services/
- NEVER use raw SQL — use Prisma client
- NEVER expose stack traces in production error responses
- NEVER skip input validation on POST/PUT/PATCH endpoints
- ALWAYS use parameterized queries (Prisma handles this)
```

## Monorepo Project (npm workspaces / Turborepo)

```markdown
# Project Context

## Overview
Monorepo containing [N] packages managed with npm workspaces.
[Brief description of what the project does].

## Tech Stack
- Node.js 22, TypeScript 5.x
- npm workspaces for package management
- Turborepo for build orchestration
- Vitest for testing

## Directory Structure
- `apps/ui/` — React frontend (port 3007)
- `apps/server/` — Express backend (port 3008)
- `libs/types/` — Shared TypeScript definitions (no dependencies)
- `libs/utils/` — Shared utilities (depends on types)
- `libs/platform/` — Platform-specific code (depends on types)

## Package Dependency Chain
Packages can only depend on packages above them:
```
types (no deps) → utils, platform → server, ui
```

## Commands
- `npm run dev` — Start all services
- `npm run build:packages` — Build all libs (required before app builds)
- `npm run test:packages` — Run all lib tests
- `npm run test:server` — Server unit tests
- `npm run lint` — ESLint across all packages

## Coding Conventions
- Import shared code from packages: `import { X } from '@scope/types'`
- NEVER import across package boundaries using relative paths
- NEVER add dependencies that violate the dependency chain
- Each package has its own `tsconfig.json` extending the root config
- Use `createLogger('package:module')` for scoped logging

## Critical Rules
- NEVER import from `../../../libs/` — use package names
- NEVER add a dependency from `types` to any other package
- ALWAYS run `npm run build:packages` after changing lib source
- ALWAYS add new shared types to `libs/types/`, not local files
```

## Python Project

```markdown
# Project Context

## Overview
[Project name] is a Python [3.11/3.12] application using [FastAPI/Django/Flask].

## Tech Stack
- Python 3.12
- FastAPI with Pydantic v2
- SQLAlchemy 2.0 with async sessions
- Alembic for migrations
- pytest for testing
- Ruff for linting and formatting

## Directory Structure
- `src/` — Application source
- `src/api/` — FastAPI route handlers
- `src/models/` — SQLAlchemy models
- `src/services/` — Business logic
- `src/schemas/` — Pydantic request/response models
- `tests/` — pytest test files
- `alembic/` — Database migrations

## Commands
- `uv run fastapi dev` — Development server
- `uv run pytest` — Run tests
- `uv run ruff check .` — Lint
- `uv run ruff format .` — Format
- `uv run alembic upgrade head` — Run migrations

## Coding Conventions
- Use async/await for all I/O operations
- Validate all inputs with Pydantic models
- Use dependency injection via FastAPI's `Depends()`
- Type-annotate all function signatures
- Use `structlog` for logging, never `print()`

## Critical Rules
- NEVER use `from module import *` — explicit imports only
- NEVER commit `.env` files — use `.env.example` as template
- NEVER use synchronous database calls — use async sessions
- ALWAYS use `async with` for database sessions
```

## General Patterns (Applicable to All Projects)

### Git Workflow Rules
```markdown
## Git Conventions
- Branch naming: `feature/short-description`, `fix/issue-description`
- Commit messages: conventional commits (feat:, fix:, refactor:, docs:, chore:)
- NEVER force push to main/master
- ALWAYS create PRs for review before merging
```

### Documentation Rules
```markdown
## Documentation
- Add JSDoc/docstring to exported functions
- Update README when adding new features
- Keep API documentation in sync with implementation
- NEVER add TODO comments without a linked issue
```
