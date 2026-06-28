# Hurricane Fundamentals Before M0

This is the hurricane prerequisite guide. Read it before the hurricane layer-0 and M0 notebooks.

Cross-hazard pattern:

```text
physics -> data-source reality -> M0-M4 translation
```

For hurricane:

```text
physics       -> tropical-cyclone wind field; surge/rain are real but owned by flood
data reality  -> RAFT gives storm structure/severity, HURDAT2 anchors frequency
pipeline      -> track -> Holland wind field -> field-intensity coupling -> storm-resolved MC
```

---

## 1. What Hurricane Means In This Repo

In this repo, "hurricane" means:

```text
tropical-cyclone wind damage
```

It does not mean the pipeline owns every damaging agent from a tropical cyclone.

One tropical cyclone can produce:

```text
wind       -> hurricane peril owns this
surge      -> flood coastal [C] owns this
rainfall   -> flood pluvial [F] owns this
```

The event identity connects them:

```text
event_family_id
```

This is the field that lets one physical storm be combined once across wind, surge, and rainfall instead of
being counted as separate unrelated events.

---

## 2. The Physical Driver: 3-Second Peak Gust

The hurricane wind damage curve consumes:

```text
3-second peak gust
```

This is the same structural wind observable used by convective wind, but the peril is different.

Convective wind:

```text
local severe storm / tornado / straight-line wind
```

Hurricane:

```text
large coherent tropical-cyclone wind field moving along a track
```

The shared observable does not make them the same peril. The footprint and event process differ.

---

## 3. Magnitude, Field, And Sampled Intensity

A hurricane has event-level descriptors:

```text
track
central pressure
maximum sustained wind
radius of maximum wind
category
```

But the asset damage curve needs the local gust at the asset:

```text
storm track + structure
    -> Holland wind field
    -> peak 3-s gust at the asset
```

ASCII:

```text
RAFT storm track
      |
      v
Holland radial wind model
      |
      v
continuous wind field
      |
      +--> gust at solar centroid
      +--> gust at turbine 1
      +--> gust at turbine 2
      +--> gust at substation
```

This is field-intensity coupling: the event produces a field, and M2 samples the field at the asset.

---

## 4. The Data-Source Split

Hurricane curation depends on not asking one source to do everything.

```text
RAFT:
    synthetic North Atlantic storm tracks
    good storm-structure/severity shape
    not used raw for frequency because genesis is oversampled

HURDAT2:
    observed historical tropical-cyclone record
    used to anchor close-passage / landfall frequency

ASCE 7-22:
    independent return-period gust validation

SLOSH:
    surge envelope source, but owned by flood coastal
```

The key move:

```text
severity shape from RAFT
frequency from HURDAT2
validation from ASCE
surge/rain cross-link to flood
```

This is why hurricane M0 is not just "load RAFT." It must also inspect observed frequency and validation
sources.

---

## 5. Why RAFT Instead Of Only A Return-Period Grid

A return-period wind grid can tell us a site gust at a probability level. It does not give physical storm
identity.

Hurricane needs storm identity because surge and rainfall must join back to the same storm.

```text
return-period grid:
    good for lookup / validation
    no event identity
    cannot connect wind + surge + rain from the same storm

storm-resolved RAFT catalog:
    event objects
    track and structure
    event_family_id
    can found wind/surge/rain compound logic
```

That is why RAFT is the catalog spine even though ASCE is useful for validation.

---

## 6. What M0 Must Teach You

M0 must make these raw sources legible:

```text
RAFT:
    track variables
    units, especially knots vs mph/m/s
    storm years and oversampling
    central pressure / RMW / intensity fields

HURDAT2:
    observed storm record
    close-passage rule
    frequency anchor

site geometry:
    solar centroid / footprint
    wind-farm turbine nodes
    coastal riders for flood cross-link
```

Unit discipline is load-bearing:

```text
knots -> mph: multiply by 1.150779
mph -> m/s: multiply by 0.44704
```

Do not apply the wrong conversion just because a sibling source uses a different unit convention.

---

## 7. What M1 Builds

M1 converts storm tracks into storm-resolved gust events.

```text
RAFT storm track
    -> Holland wind field
    -> peak gust at each site
    -> attach HURDAT2-observed frequency basis
    -> stamp event_family_id
    -> validate tail against ASCE
```

Event object:

```text
event_id
event_family_id
site_id
synthetic year / storm id
peak_gust_3s_mph
storm metadata
closest approach
frequency basis / manifest
```

The `event_family_id` is not decorative. It is the storm identity key for cross-peril combination.

---

## 8. M2 Coupling

Hurricane wind is field-intensity coupling.

For solar:

```text
storm scale >> solar footprint
gust variation across the plant is small
M2 can be approximately one centroid/effective gust
exposed_fraction = 1.0
```

For wind farms:

```text
storm field varies across a large turbine lease
M2 samples each turbine / node
field-intensity is non-degenerate
```

ASCII:

```text
large wind field

     110 mph contours
  -----------------------
      100 mph contours
   -------------------
       90 mph contours

solar: one small polygon -> one effective sample
wind:  many nodes over distance -> per-node samples
```

---

## 9. M0-M4 Translation For Hurricane

```text
Layer 0:
    define wind-only ownership, field-intensity coupling, event_family_id cross-link

M0:
    inspect RAFT, HURDAT2, ASCE validation, site geometry

M1:
    track -> Holland wind field -> per-site gust event catalog

M2:
    sample field at solar centroid or wind-farm nodes

M3:
    gust -> asset/subsystem damage curve

M4:
    storm-resolved compound-Poisson MC; combine with flood by event_family_id when needed
```

---

## 10. What To Watch In Hurricane Results

```text
[ ] Is hurricane scoped to wind only?
[ ] Are surge and rainfall routed to flood, not duplicated here?
[ ] Is event_family_id stamped and preserved?
[ ] Is RAFT used for severity shape, not raw frequency?
[ ] Is HURDAT2 used to anchor observed close-passage frequency?
[ ] Is the Holland field validated against observed/ASCE benchmarks?
[ ] Are units handled correctly: knots, mph, m/s, sustained vs gust?
[ ] Is solar field-intensity labeled spatially degenerate?
[ ] Are wind-farm nodes sampled separately when needed?
[ ] Is loss uncertainty attributed mostly to M3 curve confidence, not the validated hazard field?
```

---

## Source Context

- `docs/hazards/hurricane/README.md`
- `origin/hurricane:Notebooks/hurricane/README.md`
- `origin/hurricane:docs/plans/hurricane/00_hazard_definition.md`
- `docs/google_drive_docs/Hazard_Data_Reference.docx` - hurricane wind, SLOSH, RAFT/STORM, and flood cross-link framing.
- `docs/google_drive_docs/hazard_asset_loss_distribution_methodology.docx` - field-intensity and shared event identity.
