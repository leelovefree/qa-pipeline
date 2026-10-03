---
description: Stage 4 — generate Maestro flows from approved CASES.md, inspecting the real app (manual flow, own session)
argument-hint: <TICKET-ID> [app]
---
Stage 4 for: $ARGUMENTS

1. Check a simulator is booted and the build is installed (`bin/qa install <app>` if not). Do not reboot the simulator mid-session.
2. Use the `automation-writer` agent, Stage 4, for the approved `CASES.md`. All its guardrails apply: `inspect_screen` before every selector, at most 15 on-device actions and 5 reasoning rounds per case.
3. Run `bin/qa-check <app>`, show the new flow files, and stop. A human reads each flow and re-runs it once.
