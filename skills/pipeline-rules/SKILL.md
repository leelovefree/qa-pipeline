---
name: pipeline-rules
description: Non-negotiable rules, stage map and file contracts of the qa-pipeline AI QA automation
  pipeline (ticket → spec → cases → Maestro flows → PR → CI). Load before running or changing any
  pipeline stage in an app repo that has a qa-pipeline.config.yml, or when editing the pipeline itself.
---

# qa-pipeline — rules for every stage

Full design spec: `requirements.md` in this skill's folder. Read the section for the stage you are
working on before starting it.

## Non-negotiable principles

1. AI never declares a fail as a pass — enforced in code, not in a prompt.
2. Ambiguity halts the pipeline and asks a human — never guess at a requirement.
3. Every autonomous step has a hard ceiling (attempts, actions, or time) — no unbounded loops.
4. No code reaches the default branch without explicit human PR approval — the agent's authority ends
   at "propose."
5. Every artifact (spec, test, diff, commit, report) is traceable to its ticket, model version, and cost.

## Where things live

- **This plugin (framework, app-agnostic):** agents, these rules, the reusable CI workflow
  (`.github/workflows/regression.yml` in the qa-pipeline repo).
- **The app repo (per app):** `qa-pipeline.config.yml` (app id, platform, tracker, paths), and the
  pipeline's per-app artifacts — `<paths.specs>/<TICKET-ID>/`, `<paths.tests>/<module>/<feature>/`,
  `<paths.reports>/<TICKET-ID>/`. Never write framework files into an app repo or app files into the
  framework.
- Anything listed under `paths.protected` in the config (hand-written flows, app source, …) is never
  written, migrated or deleted by any pipeline stage.

## Stage → actor

| Stage | Actor |
|---|---|
| 1. Intake | Human (ticket) |
| 2. Parse & Clarify | `spec-extractor` agent |
| 3. Design cases | `automation-writer` agent (splits into `case-designer` in Phase 3) |
| 4. Observe & Generate | `automation-writer` agent |
| 5. Commit & Review | Human (PR) |
| 6. CI Regression | reusable `regression.yml` — installs a **prebuilt app artifact**, runs Maestro, zero AI calls |
| 7. Diagnose on failure | `repair-agent` — not built yet (Phase 3) |
| 8. Report & Audit | `reporter` — not built yet (Phase 3) |

## Hard guardrails (code-level — do not weaken)

Stage 6 — the test runner decides, not an LLM:
```js
result.passed = results.every(r => r.status === "passed");
```
`maestro test` already behaves this way (deterministic exit code). This is why Stage 6 must stay plain
Maestro CLI with zero LLM calls, and why the pipeline tests a prebuilt artifact instead of building it.

Stage 7 — a repair-agent's self-report is never trusted on its own:
```js
if (!replay.passed) review.approved = false;
```

## Session discipline

One Claude Code session per pipeline stage. Do not run Stage 2 through Stage 4 in one continuous chat.
