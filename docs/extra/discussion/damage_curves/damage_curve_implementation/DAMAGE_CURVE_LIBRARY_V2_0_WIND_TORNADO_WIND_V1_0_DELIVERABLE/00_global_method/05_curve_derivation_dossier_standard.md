# 05 · Curve Derivation Dossier Standard

The derivation dossier is the proof trail. It should let a reviewer understand exactly how a curve was curated without reverse-engineering the workbook.

## 1. Required proof trail

```text
source evidence
   │
   ▼
source interpretation
   │
   ▼
anchor selection
   │
   ▼
curve-form decision
   │
   ▼
parameter fitting
   │
   ▼
selector variants
   │
   ▼
conditioner transformations
   │
   ▼
exposure/value scaling rules
   │
   ▼
assumptions and open seams
```

## 2. Required sections

Each dossier should contain these sections.

```text
1. Executive summary
2. Cell and failure-unit identity
3. Modeled y-axis meaning
4. X-axis decision
5. Evidence inventory with links
6. Source-to-parameter mapping
7. Raw anchors and interpreted anchors
8. Curve-form alternatives considered
9. Selected curve form and rationale
10. Parameter derivation
11. Base curve assumptions
12. Selector logic
13. Conditioner logic
14. Exposure/value scaling logic
15. Variant catalog
16. QA checks
17. Assumption register
18. Open seams and update triggers
19. Implementation notes
```

## 3. Source-to-parameter mapping

Every load-bearing parameter must be mapped to evidence or an explicit assumption.

| Parameter / rule | Value | Source ID | Evidence type | Interpretation | Caveat |
|---|---:|---|---|---|---|
| `D50_default` | `52.7 mm` | `SRC_...` | lab / public test | fitted from breakage anchor | limited sample / public summary |
| `k_default` | `0.166 1/mm` | `ASSUMP_...` + anchors | derived | fit from two anchors | not claims-calibrated |
| `stow_shift_mm` | `+8 mm` | `ASSUMP_...` | placeholder | direction supported, magnitude generic | replace with tracker-specific testing |

If a parameter has no source, label it as an assumption. Do not hide assumptions as if they were derived evidence.

## 4. Anchor table

Use a table that separates raw source statements from interpreted model anchors.

| Anchor ID | Raw source statement | Interpreted model anchor | Used for | Notes |
|---|---|---|---|---|
| `A1` | Source-reported test result | `D = 50 mm, P_break = 39%` | default curve fit | sample and test protocol caveats |

## 5. Curve-form alternatives section

Every dossier must include an alternatives table:

| Curve form | Why considered | Why not selected / why selected |
|---|---|---|
| Step threshold | matches certification pass/fail thinking | too discontinuous for expected DR |
| Bounded logistic | smooth, bounded, interpretable D50 | selected for v1 severity curve |
| Piecewise linear | transparent anchors | less stable outside anchors |
| Damage-state curve | useful if evidence is state-based | future if source provides states |

This prevents the curve form from looking arbitrary.

## 6. Parameter derivation section

Show the actual math.

For a bounded logistic:

```text
P(D) = L / (1 + exp(-k × (D - D50)))
```

If `L = 1`, and an anchor is `(D_a, P_a)`, then:

```text
logit(P_a) = ln(P_a / (1 - P_a))
logit(P_a) = k × (D_a - D50)
D50 = D_a - logit(P_a) / k
```

If two anchors are used:

```text
k = [logit(P2) - logit(P1)] / (D2 - D1)
D50 = D1 - logit(P1) / k
```

If the fitted value is judgmentally shifted, explain why.

## 7. Assumption register

Every assumption should have:

```text
assumption_id
assumption_text
affects
current_value
confidence
why_needed
replacement_evidence
update_trigger
```

Example:

```text
ASSUMP_HAIL_STOW_SHIFT_MM
  Current value: +8 mm D50 shift
  Affects: stowed curve
  Confidence: low/medium
  Why needed: public sources support direction but not generic magnitude
  Replacement evidence: tracker-specific hail stow testing or field claims
```

## 8. Open seams

Open seams are not failures. They are honest boundaries.

```text
OPEN SEAM
   a material question that can change the curve or output,
   but is not fully resolved in the current version.
```

Examples:

```text
- module BOM f_hail exposed value share
- tracker stow correlation with event forecast
- source-public test sample limitations
- lack of claims calibration
```

## 9. Source links

Every source card must include a link or file pointer. A reviewer should be able to click or locate the source from the dossier.

Required source fields:

```text
source_id
title
author_or_org
year
url_or_file_path
source_type
supports
limitation
accessed_or_packaged_date
```
