---
description: Stage 2 — extract an atomic spec from a ticket (manual flow, own session)
argument-hint: <TICKET-ID> [app] [no-jira-write]
---
Stage 2 for: $ARGUMENTS

1. Make sure you are on branch `qa/<TICKET-ID>`: if not, `git fetch origin main` then `git switch qa/<TICKET-ID>` (or `git switch -c qa/<TICKET-ID> origin/main` when it does not exist). Same branch name as `bin/qa-auto`, so the automatic and manual flows can hand over to each other. Stop if there are uncommitted tracked changes.
2. Use the `spec-extractor` agent for the ticket (and app, if given; otherwise it works it out from `bin/qa apps`). If the arguments contain `no-jira-write`, tell the agent: write `open-questions.md` only, do NOT post any comment to the tracker — the human posts it.
3. Show the result: the path of `spec.md` (or `open-questions.md`) and the rule IDs. Stop. A human must read `spec.md` before Stage 3. Do not start Stage 3 in this session.
