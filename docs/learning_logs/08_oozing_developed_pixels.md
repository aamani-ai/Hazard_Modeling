# The Asset Pixel Can Be a Hole — Hazard Rasters Ooze Frequency onto Developed Land but Suppress Intensity

*At a solar site, the hazard raster cell *under the array* can report a burn probability but **zero flame
intensity** — because the array is mapped "developed," and the product oozes BP into developed pixels while
withholding intensity there. Read the site naively and you silently zero out its severity.*

**Status:** v1.0 · written 2026-06-13 · **Sourced from:** wildfire × solar, M0 (`01_wrc_geoplatform`) — the
solar-site land-cover check / [AW-15](../plans/wildfire/assumptions.md) · **Applies to:** any **site-conditioned**
peril (wildfire, flood) read off a gridded hazard product at a developed/engineered site.

---

## Where this came from

`01_wrc_geoplatform` checked the WRC layers **at the asset pixel** for both assets. At **Hayhurst**, the
array's pixel reported `BP = 5×10⁻⁴` but `CFL = FLEP4 = FLEP8 = 0`. At **Matrix**, the pixel had real
intensity. The WRC 2.0 methods doc explains it: *"FLEP4 was not oozed into developed areas."* — i.e. the
product **smears burn probability into developed/non-burnable cells for continuity, but deliberately leaves
intensity blank there.**

## Why it looks fine — the trap

The obvious, clean thing is to sample the hazard **at the asset's location** — one pixel, done. For most
fields that's right. But a utility solar array is mapped as *developed*, and a site-conditioned product
treats developed cells specially: **frequency oozes in, intensity is withheld.** So a single-pixel read
returns `BP > 0, intensity = 0` → conditional loss = 0 → **the site silently contributes no severity**, which
*looks* like a valid "low risk" answer rather than a sampling artifact.

## The lesson

> **The lesson.** For a site-conditioned peril, the asset's own pixel may be a **developed hole in the
> intensity field**. Detect it **per asset** (BP present but intensity ≈ 0), and where present, source the
> on-site hazard from the **surrounding fuel** (a boundary buffer/ring), not the centroid pixel. The hazard a
> plant faces is the fire that *reaches it from adjacent fuel* — which is exactly what the developed pixel
> omits.

`[REF]` WRC methods: intensity is not oozed into developed areas (a documented product behaviour). `[OURS]`
What building added: (1) it is **asset-specific** — Hayhurst's pixel is oozed, Matrix's is not, so you can't
assume either way; (2) the fix is to read the **surrounding-fuel footprint**, and (3) there's a ready tool —
the Hydronos `analysis="buffer_ring"` mode returns stats on a ring around the boundary (`02b`).

**Worked.** Hayhurst — asset pixel: `BP 5e-4`, `CFL 0`, `FLEP4 0`; surrounding footprint (≈386 m): `CFL ≈ 2.2
ft`, `FLEP4 ≈ 0.20`. The centroid says "no flames ever"; the surrounding grass says "modest but real." Only
the footprint read is honest.

## How to recognize it next time

- **The signal:** `BP > 0` **and** intensity (CFL/FLEP/depth) `≈ 0` **at the asset pixel** → suspect a
  developed-land hole, not genuine zero intensity.
- **The rule:** for site-conditioned perils, default to a **footprint/ring** read, and treat a single-centroid
  intensity of 0 over a non-zero-BP site as a flag to investigate, never as a result.
- Cross-check land cover (LANDFIRE/NLCD) of the asset footprint if intensity is suspiciously absent.

## Caveats and limits

- **Site-conditioned only.** For **areal hit-or-miss** (hail) the asset pixel isn't an intensity field to
  begin with; for **field-intensity** perils (wind) developed land isn't masked the same way. This is the
  flood/wildfire family.
- **Oozing is a *frequency* convenience, not error** — BP in developed cells is intentional continuity; the
  trap is only the *intensity* gap.
- The surrounding-ring read introduces its own choice (buffer distance/mode) — a parameter to set
  consciously at M2, not silently.

## Cross-references

- **Assumption it explains:** [`AW-15`](../plans/wildfire/assumptions.md) (solar-site "oozing", M2-critical).
- **Decision it informs:** [`DD-W2`](../plans/wildfire/decisions.md) (site-conditioned coupling) — M2 must
  detect oozing per-asset and read the surrounding fuel.
- **Where it shows in code:** `Notebooks/wildfire/m0_input_data/01_wrc_geoplatform.ipynb` §9 (oozing check) ·
  `02b_fsim_via_hydronos.ipynb` (the `buffer_ring` tool).
- `[REF]` WRC 2.0 Methods (developed-area oozing) — [`discussion/wildfire/02`](../extra/discussion/wildfire/02_fsim_wrc_data_dictionary.md) §6.
