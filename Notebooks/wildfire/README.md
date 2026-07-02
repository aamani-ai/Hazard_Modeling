# Wildfire - peril overview

Wildfire is organized as a site-conditioned peril. The public FSim products already summarize simulated fire seasons
into burn probability and flame-length probability at the asset location, so this folder does not build a storm-like
event catalog the way hail does.

```text
wildfire/
  m0_input_data/   <- WRC and FSim public raster evidence
  m1_catalog/      <- per-asset hazard profile: lambda + conditional flame-intensity distribution
  solar/           <- wildfire x solar M2 coupling, M3 damage, M4 loss metrics
```

The two solar examples bracket the signal:

```text
Hayhurst Texas Solar:
  low-fire / known-answer-low reference

Matrix Pleasant Valley:
  higher-fire reference
```

## M0-M4: What Each Layer Asks

```text
M0 asks:
  what wildfire raster products exist at the asset?
  what does each pixel value mean?
  are burn probability and intensity coming from the same source/vintage?
  which source is primary and which is a cross-check?

M1 asks:
  what burn probability applies to the asset footprint?
  how does BP convert to annual fire frequency lambda?
  what FLP1-6 conditional severity distribution applies given a fire?
  what intensity values in kW/m should M3 consume?

M2 asks:
  does wildfire need an areal hit/miss calculation here?
  what exposure fraction is assumed?
  does local developed/cleared asset area require an oozing or surrounding-fuel adjustment?
  what clean lambda + conditional intensity handoff goes to M3/M4?

M3 asks:
  given fire-line intensity:
    which solar BoS components are damaged?
    what damage ratio applies by component?
    what capex-weighted asset damage ratio results?
    what full conditional loss is emitted?

M4 asks:
  over many simulated years:
    how many fires occur at the site?
    what conditional intensity/loss is sampled for each fire?
    what annual AEP/OEP distribution results?
    what are EAL, PML, VaR, and TVaR?
```

The core wildfire discipline is:

```text
FSim already did the event simulation upstream.
M1 reads the pre-integrated site hazard profile.
M4 still samples occurrence and severity; it does not multiply lambda into loss rows.
```
