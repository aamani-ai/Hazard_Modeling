# Discussion: Hail × Wind Farm Exposure Model

**Status:** discussion note · **Date:** 2026-06-11 · **Decision status:** not canonical yet.

## Core Distinction

Hail × wind farm is **not** the wind-speed peril. It is the existing hail event catalog applied to a new
asset type:

```text
Peril = hail
Asset = onshore wind farm
M0/M1 = reuse the shared MRMS hail catalog
M2+   = new wind-farm coupling, damage, and loss notebooks
```

The useful modeling question is:

```text
Given an MRMS hail footprint,
which turbine points are inside it,
and what loss follows for those hit turbines?
```

## Why Solar And Wind Differ

Solar PV is a dense areal exposure: panels and trackers fill a compact plant footprint. Using one plant
area is a reasonable v1 abstraction.

```text
hail footprint overlaps solar polygon
    -> the plant is treated as hit
```

A wind farm is sparse: turbines are point assets spread across a much larger lease. A hail footprint can
cross the lease while missing most turbines.

```text
hail footprint crosses wind-farm lease
    -> maybe only 3 of 80 turbines are actually hit
```

So the bounding polygon is the wrong primary exposure model for hail × wind. The cleaner v1 model is a
per-turbine point cloud.

## Treatment Of Non-Turbine Assets

Do **not** model unknown substations, inverters, O&M buildings, or collection equipment as "one more
turbine." That mixes geometry and vulnerability.

Recommended handling:

```text
known turbine lat/lons:
  model each turbine as a point sub-asset

known substation/BOP coordinates:
  model as separate point or polygon sub-assets with separate vulnerability

unknown substation/BOP coordinates:
  exclude from v1 hail-vulnerable value, or add one clearly labeled approximate point
  with its own caveat and non-turbine vulnerability
```

The v1 notebook should be honest: **turbines-only unless we have better asset data**.

## Platform Guidance

Build hail × wind farm first as a **notebook architecture showcase**, not as a production platform result.

It is valuable internally because it proves:

```text
same hail catalog
different asset geometry
different M2 coupling
same M0 -> M4 interface
```

It should not be presented as a production-grade hail loss model for wind farms until these are in place:

- real turbine coordinates;
- a defensible turbine / blade hail vulnerability curve;
- per-turbine or component-level value allocation;
- explicit treatment of non-turbine balance-of-plant assets;
- source-locked references for whether hail is a material wind-turbine loss driver.

## Recommended V1 Notebook Scope

```text
Input:
  M1 hail catalog
  turbine lat/lons
  turbine count and farm value or turbine values

M2:
  for each hail event, intersect footprint polygon with turbine points
  derive n_hit_turbines and hit_fraction
  carry event hail size

M3:
  apply a provisional turbine/blade hail damage curve to hit turbines only
  clearly label the curve as placeholder or curated, depending on source quality

M4:
  aggregate hit-turbine losses to farm event loss
  simulate annual loss using the same M4 frame rules as hail × solar
```

This is useful if framed as:

> "Here is how the same hail event catalog couples differently to a sparse wind-farm point cloud."

It is not yet useful if framed as:

> "Here is the final hail risk number for this wind farm."
