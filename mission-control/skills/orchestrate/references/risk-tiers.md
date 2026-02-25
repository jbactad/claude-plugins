# Risk Tiers

Four-tier risk classification system that determines the level of oversight, review, and human approval required for each task in a mission.

---

## Tier Overview

| Tier | Level | Blast Radius | Rollback | Approval | Review |
|------|-------|-------------|----------|----------|--------|
| 0 | Low | Read-only or trivial writes | Easy (git reset) | None | Optional |
| 1 | Medium | User-visible changes | Moderate (revert commit) | Auto | Required (non-author) |
| 2 | High | Security, compliance, data | Difficult (migration rollback) | Human (tier2+) | Adversarial + checklist |
| 3 | Critical | Irreversible or regulated | Impossible or very costly | Explicit human | Two-step + contingency |

---

## Tier 0 — Low Risk

**Characteristics:**
- Read-only operations (research, analysis, exploration)
- Low blast radius changes (documentation, comments, logging)
- Easy rollback via `git checkout` or `git reset`
- No user-visible behavior change
- No security implications

**Examples:**
- Codebase exploration and architecture mapping
- Adding or updating code comments
- Updating documentation files
- Adding debug logging
- Fixing typos in non-user-facing strings
- Running read-only analysis scripts

**Controls:**
- Basic input validation (ensure agent has correct file paths)
- Rollback step: `git checkout -- <files>` if changes are unwanted
- No review required (but recommended for learning)

**Model assignment:** haiku (cost-efficient for low-risk work)

---

## Tier 1 — Medium Risk

**Characteristics:**
- User-visible changes (UI, API responses, behavior)
- Moderate impact if wrong (bug introduced, feature broken)
- Rollback via git revert of the commit
- Changes to application logic, components, or services
- New files or significant modifications to existing files

**Examples:**
- Adding a new UI component or page
- Modifying API endpoint behavior
- Refactoring existing functions
- Adding or modifying tests
- Changing configuration files
- Adding new dependencies

**Controls:**
- Independent review by a non-author agent (reviewer agent, not the implementer)
- Validation: run existing test suite + write at least one negative test
- Rollback note: document which commit(s) to revert if issues found
- File ownership: each file assigned to exactly one agent

**Model assignment:** sonnet (balanced capability for standard implementation)

---

## Tier 2 — High Risk

**Characteristics:**
- Security implications (authentication, authorization, input validation)
- Compliance impact (data handling, privacy, audit trails)
- Data model changes (database schema, migrations)
- Cross-cutting changes affecting multiple modules
- Difficult rollback (requires migration reversal or data fixup)

**Examples:**
- Modifying authentication or authorization logic
- Changing database schema or adding migrations
- Modifying encryption, hashing, or token handling
- Updating dependency versions with breaking changes
- Changing build or deployment configuration
- Modifying data serialization or API contracts

**Controls:**
- Dedicated reviewer agent (not the implementer, not the planner)
- Adversarial review: reviewer actively tries to break the implementation
- Failure-mode checklist (see below): all 5 questions answered before approval
- Go/no-go checkpoint: present findings to supervisor before proceeding
- Staged rollout: implement behind a feature flag or in a separate branch
- Rollback plan: documented steps to reverse the change including data migration

**Model assignment:** sonnet or opus (depending on complexity; prefer opus for security-sensitive work)

---

## Tier 3 — Critical Risk

**Characteristics:**
- Irreversible actions (data deletion, production deployment, external API calls)
- Regulated data (PII, financial, health records)
- Actions that cannot be undone or are extremely costly to reverse
- External side effects (sending emails, webhooks, third-party integrations)

**Examples:**
- Deleting data or dropping database tables
- Modifying production deployment pipelines
- Changing code that handles PII or financial data
- Integrating with external payment or notification services
- Modifying backup or disaster recovery procedures
- Any operation involving regulated compliance requirements

**Controls:**
- Minimal scope: break into the smallest possible unit of work
- Explicit human confirmation: pause execution and ask the user before proceeding
- Two-step verification: implement in staging/branch, verify, then apply to target
- Contingency plan: documented recovery procedure before execution begins
- Audit trail: log every action with timestamp, agent, and rationale
- No autonomous execution: always requires human in the loop

**Model assignment:** opus (maximum capability for critical decisions; human confirms output)

---

## Failure-Mode Checklist

Before approving any Tier 2 or Tier 3 task, the reviewer must answer all five questions:

| # | Question | Required Answer |
|---|----------|----------------|
| 1 | **What breaks if this change has a bug?** | Specific impact description (e.g., "users cannot log in") |
| 2 | **What is the rollback procedure?** | Step-by-step reversal plan (e.g., "revert commit X, run down migration") |
| 3 | **What edge cases could cause data corruption?** | List of edge cases with mitigations (e.g., "concurrent writes — handled by DB transaction") |
| 4 | **Does this change affect authentication, authorization, or data privacy?** | YES/NO with explanation. If YES, specify which controls are in place |
| 5 | **Has the change been tested with invalid, malicious, and boundary inputs?** | YES with evidence (test names/results) or NO with justification |

If any question cannot be answered satisfactorily, the task must not proceed. Escalate to human review.

---

## Model Escalation Rules

When a task fails and `retryOnFailure` is enabled, the model used for retry depends on the task's risk tier.

| Risk Tier | Attempt 1 | Attempt 2 (retry) | Attempt 3 (escalation) | Attempt 4 (split) |
|-----------|-----------|-------------------|----------------------|-------------------|
| Tier 0 | haiku | haiku (add error context) | sonnet | Split with haiku |
| Tier 1 | sonnet | sonnet (add error context) | opus | Split with sonnet |
| Tier 2 | sonnet | opus | opus (+ human review) | Human decision |
| Tier 3 | opus | opus (+ human review) | Human takeover | N/A |

**Rules:**
- Tier 0 tasks start with the cheapest model and escalate slowly.
- Tier 1 tasks start with sonnet; escalate to opus only on second failure.
- Tier 2 tasks never drop below sonnet; bring in human review on second retry.
- Tier 3 tasks always use opus; any failure triggers human involvement.
- After `maxRetries` exhausted, the supervisor must decide: split, reassign, or escalate to human.
- Always include error output from previous attempts in the retry prompt.

---

## Adaptive Execution Table

How risk tier interacts with other mission settings:

| Setting | Tier 0 | Tier 1 | Tier 2 | Tier 3 |
|---------|--------|--------|--------|--------|
| **Approval required** | No | No (auto) | Yes (`tier2+`) | Yes (always) |
| **Review agent** | Optional | Required (non-author) | Required (dedicated) | Required + human |
| **Test requirement** | None | Existing tests pass | Existing + new tests | Existing + new + adversarial |
| **Worktree isolation** | Optional | Recommended | Required | Required |
| **Concurrent execution** | Unlimited | Up to `maxConcurrentAgents` | Sequential preferred | Sequential only |
| **Checkpoint frequency** | End of mission | Per wave | Per task | Per action |
| **Rollback documentation** | Not required | Commit hash noted | Full rollback plan | Contingency plan + dry run |
| **Retry strategy** | Auto-retry | Auto-retry with escalation | Retry with human review | Human decides |
| **Budget guard** | Warn at 80% | Warn at 60% | Warn at 40% | Warn at 20% |

---

## Assigning Risk Tiers

When decomposing a mission into tasks, assign each task a risk tier using this decision tree:

```
Is the task read-only (no file writes, no side effects)?
  └─ YES → Tier 0
  └─ NO ↓

Does the task modify security, auth, data models, or compliance logic?
  └─ YES → Tier 2 (minimum)
  └─ NO ↓

Is the action irreversible or does it affect regulated data?
  └─ YES → Tier 3
  └─ NO ↓

Does the task produce user-visible changes?
  └─ YES → Tier 1
  └─ NO → Tier 0
```

When in doubt, assign the higher tier. It is always safe to over-classify; under-classification risks unreviewed damage.

---

## Overriding Risk Tiers

Risk tiers can be adjusted at multiple levels:

1. **Project settings** (`.claude/mission-control.local.md`): Set `requireApproval: always` to treat all tasks as Tier 2+.
2. **Mission scope**: Override default tier for the entire mission (e.g., "this is a security audit, minimum Tier 2").
3. **Task card**: Override tier for individual tasks when decomposition reveals different risk.
4. **Supervisor decision**: During execution, the supervisor can escalate a task's tier if unexpected complexity or risk emerges.

Tier can only be escalated at runtime, never downgraded without human approval.
