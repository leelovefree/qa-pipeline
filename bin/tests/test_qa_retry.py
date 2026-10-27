"""One-shot infrastructure retry in bin/qa. No device, no AI: python3 -m unittest discover -s bin/tests

bin/qa runs against a throw-away copy of the repo layout with a fake `maestro` (scripted per scenario) and a fake `xcrun`.
What is checked is the policy: which failures are retried, that it happens at most once, and which exit code comes out.
"""
import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

BIN = Path(__file__).resolve().parent.parent
UDID = "11111111-2222-3333-4444-555555555555"

FAKE_MAESTRO = textwrap.dedent('''\
    #!/usr/bin/env python3
    """Fake maestro. Scenario file maps attempt number -> {flow: "pass" | "step_failed" | "cut_off"}; exit 1 if any failed."""
    import json, os, sys
    from pathlib import Path
    a = sys.argv[1:]
    out, dbg = a[a.index("--output") + 1], a[a.index("--debug-output") + 1]
    flows = [x for x in a if x.endswith(".yaml")]
    state = Path(os.environ["FAKE_STATE"]); n = int(state.read_text()) + 1 if state.exists() else 1; state.write_text(str(n))
    plan = json.loads(Path(os.environ["FAKE_PLAN"]).read_text())[str(n)]
    cases, bad = [], 0
    for f in flows:
        fid = Path(f).stem; how = plan.get(fid, "pass"); d = Path(dbg) / fid; d.mkdir(parents=True, exist_ok=True)
        steps = [{"command": {"launchAppCommand": {}}, "metadata": {"status": "COMPLETED"}}]
        if how == "step_failed":
            steps.append({"command": {"tapOnElement": {}}, "metadata": {"status": "FAILED", "error": {"message": "Element not found"}}})
        elif how == "cut_off":
            steps.append({"command": {"assertConditionCommand": {}}, "metadata": {"status": "RUNNING"}})
        (d / "commands.json").write_text(json.dumps(steps))
        fail = "" if how == "pass" else "<failure>x</failure>"; bad += how != "pass"
        cases.append(f'<testcase id="{fid}" name="{fid}" file="{f}">{fail}</testcase>')
    Path(out).write_text(f'<testsuites><testsuite tests="{len(cases)}" failures="{bad}">' + "".join(cases) + "</testsuite></testsuites>")
    print("fake maestro attempt", n, "flows", [Path(f).stem for f in flows])
    sys.exit(1 if bad else 0)
''')


class RetryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "bin").mkdir()
        for name in ("qa", "qa-junit"):
            shutil.copy(BIN / name, self.tmp / "bin" / name)
        tests = self.tmp / "apps/demo/tests/mod/feat"
        tests.mkdir(parents=True)
        (self.tmp / "apps/demo/app.config.yml").write_text("name: demo\nplatform: ios\napp_id: com.example.demo\nios_device: iPhone 17\n")
        for fid in ("A", "B", "C"):
            (tests / f"{fid}.yaml").write_text("appId: com.example.demo\n---\n- launchApp\n")
        fake = self.tmp / "fakebin"
        fake.mkdir()
        (fake / "maestro").write_text(FAKE_MAESTRO)
        (fake / "xcrun").write_text("#!/bin/sh\necho \"xcrun $*\" >> \"$FAKE_XCRUN_LOG\"\nexit 0\n")
        for f in fake.iterdir():
            f.chmod(0o755)
        self.env = dict(os.environ, PATH=f"{fake}:{os.environ['PATH']}", FAKE_STATE=str(self.tmp / "state"),
                        FAKE_PLAN=str(self.tmp / "plan.json"), FAKE_XCRUN_LOG=str(self.tmp / "xcrun.log"),
                        QA_BOOT_TIMEOUT="10", QA_ENV_FILE="/nonexistent")
        self.env.pop("QA_NO_RETRY", None)

    def run_qa(self, plan, **extra):
        (self.tmp / "plan.json").write_text(json.dumps(plan))
        r = subprocess.run([str(self.tmp / "bin/qa"), "run", "demo", "--no-install", "--device", UDID],
                           cwd=self.tmp, env=dict(self.env, **extra), capture_output=True, text=True, timeout=120)
        self.attempts = int((self.tmp / "state").read_text())
        return r

    def final(self):
        root = ET.parse(self.tmp / ".qa-work/demo/report.xml").getroot()
        return {c.get("id"): c.find("failure") is None for c in root.iter("testcase")}

    def test_cut_off_flows_are_retried_once_and_can_pass(self):
        r = self.run_qa({"1": {"A": "cut_off", "B": "cut_off"}, "2": {}})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.attempts, 2)
        self.assertEqual(self.final(), {"A": True, "B": True, "C": True})
        self.assertIn("shutdown", (self.tmp / "xcrun.log").read_text())  # the simulator really was restarted
        self.assertIn("A B", r.stderr)

    def test_cut_off_flows_that_fail_again_stay_red(self):
        r = self.run_qa({"1": {"A": "cut_off"}, "2": {"A": "cut_off"}})
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.attempts, 2)  # exactly one retry, never a second
        self.assertFalse(self.final()["A"])

    def test_a_failed_step_is_never_retried(self):
        r = self.run_qa({"1": {"A": "step_failed"}, "2": {}})
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.attempts, 1)
        self.assertFalse(self.final()["A"])

    def test_real_failure_is_not_masked_by_a_rescued_flow(self):
        r = self.run_qa({"1": {"A": "step_failed", "B": "cut_off"}, "2": {}})
        self.assertEqual(r.returncode, 1)  # A is a real failure: the run stays red even though B passes on retry
        self.assertEqual(self.attempts, 2)
        self.assertEqual(self.final(), {"A": False, "B": True, "C": True})

    def test_retry_can_be_switched_off(self):
        r = self.run_qa({"1": {"A": "cut_off"}, "2": {}}, QA_NO_RETRY="1")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.attempts, 1)

    def test_green_run_never_retries(self):
        r = self.run_qa({"1": {}})
        self.assertEqual((r.returncode, self.attempts), (0, 1))

    def test_first_attempt_report_is_kept_for_the_audit(self):
        self.run_qa({"1": {"A": "cut_off"}, "2": {}})
        first = ET.parse(self.tmp / ".qa-work/demo/report.attempt1.xml").getroot()
        self.assertEqual([c.get("id") for c in first.iter("testcase") if c.find("failure") is not None], ["A"])
        self.assertTrue((self.tmp / ".qa-work/demo/debug-retry/A/commands.json").exists())


class QaJunitTest(unittest.TestCase):
    def test_flow_without_commands_json_is_real(self):
        with tempfile.TemporaryDirectory() as d:
            rep = Path(d) / "r.xml"
            rep.write_text('<testsuites><testsuite><testcase id="X"><failure/></testcase></testsuite></testsuites>')
            out = subprocess.run([str(BIN / "qa-junit"), "classify", str(rep), d], capture_output=True, text=True).stdout
            self.assertEqual(out.strip(), "REAL X")


if __name__ == "__main__":
    unittest.main()
