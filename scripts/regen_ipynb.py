#!/usr/bin/env python
"""Regenerate .ipynb from a jupytext-percent .py by EXECUTING it (fresh outputs).

Use after editing code cells (or when outputs are stale) — converts the percent .py to a
notebook, runs every cell with the chosen kernel (cwd = the notebook's own folder, so the
ROOT-finding + relative paths work), and writes the sibling .ipynb. For markdown-only edits
use sync_markdown.py instead (no kernel, preserves outputs).

Kernel: set REGEN_KERNEL (default "python3"), e.g. REGEN_KERNEL=hazard python scripts/regen_ipynb.py nb.py
Usage:  regen_ipynb.py <path/to/notebook.py> [more.py ...]
"""
import sys, os
import jupytext, nbformat
from nbconvert.preprocessors import ExecutePreprocessor

KERNEL = os.environ.get("REGEN_KERNEL", "python3")

def main(paths):
    ep = ExecutePreprocessor(timeout=1800, kernel_name=KERNEL)
    for p in paths:
        if not p.endswith(".py"):
            print("skip (not .py):", p); continue
        nb = jupytext.read(p)
        nb.metadata.setdefault("kernelspec", {"name": KERNEL, "display_name": KERNEL, "language": "python"})
        ep.preprocess(nb, {"metadata": {"path": os.path.dirname(os.path.abspath(p))}})
        out = p[:-3] + ".ipynb"
        nbformat.write(nb, out)
        print(f"wrote {out} ({len(nb.cells)} cells)")

if __name__ == "__main__":
    main(sys.argv[1:])
