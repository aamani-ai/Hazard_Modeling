# Wildfire Fundamentals Before M0

This is the wildfire prerequisite guide. Read it before the wildfire M0 notebooks.

Cross-hazard pattern:

```text
physics -> data-source reality -> M0-M4 translation
```

For wildfire:

```text
physics       -> exogenous fire reaching the asset, with intensity conditional on burn
data reality  -> FSim already pre-integrates burn probability and flame-length severity
pipeline      -> assemble a site hazard profile; do not invent hit/miss geometry
```

---

## 1. What The Physics Is

Wildfire damage comes from fire reaching the site and exposing equipment to heat/flame.

The hazard is not one scalar like hail size. It is a pair:

```text
frequency:
    burn probability / annual rate

severity:
    flame length / fire-line intensity conditional on a fire
```

The damage curve consumes fire intensity:

```text
flame length class
    -> fire-line intensity kW/m
    -> solar subsystem damage ratio
```

Frequency and severity must stay separate until M4.

---

## 2. The Main Source Reality: FSim Is Pre-Integrated

Wildfire is different from hail. We do not build events from raw observations.

FSim has already simulated many fire seasons and published per-pixel results:

```text
Burn Probability (BP)
    annual probability the pixel burns

Flame Length Probability (FLP1-6)
    severity histogram conditional on burn
```

ASCII:

```text
FSim pixel

  BP = annual P(burn)

  conditional on burn:
      FIL1  <2 ft
      FIL2  2-4 ft
      FIL3  4-6 ft
      FIL4  6-8 ft
      FIL5  8-12 ft
      FIL6  12+ ft
```

This means M1 is profile assembly, not event extraction.

---

## 3. Why WRC And FSim Are Not Interchangeable

The wildfire notebooks compare WRC and native FSim.

Mental split:

```text
native FSim:
    270 m
    BP + full FLP1-6 histogram
    severity spine

WRC:
    30 m display/product view
    collapsed intensity fields such as CFL/FLEP4/FLEP8
    useful cross-check and texture
```

They are related products, but not identical sources that can be mixed field-by-field without thought.

The curation rule:

```text
pick one severity spine,
use the other as comparison/cross-check,
document vintage and representation differences.
```

---

## 4. What M0 Must Teach You

M0 is source understanding.

```text
What is BP?
Is BP a percent-scaled integer or a probability?
What does FLP mean?
Are severity probabilities conditional on burn?
What are the flame-length bins?
What is the raster resolution?
What is the land-cover/fuel vintage?
Does the asset pixel represent fuel, or developed land?
```

The key beginner mistake is multiplying frequency and severity too early:

```text
wrong mental collapse:
    BP * average severity -> one expected damage number

right:
    lambda from BP
    conditional severity histogram
    sample annual fire occurrence and severity in M4
```

---

## 5. The Oozing Issue

Wildfire has an asset-pixel trap.

Developed/asset pixels can show burn probability but suppressed intensity because the fuel model sees the
asset area as non-burnable or developed. Fire can still threaten the asset from surrounding fuel.

Mental picture:

```text
surrounding burnable fuel ring

  f f f f f f f
  f           f
  f   asset   f   <- developed pixel may be a "hole"
  f           f
  f f f f f f f
```

So M2 may need to read the surrounding fuel ring, not only the exact asset pixel.

This is site-conditioned coupling: the hazard is local to the site, but conditioning it to the asset still
requires asset-aware logic.

For wildfire, those site conditions are often fuel, managed vegetation, defensible space, land-cover
boundaries, standoff distance, and source-product artifacts such as developed-pixel oozing. See
[`LL15`](../../learning_logs/15_site_conditioned_is_not_one_thing.md) for the cross-hazard rule.

---

## 6. What M1 Builds

M1 turns the FSim profile into the typed hazard object:

```text
BP
    -> lambda = -ln(1 - BP)

FLP1-6
    -> conditional severity distribution
    -> fire-line intensity per class

manifest
    -> source, units, bins, assumptions, fano = 1 structural
```

There is no regional collection window and no Minkowski hit probability. The rate comes from the site product
itself.

---

## 7. M2 Coupling

Wildfire is site-conditioned.

```text
site hazard profile
    -> condition to asset exposure
    -> account for oozing / surrounding fuel
    -> apply standoff / defensible-space assumptions
```

For solar V1:

```text
exposure_fraction = 1.0 if a fire reaches the site
partial fire-front sweep is deferred
```

This is different from hail:

```text
hail:
    event footprint may miss the asset

wildfire:
    BP already describes fire occurrence at/near the site
```

---

## 8. M0-M4 Translation For Wildfire

```text
M0:
    inspect WRC and FSim source products

M1:
    assemble lambda + conditional flame-length / fire-line-intensity distribution

M2:
    condition the site profile to asset exposure and surrounding fuel

M3:
    fire-line intensity -> subsystem damage ratio

M4:
    simulate annual fires and event severities, then read annual loss metrics
```

ASCII:

```text
FSim BP + FLP
      |
      v
lambda + conditional severity histogram
      |
      v
site-conditioned coupling / oozing guard
      |
      v
kW/m -> damage ratio
      |
      v
annual loss distribution
```

---

## 9. What To Watch In Wildfire Results

```text
[ ] Is BP kept separate from conditional severity?
[ ] Is native FSim FLP1-6 used as the severity spine?
[ ] Is WRC used as cross-check/texture rather than mixed silently?
[ ] Is BP conversion documented?
[ ] Is oozing checked before trusting the asset pixel?
[ ] Is M2 site-conditioned, with no fake p_hit thinning?
[ ] Is partial burn / fire-front sweep labeled deferred?
[ ] Is M3 curve uncertainty identified as the dominant limitation?
```

---

## Source Context

- `docs/hazards/wildfire/README.md`
- `Notebooks/wildfire/m0_input_data/README.md`
- `Notebooks/wildfire/m1_catalog/README.md`
- `docs/hazards/wildfire/solar.md`
- `docs/google_drive_docs/Hazard_Data_Reference.docx` - wildfire source landscape and FSim/WRC role.
- `docs/google_drive_docs/hazard_asset_loss_distribution_methodology.docx` - site-conditioned coupling.
