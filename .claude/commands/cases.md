---
description: Stage 3 — design test cases (CASES.md) from an approved spec (manual flow, own session)
argument-hint: <TICKET-ID> [app]
---
Stage 3 only for: $ARGUMENTS

Use the `automation-writer` agent, Stage 3 only: write `apps/<app>/tests/<module>/<feature>/CASES.md` from `apps/<app>/specs/<TICKET-ID>/spec.md`. Refuse if `open-questions.md` exists next to the spec. Before writing, check the existing `CASES.md` files for cases that already cover a rule and tell the human about any overlap instead of silently duplicating it. Do NOT write any Maestro flow. Stop and ask the human to review CASES.md (test data, steps, expected results).
