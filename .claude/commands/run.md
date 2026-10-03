---
description: Run flows locally with bin/qa — the runner's exit code is the only verdict
argument-hint: <app> [module/feature]
---
Run: $ARGUMENTS

Run `bin/qa run <app> --module <module/feature> --no-install` (omit `--module` for every flow). Report the runner's own output and exit code verbatim. Do not re-interpret, retry, or declare a pass yourself; a red run is red until the runner says otherwise. On red, triage per `docs/huong-dan-qa-pipeline.md` §9.1 before touching anything.
