#!/usr/bin/env python
"""Sync markdown cells from a jupytext-percent .py into its sibling .ipynb WITHOUT re-executing.

For a documentation-only pass: rewrite the .py's markdown (headers, section intros), then run this to push
the new text into the .ipynb while keeping every code cell + its existing outputs untouched. Much faster and
safer than a full regen (no kernel, no network, outputs preserved).

Requires the .py and .ipynb to have the SAME sequence of cell types (markdown/code) — i.e. you edited markdown
*content* only, not structure. If the sequences differ it refuses and tells you to use regen_ipynb.py instead.

Usage: sync_markdown.py <path/to/notebook.py> [more.py ...]
"""
import sys, re
from pathlib import Path
import nbformat

def strip_header(src):
    lines = src.splitlines()
    if lines and lines[0].strip() == "# ---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "# ---":
                return "\n".join(lines[i + 1:]).lstrip("\n")
    return src

def py_cells(src):
    """[(kind, text)] where kind in {'markdown','code'}; markdown text has the leading '# ' stripped."""
    cells, cur, is_md = [], [], False
    def flush():
        if not cur: return
        body = "\n".join(cur).strip("\n")
        if is_md:
            text = "\n".join(re.sub(r"^# ?", "", l) for l in body.splitlines())
            if text.strip(): cells.append(("markdown", text))
        elif body.strip():
            cells.append(("code", body))
    for line in src.splitlines():
        if line.startswith("# %%"):
            flush(); cur, is_md = [], line.strip().endswith("[markdown]"); continue
        cur.append(line)
    flush()
    return cells

def sync(py_path):
    py = Path(py_path); ipynb = py.with_suffix(".ipynb")
    if not ipynb.exists():
        print(f"SKIP {py.name}: no .ipynb (use regen_ipynb.py)"); return
    pc = py_cells(strip_header(py.read_text()))
    nb = nbformat.read(ipynb, as_version=4)
    nbc = [c for c in nb.cells if c.cell_type in ("markdown", "code")]
    if [k for k, _ in pc] != [c.cell_type for c in nbc]:
        print(f"SKIP {py.name}: cell-type sequence differs (.py {len(pc)} vs .ipynb {len(nbc)}) — use regen_ipynb.py"); return
    n_md = 0
    for (kind, text), cell in zip(pc, nbc):
        if kind == "markdown" and cell.source != text:
            cell.source = text; n_md += 1
    nbformat.write(nb, ipynb)
    print(f"synced {ipynb.name}: {n_md} markdown cell(s) updated (code + outputs untouched)")

if __name__ == "__main__":
    for p in sys.argv[1:]:
        sync(p)
