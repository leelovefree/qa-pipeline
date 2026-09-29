# qa-pipeline

App-agnostic, AI-assisted mobile QA automation pipeline, packaged as a **Claude Code plugin** plus a
**reusable GitHub Actions workflow**. It turns a ticket into a reviewed, CI-running Maestro regression
test, with a human gate at every step:

```
ticket ─► spec.md ─► CASES.md ─► <case>.yaml ─► PR (human) ─► CI regression on a prebuilt app (no AI)
 Stage 1   Stage 2     Stage 3      Stage 4       Stage 5          Stage 6
```

The framework never builds the app. The app repo builds it (however it builds) and hands over an
artifact; the framework installs that artifact and runs the app repo's flows. Full design:
[`skills/pipeline-rules/requirements.md`](skills/pipeline-rules/requirements.md).

## What's in here

| Path | What |
|---|---|
| `agents/spec-extractor.md` | Stage 2 — ticket → `specs/<TICKET>/spec.md` (or `open-questions.md` + stop) |
| `agents/automation-writer.md` | Stages 3+4 — spec → `CASES.md` → Maestro flows, selectors only from the live app |
| `skills/pipeline-rules/` | Non-negotiable rules + full design spec, loaded by both agents |
| `.github/workflows/regression.yml` | Stage 6 — reusable workflow, installs a prebuilt artifact, runs Maestro, zero AI |
| `templates/` | Files to copy into an app repo when onboarding |

## Onboarding an app

Prerequisites on the machine running Claude Code: Maestro CLI (`curl -fsSL "https://get.maestro.mobile.dev" | bash`
— **not** `brew install maestro`, that is a different product), the Maestro MCP server registered with an
absolute binary path (`claude mcp add maestro -e JAVA_HOME=<jdk17> -- ~/.maestro/bin/maestro mcp`), and an MCP
server for your ticket tracker.

1. **Config** — copy `templates/qa-pipeline.config.yml` to the app repo root; set `app.app_id`,
   `app.platform`, `tracker.mcp_server`, and `paths` (use `qa-tests` rather than `tests` if the repo already
   has a `Tests/` folder — macOS filesystems are case-insensitive).
2. **Plugin** — copy `templates/.claude/settings.json` into the app repo's `.claude/` so everyone who opens
   the repo in Claude Code is offered the plugin. Or install it yourself:
   ```bash
   claude plugin marketplace add leelovefree/qa-pipeline
   claude plugin install qa-pipeline@qa-pipeline
   ```
   Agents are then available as `qa-pipeline:spec-extractor` and `qa-pipeline:automation-writer`.
3. **CI** — copy `templates/.github/workflows/qa.yml`; replace the `build` job with the app's own build. It
   must upload **one** artifact:
   - iOS: a zipped **simulator** build (`*.app.zip`, `ditto -c -k --keepParent`). An `.ipa` is a device
     build and cannot run on a simulator — ask the app's CI to export a simulator build alongside it.
   - Android: an `.apk` (CI support not implemented yet).

   Alternatively pass `app_url:` (a direct download URL) instead of `app_artifact:`.
4. **Private repos** — because this repo is private, its reusable workflow is only callable after
   enabling *Settings → Actions → General → Access → "Accessible from repositories owned by the user"*.

### `regression.yml` inputs

| Input | Default | |
|---|---|---|
| `platform` | — (required) | `ios` \| `android` (android: not implemented yet) |
| `app_artifact` / `app_url` | — | exactly one: artifact name from the same run, or a download URL |
| `tests_dir` | `qa-tests` | pipeline-managed flows |
| `extra_flows_dir` | — | optional additional folder (e.g. hand-written `.maestro/` smoke flows) |
| `include_tags` | — | e.g. `smoke` for a fast PR subset |
| `ios_device` | `iPhone 16` | simulator name on the runner image |
| `runner` / `timeout_minutes` | `macos-15` / `30` | |

## Running a ticket through the pipeline

One Claude Code session per stage, in the app repo:

1. `Use qa-pipeline:spec-extractor on <TICKET-ID>` → read `specs/<TICKET-ID>/spec.md` yourself.
2. New session: `Use qa-pipeline:automation-writer for <TICKET-ID>, Stage 3 only` → review `CASES.md`.
3. Boot a simulator with the app installed. New session: `… Stage 4` → review and run the flows.
4. Open a PR; CI (`qa.yml` → `regression.yml`) runs the flows against a fresh build. A human merges.

## Versioning

App repos pin `regression.yml@<tag>`. Tag every change to the workflow or agents (`v0.1.0`, …) and bump
the pin in each app deliberately.

## Status

Phase 1+2 of the design spec: proven end-to-end on one iOS app
([ios-shop-demo](https://github.com/leelovefree/ios-shop-demo)). Not built yet: Stage 7 (repair-agent),
Stage 8 (reporter), Android CI, per-agent tool locking.
