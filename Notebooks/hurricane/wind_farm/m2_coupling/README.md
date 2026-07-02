# M2 — coupling (hurricane × wind-farm)

**Per-node field-intensity** — the non-degenerate form hurricane × solar foreshadowed. Samples the Holland 3-s gust at
all 105 nodes (104 turbines + collector) for the shared Amazon storm catalog, and *demonstrates* the field varies
across the ~18 km lease (per-storm spread median 4.4%, p95 21%) → per-node sampling required. Field math identical to
hurricane M1/M2; `value_exposed_fraction = 1.0` per node.

- Notebook: [`01_coupling`](01_coupling.ipynb)
- Output: `data/hurricane/tc_windfarm_m2_coupling.parquet` (+ manifest)
- Next: [M3 damage](../m3_damage/01_damage.ipynb)

## What Hurricane Wind-Farm M2 Asks

```text
M2 asks, for each storm:
  what 3-second gust reaches each turbine?
  what gust reaches the collector node?
  what is the min/mean/max gust across the lease?
  is the field non-degenerate enough to require per-node sampling?
  what event_family_id must stay attached?
```

It does not ask what those node gusts cost. M3 handles damage.
