#!/usr/bin/env python3
"""Read-only pre-demo check. Changes nothing (no commits, no Jira writes, no simulator changes).

  python3 docs/demo/preflight.py [DEMO-TICKET-KEY ...]

Exit code 0 = every REQUIRED check passed. WARN lines are things to look at, not blockers.
"""
import base64
import fcntl
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWNER_REPO = "leelovefree/ios-shop-demo"
failed = 0


def report(ok, label, detail="", required=True):
    global failed
    tag = "PASS" if ok else ("FAIL" if required else "WARN")
    if not ok and required:
        failed += 1
    print(f"[{tag}] {label}" + (f" — {detail}" if detail else ""))


def run(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:  # noqa: BLE001
        return 1, str(e)


def jira(path):
    base = os.environ["JIRA_BASE_URL"].rstrip("/")
    auth = base64.b64encode(f"{os.environ['JIRA_EMAIL']}:{os.environ['JIRA_API_TOKEN']}".encode()).decode()
    req = urllib.request.Request(base + path, headers={"Authorization": f"Basic {auth}", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def main():
    keys = sys.argv[1:]
    # --- tools
    for tool in ("maestro", "xcrun", "gh", "python3", "java", "claude", "git"):
        report(shutil.which(tool) is not None or (tool == "maestro" and (Path.home() / ".maestro/bin/maestro").exists()),
               f"tool: {tool}")
    rc, out = run(["gh", "auth", "status"])
    report(rc == 0, "gh authenticated", out.splitlines()[1].strip() if rc == 0 and len(out.splitlines()) > 1 else out[:120])

    # --- git
    rc, branch = run(["git", "branch", "--show-current"])
    report(branch == "main", "on branch main", f"current: {branch}")
    rc, dirty = run(["git", "status", "--porcelain", "--untracked-files=no"])
    report(dirty == "", "no uncommitted changes to tracked files (qa-auto refuses to start otherwise)", dirty[:200])
    rc, _ = run(["git", "fetch", "origin", "main"])
    rc, behind = run(["git", "rev-list", "--count", "HEAD..origin/main"])
    report(rc == 0 and behind == "0", "local main is up to date with origin/main", f"behind by {behind}" if behind != "0" else "")

    # --- credentials and Jira
    envf = Path.home() / ".config/qa-auto/env"
    ok_env = envf.exists()
    if ok_env:
        for line in envf.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()
    report(ok_env and all(os.environ.get(k) for k in ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN")),
           "~/.config/qa-auto/env has JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN")
    try:
        me = jira("/rest/api/3/myself")
        report(True, "Jira API reachable and token valid", me.get("displayName", ""))
        q = urllib.parse.urlencode({"jql": "project = SCRUM AND labels = qa-auto", "fields": "labels,summary", "maxResults": 50})
        tagged = jira(f"/rest/api/3/search/jql?{q}").get("issues", [])
        stale = [i["key"] for i in tagged if i["key"] not in keys]
        report(not stale, "no unrelated ticket carries the label qa-auto",
               f"{', '.join(stale)} — poller will inspect them (they are finished: harmless, but noisy)" if stale else "", required=False)
        for k in keys:
            i = jira(f"/rest/api/3/issue/{k}?fields=labels,summary,status")
            lab = i["fields"]["labels"]
            report(not any(l.startswith("qa-") for l in lab), f"{k} has no qa-* labels yet (live trigger not pulled)",
                   f"labels now: {lab}" if lab else i["fields"]["summary"][:70])
    except Exception as e:  # noqa: BLE001
        report(False, "Jira API reachable and token valid", str(e)[:150])

    # --- app build and simulator
    rc, out = run(["gh", "release", "view", "build-1", "-R", OWNER_REPO, "--json", "assets", "--jq", ".assets[].name"])
    report(rc == 0 and "ShopDemo.app.zip" in out, f"build asset build-1/ShopDemo.app.zip exists in {OWNER_REPO}", out[:100] if rc else "")
    rc, out = run(["xcrun", "simctl", "list", "devicetypes"])
    report("iPhone 17" in out, "simulator device type 'iPhone 17' available (app.config ios_device)")
    rc, out = run(["xcrun", "simctl", "list", "devices", "available"])
    leftovers = [l.strip() for l in out.splitlines() if "qa-auto" in l]
    report(not leftovers, "no leftover 'qa-auto' simulator from an earlier run", "; ".join(leftovers)[:160], required=False)

    rc, out = run(["xcrun", "simctl", "list", "devices", "booted"])
    booted = [l.strip().split(" (")[0] for l in out.splitlines() if "(Booted)" in l]
    report(not booted, "no simulator is booted (shut down intro simulators before Stage 4: xcrun simctl shutdown all)",
           ", ".join(booted), required=False)

    # --- lock and machine state
    lockf = ROOT / ".qa-work/auto/lock"
    if lockf.exists():
        with open(lockf, "w") as fh:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                report(True, "no other qa-auto instance is running")
            except BlockingIOError:
                report(False, "no other qa-auto instance is running", "lock is held")
    else:
        report(True, "no other qa-auto instance is running")
    rc, out = run(["pgrep", "-fl", "Simulator.app"])
    report(rc == 0, "Simulator.app is open (so the audience sees the 'qa-auto' simulator boot)",
           "run: open -a Simulator", required=False)
    rc, out = run(["pmset", "-g", "assertions"])
    report("PreventUserIdleSystemSleep" in out and "caffeinate" in out, "machine is kept awake (caffeinate)",
           "run: caffeinate -dims &", required=False)
    rc, out = run(["gh", "run", "list", "-R", "leelovefree/qa-pipeline", "--limit", "1", "--json", "conclusion", "--jq", ".[0].conclusion"])
    report(out == "success", "latest GitHub Actions run on qa-pipeline is green",
           f"latest conclusion: {out or 'unknown'} (known: account billing issue, not a pipeline fault)", required=False)

    print("\nRESULT:", "all required checks passed" if failed == 0 else f"{failed} required check(s) FAILED")
    sys.exit(1 if failed else 0)


main()
