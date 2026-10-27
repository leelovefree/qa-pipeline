"""Shared helpers for the qa-* tools that build on bin/qa-auto (qa-report, qa-repair).

bin/qa-auto has no .py extension, so it is loaded by path. Its `main()` only runs when executed directly, which
makes its gates (fix_is_legit, assert_lines, known-bug check) and helpers importable instead of copied.
"""
import importlib.machinery
import importlib.util
from pathlib import Path

BIN = Path(__file__).resolve().parent


def load_qa_auto():
    loader = importlib.machinery.SourceFileLoader("qa_auto", str(BIN / "qa-auto"))
    spec = importlib.util.spec_from_loader("qa_auto", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module
