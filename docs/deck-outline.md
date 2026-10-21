# Deck outline — AI-assisted mobile QA (qa-pipeline) · 35-minute version

Audience: third party, experienced with AI. No "what is an LLM"; focus on risks, controls and evidence.

## How to read this file

Every slide has three separate blocks:
- **[ON SLIDE]**: what appears on screen (keep it short when building the real slide).
- **[SCRIPT]**: what you say out loud; not on the slide.
- **[NOTES — do not read out]**: preparation and answers for questions.

Status labels used on slides: **Built** (works, with evidence) · **Designed** (controls specified, not built) · **To measure** (only claimed after the pilot).
All qa-pipeline numbers were measured on **one simple app, 5 runs, one operator**: use them as a data point and a starting point, not a standard. "Estimate" and "starting target" columns are assumptions with reasons, not measured results. All baseline numbers come from `runs.jsonl` (SCRUM-8/9/11/12/13), `bin/qa-auto` and `docs/requirements.md`.

## Glossary (use one name per concept across the deck)

| Term | Meaning |
|---|---|
| ticket | a requirement written in Jira |
| rule | one small, checkable requirement extracted from a ticket (spec = the set of rules) |
| test case | a check written in business language, one per rule |
| flow | an automated test file run by Maestro, one per test case |
| selector | how a test finds a button/field on screen |
| assertion | the step in a flow that checks "is the result correct" |
| regression | re-running all tests to see whether anything broke |
| pilot | a trial with a clear scope and deadline |

Title options: (1) **AI Proposes, the Runner Decides** · (2) **A Test That Can't Lie** · (3) **Trust the Exit Code, Not the Model**

## Time plan (35 min)

| Block | Min |
|---|---|
| S1–S5: problem, process, controls, cost | 11.5 |
| S6 + **Demo 1** (ticket → PR) | 1 + 6 |
| **Demo 2** (CI replay → fix or refuse → report) + S7 | 5 + 1.5 |
| S8–S10: evaluation, governance + limits, roadmap + pilot | 7 |
| Buffer | ~2.5 |

If Q&A must fit inside the 35 min: play Demo 2 as a recording and trim S9.

---

## S1. Title (0.5 min)

**[ON SLIDE]**
- Title (pick one) · subtitle: "From Jira ticket to reviewed PR to CI regression — with the AI on a leash"

**[SCRIPT]**
"Today I am not going to talk about how well AI writes tests. I want to talk about how you can trust the result: which controls exist, what it costs, and what we have actually measured."

---

## S2. Letting AI write tests: 4 risks and how we control them (2 min)

**[ON SLIDE]**

| Risk | What it means | Our control |
|---|---|---|
| "Fake green" | AI edits the test so it passes instead of reporting the failure | The test runner decides pass/fail, not the AI |
| AI guessing | The ticket is vague but AI writes tests from assumptions | On ambiguity the pipeline stops and asks a human |
| Runs forever | AI retries again and again, burning money and time | Every step has a cost, time and attempt ceiling |
| No traceability | Nobody knows which model did what, who approved, what it cost | Model, cost and approver recorded per step |

- Real example (SCRUM-9): the pipeline once opened a PR reporting "green" although no test had been generated. Fixed: green only when every rule has a test **and** the tests pass. **Built**

**[SCRIPT]**
"Everyone knows AI can write tests. The real question is: can we trust it? I group it into four risks. One, fake green: the AI edits the test to make it pass. Two, the AI guesses when a requirement is vague. Three, the AI runs on without stopping. Four, nobody can trace who did what. Each has a control, and the rest of the talk walks through them. The first risk is not theoretical: our own system once reported green with no tests. We found it by running on a real ticket and fixed it."

**[NOTES — do not read out]**
- These four risks frame the talk: S4 answers risks 1–2, S5 answers risk 3, S9 answers risk 4.

---

## S3. The 8-step process (3 min) — core slide

**[ON SLIDE]**
Diagram: Receive ticket → Clarify → Design cases → Write tests → Review & merge → CI regression → Diagnose on failure → Report. Colours: **AI** / **Human gate** / **No AI**.

| # | Step | Who | Status |
|---|---|---|---|
| 1 | Receive ticket (Jira) | Human | Built |
| 2 | Clarify: split the ticket into rules | AI; human answers ambiguity | Built |
| 3 | Design test cases | AI; human approves rules + cases | Built |
| 4 | Write flows against the real app | AI, bounded | Built |
| 5 | Review & merge PR | Human | Built |
| 6 | CI regression | **No AI**: Maestro's own result | Built |
| 7 | Diagnose a failing test | AI; human merges any patch | Designed |
| 8 | Report & audit | Mostly code; a cheap AI writes only the summary | Designed |

- Every red test is triaged by a **human**: **A** app bug · **B** ticket wrong · **C** AI misread · **D** requirement changed.

**[SCRIPT]**
"This is the whole process in eight steps. Blue is AI, orange is a human gate, grey means no AI at all. Three things to notice. One: three of the eight steps have a human gate. Two: the CI regression step has no AI; pass or fail is the test tool's result. Three: when a test goes red, a human classifies the cause, the AI never decides that. QA works in Jira and never has to open the repo. Steps 7 and 8 are still being built, so the slide marks them as designed."

**[NOTES — do not read out]**
- Agent names (if asked): `spec-extractor` (step 2), `case-designer` (step 3), `automation-writer` and `flow-fixer` (step 4), `repair-agent` (step 7), `reporter` (step 8).

---

## S4. How the system works and where the stops are (3 min)

**[ON SLIDE]**
```
Jira ticket
   ▼
AI #1: split the ticket into rules  ──▶ ambiguous? stop and ask a human
   ▼
AI #2: design test cases
   ▼
[Human] QA approves rules + cases
   ▼
AI #3: write tests against the real app (cost and time ceilings)
   ▼
Run tests with Maestro  ◀── this tool decides pass/fail, no AI
   ▼
Pull request ──▶ [Human] reviews and merges
```
- Each AI is a separate agent: one job, in a fresh working session.
- Steps hand results to each other as **files in git** (spec, cases, tests). Humans can read and edit them; there is no hidden AI memory.

| Control | How it works | Enforced by |
|---|---|---|
| Pass/fail | Decided by Maestro's own result; CI has no AI step | **Code/CI** |
| Every requirement covered | Each rule in the spec must have a matching test case | **Code** |
| Honest "green" | Green only when every rule has a test and the tests pass | **Code** |
| No editing requirements to pass | CI blocks a PR that changes a spec and a test together without human approval | **CI** |
| Auto-fix cannot touch checks | The auto-fix step may only change selectors or wait times, never assertions | **Code** |
| Elements come from the real app | AI must look at the real app screen before writing a selector | **Prompt + MCP** |

**[SCRIPT]**
"How it works is simple. Three AIs in a chain, each doing one job and handing over files in git, so a human can read and edit them. In between are two human gates: answering ambiguity, and approving rules and test cases. Most important is the box in the middle: the test tool decides pass or fail, not an AI. The table is the six controls. I will be direct: five are enforced by code or CI. The last one, 'must look at the real app before writing a selector', is still an instruction to the AI, with no code check behind it."

**[NOTES — do not read out]**
- Technical names, only if asked: orchestrator `bin/qa-auto`, test runner `bin/qa`, coverage check `bin/qa-check`, assertion lock `fix_is_legit`, spec check `spec-integrity`, screen inspection `inspect_screen` (Maestro MCP).
- Say which rows are prompt-level only; experienced audiences trust that more than an over-claim.

---

## S5. Cost: small, measured, capped (3 min)

**[ON SLIDE]**
- Chart: AI cost per ticket by step (5 ShopDemo runs).
- Three big numbers: **~$0.4 per test** (ShopDemo) · **$0** AI when CI re-runs tests · **~$10–70** AI for the whole 10–15-ticket pilot (estimate).
- Caption: "This is one data point, not a standard. ShopDemo is a simple app; a real app may cost 1–3× more (assumption). Hard ceilings per step: $1.5 · $2 · $12 · $4 — guard rails, not a budget."

| Item | Measured (ShopDemo, 5 runs) | Estimate for a real app |
|---|---|---|
| Cost per generated test | ~$0.40–$0.46 | ~$0.4–$1.3 (assumes an app 1–3× more complex) |
| One ticket with 2–4 tests | $0.81–$1.38 | $0.8–$4.5 |
| One auto-fix of a selector | $0.09–$0.29 (5 sessions) | same order |
| Step 7 and step 8 | not built | not measured (step 8 is mostly code) |
| CI regression | $0 AI | $0 AI |
| Whole pilot, 10–15 tickets | — | ~$10–70 |

**[SCRIPT]**
"On cost I separate three layers. One: the hard ceiling. If an AI runs away it is stopped at this level; the ceiling is far above real spend because it is a guard rail, not a budget. Two: what we measured on five real tickets of a simple demo app, about 0.4 dollars per test. This is one data point, not a standard: a real app is more complex, so it may cost one to three times more, and the pilot will measure the real number. Three: to picture it, 0.4 dollars is about half a minute of an engineer's time at, say, 50 dollars an hour. So the real cost is review time, not AI spend. Finally, the daily regression run costs no AI money at all."

**[NOTES — do not read out]**
- **Why it is not a standard:** 5 runs, 1 simple app, 1 operator, 1 machine. Use it only as a starting point; the pilot replaces it with measured data.
- **How the estimate is built:** ticket cost ≈ ~$0.5 fixed (split rules ~$0.3 + design cases ~$0.2) + ~$0.17 per test written (measured: SCRUM-8 $0.17, SCRUM-12 $0.19, SCRUM-13 $0.16). Check against SCRUM-13: $0.49 + $0.32 = $0.81.
- **"1–3×" is an assumption**, not a measurement: real apps have more screens and longer flows. Pilot: 10 tickets × $0.84 ≈ $10 (lower bound); 15 tickets × ~$3.5 (3×) ≈ $53, plus step 7 → ~$70 (upper bound).
- **"Half a minute" example:** $0.4 ÷ $50/hour ≈ 29 s. $50/hour is an illustrative assumption; replace with the partner's real rate.
- One measured improvement: splitting out `case-designer` made the design-cases step ~$0.30 cheaper per ticket (from ~$0.47 to $0.17; 3 earlier measurements, 1 later). **Do not say "from $1.35 to $0.81"**: those tickets had different numbers of tests.
- No daily spend cap yet. Excludes macOS CI runner minutes.

## S6. Demo scenario (1 min)

**[ON SLIDE]**
ShopDemo (iOS) app on a simulator, three versions:

| Version | Change | Expected outcome |
|---|---|---|
| Original (`build-1`, exists) | none | tests pass |
| Changed element ID (**to build**) | a button's ID renamed, behaviour identical | AI patches the selector with evidence, replay passes — Designed |
| Real defect (**to build**) | a genuine logic bug | AI **refuses to fix**, test stays red, human classifies as app bug (A) — Designed |

**[SCRIPT]**
"I will demo two parts. Part one: from a Jira ticket to a PR, live. Part two: re-running the tests on three versions of the app. Watch for one thing: not that the AI can fix a test, but that it knows when it may fix it and when it must refuse."

---

## Demo 1 — ticket to PR (≈6 min, live) · Steps 2–5 · Built

**[ON SCREEN]**
1. A Jira ticket with the label `qa-auto`; the spec appears.
2. A single Jira comment with rules + test cases; you add `qa-approved`.
3. Flows are generated on a real simulator; local run; a PR opens, its description lists model, sessions and cost.
4. (Screenshot, not live) the `qa-needs-info` comment on a vague ticket.

**[SCRIPT]**
"This is a real ticket in Jira. I add the label qa-auto. The system reads the ticket and splits it into rules. Here is the single comment sent to QA, with both rules and test cases. I add the approval label. Now the AI opens the real app on the simulator to write the tests; that takes about two minutes. While we wait you can see the cost and time ceilings running. Done: here is the PR, with the model used and the total cost. And if the ticket is vague, the system stops and asks, like on this screen, instead of guessing."

**[NOTES — do not read out]**
- Start the ticket before you speak so the split-rules and design-cases steps are already done. Real timings: split rules ~33 s, design cases ~40 s, write tests ~139 s, create simulator ~86 s.
- Backup: a recording of this exact run.

---

## Demo 2 — CI regression, fix or refuse, report (≈5 min, pre-run results) · Steps 6–8

**[ON SCREEN]**
1. CI re-runs on the original version (the `smoke` group, 6 flows) → green. Built
2. Changed-ID version → red → the AI opens a PR patching the selector, with screen evidence → re-run is green. Designed
3. Real-defect version → red → the AI **refuses**, test stays red, hands over to a human. Designed
4. Report: model, attempts, cost, approver. Designed

**[SCRIPT]**
"Now the CI regression run, with no AI. The original version is green. In the second version a button's ID was renamed: the test goes red, the AI looks at the real screen, sees the button is still there with a new ID, and proposes a PR that fixes the selector. Re-run is green. In the third version the app calculates a value wrongly: the test is also red, but this time the AI refuses to fix it, because it is the app that is wrong. The test stays red and goes to a human. Finally, the report for the run."

**[NOTES — do not read out]**
- A full 21-flow run takes ~12 min, so use the `smoke` group or a recording. Run step 7 live only if you have measured it at under ~2 min per run (not measured yet).
- Fallback that works today: SCRUM-7, a real app bug whose test stays red (tagged `known-bug` with a ticket key, excluded from CI). Use it to show the system does not hide a bug even if step 7 is not finished.

---

## S7. The key point: knowing when NOT to fix (1.5 min)

**[ON SLIDE]**

| AI may fix on its own | AI must refuse and hand to a human |
|---|---|
| The UI changed but the app is still correct. Example: a button's ID was renamed | The app behaves wrongly. Example: a displayed number is wrong |
| Update the selector with evidence from the real screen, re-run, open a PR for review | The test stays red; a human classifies it as A/B/C/D |

- **Making a test green is easy; the hard part is telling "the UI moved" from "the app is wrong".**

**[SCRIPT]**
"This is what I want you to remember. Making a test green is easy; an AI can do it right away. The hard part is knowing when not to. A self-healing tool that cannot tell 'the UI moved' from 'the app is wrong' turns every real bug into a green test. That is why we limit it tightly and leave every other case to a human."

**[NOTES — do not read out]**
- This answers "fake self-healing". Swap the examples to match the two demo builds once built.
- Technical detail, only if asked (**Designed**): max 2 attempts · the case must be re-run · a patch that makes the test check less is rejected automatically · the output is always a PR for a human.
- You can drop this slide if you need time; Demo 2 already makes the point.

---

## S8. Effectiveness: what exists, starting targets, what we will measure (2 min)

**[ON SLIDE]**

| Measure | Exists (ShopDemo) | Starting target for the pilot |
|---|---|---|
| Every rule has a test case | Code blocks if missing; 8 tickets, 32 flows — Built | 100% (enforced by code) |
| Tickets reaching a green PR with no human fixing a flow | 3/5 runs | ≥ 60% (reference: Meta 57%¹) |
| "Fake green" | 1 case, fixed | 0 |
| Self-fix: right or wrong | not measured (we have 2 known-answer builds) — To measure | 2/2 right, 0 masking a real bug |
| Machine time, maintenance effort | ShopDemo: 4–5 min/ticket; maintenance not measured | no number in advance — the pilot measures |

- How we measure: the same 10–15 real tickets in two arms (**current way of working** vs **with AI**), same app, same reviewers; sample size next to every number.
- ¹ Meta TestGen-LLM (FSE 2024): 57% of AI-generated tests ran reliably. Those are unit tests, a different domain — a reference only.

**[SCRIPT]**
"I split this plainly: what exists, starting targets, and what we have not measured. What exists: every rule has a test case, because code blocks the pipeline otherwise. The starting targets are a place to begin the conversation with you, not an industry standard. The only reference I have is Meta's study: 57 percent of AI-generated tests ran reliably. Those are unit tests, so a different domain; I use it only as a sanity check on our 60 percent target. For machine time and maintenance effort I set no number in advance, because I want the pilot to answer with your own data."

**[NOTES — do not read out]**
- **Why not set a "standard":** our numbers come from 1 app and 5 runs. Calling them a standard invites an immediate challenge from an experienced audience. "Starting target, agreed together" is safer.
- **Basis for "≥ 60%":** 3/5 unattended runs (SCRUM-8, 12, 13 green; SCRUM-9 fake green, SCRUM-11 red from an infrastructure fault, both fixed) and the Meta 57% reference. Two independent sources near 60%, but both are small samples or a different domain.
- **Meta:** Alshahwan et al., "Automated Unit Test Improvement using LLMs at Meta" (arXiv 2402.09171, FSE 2024 Industry): 75% of tests built, 57% passed reliably, 25% increased coverage; 73% of recommendations accepted in the test-a-thon. Re-read the paper before citing it on a slide.
- **Do not use** "maintenance is 40–70% of effort": it only appears in vendor blogs, with no reliable research source.
- "2/2 right" and "0 masking" are design targets on 2 known-answer builds, not statistics.
- Do not claim reduced QA effort or better defect detection.

## S9. Governance, audit and limits (2 min)

**[ON SLIDE]**
- **Audit:** the PR description records model, sessions and total cost; approvals are the Jira label history; traceable ticket → spec → case → flow → PR. Built. A report per run (step 8): Designed.
- **Data:** no real customer/rider data; credentials only in machine config and CI secrets. Built.
- **Not done:** data residency and EU AI Act review — to confirm before the pilot.
- **Current limits:**
  - One app (ShopDemo), iOS only; no Android yet.
  - Steps 7 and 8 are not built.
  - Only 5 runs, 1 app, 1 operator.
  - No daily spend cap.
  - Generated assertions are checked by human PR review and rule-level coverage; no code check that each approved expected result became an assertion.
  - Jira/GitHub run on personal accounts; the pilot needs a service account and a neutral CI runner.

**[SCRIPT]**
"On audit: every PR states which model did the work and what it cost, and who approved is in the Jira history. On data: we use no real customer data. One thing is not done and I want to say it now: we have not yet reviewed data residency and the EU AI Act, and that must be confirmed before a pilot. The limits are on the slide: one app, iOS only, five runs. I say this plainly because the pilot is designed to answer exactly the points we are unsure about."

**[NOTES — do not read out]**
- Say the limits yourself; it is better coming from you than from the audience.
- Only if asked: GitHub branch protection is not verified; `bin/qa-auto` has no tests of its own; flows still hard-code demo credentials.

---

## S10. Roadmap, pilot and close (2.5 min)

**[ON SLIDE]**
- **Roadmap:** (1) second app + Android (the multi-app layout already exists) → (2) parallel runs: neutral CI runner, CI sharding, daily spend cap, service account → (3) several model providers, enterprise authentication → (4) loop: CI failure → ticket → fix PR → report.
- **Proposed pilot:** 1 app, 10–15 real tickets, 4–6 weeks.
  - Weeks 0–1: setup (build source, Jira + service account, repo, test accounts without real data, a QA owner).
  - Weeks 1–5: run both arms, weekly review.
  - Week 6: evaluation report against S8.
  - Expected AI cost: **~$10–70** for the whole trial (estimate, to be replaced by measured data) (excluding CI minutes and people time).
- Continue / stop / widen criteria agreed in advance.

**[SCRIPT]**
"The next step is a small pilot: one app, ten to fifteen real tickets, four to six weeks. I estimate the AI cost at roughly ten to seventy dollars for the whole trial, and that number will be replaced by measured data. What we bring is not just 'we use AI', but discipline around the AI: the test tool decides, humans own the gates, limits are in code, and we publish the numbers even when they are not yet good. Thank you."

**[NOTES — do not read out]**
- Roadmap item (3) has not started; it comes only after (1) and (2).
- Do not claim "reduced QA effort" or "better defect detection": those are hypotheses the pilot tests.

---

## Appendix / FAQ (not presented)

- **Never decided by the AI:** pass/fail · editing a spec, an expected result in a test case or an assertion · resolving an ambiguity · adding the `known-bug` tag · A/B/C/D triage · merging.
- **Five non-negotiables:** AI never declares a fail as a pass · ambiguity halts and asks a human · every autonomous step has a hard ceiling · no code reaches `main` without human PR approval · every artefact is traceable to ticket, model version and cost.
- **Two modes:** automatic (label `qa-auto`) or manual (`/spec /cases /flows /run /fix /pr`), switchable per ticket.
- **Cost per step (SCRUM-13, 2 tests):** split rules $0.32 · design cases $0.17 · write tests $0.32. CI: 21 flows ≈ 12 min, ~80% sequential test time; the `smoke` group = 6 flows.
- **Likely hard questions:**
  - "Why not Maestro's AI analysis in CI?" — Pass/fail must not depend on a model; forbidden in CI by design.
  - "Does the generated assertion match the approved expected result?" — Today it relies on human PR review and rule-level coverage; a code check is a known gap.
  - "Can auto-fix hide a bug?" — It cannot change assertions or add `known-bug` (blocked by code); the re-run result belongs to the test tool.
  - "What about data residency?" — Open item; answer before the pilot.
