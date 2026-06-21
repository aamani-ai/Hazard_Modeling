#!/usr/bin/env python
"""Regenerate executed .ipynb from a jupytext-percent .py (jupytext not installed).

Splits on `# %%` / `# %% [markdown]` cells, builds an nbformat notebook, executes it
(network calls are HTTP-cached so this is fast on re-run), and writes the sibling .ipynb.

Usage: regen_ipynb.py <path/to/notebook.py> [more.py ...]
"""
import os, sys, re
from pathlib import Path
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
from nbclient import NotebookClient

# Kernel to execute with. Portable default is the standard "python3" spec; override on a
# machine whose libs live in a named env via REGEN_KERNEL (e.g. REGEN_KERNEL=hazard) — that
# override is local-only and must NOT be hard-coded here.
KERNEL = os.environ.get("REGEN_KERNEL", "python3")

def strip_header(src):
    # drop the leading `# --- jupyter: ... # ---` YAML header block if present
    lines = src.splitlines()
    if lines and lines[0].strip() == "# ---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "# ---":
                return "\n".join(lines[i + 1:]).lstrip("\n")
    return src

def to_cells(src):
    cells, cur, is_md = [], [], False
    def flush():
        if not cur: return
        body = "\n".join(cur).strip("\n")
        if is_md:
            text = "\n".join(re.sub(r"^# ?", "", l) for l in body.splitlines())
            if text.strip(): cells.append(new_markdown_cell(text))
        else:
            if body.strip(): cells.append(new_code_cell(body))
    for line in src.splitlines():
        if line.startswith("# %%"):
            flush(); cur, is_md = [], line.strip().endswith("[markdown]")
            continue
        cur.append(line)
    flush()
    return cells

def regen(py_path):
    py = Path(py_path)
    src = strip_header(py.read_text())
    nb = new_notebook(cells=to_cells(src))
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": KERNEL}
    nb.metadata["language_info"] = {"name": "python"}
    NotebookClient(nb, timeout=1200, kernel_name=KERNEL,
                   resources={"metadata": {"path": str(py.parent)}}).execute()
    out = py.with_suffix(".ipynb")
    nbformat.write(nb, out)
    print("wrote", out, f"({len(nb.cells)} cells)")

if __name__ == "__main__":
    for p in sys.argv[1:]:
        regen(p)
