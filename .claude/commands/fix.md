---
description: Repair selectors/timing in a failing flow (never assertions, never the spec)
argument-hint: <flow file or REQUIREMENT_ID>
---
Failing flow: $ARGUMENTS

First triage: if the failing assertion may be a real app difference (wrong value, element the spec says must exist is missing), stop and report `POSSIBLE_APP_BUG` — nothing is edited. Otherwise use the `flow-fixer` agent on the flow. It may only change selectors/timing in existing `apps/<app>/tests/**/*.yaml`; it must not touch any `assert*` line, `spec.md`, `CASES.md`, or add `known-bug` tags. After it finishes, show `git diff` and tell the human to re-run `/run`. Never claim the flow is fixed until `bin/qa` says so.
