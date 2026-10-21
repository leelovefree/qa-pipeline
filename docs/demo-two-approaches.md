# AI in QA Testing — Two Approaches, One Workflow

**Purpose of this file:** fact base for building a demo slide deck. Paste it into ChatGPT (or any LLM) together with the prompt in section 0.
**Date:** 2026-10-08. **Currency:** USD (as reported by the Claude CLI / OpenAI usage).

---

## 0. Prompt to give ChatGPT with this file

> You are helping a QA engineer build a ~15–20 slide deck titled "AI in QA Testing: two approaches, one workflow". Use ONLY the facts in the attached file; do not invent numbers, tools or results. Where the file says "not measured", "not verified" or "known gap", keep that wording honest on the slide (e.g. in a "Limits" box). Audience: engineering + QA leadership. The deck must cover these five themes, in this order, each comparing Approach A and Approach B:
> 1. QA process / workflow
> 2. Architecture & technical guardrails
> 3. Effectiveness evaluation
> 4. Context management, token & cost optimization
> 5. Governance & scale-up
>
> Start with one slide showing the shared 8-stage workflow, then one slide per approach with its 3–5 signature traits (section 3), then the five themes, then a closing slide "What each approach teaches the other". Provide speaker notes (2–3 sentences per slide). Prefer tables and simple diagrams over long bullet lists.

---

## 1. The shared workflow (same for both approaches)

Both projects implement the same QA lifecycle with AI assistance. The difference is **who orchestrates it and where control lives**.

| # | Stage | What happens |
|---|---|---|
| 1 | Intake | A requirement arrives (ticket / document) |
| 2 | Parse & clarify | AI extracts atomic rules; ambiguity stops the pipeline and asks a human |
| 3 | Design cases | AI derives test cases traceable to rules |
| 4 | Human approval | A person approves rules + cases before any automation is written |
| 5 | Generate automation | AI inspects the real app and produces Maestro flows |
| 6 | Replay / regression | Maestro runs the flows — **no AI in the verdict** |
| 7 | Diagnose on failure | Classify: locator drift vs real app defect; repair only what is safe |
| 8 | Report & audit | Results, evidence, model/cost provenance |

**Principles both projects share:** the AI never declares a failure to be a pass; ambiguity halts and asks a human; every autonomous step has a hard ceiling (attempts / actions / time); humans approve before anything is authoritative; artifacts are traceable to their source.

---

## 2. The two approaches in one line each

| | **Approach A — `mobile-test-lab`** | **Approach B — `qa-pipeline`** |
|---|---|---|
| Philosophy | **Engine-first:** deterministic code wraps the model | **Process-native:** AI agents work inside the team's existing tools |
| Orchestrator | A Node.js coordinator (state machine) | Humans + Jira labels + GitHub PRs; `bin/qa-auto` driver chains `claude -p` sessions |
| Model's role | A bounded function: input → schema-validated JSON | An agent with tools that reads/writes files in the repo and inspects the app via Maestro MCP |
| Control lives in | **Code** (validators, compiler, locks, hashes) | **Process + CI** (human gates, Jira labels, PR review, spec-integrity workflow) with code guardrails at runner/CI level |
| Platform / app | One bundled demo shop app (Android in the analysed snapshot; iOS reported by the owner for the latest version) | iOS "ShopDemo" simulator build, multi-app layout (`apps/<app>/`) |
| Model provider | OpenAI (Responses API), configurable model per role | Anthropic Claude (Claude Code CLI), model per agent |
| Human interface | Local web dashboard | Jira (QA never has to open the repo) + GitHub PRs |

---

## 3. Signature traits (3–5 per approach — use these for the "approach" slides)

### Approach A — mobile-test-lab: "Engine-first, guardrails in code"

1. **Deterministic coordinator; the model is just a function.** Seven stages (requirements → cases → automation → replay → repair → review → report) are driven by a state machine. Each AI stage is one call returning strict JSON (`additionalProperties:false`). Stages that generate content are immutable once completed.
2. **The model never writes test scripts directly.** It emits steps from a 5-action vocabulary (`launch`, `tapId`, `inputText`, `assertText`, `assertId`); a code compiler turns them into Maestro YAML (max 20 flows × 100 steps, regex-escaped assertions, `clearState` enforced).
3. **Guardrails are code, not prompts.** Prompts are 1–3 lines; rules are enforced by validators: source quotes must be exact substrings of the input, every requirement must be covered by a case, every expected value must appear as an assertion in its flow, generated selectors must have been *observed* on a real screen, case approval is bound to content hashes.
4. **Evidence-backed repair that cannot hide a real bug.** Repair may only replace a resource ID that matches exactly one element in the current UI hierarchy, never touches assertion IDs, allows max 2 attempts, must pass the **full suite twice**, and the original failure is always preserved. A real defect build stays red.
5. **Rehearsal mode + dashboard for reliable demos.** "Fixture rehearsal" runs real device execution with predetermined artifacts (zero model calls); three app builds (baseline / locator-change / defect) demonstrate repair vs genuine failure.

### Approach B — qa-pipeline: "Process-native, human-gated, measured"

1. **Lives inside the tools the team already uses.** Jira label `qa-auto` → spec → cases → one approval label `qa-approved` → flows → local test → PR → CI. QA works in Jira; a human merges the PR.
2. **One agent and one session per stage.** `spec-extractor`, `case-designer`, `automation-writer` (+ `flow-fixer`) each run in a fresh `claude -p` session with an explicit tool allowlist, a dollar ceiling and a timeout. State is read from files on branch `qa/<TICKET>` and the PR — not from chat memory.
3. **Spec integrity and human triage.** A failing test is never "fixed" by editing its spec. A CI check blocks PRs that change a spec and a flow together unless a human adds `spec-change-approved`. Every red is triaged by a person: A app bug / B ticket wrong / C AI misread / D requirement changed.
4. **The verdict belongs to the runner, not an LLM.** CI (`regression.yml`) has zero AI calls; pass/fail is Maestro's exit code. Local "green" requires every rule to have a flow. Known app bugs are tagged `known-bug` with a ticket key and excluded from CI, never silently deleted.
5. **Measured and scalable by design.** Real model/token/cost per stage are logged (`runs.jsonl`); multi-app layout, build published by the app repo → CI dispatch, nightly + smoke tag. Typical cost: **$0.81–$1.38 per ticket** (see §6).

---

## 4. Theme 1 — QA process / workflow

### Approach A
- **Input:** Markdown / plain-text requirements (also GitHub issue form "Client requirement"). Max 200,000 characters.
- **Flow:** create run → Requirements → Test design → *(human approves cases in live mode)* → Automation (inspect device, explore, export YAML) → Replay → Repair (if failed) → Review → Report.
- **Two modes:** *Fixture rehearsal* (predetermined artifacts, real device, no model calls) and *Live AI* (OpenAI calls; no silent fallback to fixture output).
- **Human touchpoints:** resolve ambiguities (a new run is required — the stage is immutable), approve generated cases, review draft PRs.
- **GitHub planning layer:** requirement issues → delivery task issues (labels `requirement`, `task`, `priority:P0/P1/P2`, `area:*`, `blocked`) → PR template that checks "generated assertions still represent the approved business expectation".

### Approach B
- **Input:** Jira ticket (JQL from `app.config.yml`, label `qa-auto`).
- **Flow (unattended mode `bin/qa-auto`):** spec → *ambiguity? comment on Jira and wait* → cases → **one combined Jira comment** (rules + cases) → QA adds `qa-approved` → build flows (inspect real app via Maestro MCP) → run locally → up to 3 auto-fix attempts for selectors/timing → open PR (GREEN or draft RED) → human reviews and merges → CI regression.
- **Manual mode (same stages):** `/spec`, `/cases`, `/flows`, `/run`, `/fix`, `/pr` slash commands, one session per stage. QA can switch between auto and manual per ticket by adding/removing the label.
- **Human touchpoints:** answer ambiguity questions, approve rules+cases, review/merge PR, triage every red (A/B/C/D).
- **Evidence in practice:** 8 ticket specs, 32 Maestro flows for the ShopDemo iOS app; tickets SCRUM-8, 9, 11, 12, 13 ran end-to-end through the unattended driver; SCRUM-10 through the manual path (PR #24).

---

## 5. Theme 2 — Architecture & technical guardrails

### Approach A — architecture
```
requirements.md ─▶ [Coordinator: Node state machine] ─▶ artifacts/ (JSON, YAML, evidence) + manifest.json + events.jsonl
                         │  per stage: 1 OpenAI Responses call (strict JSON schema)
                         ├─ Automation: bounded tool loop (inspect_mobile_screen, execute_mobile_steps)
                         ├─ Compiler: JSON steps ─▶ Maestro YAML (code, not model)
                         ├─ Device worker: adb / Maestro CLI, one exclusive lock per device
                         └─ Dashboard (local web UI, binds 127.0.0.1)
```
**Guardrails enforced in code (verified by reading `src/core/*.mjs`):**

| Guardrail | Mechanism |
|---|---|
| Output shape | Strict JSON schema on every call; validator rejects unexpected or missing fields |
| Traceability | Requirement `sourceQuote` must be an exact substring of the input; unique IDs |
| Ambiguity halts | Non-empty `ambiguities` blocks the Cases stage |
| Coverage | Every requirement must be linked to ≥1 case, else error |
| Assertion preservation | Every case's `expected` string must appear as an `assertText`/`assertId` step in its flow |
| Selector honesty | Tap/assert selectors must have been observed in a captured UI hierarchy; unobserved ones are rejected before touching the device |
| Action vocabulary | Only 5 actions; no arbitrary commands; selectors regex-validated |
| Bounded exploration | 12 tool rounds, 40 actions, 4 calls per round, 120 s per request, 10 min per stage, 12,000 max output tokens per request |
| No fake green | Replay must return exactly one authoritative result per script; `passed` is computed from results; review `approved` is forced to false if replay failed |
| Safe repair | Locator-only; new ID must match exactly one element; cannot modify assertion IDs; max 2 attempts; candidate must pass 2 complete replays; original failure retained |
| Approval integrity | Case approval stores hashes of cases, requirements and input; changed content invalidates approval |
| Concurrency | Cross-process run lock (recovers dead owners), one stage at a time per run, one device lock |
| Privacy | Server binds to 127.0.0.1; `store:false` on API calls; `.env` ignored by Git; "no real customer data" rule |

*Note:* in the analysed snapshot the "independent" review role uses the same provider (OpenAI) and, by default, the same model setting as other roles — independence is a separate invocation with different instructions, not a different model.

### Approach B — architecture
```
Jira ticket ─▶ bin/qa-auto (Python driver) ─▶ claude -p session per stage (allowlist + $ ceiling + timeout)
   spec-extractor ─▶ case-designer ─▶ [QA approves in Jira] ─▶ automation-writer (Maestro MCP inspects real app)
                                                    │                       └─ flow-fixer (≤3 attempts, selectors/timing only)
                                                    ▼
                          bin/qa run (Maestro, exit code = verdict) ─▶ PR on branch qa/<TICKET> ─▶ human merge
GitHub Actions: regression.yml (zero AI) · qa-check.yml · spec-integrity.yml · app-<app>.yml (when to run)
```
**Guardrails (verified in repo):**

| Guardrail | Mechanism |
|---|---|
| Verdict | `bin/qa` returns Maestro's own exit code; `regression.yml` contains no AI step; `maestro test --analyze` is forbidden in CI |
| Build identity | `bin/qa install` refuses a build whose bundle id differs from the app's `app_id` |
| Coverage | `bin/qa-check`: every spec rule must appear in a CASES.md (error); case without flow (warning) |
| Known bugs | Flow tagged `known-bug` must carry a real ticket header (`# Known-bug: KEY-123`); excluded from CI; new `known-bug` tags in auto-generated PRs are blocked (PR #19) |
| Spec integrity | CI blocks spec + flow edits in the same PR without human label `spec-change-approved` |
| False-green detection | Auto-PR is GREEN only if every rule has a flow *and* tests pass (fix for a real false-green found on SCRUM-9, PR #12) |
| Autonomy ceilings | Per stage: spec $1.5 / 15 min, cases $2.0 / 15 min, build $12 / 60 min, fix $4 / 20 min; max 3 fix attempts; flow-fixer may not touch assertions/specs/CASES |
| Infra isolation | Dedicated simulator `qa-auto` created and deleted per run (fixed recurring `DeviceUnreachable` failures; 3/3 pass after the change) |
| Secrets | Jira credentials only in `~/.config/qa-auto/env`; test accounts/tokens in CI secrets; no real customer/rider data |
| Authority | Agent authority ends at "propose": nothing reaches `main` without a human-approved PR |

**Known gaps (be honest on the slide):** no daily spend cap yet (only per-stage ceilings); GitHub branch-protection not verified; `bin/qa-auto` has no automated tests of its own; flows still contain hard-coded demo credentials and duplicated login steps; Android runner not implemented; Stage 7 (repair-agent) and Stage 8 (reporter) are planned, not built.

---

## 6. Theme 3 — Effectiveness evaluation

**Be explicit on the slide: neither project has a defect-detection rate, flakiness rate or manual-effort comparison. The evidence below is demonstration evidence from small samples.**

### Approach A — what exists
- **Demonstrated scenario (fixture rehearsal, real Android execution):** baseline build passes N times (default 5) → locator-change build fails → repair proposes the ID swap, candidate passes twice, review approves, promoted → a genuine-defect build fails and repair refuses to promote (assertions unchanged, failure retained).
- **Framework tests:** ~600 lines of pipeline tests (e.g. "runner cannot fabricate green with empty results", "real assertion defect prevents candidate promotion", "exploration rejects unobserved actions before touching the device", "promotion requires two complete passing candidate suites") plus issue-worker tests.
- **Not verified:** the README itself states the live-AI path has not been verified against a real model in this snapshot (mocked provider tests do not substitute); generated-test quality and repair accuracy "must be measured against the target app". In fixture mode the repair proposal and review are predetermined — the rehearsal proves the pipeline's guardrails, not the model's repair ability.
- *Analysis note:* I read the code; I did not execute it.

### Approach B — what exists (real runs)
| Ticket | Mode | Agent time (sum of stages) | Cost | Outcome |
|---|---|---|---|---|
| SCRUM-8 | unattended | 138 s | $0.91 | 2 rules → 2 flows → green after 3 auto-fix attempts → PR #8 |
| SCRUM-9 | unattended | 180 s | $1.35 | exposed a false green (no flow generated) → fixed (PR #12) |
| SCRUM-11 | unattended | 204 s | $1.38 | red `DeviceUnreachable` → led to dedicated-simulator fix (PR #17) |
| SCRUM-12 | unattended, clean run | 212 s | $1.32 | 3 flows, PR #18 GREEN, no infra errors |
| SCRUM-13 | unattended (after model tuning) | 234 s | $0.81 | green; ~40% cheaper than the earlier ~$1.35 run |
| SCRUM-10 | manual slash commands | — | — | PR #24 merged; 5/6 flows pass locally, 1 red = known app bug SCRUM-7 (triage A) |

- **Real defect found and tracked:** `MINUS_DISABLED_AT_MIN` — the app does not disable "−" at quantity 1 → bug SCRUM-7; test stays red locally, tagged `known-bug`, excluded from CI.
- **Process defects found by running it for real:** false green (no flows, PR #12), orphaned Maestro driver + shared simulator causing `DeviceUnreachable` (PR #17), whole-module runs picking up unrelated flaky/known-bug flows (fixed by scoping to `<module>/<feature>`).
- **CI:** a full run of the earlier 21-flow suite took ~12 min, ~80% of it sequential test time; a 6-flow `smoke` tag was added for PRs.
- **Not measured:** flake rate over time, escaped-defect rate, comparison with hand-written tests, time saved vs manual.

---

## 7. Theme 4 — Context management, token & cost optimization

### Approach A
- **Context = explicit artifacts.** Each stage receives only the prior artifacts it needs (e.g. repair gets failure + fresh UI hierarchy + original flows); outputs are saved as hashed JSON; nothing relies on chat history. `store:false` means no provider-side conversation retention.
- **Cost controls present:** per-role model and reasoning effort (defaults: requirements/report `low`, others `medium`); bounded exploration (12 rounds / 40 actions / 12k output tokens per request / 10-min stage timeout); **replay and rehearsal use zero model calls**; token usage summed per stage and stored with prompt hash and input hash.
- **Not present:** no dollar budget and no cost estimator (stated in the README: limits are execution bounds, "not a guaranteed dollar-spend cap").
- **Risk to mention (not measured):** during live exploration the full conversation, including UI hierarchies returned by each tool call, is resent every round.

### Approach B
- **Context = files + one session per stage.** Sessions are short and isolated; the current stage is derived from files on the branch and the PR; shared rules live in `CLAUDE.md` and `docs/requirements.md` sections that each agent reads on demand.
- **Cost controls present:** hard `--max-budget-usd` and timeout per stage; tool allowlist per session; `claude-sonnet` set per agent (moving the builder from Opus to Sonnet, plus splitting out `case-designer`, cut an end-to-end ticket from ~$1.35 to **$0.81**); real per-model tokens and cost recorded from the CLI's `modelUsage` for every stage (including a cheap Haiku helper); CI has zero AI cost; only affected module/feature is re-run; `smoke` tag for fast PR checks.
- **Typical cost per ticket:** $0.81–$1.38 (5 real runs). Stage breakdown (SCRUM-13): spec $0.32, cases $0.17, build $0.32.
- **Planned / not done:** daily spend cap, CI caching (Maestro/JDK), matrix sharding of the regression run.

---

## 8. Theme 5 — Governance & scale-up

### Approach A
- **Governance:** GitHub issues as the review boundary (requirements approved by a person before tasks are created); PR template with assertion-preservation checklist; approvals bound to content hashes; full provenance per stage (provider, model, prompt hash, input hash, token usage, response IDs).
- **Autonomous issue worker (note: builds the lab tool itself, not target-app tests):** polls approved GitHub task issues (`task` + `agent:ready`, dependencies closed), creates an isolated worktree, runs Codex in a `workspace-write` sandbox, then **independently** runs trusted verification commands, opens a **draft PR**, never merges or closes the issue; issue text is treated as untrusted data.
- **Scale-up path (from its roadmap):** other model providers, arbitrary app packages, device farm, CI replay, client-document approval workflow, production hardening. Owner reports iOS support in the latest version (not present in the analysed snapshot — confirm before presenting). Currently one app, one device, one local operator, no CI workflows, no Jira integration.

### Approach B
- **Governance:** the 7 non-negotiable principles (AI never converts fail→pass; ambiguity halts; every step has a ceiling; no merge without human PR approval; traceability to ticket/model/cost; secrets in CI only; spec integrity); A/B/C/D failure triage; CI gates `qa-check` and `spec-integrity`; labels as visible state (`qa-needs-info`, `qa-ready-for-review`, `qa-approved`, `qa-pr-open`, `qa-red`, `qa-error`).
- **Scale-up path (implemented):** repo layout `apps/<app>/` (one framework, many apps); the app's own repo publishes a build and dispatches CI; per-app caller workflows; pinned builds; nightly + smoke.
- **Scale-up path (planned):** Stage 7 repair-agent (selector-only repair, refuse real bugs), Stage 8 reporter (model, attempts, cost, approver per run), neutral runner (GitHub Actions macOS / Mac mini) instead of the QA's own Mac, service account for Jira, daily cost cap, CI sharding, Android runner.
- **Open governance items:** data-handling review for company data/PII before scaling to real projects; branch protection not yet verified.

---

## 9. What each approach can learn from the other (closing slide)

| Approach A → B | Approach B → A |
|---|---|
| Move more rules from prompts into code in Stages 2–4 (coverage and ambiguity gates, "selector must be observed", assertion-preservation check) | Connect to the tools teams already use (Jira, PRs, CI) so QA does not need a separate UI |
| Evidence-backed repair for Stage 7: locator-only, two clean full-suite replays, original failure retained, independent review | Real cost and token logging per stage, hard dollar ceilings, model-per-role tuning measured on real tickets |
| Hash-bound approvals and fixture rehearsal for reliable live demos | Multi-app layout, CI regression with zero AI, known-bug handling, dedicated simulators for stability |
| Two-build fixture (locator change vs real defect) to prove the repair-agent cannot "heal" a real bug | Human triage taxonomy A/B/C/D and spec-integrity gate |

**One-sentence framing for the opening slide:** *Same workflow, two control models — A wraps the model in deterministic code; B wraps the agent in a human-gated process.*

---

## 10. Source notes and caveats

- **Approach A** was analysed by reading the code and docs in the folder `mobile-test-lab-main` (files dated 2026-09-08): `README.md`, `IMPLEMENTATION_PLAN.md`, `config/*`, `prompts/*`, `src/core/*`, `src/device.mjs`, `scripts/*`, `.github/*`, `tests/*`. It was **not executed**. That snapshot's device layer is Android/ADB only; iOS support in the latest version is reported by the project owner and should be confirmed.
- **Approach B** figures come from the repository (`bin/`, `.github/workflows/`, `.claude/agents/`, `docs/`) and from the logged `runs.jsonl` of tickets SCRUM-8/9/11/12/13 on one developer's machine. Samples are small (5 unattended runs, 1 app).
- No claim is made that either approach reduces total QA effort or increases defect detection; neither has been measured.
