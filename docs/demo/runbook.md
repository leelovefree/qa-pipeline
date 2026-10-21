# Demo runbook — Jira label → PR, fully automatic (Demo 1)

Everything here is the **real pipeline** (`bin/qa-auto`), no mock. One run costs real Claude quota (about $1) and opens a real PR on `leelovefree/qa-pipeline`.

## 0. Tickets and labels

| Ticket | Purpose | Expected behaviour |
|---|---|---|
| **SCRUM-14** (clean) | The happy path | `qa-auto` → spec → cases → comment, label `qa-ready-for-review` → you add `qa-approved` → flows → local run → PR, label `qa-pr-open` |
| **SCRUM-15** (vague) | The ambiguity gate | `qa-auto` → pipeline stops, comment with questions, label `qa-needs-info`. **Never run live yet: rehearse it first** |

Create more copies with `python3 docs/demo/new_ticket.py clean|vague` (creates a real Jira issue, no labels). A ticket that already has a PR cannot be reused: make a fresh one for every rehearsal and for the live run, and update the keys below.

Labels seen on Jira: `qa-auto` (you add) → `qa-needs-info` or `qa-ready-for-review` (tool adds) → `qa-approved` (you add) → `qa-pr-open` (GREEN) or `qa-red` (draft PR) or `qa-error` (stopped, tool ignores it until you remove the label).

## 1. Windows on screen

1. Jira board / ticket in the browser (SCRUM-14, SCRUM-15).
2. Terminal A at the repo root running the poller (the narration source).
3. `Simulator.app` (so the audience sees the throw-away `qa-auto` simulator boot, run the app, then disappear).
4. GitHub PR page (opens at the end).
5. Optional: Terminal B `tail -f` on `.qa-work/auto/<KEY>/runs.jsonl` for live cost/model lines.

## 2. Checklist

**T-60 min**
```bash
cd /Users/macbook/Projects/Cursor/claudepj/qa-pipeline
git switch main && git pull --ff-only
python3 docs/demo/preflight.py SCRUM-14 SCRUM-15     # read-only; every REQUIRED line must be PASS
```
- Rehearse once end to end with a **throw-away copy** of each ticket (`new_ticket.py clean`, `new_ticket.py vague`). Cost ~ $1.2 for clean, ~ $0.3 for vague.
- Record the rehearsal screen (backup video for Demo 1).
- Optional noise reduction: remove the `qa-auto` label from the finished SCRUM-8/9/11/12/13 in Jira (the poller only logs them as `pr_open`, harmless).

**T-15 min**
```bash
caffeinate -dims &          # machine must not sleep
open -a Simulator           # window visible before the poller boots its own simulator
python3 docs/demo/preflight.py SCRUM-14 SCRUM-15
```
- Be on `main`, no tracked changes (untracked files such as docs/demo are fine). Do not touch the repo or switch branch while the pipeline runs.
- Screen layout, font sizes, notifications off, Jira logged in.

**T-5 min**
```bash
bin/qa-auto poll --interval 20      # keep this terminal visible; 20 s so the audience does not wait for the next cycle
```

## 2b. App introduction (optional, ≈ 60–90 s) — recommended

Show the app under test before the pipeline runs, on **your own** simulator (the pipeline never touches it: `qa-auto` creates its own `qa-auto` simulator and passes `--device <its udid>` to every install and test run).

```bash
open -a Simulator
bin/qa install shopdemo                      # boots iPhone 17 if none is booted, downloads build-1, installs it
xcrun simctl launch booted com.qademo.iosshopdemo
```
Suggested walk-through (it also sets up the SCRUM-14 scenario): login (test account, fake data) → Home with category chips → a product detail (size, colour, quantity) → Buy Now → cart → Proceed to Checkout → Place Order → "Order Confirmed!" → Back to Home. One sentence of context: "ShopDemo is the dev team's iOS app; QA only knows which build to test."

**Shut it down before Stage 4 starts** (i.e. before you add `qa-approved`):
```bash
xcrun simctl shutdown all
```
Why: the agent that writes the flows is told in its prompt to use only the `qa-auto` simulator, but that is an instruction, not a code check; with a single booted device there is nothing to confuse. Specs and cases (Stage 2–3) use no simulator, so your simulator may stay open until then. `preflight.py` warns while any simulator is booted; that is expected during the intro.

Time: this comes out of the Demo 1 slot, so either shorten the walk-through to about a minute or take it from the buffer.

## 3. Live script (≈ 6–8 min of machine time; the deck allows 6 min, so use the staged variant)

**Staged variant (recommended).** Start SCRUM-14 ≈ 10 min before the talk: add `qa-auto`, wait until the label `qa-ready-for-review` and the comment appear (≈ 2 min). Then, live:

1. **Ambiguity gate (optional, ≈ 1 min):** on SCRUM-15 add `qa-auto`. Within ≈ 20 s + ≈ 40 s the poller posts questions and sets `qa-needs-info`. *Say:* "vague ticket → the pipeline stops and asks, it never guesses." If this does not happen when you rehearse it, drop this step and show a screenshot instead; **remove the `qa-auto` label from SCRUM-15** so the poller leaves it alone.
2. Open **SCRUM-14**: show the single comment (each rule with Given/When/Then and its test case). *Say:* "one comment, QA reads rules and cases together."
3. **Add the label `qa-approved`** (human gate). Within ≈ 20 s the poller starts Stage 4.
4. While it runs, narrate (the poller is sequential, one pipeline at a time):
   - a fresh `qa-auto` simulator boots (≈ 86 s), the app is installed;
   - the `automation-writer` agent inspects the real screen through the Maestro MCP and writes the flows (≈ 2–2.5 min);
   - `bin/qa-check` verifies every rule has a case; the flows run on a fresh simulator; up to 3 auto-fix attempts if red;
   - `runs.jsonl` shows model, tokens and cost per stage.
5. The PR link is posted on SCRUM-14, label `qa-pr-open` (GREEN) or `qa-red` (draft). Open the PR: body shows models, sessions, total cost, fix attempts; files = spec, CASES.md, flows.
6. **Do not merge during the demo.** *Say:* "nothing is merged by the AI; a human reviews and merges."

**Full-live variant:** same, but add `qa-auto` to SCRUM-14 live (spec ≈ 30–75 s, cases ≈ 40 s) and then `qa-approved`. Needs ≈ 8–9 min.

Typical figures from earlier real runs (use them, do not invent): ticket cost $0.81–$1.38; spec 21–75 s, cases 36–47 s, build 77–139 s, fix session 11–66 s. Wall-clock from `qa-approved` to PR was not recorded: estimate 5–7 min including two simulator creations.

## 4. If something goes wrong

| Symptom | Action |
|---|---|
| Label `qa-error` + Jira comment | Read the comment. Do not retry live (costs again). Cut to the recorded rehearsal. Later: fix the cause, remove `qa-error` |
| `DeviceUnreachable` / simulator hang | The tool retries once by itself. If red again, cut to the recording. Check no stray `qa-auto` simulator: `xcrun simctl list devices | grep qa-auto` |
| GitHub release download 500 | Known intermittent. Re-run `bin/qa-auto run SCRUM-14` once |
| `another instance is running` | A previous poller is still alive: `pgrep -fl qa-auto`, stop it, retry |
| Ticket has `qa-auto` but nothing happens | Poller not running, or branch not `main`/`qa/<KEY>`: read the terminal message |
| PR is draft/red | Say so honestly: red is the runner's verdict and the PR stays a draft. Do not edit flows to turn it green |
| Vague ticket does not stop at `qa-needs-info` | Remove `qa-auto` immediately, show the screenshot from rehearsal instead |

## 5. After a run (rehearsal reset — do these by hand, they delete things)

1. Stop the poller (Ctrl-C) and `caffeinate` (`kill %1` or `pkill caffeinate`).
2. Close the rehearsal PR on GitHub (do not merge) and delete its branch: `gh pr close <n> --delete-branch -R leelovefree/qa-pipeline`.
3. Locally: `git switch main`; the local branch `qa/<KEY>` can be removed with `git branch -D qa/<KEY>` only after you have looked at it.
4. Remove the labels from the rehearsal ticket (or just abandon the ticket) and create a fresh one for the next run.
5. `bin/qa-auto status` lists tracked tickets; state lives in `.qa-work/auto/` (gitignored).

## 6. Demo 2 (CI replay → repair or refuse → report): current status

Not ready, and not covered by this runbook:
- `repair-agent` (Stage 7) and `reporter` (Stage 8) are **not built**.
- The two known-answer builds (element ID renamed; real logic defect) **do not exist**: the app repo has only `build-0` and `build-1`.
- GitHub Actions on `leelovefree/qa-pipeline` currently fails because of an **account billing problem**, not a pipeline fault. Fix it, or use pre-run results.
- Fallback that works today: **SCRUM-7**, a real app bug whose flow stays red locally, is tagged `known-bug` with the ticket key and is excluded from CI. It shows "the pipeline does not paper over a real bug".

## 7. What not to claim

- Not "AI does everything": the human gates are the point.
- No numbers beyond those above; the cost estimate for a real app (~1–3× ShopDemo) is an assumption.
- Stage 7 and 8 are designed, not built. Data residency / EU AI Act review is not done.
