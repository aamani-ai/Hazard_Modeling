# tasks_history/

Per-session **task documentation** — the bridge between chat sessions / model switches. At the end of a
substantial session we drop a folder here so the next session starts with full, accurate context (created via
[`.cursor/commands/PROMPT_CREATE_TASK_DOCS.md`](../../../.cursor/commands/PROMPT_CREATE_TASK_DOCS.md)).

## Folder naming

`YYYY-MM-DD__area__short-slug`  (e.g. `2026-06-09__hail-pipeline__m0-m4-end-to-end`)

## Each folder has 4 files

| File | Purpose |
|---|---|
| `task_context.md` | objective · background · problems · what we built/fixed · files touched · status · next steps |
| `decisions.md` | key design decisions + rationale (indexes the canonical `docs/plans/hail/decisions.md`) |
| `notes.md` | implementation detail · commands · verification · metrics · key insights |
| **`handoff.md`** | **read-me-first**: 60-sec summary + repro + the **NEXT ACTION roadmap** for the next session |

## Index (newest first)

| Date | Area | Slug | One-line |
|---|---|---|---|
| 2026-06-10 | notebooks | [`peril-asset-restructure`](2026-06-10__notebooks__peril-asset-restructure/handoff.md) | Restructured notebooks peril→asset (`hail/solar/`), verified+sharpened M4 README, de-staled docs, shared with team + repo public; next = wildfire × solar + hail × wind farm. |
| 2026-06-09 | hail-pipeline | [`m0-m4-end-to-end`](2026-06-09__hail-pipeline__m0-m4-end-to-end/handoff.md) | Hail × solar M0→M4 built, math-validated, pushed; next = wildfire (hazard 2 of 3). |

## How to add one

At the end of a session, follow `PROMPT_CREATE_TASK_DOCS.md`: create the dated folder + the 4 files, add a row
above, commit. Start the *next* session by reading the latest `handoff.md`.
