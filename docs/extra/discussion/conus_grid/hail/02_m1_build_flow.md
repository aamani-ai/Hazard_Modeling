# 02 — Hail M1 Build Flow

*The short implementation-facing flow for the CONUS hail hazard layer. This does not replace the research
record or sourcing triage; it is the simple "what do we build first, and why?" bridge from those docs to a
pilot.*

---

## The conclusion in one line

**Hail M1 is self-build, anchored.** We build the per-cell frequency + size distribution ourselves from
gridded radar evidence, then anchor and validate it against the best available hail science and reports.

```text
MRMS + MYRORSS raw MESH
  -> aggregate to 0.25° cells
  -> fit per-cell frequency + size distribution
  -> de-bias / validate with Murillo & Homeyer + Storm Events
  -> add EVT tail where the observed radar record runs out
  -> write the durable per-cell M1 hazard layer
```

Why: [00 research](00_m1_data_products_research.md) found **no FSim-equivalent for hail**. No public product
hands us both:

1. annual severe-hail frequency per cell, and
2. a full hail-size distribution per cell.

The decision distilled from that evidence is [01 sourcing triage](01_m1_sourcing_triage.md): self-build, but
well anchored.

---

## What we are not doing

- **Not using FEMA NRI as M1.** NRI is a downstream risk / EAL index, not a physical hail hazard field.
- **Not using raw Storm Events as the grid.** Reports are long and useful, but population-biased and point-based.
- **Not treating MRMS as truth.** Raw MESH over-predicts hail and needs bias correction / validation.
- **Not bootstrapping the deep tail forever.** The radar record under-samples rare large hail, so the size tail
  needs a fitted / EVT treatment before `rp500` and high TVaR readouts are treated as final.

---

## The build flow

### 0. Confirm the gating decisions

Before code, turn the open triage questions into explicit decisions:

| Decision | Recommended answer |
|---|---|
| `DEC-H1` | Adopt **self-build, anchored** for hail M1. |
| `DEC-H2` | Include **MYRORSS** to extend the radar record, with a cross-era homogeneity check. |
| `DEC-H3` | Check **Das & Allen 2024** data access for the hail-size tail. If unavailable, mirror the method. |
| `DEC-H4` | Replicate / adapt the **Murillo & Homeyer** MESH de-biasing logic. |
| `DEC-H5` | Keep **FEMA NRI** only as an external EAL sanity check. |

### 1. Start with a pilot, not all CONUS

Pick a small cell set that proves the M1 machinery before scaling:

```text
high-hail cells       -> Plains / TX-OK-KS risk core
medium-hail cells     -> transition regions
low-hail cells        -> quiet controls
Hayhurst cell         -> bridge back to the existing hail × solar notebook
```

The pilot should write the **same schema** the full CONUS run will write, just for fewer cells.

### 2. Build the raw gridded evidence table

Use MRMS `MESH_Max_1440min` first because it is already familiar from the hail notebook and cached locally for
the recent record. Add MYRORSS once the MRMS-only pilot works.

For each day / grid cell:

```text
cell_id
date
max_mesh_mm
n_native_pixels_above_25_4mm
area_above_25_4mm
size_summary_or_histogram
source_product
qa_flags
```

The native radar grid is finer than the serving grid: MRMS is about 0.01° (~1 km), while the platform grid is
0.25° (~25 x 25 native pixels). Aggregating to 0.25° is both the CONUS serving step and the first de-noising
step.

### 3. Fit per-cell frequency

From the daily evidence, estimate severe-hail occurrence per cell:

```text
hail_day = max_mesh_mm >= 25.4
lambda_cell = annualized hail-day / event rate
frequency_family = Negative Binomial, Poisson nested
fano_phi = over-dispersion estimate or pooled / shrunk value
n_events_cell = sample-size QA
```

Sparse cells should not get over-confident independent fits. They need a pooling / shrinkage rule, borrowing
from the same family of ideas as Murillo & Homeyer smoothing and Das & Allen spatial Bayesian pooling.

### 4. Build per-cell size distribution

For each cell, estimate the conditional size distribution:

```text
P(hail_size | severe-hail event, cell)
```

Use MESH as the gridded empirical source, but do not treat it as ground truth. Storm Events is the report-side
calibration / validation source. The distribution should carry a body and a tail:

```text
body: empirical / parametric distribution from MESH and reports
tail: EVT-style fit or Das & Allen 2024 field if obtainable
```

This is the decisive gap from the research: the size distribution is what no ready public product gives us.

### 5. Anchor and validate

Use each source for its proper role:

| Source | Role |
|---|---|
| **MRMS MESH** | gridded self-build baseline |
| **MYRORSS** | record extension / longer radar evidence |
| **Murillo & Homeyer** | bias-correction recipe + frequency validation target |
| **Storm Events / SPC** | ground-truth reports for frequency and size calibration |
| **Das & Allen 2024** | possible size-tail field or method reference |
| **FEMA NRI** | downstream EAL sanity check only |

The validation question is not "does every cell match one external product?" It is: do the frequency map,
size map, and final loss map behave coherently against the best available anchors, with caveats visible?

### 6. Write the durable M1 hazard layer

The output of this work is the Stage-1 storage-boundary artifact:

```text
cell_id
hazard = hail
record_span
source_products
frequency_dist_family
lambda_cell
fano_phi
size_distribution_params
evt_tail_params
n_events_cell
qa_flags
model_version
```

This artifact does **not** contain EAL, VaR, PML, or TVaR. It feeds Stage 2. The risk-metrics layer is written
after coupling this hazard layer to the canonical solar and wind assets.

---

## The first useful pilot

The first build should prove this path:

```text
MRMS-only, selected cells
  -> daily cell evidence
  -> initial frequency + size distributions
  -> QA against Hayhurst / Storm Events / broad hail climatology
  -> tiny M1 hazard layer
  -> one Stage-2 solar run to verify final metrics can be produced
```

Only after that should we add MYRORSS, Murillo & Homeyer de-biasing, the EVT tail, and full CONUS scale.

---

## Cross-references

- Evidence base: [00_m1_data_products_research.md](00_m1_data_products_research.md).
- Decision triage: [01_m1_sourcing_triage.md](01_m1_sourcing_triage.md).
- Storage-boundary architecture: [../01_ideal_architecture_compute_and_grid.md](../01_ideal_architecture_compute_and_grid.md).
- Per-cell output schema: [../02_per_cell_output_schema.md](../02_per_cell_output_schema.md).
- Hail notebook precedent: [../../../../Notebooks/hail/README.md](../../../../Notebooks/hail/README.md).
