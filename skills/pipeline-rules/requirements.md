# iOS Mobile QA Automation — Implementation Requirements

**Purpose of this document:** a build spec for Claude Code. It defines what to build, the non-negotiable
guardrails, the file/data contracts, and a concrete ordered task list. Hand this file to Claude Code as-is
(e.g. `claude "Read ios-qa-automation-requirements.md and start with Phase 1, task 1"`) and it can execute
against it directly.

**Scope:** AI-assisted test automation for one iOS app, using Claude Code + MCP as the primary engine and
Maestro as the mobile-automation driver. This is Approach 1 from the Guardrail QA pitch deck — the
Claude-Code-native approach, not the standalone VPS platform (Approach 2).

**Non-negotiable principles (do not relitigate these while building):**
1. AI never declares a fail as a pass — enforced in code, not in a prompt.
2. Ambiguity halts the pipeline and asks a human — the system never guesses at a requirement.
3. Every autonomous step has a hard ceiling (attempts, actions, or time) — no unbounded loops.
4. No code reaches `main` without explicit human PR approval — the agent's authority ends at "propose."
5. Every artifact (spec, test, diff, commit, report) is traceable to its ticket, model version, and cost.

---

## 0. What "runs end-to-end" means here (build this first)

Everything below is the full target design. But the near-term goal is narrower: **get one ticket flowing
through Stages 1–6 for one app, with a human reviewing each intermediate file, and CI actually re-running
the result.** Nothing else matters until that works once.

Concretely, defer these until the basic loop is proven — they are optimization/hardening, not part of
"it runs":
- Stage 7 (self-healing / repair-agent) — until Stages 1–6 work, there is nothing to self-heal.
- Strict per-agent tool locking (Section 4) — one loosely-configured agent reused across stages is fine
  for the first pass; split and lock down permissions once the flow itself is proven.
- Module-level `CLAUDE.md` (Section 5) — with one app and one module in the pilot, the root file alone is
  enough; split later only if a second module actually needs different rules.
- Cost tiering, prompt caching, Batch API (Section 6) — real optimizations, but premature before there's
  a working baseline to optimize.
- Metrics instrumentation (Section 8) and governance hardening (Section 9) — needed before scaling past
  the pilot, not needed to prove the loop runs.

This corresponds exactly to **Phase 1 + Phase 2** in the build order (Section 11). Stop there, demo it,
then decide whether to continue into Phase 3.

---

## 1. Tech stack decisions (fixed)

| Layer | Choice | Why |
|---|---|---|
| Orchestration | Claude Code, one session per pipeline stage | native to how the team already works; no separate platform to run/maintain |
| Mobile driver | **Maestro** | YAML flows are easy for an LLM to generate and to diff/review; MCP server for Maestro is free and already maintained |
| Fallback driver | Appium | only for native/hybrid interactions Maestro can't reach (deep native gestures, complex WebViews) |
| Target device | iOS Simulator (Xcode) for CI; a small pool of physical devices for the pilot's manual spot-check only | simulators are reproducible and free; physical devices are for validating against Maestro's own device-farm gaps |
| Requirement source | Jira ticket or GitHub Issue | wherever the team already tracks work — no new system introduced |
| Spec/case storage | Markdown files committed to the repo (not JSON blobs in a run folder) | version-controlled, human-readable, diffable in PRs, and it's what Spec-Driven-Development tooling (GitHub Spec Kit and similar) already standardizes on |
| CI | whatever the repo already uses (GitHub Actions / Bitrise / etc.) | Step 6 (CI Regression) must run with **zero AI calls** — plain script execution |
| Model | Claude, tiered by step (see Section 6) | cheap model for low-stakes steps, strong model for diagnosis/generation |

---

## 2. Repository structure to create

```
repo/
  CLAUDE.md                          # root rules — see Section 5
  .claude/
    agents/
      spec-extractor.md
      case-designer.md
      automation-writer.md
      repair-agent.md
      reviewer.md
      reporter.md
  specs/
    <TICKET-ID>/
      spec.md                        # normalized requirement spec (temporary, per-ticket)
      open-questions.md              # populated only if ambiguity was found (Step 2)
  tests/
    <module>/
      CLAUDE.md                      # module-level rules, lazy-loaded — see Section 5
      <feature>/
        CASES.md                     # permanent, human-readable test case doc for this feature
        <case-id>.yaml                # Maestro flow file, one per test case, co-located with CASES.md
  reports/
    <TICKET-ID>/
      run-<timestamp>.md             # Step 8 output — see Section 7
  .github/workflows/
    ci-regression.yml                # Step 6 — no AI, plain test runner
```

Key rule: **the case doc and the automation script live side by side, permanently.** Do not delete
`CASES.md` once a script exists — they answer different questions (what should happen vs. what the
robot does) and both get read during future debugging and future ticket work.

---

## 3. The 8-stage pipeline

Each stage below states: trigger, actor, output, and the guardrail specific to that stage. Build them as
separate Claude Code sessions / separate subagent invocations — never as one long-running session that
does all 8 stages back to back.

### Stage 1 — Intake *(Human)*
- **Trigger:** PM/QA opens a ticket with a requirement and acceptance criteria.
- **Output:** a Jira ticket ID or GitHub Issue number. Nothing else — no AI runs yet.

### Stage 2 — Parse & Clarify *(AI — `spec-extractor` agent)*
- **Trigger:** ticket is tagged ready (e.g. label `ai-testable`, or a `/generate-tests` comment).
- **Input:** raw ticket text.
- **Output:** `specs/<TICKET-ID>/spec.md` — a normalized set of atomic, testable rules (Given/When/Then),
  each rule tagged with a requirement ID (Section 8) and a `source_span` (the exact ticket text it came
  from — no rule may exist that doesn't cite one).
- **Guardrail:** if any rule's confidence is low, or any part of the ticket is ambiguous, the agent
  writes `specs/<TICKET-ID>/open-questions.md` and **stops** — it posts the open questions back to the
  ticket and does not proceed to Stage 3 under any configuration. This is a hard gate, not a suggestion.

### Stage 3 — Design cases *(AI drafts, human signs off)*
- **Input:** `spec.md` (must have zero open questions).
- **Output:** `tests/<module>/<feature>/CASES.md` — one entry per rule, each with steps and expected
  result, referencing the requirement ID.
- **Guardrail:** every rule ID in `spec.md` must appear in `CASES.md` at least once (a coverage check,
  can be a simple grep/script, not an LLM judgment call). A human reviews `CASES.md` in the PR before
  automation is written — this is the sign-off checkpoint.

### Stage 4 — Observe & Generate *(AI, bounded — `automation-writer` agent)*
- **Input:** approved `CASES.md`.
- **Output:** one Maestro `.yaml` flow per case, co-located with `CASES.md`.
- **Guardrail (hard):**
  - The agent must inspect the real running app (via the Maestro MCP server / simulator UI hierarchy)
    before writing any selector. It may never write a selector from memory or from guessing at an ID.
  - Both the number of reasoning rounds and the number of on-device actions per case have a ceiling.
    Start with a conservative number (e.g. 15 actions / 5 tool-rounds per case) and tune it during the
    pilot using the metrics in Section 9 — do not treat the starting number as correct, treat it as a
    hypothesis to calibrate.

### Stage 5 — Commit & Review *(Human)*
- The generated `.yaml` files and `CASES.md` are opened as a PR. A human approves before merge — no
  exceptions, no auto-merge path exists in this design.

### Stage 6 — CI Regression *(No AI)*
- Runs on a schedule (e.g. nightly) and on every PR touching `tests/`.
- Plain Maestro CLI execution against the simulator. **Zero LLM calls.** This is deliberate: it is both
  the cheapest part of the pipeline and the part that must behave identically every time.
- Code-level enforcement (put this literally in the runner, not in a prompt):
  ```js
  // the real test runner decides — nothing upstream of this can override it
  result.passed = results.every(r => r.status === "passed");
  ```

### Stage 7 — Diagnose on failure *(AI — `repair-agent`, only runs when Stage 6 is red)*
- **Input:** the failing case's structured result (not raw stdout).
- **Output:** a diagnosis: is this a locator/UI change (safe to auto-repair) or a real product defect
  (must not be touched)?
- **Guardrail (hard, this is the most important one in the whole system):**
  ```js
  // even if the agent reports "approved: true", the gate below is what actually decides
  if (!replay.passed) review.approved = false;
  ```
  Concretely: the agent may propose a patch to the **test** (e.g. an updated `id:` selector) only when
  it can point to evidence that the UI genuinely changed. It must **refuse** to patch anything when the
  failure looks like a real behavior/value bug. It must never delete or weaken an assertion to make a
  test pass — if the proposed patch reduces what a test checks, that patch is auto-rejected regardless
  of what the agent's own diagnosis claims. This is the same anti-pattern to block that a fail-labeled-as-
  pass bug represents, just one layer earlier.
- After a repair patch, the fixed case must be re-run before it's proposed in a PR (same as Stage 5/6).
- A capped number of repair attempts (e.g. 2) — beyond that, escalate to a human rather than keep trying.

### Stage 8 — Report & Audit *(Both)*
- **Output:** `reports/<TICKET-ID>/run-<timestamp>.md` containing: which rules were covered, which model
  ran each step, how many repair attempts were used, human approvals with timestamps, and a link back to
  the ticket and the PR.
- This reuses Git + Jira as the audit trail — do not build a separate audit database for the pilot.

---

## 4. Subagents to create

*(Full target design below. For the first end-to-end pass — Section 0 — it's fine to use one or two
loosely-configured agents, or even plain Claude Code prompts with no `.claude/agents/` files at all, and
split them out once the loop works. Don't build the least-privilege split before there's a working flow
to split.)*

Create each as `.claude/agents/<name>.md` with YAML frontmatter restricting its tools. Least privilege is
the point — a review-only agent must not physically be able to write files, not just be told not to.

| Agent file | Role | Tools allowed | Model tier |
|---|---|---|---|
| `spec-extractor.md` | Stage 2: ticket → rules | Read (ticket text), Write (spec.md only) | mid |
| `case-designer.md` | Stage 3: rules → test cases | Read, Write (CASES.md only) | mid |
| `automation-writer.md` | Stage 4: cases → Maestro flows | Read, Write, Maestro MCP tools | strong |
| `repair-agent.md` | Stage 7: diagnose + patch | Read, Edit (test files only, never app source), Maestro MCP tools | strong |
| `reviewer.md` | sanity-check a proposed patch before it's shown to a human | Read only | cheap |
| `reporter.md` | Stage 8: assemble the run report | Read, Write (reports/ only) | cheap |

Example frontmatter (adapt per agent):
```yaml
---
name: repair-agent
tools: [Read, Edit, mcp__maestro__*]
model: claude-sonnet-5
---
Diagnose the failing case. Propose a patch only when you can cite UI evidence for a locator change.
Refuse and escalate if the failure looks like a product defect. Never weaken or remove an assertion.
```

---

## 5. CLAUDE.md structure

**Root `CLAUDE.md`** (loaded in full, every session, so keep it short — principles and pointers, not
detail):
- The 5 non-negotiable principles from the top of this document.
- The repo layout (point to Section 2 above).
- Which agent handles which stage.
- The two hard code-level guardrails from Stages 6 and 7 (so any session that touches them knows they exist).

**Module-level `tests/<module>/CLAUDE.md`** (only loaded when a session reads files inside that
directory) — put here anything specific to that module: its own Maestro flow conventions, module-specific
fixtures/test accounts, quirks of that part of the app. Do not put project-wide rules here — that's what
the root file is for. Split by module only when there's an actual reason (a module-specific convention),
not just to make files shorter.

**Session discipline:** one Claude Code session per pipeline stage. Do not run Stage 2 through Stage 4 in
one continuous chat — each stage should start a fresh session so it only loads what that stage needs.

---

## 6. Cost controls to implement from day one

- **Model tiering:** cheap model for `reviewer` and `reporter` (low-stakes, mechanical); strong model for
  `automation-writer` and `repair-agent` (the steps that need real reasoning about UI state and code).
- **Prompt caching:** CLAUDE.md and each agent's instructions are identical across runs — structure calls
  so these are cached (cheap re-reads) rather than resent as fresh input every time.
- **Batch API** for anything that doesn't need an immediate answer (e.g. nightly report generation across
  many tickets) rather than synchronous calls.
- **Action ceilings double as cost ceilings** (Stage 4's per-case cap, Stage 7's repair-attempt cap) — a
  runaway loop is a cost problem before it's anything else.
- **Log every model call**: which model, input/output tokens, per ticket — this feeds both the audit
  trail (Section 3, Stage 8) and future budget forecasting. Do not skip this even in the pilot.
- Stage 6 (CI Regression) running at zero AI cost is the single biggest lever — protect that invariant.

---

## 7. Requirement ID scheme

Format: `<MODULE>.<FEATURE>.<RULE>` — for example `CHECKOUT.VOUCHER.APPLY_VALID`.

- Stable across tickets — if the same feature area gets touched by five different tickets over a year,
  the ID scheme should still make sense. Do not use the ticket ID as part of the requirement ID.
- Each rule's record still keeps a `source_ticket` field for history (which ticket first introduced it),
  but the ID itself is ticket-independent.
- `CASES.md` entries and `.yaml` flow filenames both reference this ID, so a human can grep one ID and
  find the requirement, the case, and the automation script together.

---

## 8. Metrics to instrument (Stage 8 report + a lightweight dashboard)

| Metric | Formula | Notes |
|---|---|---|
| Coverage | IDs with a case / total IDs in spec | script-computable, fully automatic |
| Self-heal accuracy | correct repairs / total repairs proposed | requires deliberately building 2–3 known-answer test builds (a locator-only change, and a real-defect change) to check the agent's judgment against a known right answer — this doesn't happen for free during normal operation |
| False-positive rate | repairs that mask a real bug / total repairs proposed | same known-answer builds as above; lower is better |
| Maintenance time saved | (manual hours − AI-assisted hours) / manual hours | pull timestamps from Git/Jira, don't estimate |

Do not publish a fixed target number (e.g. "90% self-heal accuracy") before the pilot has run — calibrate
against the pilot's own data first.

---

## 9. Governance requirements

- No real customer/rider/partner PII or PCI data enters this pipeline at any stage. If a ticket's repro
  steps embed real user data, that must be anonymized before Stage 2 runs.
- Branch protection on `main`: PR-only, minimum 1 human approval, no force-push — enforced server-side,
  not by agreement.
- Changes to any `CLAUDE.md` or `.claude/agents/*.md` file go through the same PR review as code — these
  files define the AI's behavioral rules, so they need the same scrutiny as anything else that changes
  system behavior.
- Because Pandora sits within the EU (Delivery Hero SE), confirm data residency and EU AI Act
  transparency obligations with Security/Legal before running against any real app data — do this before
  the pilot starts, not after.

---

## 10. Pilot scope (fill in before handing to Claude Code)

- App: `[ app / brand name ]`
- Platform: iOS (this document only — Android is a separate, later phase)
- Representative test cases for the pilot: `[ e.g. 5–8 cases, pick a mix of one simple flow and one that has changed recently ]`
- Timeline: `[ number of weeks ]`
- Repo this gets built into: `[ repo path/URL ]`

---

## 11. Build order — hand this to Claude Code as-is

Execute in this order. Do not start a later phase before the previous phase's exit check passes.
**Phase 1 + Phase 2 together are the "runs end-to-end" milestone from Section 0 — the current priority.**
Phase 3 and Phase 4 are explicitly deferred until that milestone is demoed and reviewed.

**Phase 1 — Scaffolding (minimal version)**
1. Create the repository structure in Section 2 (empty files/folders are fine at this point; skip
   module-level `CLAUDE.md` for now — one module in the pilot doesn't need it yet).
2. Write the root `CLAUDE.md` per Section 5.
3. Create one or two working agent prompts covering spec-extraction, case-design, and automation-writing
   — a full split into 6 separately-locked subagent files (Section 4) can wait until after Phase 2's demo.
4. Confirm Maestro is installed and its MCP server is reachable from this Claude Code setup; confirm the
   iOS Simulator can boot the pilot app. **This step is the most likely source of delay — budget extra
   time if signing/provisioning or Maestro's UI-inspection has any friction with this specific app.**
5. *Exit check:* Claude Code can read `CLAUDE.md`, drive Maestro against the booted simulator, and see the
   pilot app's UI hierarchy — no automation logic yet, just wiring.

**Phase 2 — One ticket, end to end, manually gated at every step**
6. Pick one real ticket from Section 10's pilot scope. Run Stage 2 (`spec-extractor`) against it by hand;
   read the resulting `spec.md` yourself before continuing — do not automate this trust step yet.
7. Run Stage 3 (`case-designer`); manually review `CASES.md`.
8. Run Stage 4 (`automation-writer`); manually review the generated `.yaml` flow and run it once yourself
   against the simulator before it goes in a PR.
9. Open the PR (Stage 5), merge it yourself after review.
10. Wire Stage 6 (CI Regression) to run this one flow on a schedule — verify it runs with zero AI calls
    and reports pass/fail correctly on both a passing and a deliberately-broken build.
11. *Exit check:* one ticket has gone from raw text to a merged, CI-running Maestro flow, with a human
    reading every intermediate artifact.

**Phase 3 — Hardening: turn on Stage 7 (self-healing), lock down agent permissions, and add the remaining pilot cases** *(start only after Phase 1+2 is demoed)*
12. Build two deliberately known-answer test builds: one with only a locator/ID change (should be
    auto-repaired) and one with a real logic/value defect (should be refused). Confirm `repair-agent`
    gets both right before trusting it on anything else.
13. Run the remaining pilot cases from Section 10 through Stages 2–6 with progressively less manual
    review per step, now that Phase 2 has validated the pipeline once.
14. Turn on Stage 8 reporting for all pilot tickets; confirm the audit trail (model used, attempts,
    approvals, timestamps) is actually populated, not just present in template form.
15. *Exit check:* the metrics in Section 8 are computable from real pilot data, not estimated.

**Phase 4 — Calibration and handoff**
16. Using the Section 8 metrics from the pilot, tune the Stage 4 action ceiling and Stage 7 repair-attempt
    ceiling — replace the starting placeholder numbers with pilot-informed ones.
17. Write up the pilot's actual numbers (coverage, self-heal accuracy, false-positive rate, time saved)
    against the formulas in Section 8 — this becomes the evidence for whether/how to scale beyond one app.
18. Do not proceed to a second app or Android until Phase 4's numbers have been reviewed by the team.
