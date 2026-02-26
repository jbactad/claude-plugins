# Mission Control - Project Settings

Copy this file to `.mission-control/settings.md` in your project root and adjust
settings to match your project's needs. Mission Control reads this file at the start
of every mission.

---

## Complete Settings Reference

```yaml
---
# Model & Planning
defaultModel: sonnet            # Default model for agents: haiku, sonnet, opus
defaultPlanningDepth: spec      # How deeply to plan: skip, lite, spec, full

# Approval & Safety
requireApproval: tier2+         # When human approval is needed: never, tier1+, tier2+, always
maxConcurrentAgents: 3          # Maximum parallel agents during execution

# Commands
testCommand: ""                 # Shell command to run tests (e.g., "npm test", "pytest")
devCommand: ""                  # Shell command to start dev server (e.g., "npm run dev")

# Isolation
useWorktrees: true              # Run implementer agents in isolated git worktrees

# Quality Gates
autoReview: true                # Automatically spawn reviewer agent for Tier 1+ tasks
autoTest: true                  # Automatically run testCommand after implementation

# Failure Handling
retryOnFailure: true            # Retry failed tasks automatically
maxRetries: 2                   # Maximum retry attempts per task (total attempts = maxRetries + 1)
escalateModelOnRetry: true      # Upgrade model on retry (haiku -> sonnet -> opus)

# Memory & Learning
memoryEnabled: true             # Load learnings from .mission-control/memory/ at mission start
autoLearn: true                 # Extract and save learnings during /debrief
---
```

---

## Custom Agent Types

Define project-specific agent types below. These extend the built-in agents
(mission-planner, researcher, implementer, reviewer, retrospective) and are
available for task assignment during mission decomposition.

| Type | Description | subagent_type | model | Notes |
|------|-------------|---------------|-------|-------|

<!-- Add your custom agents here. See examples/project-agents-example.md for templates. -->

---

## Example Configurations

### Rapid Prototyping Team

Fast iteration with minimal overhead. Good for hackathons, spikes, and throwaway prototypes.

```yaml
---
defaultModel: haiku
defaultPlanningDepth: lite
requireApproval: never
maxConcurrentAgents: 5
useWorktrees: false
autoReview: false
autoTest: false
retryOnFailure: false
memoryEnabled: false
autoLearn: false
---
```

### Enterprise Team

Maximum safety controls. Every change is reviewed, tested, and approved. Good for
production systems with strict compliance or reliability requirements.

```yaml
---
defaultModel: sonnet
defaultPlanningDepth: full
requireApproval: always
maxConcurrentAgents: 2
testCommand: "npm run test:all"
devCommand: "npm run dev"
useWorktrees: true
autoReview: true
autoTest: true
retryOnFailure: true
maxRetries: 3
escalateModelOnRetry: true
memoryEnabled: true
autoLearn: true
---
```

| Type | Description | subagent_type | model | Notes |
|------|-------------|---------------|-------|-------|
| `security-auditor` | Security review and vulnerability analysis | general-purpose | opus | Required for all Tier 2+ tasks |
| `compliance-checker` | Regulatory and policy compliance validation | general-purpose | opus | Required for data handling changes |

### Data Science Team

Opus-heavy for reasoning tasks with custom ML-focused agents. Good for projects
with model training, experiment tracking, and data pipeline work.

```yaml
---
defaultModel: opus
defaultPlanningDepth: spec
requireApproval: tier1+
maxConcurrentAgents: 3
testCommand: "pytest -x"
useWorktrees: true
autoReview: true
autoTest: true
retryOnFailure: true
maxRetries: 2
escalateModelOnRetry: false
memoryEnabled: true
autoLearn: true
---
```

| Type | Description | subagent_type | model | Notes |
|------|-------------|---------------|-------|-------|
| `ml-researcher` | Model training, evaluation, and experiment tracking | general-purpose | opus | Use for all ML pipeline tasks |
| `data-engineer` | ETL pipelines and data quality | general-purpose | sonnet | Use for ingestion and transformation |
| `notebook-author` | Jupyter notebook creation and analysis | general-purpose | sonnet | Use for exploratory data analysis |
