# Common — Validation

Validation has two jobs:

1. catch source/data mistakes before a full grid fanout; and
2. keep the grid product consistent with deep asset runs.

## Required Validation Families

| Family | What it checks | Applies to |
|---|---|---|
| Grid join validation | source pixels/events attach to the intended `cell_id`; no key drift | all hazards |
| Coverage validation | no-data is not treated as zero risk | all hazards |
| External anchor validation | broad spatial pattern agrees with independent climatology or source product | all hazards |
| Point-vs-cell validation | known assets/cells behave consistently with deep asset notebooks, allowing for exposure differences | all hazards |
| Metric identity validation | `PML_T = VaR_(1 - 1/T)` and AEP/OEP frames do not mix | risk layer |
| Tail caveat validation | sparse/short-record cells and bootstrap-limited tails are flagged | risk layer |

## Hail-Specific First Checks

- MRMS severe-hail-day counts are plausible in high, medium, low, and reference cells.
- MESH size distribution is clearly marked as radar-estimated, not ground truth.
- Storm Events agrees directionally where reports exist, without treating reports as complete truth.
- Sparse cells are flagged before fitting tails.

## Wildfire-Specific First Checks

- Per-cell burn probability aggregation agrees with FSim/WRC source expectations.
- Flame-length distribution is internally coherent with the selected source vintage.
- Developed/non-burnable pixel caveats from WRC/FSim are carried into provenance where relevant.
