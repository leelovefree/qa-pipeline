"""Gate tests for Stage 7. No device, no AI: python3 -m unittest discover -s bin/tests

The gate decides whether a repair patch is acceptable no matter what the agent claims, so every way of cheating gets a test.
"""
import importlib.machinery
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BIN))
_loader = importlib.machinery.SourceFileLoader("qa_repair", str(BIN / "qa-repair"))
_spec = importlib.util.spec_from_loader("qa_repair", _loader)
repair = importlib.util.module_from_spec(_spec)
_loader.exec_module(repair)

FLOW = """# Requirement: X.Y.Z
appId: com.example
---
- tapOn:
    id: old_button
- assertVisible:
    id: price_label
    text: "\\\\$300"
- assertNotVisible:
    id: error_label
"""
OTHER = "appId: com.example\n---\n- tapOn:\n    id: a\n- assertVisible:\n    id: b\n"
SHARED = "appId: com.example\n---\n- tapOn:\n    id: login_submit_button\n"
F, O, S = "apps/demo/tests/mod/feat/X.Y.Z.yaml", "apps/demo/tests/mod/feat/OTHER.yaml", "apps/demo/shared/login.yaml"


def git(cwd, *a):
    subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True)


class GateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.remote, self.wt = root / "remote.git", root / "wt"
        git(root, "init", "--bare", "-b", "main", str(self.remote))
        git(root, "clone", str(self.remote), str(self.wt))
        git(self.wt, "config", "user.email", "t@example.com")
        git(self.wt, "config", "user.name", "t")
        for rel, text in ((F, FLOW), (O, OTHER), (S, SHARED)):
            (self.wt / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.wt / rel).write_text(text)
        git(self.wt, "add", "-A")
        git(self.wt, "commit", "-m", "base")
        git(self.wt, "push", "-u", "origin", "HEAD:main")
        git(self.wt, "fetch", "origin")

    def tearDown(self):
        self.tmp.cleanup()

    def edit(self, rel, old, new):
        p = self.wt / rel
        assert old in p.read_text(), old
        p.write_text(p.read_text().replace(old, new))

    def gate(self, **kw):
        return repair.repair_gate(self.wt, "demo", F, **kw)

    def test_selector_change_on_a_tap_is_allowed(self):
        self.edit(F, "id: old_button", "id: new_button")
        self.assertTrue(self.gate()[0])

    def test_shared_subflow_selector_change_is_allowed(self):
        self.edit(S, "login_submit_button", "login_submit_btn")
        self.assertTrue(self.gate()[0])

    def test_changed_expected_value_is_rejected(self):
        self.edit(F, '\\\\$300', '\\\\$301')
        ok, why, _ = self.gate()
        self.assertFalse(ok)
        self.assertIn("assertion", why)

    def test_removed_assertion_is_rejected(self):
        self.edit(F, "- assertNotVisible:\n    id: error_label\n", "")
        self.assertFalse(self.gate()[0])

    def test_added_assertion_is_rejected(self):
        (self.wt / F).write_text((self.wt / F).read_text() + "- assertVisible:\n    id: extra\n")
        self.assertFalse(self.gate()[0])

    def test_assertion_id_change_needs_the_flag(self):
        self.edit(F, "id: price_label", "id: price_value")
        self.assertFalse(self.gate()[0])
        ok, _, notes = self.gate(allow_assert_selector=True)
        self.assertTrue(ok)
        self.assertTrue(notes)  # flagged for the reviewer

    def test_assertion_value_change_stays_rejected_even_with_the_flag(self):
        self.edit(F, "id: price_label", "id: price_value")
        self.edit(F, '\\\\$300', '\\\\$301')
        self.assertFalse(self.gate(allow_assert_selector=True)[0])

    def test_another_flow_is_rejected(self):
        self.edit(O, "id: a", "id: c")
        self.assertIn("another flow", self.gate()[1])

    def test_new_file_is_rejected(self):
        (self.wt / "apps/demo/tests/mod/feat/NEW.yaml").write_text(OTHER)
        self.assertIn("new files", self.gate()[1])

    def test_spec_or_cases_edit_is_rejected(self):
        (self.wt / "apps/demo/specs/T-1").mkdir(parents=True)
        (self.wt / "apps/demo/specs/T-1/spec.md").write_text("x")
        git(self.wt, "add", "-A")
        git(self.wt, "commit", "-m", "spec")
        (self.wt / "apps/demo/specs/T-1/spec.md").write_text("y")
        self.assertIn("forbidden", self.gate()[1])

    def test_optional_true_is_rejected(self):
        self.edit(F, "- tapOn:\n    id: old_button\n", "- tapOn:\n    id: old_button\n    optional: true\n")
        self.assertIn("optional", self.gate()[1])

    def test_known_bug_tag_is_rejected(self):
        self.edit(F, "appId: com.example\n", "appId: com.example\ntags:\n  - known-bug\n")
        self.assertIn("known-bug", self.gate()[1])

    def test_no_change_is_reported(self):
        self.assertEqual(self.gate()[1], "no change")


class BlockParserTest(unittest.TestCase):
    def test_multiline_blocks_are_compared_whole(self):
        a = repair.assertion_blocks(FLOW)
        self.assertEqual(sum(a.values()), 2)
        self.assertNotEqual(a, repair.assertion_blocks(FLOW.replace("300", "301")))

    def test_inline_assertion(self):
        self.assertEqual(sum(repair.assertion_blocks('- assertVisible: "Hello"\n').values()), 1)


if __name__ == "__main__":
    unittest.main()
