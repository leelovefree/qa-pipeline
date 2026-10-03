---
description: Stage 5 — commit spec/cases/flows on qa/<TICKET-ID> and open the PR (a human reviews and merges)
argument-hint: <TICKET-ID> [app]
---
Stage 5 for: $ARGUMENTS

1. Confirm the branch is `qa/<TICKET-ID>` and `bin/qa-check <app>` passes.
2. Show the human `git status` and the list of files to commit (only under `apps/<app>/specs` and `apps/<app>/tests`). Wait for their OK.
3. After the OK: commit with message `<TICKET-ID>: <feature> spec, cases, flows`, push, and `gh pr create` with the ticket link, the rule IDs covered, and the last `bin/qa` result. Never merge — a human approves and merges.
