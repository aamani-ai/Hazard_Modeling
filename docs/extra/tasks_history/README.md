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
| 2026-07-02 | hazard-docs | [`m0-m4-flood-scope`](2026-07-02__hazard-docs__m0-m4-flood-scope/handoff.md) | Expanded hazard and notebook docs around the **M0-M4 contract**, source-selection vs modeling-choice split, return-period/event/hybrid input modes, and flood riverine/pluvial/coastal method explanations with ASCII-style mental models. Documented solar flood's representative value-mix assumption and inland worse-source-wins combine rule. Key finding for next chat: flood × wind-farm collector/substation mapping is strong **dependency/exposure** evidence, but should not be baseline physical loss unless ownership and TIV inclusion are confirmed; current flood wind M3/M4 `substation = 0.09` assumption needs a deliberate scope decision before code changes. |
| 2026-06-25 | hazard-conus-grid | [`package-qc-and-guide`](2026-06-25__hazard-conus-grid__package-qc-and-guide/handoff.md) | Took the hail × solar CONUS grid off notebooks into a **reusable package** (one engine, two drivers: `shared/risk_engine` + `pipelines/hail` + `drivers/conus_grid`), each extraction bit-identical (engine 2.1e-16 · M0/M1 0.0 · driver 2.06e-16). **Built + applied the plausibility QC** (cap impossible MESH at 203 mm; 585 hard artifacts + 61 frequency spikes flagged/held-out; frequency untouched) → QC'd 13,085-cell risk layer; **solar loss QC-invariant** (curve saturates ~100 mm); artifacts cluster over the Ohio Valley (validates vs the MESH literature). Viz notebook + shareable map page. **Reuse guide** (`docs/guides/`: five-blank recipe + cross-driver QC + research-pass Step 0) + deep-per-asset second-driver discussion. Pushed @ `7f7158c`. Next = **schema docs + GCP-bucket docs**, then the deep-per-asset driver + wildfire. |
| 2026-06-17 | convective-wind | [`m0-m4-built-wind-farm-cell`](2026-06-17__convective-wind__m0-m4-built-wind-farm-cell/handoff.md) | Built convective-wind × wind-farm **M0→M4** (both sub-perils, both sites); renamed `wind/`→`convective_wind/` + `wind_farm/` asset cell (M2 folder-fork, M3/M4 shared); **M3 upgraded to two sub-peril curves** (tornado more severe than straight-line wind at the same gust — DD-WN-16/AWN-32); corrected VaR aggregation (summing **understates** the joint ~26%); 0 errors, 0 broken links; pushed @ `e445b42`. Next = production folder architecture. |
| 2026-06-13 | wind | [`route-zero-planning`](2026-06-13__wind__route-zero-planning/handoff.md) | Wind hazard route-zero (hazard 3 of 3): layer-0 hazard-definition + DD-WN-1..13 + M0–M4 plans + coupling discussion, inland-convective (strong wind → tornado), 2 sites; built+reviewed+verified via workflows. Also: wildfire M4 close-out (wildfire × solar complete) + MC effective-sample-size learning. Next = build the wind notebooks layer-0 → M4. |
| 2026-06-10 | notebooks | [`peril-asset-restructure`](2026-06-10__notebooks__peril-asset-restructure/handoff.md) | Restructured notebooks peril→asset (`hail/solar/`), verified+sharpened M4 README, de-staled docs, shared with team + repo public; next = wildfire × solar + hail × wind farm. |
| 2026-06-09 | hail-pipeline | [`m0-m4-end-to-end`](2026-06-09__hail-pipeline__m0-m4-end-to-end/handoff.md) | Hail × solar M0→M4 built, math-validated, pushed; next = wildfire (hazard 2 of 3). |

## How to add one

At the end of a session, follow `PROMPT_CREATE_TASK_DOCS.md`: create the dated folder + the 4 files, add a row
above, commit. Start the *next* session by reading the latest `handoff.md`.
