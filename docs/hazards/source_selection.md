# Hazard Source Selection Records

This is the missing bridge between the Google Drive reference set and the implementation notebooks.

The Drive references tell us **what public hazard data exists**. The notebooks show **what we actually built**.
The source-selection record explains the decision in between:

```text
Which candidate source did we choose for V1, which did we reject or defer, and why?
```

More precisely, source selection decides which evidence path we use for the hazard-side ingredients, and flags
when a source already mixes in exposure, vulnerability, or loss and therefore should **not** be used as M1:

```text
event frequency / count process
event intensity / coupling process
damage/loss evidence only when the source explicitly carries it, and then with clear boundaries
```

This is not a replacement for `Hazard_Data_Reference`, a notebook, or a decisions log. It is the durable
asset-free record of how a hazard/sub-peril's evidence became the source plan for M0/M1.

---

## Why This Layer Exists

Without this layer, the reasoning gets scattered:

```text
Google Drive reference
  -> lists candidates

M0 notebooks
  -> explore and prove specific candidates

plans/decisions
  -> record implementation choices

hazard anchor
  -> summarizes the current state
```

That works while the author remembers the discussion. It fails later when someone asks:

```text
Why did we use MRMS instead of NOAA?
Why is NRI not an M1 source?
Why is MYRORSS deferred?
Why is FSim enough for wildfire but hail has to self-build?
```

The source-selection record is where those answers live.

## The Documentation Flow

```text
1. Google Drive references
   broad candidate universe, vocabulary, methodology
        |
        v
2. docs/hazards/<hazard>/source_selection.md
   source candidates, QA/QC findings, V1 selection, rejected/deferred options
        |
        +----> M0 notebooks
        |      meet the data, decode files, profile fields, run source-specific QA
        |
        +----> plans/decisions
        |      commit the plan-of-record and implementation gates
        |
        v
3. docs/hazards/<hazard>/README.md
   short shareable anchor that summarizes the selection and links down
        |
        v
4. M1-M4 notebooks
   event catalog, coupling, damage, annual loss metrics
```

The key rule:

```text
source_selection.md decides source roles;
M0 proves the chosen source can be used correctly;
M1 consumes the source into the model contract.
```

The anti-bias rule:

```text
Pressure-test the source against the model object we need,
not against the implementation we already have.
```

If the current source wins, say why. If it only wins because it is already wired into a notebook, the pressure test
has failed. A good source-selection record must be able to say, "this source is good enough for V1, but here are the
findings that would make us downgrade, replace, or relabel it."

## What Each Record Must Answer

Every hazard-level source-selection record should include:

1. **Model need** — what M0/M1 must produce for this hazard/sub-peril.
2. **Candidate universe** — the sources from `Hazard_Data_Reference` plus any later research candidates.
3. **Selected V1 source(s)** — the source spine and any validation/calibration sources.
4. **Pressure-test summary** — the high-level comparison of why the selected source won and why alternatives did
   not; detailed pressure-test reasoning belongs in `docs/extra/discussion/<hazard>/`.
5. **Rejected or deferred sources** — not just names, but the actual reason.
6. **Access & dependency profile** — where the data comes from, auth/licensing, file/API shape, scale, update
   cadence, and whether we need a heavy batch job or a lightweight direct fetch.
7. **Caveat ledger** — what can still go wrong even after selection, how V1 treats it, and when to revisit.
8. **QA/QC burden** — what must be checked before the source can drive loss.
9. **Allowed and not-allowed uses** — source roles by pipeline component.
10. **Downstream consequences** — what the source choice implies for frequency, severity, coupling, and tail
   confidence.
11. **Surprising findings / watchlist summary** — the few unintuitive facts or unresolved risks that should stay
    visible here; detailed watchlists belong in discussion notes.
12. **Deep references** — links to the notebooks, discussion notes, decisions, assumptions, and branch docs that
    carry the full reasoning.

The minimum useful candidate-role table is:

| Source | Evidence type | Current role | Why not more? | Revisit trigger |
|---|---|---|---|---|
| source name | gridded field / report / index / model product | spine / validation / cross-check / deferred | limitation that blocks primary use | when it can be promoted |

Every record should also include a compact pressure-test table. This is the table that keeps the reasoning from
becoming "we picked X because X is in the notebook"; it should summarize the due diligence, not duplicate the full
discussion note:

| Candidate / choice | What it could solve | Pressure test | V1 decision | Caveat carried |
|---|---|---|---|---|
| source or modeling choice | frequency / severity / footprint / validation / access | why it passes or fails the actual M0/M1 need | selected / validation-only / rejected / deferred | what remains true even after the decision |

And every record should include a caveat ledger:

| Caveat | Why it matters | V1 treatment | Revisit trigger |
|---|---|---|---|
| concrete limitation | how it can bias frequency/severity/coupling/loss | QA flag / label / calibration / exclusion / deferred | what evidence or product would change the treatment |

Every record should also include a compact watchlist summary. The caveat ledger says what can go wrong; the
watchlist says what surprised us or what could change our mind. If a detailed pressure-test discussion exists, keep
the full watchlist there and only carry the highest-signal items here:

| Finding / watch item | Why it matters | What would change the decision |
|---|---|---|
| unintuitive source fact, unresolved risk, or promoted candidate | effect on source role, confidence, or M0/M1 object | data, QA result, access change, or model need that would change V1 treatment |

The high-level page should then point to the deep work instead of repeating it:

```text
Deep References
  - M0 notebook(s): how the raw source was inspected.
  - M1 notebook(s): how the source became frequency / severity / event objects.
  - Decisions / assumptions: what was committed.
  - Discussion notes: pressure-test reasoning, open questions, and alternatives.
  - Branch links: only when the implementation has not landed on main yet.
```

Use links aggressively here. The source-selection page should summarize the argument; it should not become the
full research dossier.

In short:

```text
discussion note       = pressure-test reasoning and full watchlist
source_selection.md   = selected source roles + high-level comparison + compact findings
hazard README         = shortest anchor / current-state map
```

Every record should also carry an access profile:

| Source | Access path | Auth/license | Format / size | Operational dependency |
|---|---|---|---|---|
| source name | bucket/API/download/provider | public/no-auth/API key/vendor | files/rasters/tables and scale | direct fetch / batch scan / provider dependency |

The access profile matters because a scientifically good source can still be a poor V1 spine if it requires
manual requests, secret keys, unstable APIs, unclear licensing, or a batch process we cannot reproduce.

For gridded or high-volume products, also name the **selected product grain**:

```text
source family:       broad archive or provider
selected product:    exact variable/product path used
temporal grain:      daily max / hourly / event / return-period surface / catalog
spatial grain:       native resolution and how it maps to the asset/grid
raw retention:       whether raw files are stored, cached, or only fetched transiently
derived artifact:    compact object we keep and feed to M1/M2
```

This prevents a false statement like "we use MRMS" when the real implementation choice is narrower:
"we use the public MRMS 24-hour maximum MESH product, one selected tile per accepted date, not the full MRMS
archive."

For large gridded or catalog sources, also document the storage boundary:

```text
external raw source
  -> selected product / selected grain
  -> ingest reducer or batch job
  -> compact derived artifact we keep
  -> M1/M2/M3/M4 consumers
```

The key question is not only "can we download it?" It is:

```text
what do we persist because it is expensive and useful,
and what do we leave at the provider because mirroring it would add cost without model value?
```

## Maturity States

Not every hazard will have a final source decision yet. The point of this layer is honest traceability, not
forcing premature certainty.

Use one of these states at the top of each record:

| State | Meaning |
|---|---|
| **decided** | Candidate sources were compared and the V1 source roles are committed. |
| **provisional** | A working source is used in notebooks, but the side-by-side candidate assessment is not complete. |
| **preview** | The selection exists on another branch or in another team's work and is summarized for orientation. |
| **candidate ledger** | We have source candidates, but not enough implementation evidence to choose. |
| **deferred** | The hazard/sub-peril is explicitly outside the current build. |

The file should still exist for `provisional` or `candidate ledger` hazards. In that case it should say:

```text
what we are using now,
why it is plausible,
what has not yet been compared,
what evidence would promote it to decided.
```

That is better than leaving the reasoning implicit in notebook comments.

## How This Differs From Neighboring Docs

| Doc | Question it answers |
|---|---|
| `docs/google_drive_docs/Hazard_Data_Reference.docx` | What public sources exist for each peril? |
| `docs/hazards/fundamentals_before_m0.md` | What must a modeler understand before opening M0? |
| `docs/hazards/<hazard>/source_selection.md` | Which source(s) did this project select for V1, and why? |
| `docs/hazards/<hazard>/README.md` | What is the current high-level hazard model? |
| `docs/plans/.../decisions.md` | What implementation decision is committed for this build? |
| `Notebooks/.../m0_input_data/` | What did source exploration and QA show in executable form? |
| `docs/learning_logs/` | What transferable lesson did this source choice teach? |

## Grain

Source selection is asset-free, so its natural home is the hazard folder:

```text
docs/hazards/
  source_selection.md              <- cross-hazard convention
  hail/
    source_selection.md            <- hail-wide M0/M1 source choice
  wildfire/
    source_selection.md            <- FSim/WRC source roles
  convective_wind/
    source_selection.md            <- tornado vs strong-wind source split
  flood/
    source_selection.md            <- likely split by riverine / pluvial / coastal
  hurricane/
    source_selection.md            <- likely split by wind / surge / rainfall
```

For multi-sub-peril hazards, one file can carry sub-sections:

```text
flood/source_selection.md
  riverine: BLE/NFHL/gauge/hydraulic model choice
  pluvial: rainfall-frequency/proxy/depth-model choice
  coastal: SLOSH/surge/storm-tide choice
```

If a source-selection page grows too large, split by sub-peril only after the single page stops being readable.

## Promotion Rule

A candidate source can be promoted from "research" to "V1 source" only when the record names:

```text
[ ] the model component it serves
[ ] access path, auth/license, format, and scale
[ ] selected product grain and raw-vs-derived artifact boundary
[ ] pressure-test status: completed / branch-preview / candidate-ledger / not-yet-tested
[ ] the denominator or return-period frame it provides
[ ] the spatial grain and how it maps to the asset/grid
[ ] known bias and QA/QC treatment
[ ] caveat ledger with V1 treatment and revisit trigger
[ ] surprising findings / watchlist with what could change the decision
[ ] deep references to notebooks, decisions, assumptions, and discussion notes
[ ] what it cannot be used for
[ ] the downstream confidence label
```

This prevents the common mistake of using a source because it is convenient or long rather than because it
matches the component the model actually needs.

## Current Records

| Hazard | Source-selection record | State | Pressure-test status |
|---|---|---|---|
| Hail | [`hail/source_selection.md`](hail/source_selection.md) | decided for V1; MRMS spine, NOAA validation, MYRORSS deferred | Strongest on main; source triage and MRMS grid QA are documented. |
| Wildfire | [`wildfire/source_selection.md`](wildfire/source_selection.md) | decided for V1; native FSim severity spine, WRC cross-check | Strong on main; FSim/WRC comparison and caveats are documented. |
| Convective wind | [`convective_wind/source_selection.md`](convective_wind/source_selection.md) | decided for V1; split by tornado vs strong-wind sub-peril | Built on main; deeper pressure test lives in [`discussion/convective_wind/05`](../extra/discussion/convective_wind/05_source_selection_pressure_test.md). |
| Flood | [`flood/source_selection.md`](flood/source_selection.md) | preview from `flood` branch; split by riverine / pluvial / coastal | Branch-preview; deeper pressure test lives in [`discussion/flood/01`](../extra/discussion/flood/01_source_selection_pressure_test.md). |
| Hurricane | [`hurricane/source_selection.md`](hurricane/source_selection.md) | preview from `hurricane` branch; RAFT severity, HURDAT2 frequency, ASCE validation, flood-owned surge/rain | Branch-preview; deeper pressure test lives in [`discussion/hurricane/01`](../extra/discussion/hurricane/01_source_selection_pressure_test.md). |

## Cross-References

- Drive source universe: [`docs/google_drive_docs/README.md`](../google_drive_docs/README.md).
- Cross-hazard prerequisite guide: [`fundamentals_before_m0.md`](fundamentals_before_m0.md).
- Source-onboarding lesson: [`LL03`](../learning_logs/03_meet_complex_raw_data_from_scratch.md).
- Multi-source lesson: [`LL04`](../learning_logs/04_two_datasets_one_peril_decompose.md).
