# Hail Fundamentals Before M0

This is the hail-specific prerequisite guide. Read it before the hail M0 notebooks.

Cross-hazard pattern:

```text
physics -> data-source reality -> M0-M4 translation
```

For hail:

```text
physics       -> damaging hailstone impact, represented operationally by hail size
data reality  -> MESH is a radar-estimated gridded field, not ground-truth hail size
pipeline      -> build hail-day footprints from raw grids, then couple by areal hit/miss
```

---

## 1. What The Physics Is

Hail damages exposed equipment through impact.

For solar PV, the key physical pathway is:

```text
hailstone impact
    -> module glass/cell breakage
    -> module replacement damage ratio
```

The operational hazard intensity is hail size:

```text
MESH-equivalent hail diameter, mm
```

The severe-hail event threshold is:

```text
MESH >= 25.4 mm
```

That threshold defines what M1 counts as severe hail. It does not mean the asset damage curve has already
left zero. For solar, the module curve has its own damage shape; hail around the threshold may produce small
damage, while larger hail drives replacement.

---

## 2. The Main Source Reality: MESH Is An Estimate

MRMS MESH is not a direct observation of a hailstone on the ground.

It is:

```text
radar reflectivity + algorithm
    -> Maximum Estimated Size of Hail
    -> gridded daily maximum field
```

Mental picture:

```text
MRMS daily MESH grid

  12  18  31  45   9
  22  41  68  52  14
  17  29  55  38  11

threshold at 25.4 mm

   .   .   X   X   .
   .   X   X   X   .
   .   X   X   X   .

severe pixels -> footprint -> hail-day event
```

This source gives us spatial completeness and footprints. It also has two big caveats:

```text
short operational record
radar-estimated size can overstate or produce impossible extremes
```

So hail M0 is not just "download data." It is source qualification:

```text
What is the grid?
What are the units?
What is the temporal window?
What does one daily max file mean?
What values are physically plausible?
What should be flagged but not silently deleted?
```

---

## 3. Why NOAA Reports Do Not Replace MRMS

NOAA Storm Events and SPC-style reports are useful, but they are not the spine.

```text
NOAA reports:
    long record
    point observations
    population/reporting bias
    no event footprint

MRMS MESH:
    short record
    complete gridded field
    event footprints
    radar-estimated size caveats
```

The curation rule is:

```text
MRMS = spine for footprints and event construction
NOAA = cross-check / future calibration, not extra events in the current spine
```

Why no naive merge?

```text
NOAA point report + MRMS grid are not two equal event lists.
Merging them as parallel events would double-count some storms and miss the reporting bias.
```

---

## 4. What M0 Must Teach You

Before modeling, M0 must make the raw hail evidence legible.

```text
M0 does not produce loss.
M0 does not decide hit probability.
M0 does not fit the final risk metric.

M0 answers:
    what did the source measure?
    what is one row / file / pixel?
    what are the units and time grain?
    what is reliable: occurrence, size, footprint, or all three?
```

For hail, the most important M0 lesson is:

```text
frequency evidence is more robust than raw size severity
```

A severe MESH pixel is still useful for detecting a severe hail day. But the exact extreme MESH value may be
unfit to drive loss without capping, de-biasing, or sensitivity labels.

---

## 5. What M1 Builds

M1 turns gridded evidence into catalog objects.

```text
daily MESH field
    -> threshold severe pixels
    -> union/aggregate into footprint polygon
    -> compute footprint area F
    -> record peak MESH
    -> one hail-day event
    -> fit annual count process
```

The M1 event object is roughly:

```text
event_id
date
footprint polygon
footprint area
peak MESH diameter
source flags
```

For the deep asset run, annual counts were over-dispersed, so the count process is Negative Binomial. For the
CONUS grid, current V1 uses Poisson per cell because most cells have too little local history to estimate
dispersion honestly.

---

## 6. Why Hail Uses Areal Hit-Or-Miss Coupling

Hail reaches a solar asset through footprint overlap.

```text
event footprint
       +
solar plant footprint
       |
       v
does this event hit the plant?
```

For an extended solar plant, the hit probability is not just `F / A` or `s / A`. The event footprint and the
asset footprint both have size.

The simple teaching approximation is:

```text
p_hit = (sqrt(F) + sqrt(s))^2 / A

F = event footprint area
s = solar plant footprint area
A = collection-region area
```

This is a compact Minkowski-style approximation: expand the event by the asset or the asset by the event, then
ask what fraction of the collection region would produce an overlap.

Mental picture:

```text
collection region A

+------------------------------------------------+
|                                                |
|        event footprint F                       |
|          +---------+                           |
|          |         |    solar footprint s      |
|          +---------+       +---+               |
|                            +---+               |
|                                                |
+------------------------------------------------+

hit probability asks:
where could the event center/placement be so the two shapes overlap?
```

This belongs in M2, not M1. M1 is asset-free; it records the event footprint. M2 is where the asset geometry
enters.

---

## 7. M0-M4 Translation For Hail

```text
M0:
    meet MRMS MESH, NOAA reports, MYRORSS qualification

M1:
    build hail-day footprint catalog and count process

M2:
    for a specific asset, compute hit probability / sampled hit events

M3:
    convert hail diameter to damage ratio through the asset damage curve

M4:
    simulate annual event counts, hits, event losses, and metrics
```

ASCII pipeline:

```text
MRMS daily MESH
      |
      v
threshold >= 25.4 mm
      |
      v
hail-day footprints + peak size
      |
      v
M2 asset overlap / p_hit
      |
      v
M3 size -> damage ratio
      |
      v
M4 annual losses
```

---

## 8. What To Watch In Hail Results

```text
[ ] Is MESH being treated as radar-estimated size, not ground truth?
[ ] Is NOAA being used as validation/cross-check, not a naive second spine?
[ ] Is one event = one hail-day clearly stated?
[ ] Is M1 still asset-free?
[ ] Does M2 use footprint overlap / Minkowski logic rather than a simple F/A shortcut?
[ ] Are deep-run and grid frequency choices explained separately?
[ ] Are extreme raw MESH values capped/flagged before severity/loss use?
[ ] Is the damage curve applied to the correct asset value bucket, not the whole plant by accident?
```

---

## Source Context

- `docs/hazards/hail/README.md`
- `Notebooks/hail/m0_input_data/README.md`
- `Notebooks/hail/m1_catalog/README.md`
- `docs/google_drive_docs/Hazard_Data_Reference.docx` - hail source landscape and MESH role.
- `docs/google_drive_docs/hazard_asset_loss_distribution_methodology.docx` - areal hit-or-miss coupling.
