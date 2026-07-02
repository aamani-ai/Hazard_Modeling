# Task context — hazard docs M0-M4 + flood scope handoff (2026-07-02)

## Objective
Make the hazard documentation easier to revisit by explaining the M0-M4 modeling contract, the source-selection
reasoning, and the notebook methodology in plain English. Close the session with enough handoff context for a new chat
to pick up the newly discovered flood x wind-farm scope issue without re-deriving it.

## Background
- The repo is notebooks-first, with hazard methods organized around M0 through M4. The user wanted the documentation to
  explain not only *what source was selected*, but also *what modeling choices were made and why*.
- Earlier docs were too link-heavy in notebook READMEs. The user asked for compact mental models, ASCII diagrams, and
  step-by-step explanations that a non-specialist can re-read later.
- The discussion moved from convective wind source conversion, to general M0/M1 input modes, to flood riverine/pluvial/
  coastal physics, and then to asset-specific coupling for solar and wind farms.
- A major late-session finding changed the flood x wind-farm framing: a mapped collector substation is not automatically
  part of the wind farm's physical-damage TIV. It may belong in dependency/disruption modeling unless ownership and
  value-schedule evidence are confirmed.

## Problems encountered
1. **Return-period products were easy to confuse with event catalogs.**
   We clarified that M0/M1 can be event-first, return-period-first, or hybrid, and each mode has different assumptions,
   quality-control burden, and flexibility.
2. **Flood M1/M2 had too many unexplained hydrology terms.**
   We explained discharge `Q(T)`, depth `D(T)`, 100/500-year BLE depth anchors, the 10-year extent mask, and why USGS
   flow-frequency curves densify missing 10/25/50-year depth points.
3. **Notebook README files were too skeletal.**
   The user wanted README files to carry the method itself, not only point to notebooks and plans.
4. **Solar and wind flood coupling were being blurred.**
   Solar can use polygon-level inundated fraction and conditional depth; wind turbines are discrete nodes, with pad
   height and component height mattering.
5. **Collector-substation mapping was almost over-promoted into physical loss.**
   The hull + OSM/HIFLD collector finder is strong exposure/dependency mapping, but direct physical loss requires
   ownership/TIV evidence.

## What changed
1. Added and expanded hazard-level documentation for the M0-M4 contract, including input modes and pros/cons.
2. Added `modeling_choices.md` style docs for hazards so source selection and modeling assumptions are separated.
3. Expanded hazard README files so each hazard folder explains M0 through M4, the major assumptions, and open questions.
4. Expanded notebook README files with plain-English summaries, "what this layer asks" blocks, and ASCII diagrams.
5. Added flood fundamentals for riverine, pluvial, and coastal physics, including how site conditioning turns flood
   fields into exposed fraction, conditional depth, or node-specific water depth.
6. Documented the solar representative value-mix assumption: wet area fraction proxies wet value fraction when exact
   inverter/substation/PV/civil locations are unavailable.
7. Added wind-farm collector-location diagrams, then corrected the wording so the collector is treated as dependency /
   exposure evidence unless ownership and physical-value inclusion are confirmed.
8. Added this task-history folder to preserve the reasoning and next-session roadmap.

## Files touched
Primary documentation areas:
- `docs/hazards/README.md`
- `docs/hazards/m0_m4_event_loss_contract.md`
- `docs/hazards/*/README.md`
- `docs/hazards/*/source_selection.md`
- `docs/hazards/*/modeling_choices.md`
- `docs/hazards/*/fundamentals_before_m0.md`
- `Notebooks/**/README.md`
- `docs/plans/flood/**`
- `docs/plans/hurricane/**`

Important flood-specific paths:
- `docs/hazards/flood/README.md`
- `docs/hazards/flood/fundamentals_before_m0.md`
- `docs/hazards/flood/modeling_choices.md`
- `Notebooks/flood/solar/m2_coupling/README.md`
- `Notebooks/flood/wind_farm/README.md`
- `Notebooks/flood/wind_farm/m2_coupling/README.md`
- `Notebooks/flood/wind_farm/m3_damage/README.md`

Working-tree caution:
- The repo also contains unrelated or broader code/data changes under `drivers/`, `shared/`, `pipelines/`, and `data/`.
  Do not assume all dirty files belong to this documentation task.

## Current status
- [x] Hazard-level docs now explain the M0-M4 modeling contract more clearly.
- [x] Notebook README pattern now favors method explanations, ASCII diagrams, and layer questions.
- [x] Flood riverine/pluvial/coastal explanations are much clearer than before.
- [x] Solar value-mix assumption is documented.
- [x] Wind-farm collector mapping is documented as strong exposure/dependency mapping, not automatic physical loss.
- [ ] Flood x wind-farm physical-only notebook scope still needs a deliberate next-session decision.
- [ ] If the flood wind-farm notebooks remain in scope, M3/M4 must be revisited before treating their collector-driven
  physical loss as baseline.

## Next steps
1. Start next chat by reading `handoff.md` in this folder.
2. Decide flood x wind-farm scope before editing code: physical-only baseline, dependency/disruption product, or a
   sensitivity with ownership/TIV evidence.
3. If keeping a physical-only flood x wind-farm notebook, revise M3/M4 so a mapped collector is not priced as direct
   physical loss unless evidence supports it.
4. If building disruption losses, create a separate routing/process for outage duration and revenue loss instead of
   mixing it into M3 physical damage.
