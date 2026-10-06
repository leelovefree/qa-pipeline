# qa-pipeline — mono QA repo

QA-owned repo for AI-assisted mobile test automation. One framework, many apps. App source code lives in
the dev teams' own repos; this repo only knows **which build to test** (`apps/<app>/app.config.yml`).
Full design spec: `docs/requirements.md` — read the relevant section before working on any stage.

## Layout

```
.claude/agents/            spec-extractor (Stage 2), case-designer (Stage 3), automation-writer (Stage 4), flow-fixer (selector/timing repairs)
.claude/commands/          /spec /cases /flows /run /fix /pr — manual, one session per stage
bin/qa                     runner: install a build + run Maestro flows (same command locally and in CI)
bin/qa-auto                 unattended driver: Jira label `qa-auto` → spec → (QA approves) → tests → PR, in your checkout on branch qa/<KEY>
.github/workflows/
  regression.yml           Stage 6 — HOW to test (reusable, zero AI calls)
  app-<app>.yml            WHEN to test one app (dispatch from app repo, PRs, nightly, manual)
apps/<app>/
  app.config.yml           app_id, platform, build source, tracker
  specs/<TICKET-ID>/       Stage 2 output
  tests/<module>/<feature>/ CASES.md + <REQUIREMENT_ID>.yaml (Stages 3/4)
  reports/                 Stage 8 output (not built yet)
templates/app/             files to copy when adding an app
docs/                      design spec + onboarding guide
```

## Non-negotiable principles

1. AI never declares a fail as a pass — enforced in code, not in a prompt.
2. Ambiguity halts the pipeline and asks a human — never guess at a requirement.
3. Every autonomous step has a hard ceiling (attempts, actions, or time) — no unbounded loops.
4. No code reaches `main` without explicit human PR approval — the agent's authority ends at "propose."
5. Every artifact (spec, test, diff, commit, report) is traceable to its ticket, model version, and cost.

## Stage → actor

| Stage | Actor | Status |
|---|---|---|
| 1. Intake | Human (ticket) | — |
| 2. Parse & Clarify | `spec-extractor` | implemented |
| 3. Design cases | `case-designer` | implemented |
| 4. Observe & Generate | `automation-writer` | implemented |
| 5. Commit & Review | Human (PR in this repo) | process |
| 6. CI Regression | `regression.yml` + `bin/qa` — no AI | implemented |
| 7. Diagnose on failure | `repair-agent` | Phase 3 |
| 8. Report & Audit | `reporter` | Phase 3 |

## Hard guardrails (code-level — do not weaken)

Stage 6 — the test runner decides, not an LLM. `bin/qa` returns Maestro's own exit code; never wrap it
in anything that can turn a failure into a pass, and never add `maestro test --analyze` (AI) to CI.
`bin/qa install` refuses a build whose bundle id differs from the app's `app_id`.

Spec integrity — a failing test is never fixed by editing its spec. No agent edits `spec.md`, a CASES.md
expected result, or a flow assertion to turn a failing test into a passing one. Spec changes come from the
source ticket (re-run Stage 2) or a human-approved PR that states the reason. Triage every fail first:
A app bug → bug ticket, test stays red; B ticket wrong → fix ticket, re-run Stage 2; C AI misread ticket →
spec PR with reason; D requirement really changed → new ticket. See `docs/huong-dan-qa-pipeline.md` §9.1.

Stage 7 (future) — a repair-agent's self-report is never trusted on its own:
```js
if (!replay.passed) review.approved = false;
```

## Working rules

- Everything for one app stays inside `apps/<app>/`. Framework changes (`bin/`, `.github/`, `.claude/`)
  affect every app — their PRs run every app's suite.
- One Claude Code session per pipeline stage. Do not run Stage 2 through Stage 4 in one continuous chat.
- Test accounts and tokens go in CI secrets, never in the repo. No real customer/rider data.
