# Decisions — Hail pipeline (2026-06-09)

Session-level summary. The canonical ADR log is [`docs/plans/hail/decisions.md`](../../../plans/hail/decisions.md)
(DD-1..4); the generalizable lessons are in [`docs/learning_logs/`](../../../learning_logs/) (01–05). This
file is the index + the *why*.

## 1. MRMS is the spine, NOAA is a cross-check (not a naive splice) — DD-1

**Decision.** v1 catalog = **MRMS-only** (gridded footprints), homogeneous; NOAA point reports are a
calibration/cross-check overlay that adds **no events**. **Rationale.** Combining two sources of one peril is
a "hybrid validated backbone," not a symmetric merge; a naive NOAA(long,biased)+MRMS(short,clean) temporal
splice fabricates a rate discontinuity at the seam (inhomogeneity trap). Homogeneity > length for a
trustworthy λ. See `learning_logs/01`.

## 2. Frequency = Negative Binomial, prior then fit — DD-2

**Decision.** Declare `frequency_process = negative_binomial` (nests Poisson) with a weakly-informative
prior on the Fano factor (φ median 2); **don't assume — test dispersion and fit** when the record is wide
enough. **Rationale.** Count distribution is a *tail* decision (barely moves EAL, strongly moves VaR/PML);
SCS counts cluster → over-dispersed. At v1 (≤6 annual counts) the test is underpowered → prior carries it.
*Now fitted* on the widened record (φ = 3.37, over-dispersion confirmed). See `learning_logs/02`.

## 3. Frequency & catalog sources, **by component** — DD-3

**Decision.** `p` (spatial factor) ← MRMS always (only it has footprints); `λ_collection` (rate) ←
**MRMS-widen now** (Stage 1, done) → **NOAA-calibrated extension** later (Stage 2, for a longer record).
**Rationale.** "Which dataset is primary?" is the wrong question — decompose `λ_asset = λ_collection × p`
and take each component from its best source; raw NOAA counts are biased, so NOAA *extends* the rate
(calibrated), it doesn't replace MRMS. See `learning_logs/04`.

## 4. Frame consistency — all tail metrics off the same per-year vectors — DD-4

**Decision.** Every metric reads off the same `AEP_year` / `OEP_year` vectors; never compare an OEP number to
an AEP number; PML at return period T = the (1−1/T) percentile. **Rationale.** The old repo's worst bug was a
frame mismatch (~175× invariant violation). The math-validation audit confirmed our frame is correct —
recording it pins the invariant.

## 5. Damage curve = capex-weighted subsystem blend (temporary)

**Decision.** Asset DR = `Σ wᵢ·DRᵢ` from `infrasure-damage-curves` (PV_MODULE L=0.95 + TRACKER L=0.40 × NREL
capex weights → caps ~34%), replacing the literature curve that extrapolated to ~100%. **Rationale.** The
asset can't lose ~100% to hail — ~64% of value (inverters/substation/electrical/civil/SCADA) is hail-immune.
This is a **temporary** asset-level fix; the curve repo gets a full revamp (better weights, conditional-DR
distribution, plant-specific at-risk value-allocation). See `learning_logs/05`.

## 6. Process decisions (how we work)

- **`docs/learning_logs/`** — a derived-knowledge tier (knowledge not in the references); mark `[REF]` vs `[OURS]`.
- **Assumptions register** (`assumptions.md`, A1–A23) — every input/curve/simplification, with status +
  revisit; surfaced per-layer in notebooks + READMEs.
- **Per-layer folder READMEs** — first-reader orientation for each m0/m1/m2/m3/m4 folder.
- **Build strategy** — notebooks-first across 3 hazards, *then* the production architecture (not before).
- **`scripts/`** = testing/one-time/utility, explicitly not production code.
- **Metrics shown as % of TIV** alongside dollars.
