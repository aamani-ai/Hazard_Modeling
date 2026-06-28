# Site-Conditioned Is Not One Thing — Classify The Condition Surface Before Choosing M2

*`site-conditioned` says the hazard is already local to the asset; it does not say which site conditions
matter, whether they are natural or engineered, or whether they belong in M2, M3, value allocation, or data QA.*

**Status:** v1.0 · written 2026-06-26 · **Sourced from:** flood fundamentals, wildfire M2/site-condition
discussion, convective-wind strong-wind coupling, and the cross-hazard coupling taxonomy · **Applies to:**
any site-conditioned peril, plus any field-intensity peril whose local field must be adjusted before damage.

---

## Where this came from

The flood work made a gap visible that wildfire had already hinted at. We were comfortable saying both
wildfire and flood are `site-conditioned`, because neither should use hail-style regional hit probability.
But that label was too coarse:

- **Wildfire** site conditions often look like fuel, vegetation management, defensible space, land-cover
  boundaries, setbacks, and site layout. Some are natural, but many are managed or manmade.
- **Flood** site conditions include natural geometry such as ground elevation, drainage path, river proximity,
  coastal setting, and local slope, plus engineered protection such as levees, flood walls, grading, culverts,
  pads, pumps, and equipment elevation.
- **Strong wind** can also be site-conditioned when the source is a local return-period gust profile: terrain,
  exposure category, topography, hub height, and turbine class decide how the local field becomes asset load.

That means `site-conditioned` is a coupling family, not a complete model.

## Why it looked fine — the trap

The coupling taxonomy is useful:

```text
areal hit-or-miss      field-intensity           site-conditioned
-----------------      ---------------           ----------------
footprint overlaps?    sample local field        local profile / condition
```

The trap is to stop there. Once a hazard is labeled `site-conditioned`, it is tempting to create one generic
adapter: read the local raster value, maybe apply one scalar site factor, then send it to M3. That looks clean,
but it hides the actual physical question:

```text
conditioned on what?
```

Flood depth at an inverter is not the same kind of condition as vegetation clearance around a solar array.
Both are site conditions, but they enter the model in different places.

## The lesson

> **The lesson.** Before building M2 for a site-conditioned hazard, write a **site-condition ledger**: list
> each condition surface, identify whether it is natural, engineered, operational, asset-geometric, or a data
> artifact, and assign it to the stage where it actually changes the model.

The useful split is:

```text
site-conditioned coupling
    |
    +-- natural surface
    |     elevation, slope, river distance, drainage path, terrain exposure, surrounding fuel
    |
    +-- engineered / managed surface
    |     flood wall, levee, grading, pad, culvert, vegetation management, defensible space
    |
    +-- asset geometry / component placement
    |     inverter height, panel height, turbine hub height, substation pad, equipment critical elevation
    |
    +-- operational or event-time state
    |     temporary barriers, pumps, shutdown/stow decisions, maintenance state
    |
    +-- source-product artifact
          DEM resolution, datum mismatch, land-cover class, developed-pixel oozing, raster smoothing
```

And the stage test is:

```text
M2 coupling
  if the condition changes the hazard intensity/contact that reaches the component
  examples: WSE - equipment elevation; fuel ring around site; 10 m gust -> hub-height gust

M3 damage
  if the condition changes vulnerability given the same contact intensity
  examples: waterproofing, glass standard, module mounting, component fragility class

Value / exposure allocation
  if the condition changes how much value is exposed to the damaged component or subsystem
  examples: only the inundated block of an array, only inverters below a pad threshold

Data QA / source qualification
  if the condition is not physical but created by the source product
  examples: developed-pixel wildfire oozing, DEM vertical error, datum mismatch
```

`[REF]` The methodology and principle docs already separate coupling types and require hazard-specific
physics behind a standard interface. `[OURS]` What the flood/wildfire comparison adds is a second-level rule:
once the coupling type is `site-conditioned`, classify the **condition surface** before deciding what M2 does.

### Same label, different mechanics

| Hazard | Site-condition shape | What M2 must not hide |
|---|---|---|
| Wildfire × solar | Surrounding fuel, defensible space, land-cover boundary, standoff distance, site layout. | The asset pixel may be a developed hole; a ring/footprint read can be more honest than a centroid read. |
| Flood × solar | WSE/depth field, ground elevation, equipment height, flood walls, levees, drainage, river/coastal proximity. | Depth is often `water surface - local critical elevation`, not just a raster value at the centroid. |
| Strong wind × wind farm | Return-period gust profile, exposure category, terrain/topography, hub height, turbine class. | A 10 m reference gust is not automatically the hub-height gust the damage curve needs. |

The site-condition label therefore means:

```text
no regional p_hit thinning
```

It does **not** mean:

```text
no spatial math
no asset geometry
one generic site factor
one stage owns every condition
```

## How to recognize it next time

- If the phrase `site-conditioned` appears, immediately ask: **conditioned on what surfaces?**
- If the first M2 design has one scalar site factor, check whether it accidentally mixes natural elevation,
  engineered protection, component height, and source-product artifacts.
- If a mitigation is controllable, such as vegetation management or a flood wall, do not bury it as a fixed
  hazard value unless v1 explicitly chooses that simplification.
- If the data source is a raster at a developed site, inspect whether the source product has created a hole,
  smear, datum mismatch, or resolution artifact.
- If the same local intensity feeds multiple components, ask whether the component-specific condition belongs
  in M2 (`depth at inverter`) or M3 (`inverter fragility at that depth`).

## Caveats and limits

- This does not remove the coupling taxonomy. `areal hit-or-miss`, `field-intensity`, and `site-conditioned`
  are still the right first split. This learning adds the second split needed inside `site-conditioned`.
- Natural vs manmade is useful, but not sufficient. Data-product artifacts and operational states are their
  own categories because they lead to different implementation and documentation choices.
- Some conditions are deferred in v1. That is acceptable when explicit, but the ledger should still name the
  omitted condition and say whether it is a physics omission, data omission, or product-scope choice.
- The line between M2 and M3 is practical, not metaphysical. Use the stage test: does the condition change
  the contact intensity reaching the component, or the damage response after contact intensity is known?

## Cross-references

- Principle: [`standard interface, not standard physics`](../principles/hazard_asset_specificity.md).
- Cross-hazard prerequisite guide: [`fundamentals_before_m0`](../hazards/fundamentals_before_m0.md).
- Flood fundamentals: [`flood/fundamentals_before_m0`](../hazards/flood/fundamentals_before_m0.md).
- Wildfire fundamentals: [`wildfire/fundamentals_before_m0`](../hazards/wildfire/fundamentals_before_m0.md).
- Convective-wind fundamentals: [`convective_wind/fundamentals_before_m0`](../hazards/convective_wind/fundamentals_before_m0.md).
- Sibling learning: [`08_oozing_developed_pixels`](08_oozing_developed_pixels.md) — the wildfire version of
  the data-product-artifact problem.
- Sibling learning: [`09_pre_integrated_vs_extracted_catalog`](09_pre_integrated_vs_extracted_catalog.md) —
  source shape and coupling type often align, but they are not the same classification.
