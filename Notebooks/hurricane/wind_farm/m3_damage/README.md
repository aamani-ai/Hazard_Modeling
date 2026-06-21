# M3 — damage (hurricane × wind-farm)

Maps each node's 3-s gust → **per-storm, per-subsystem** wind DR, stamped `event_family_id` — **the deliverable** the
flood-coastal × wind M4 compound combine joins to the surge leg (JD-FL-12, `max(wind_DRᵢ, surge_DRᵢ)` per subsystem).
Reuses convective_wind's turbine wind curve (hurricane wind on a turbine ≈ straight-line wind): aero reach only
(rotor/nacelle/electrical/substation), asset DR caps ~0.65 (no tower-collapse total-loss mode). **Low confidence.**

- Notebook: [`01_damage`](01_damage.ipynb)
- Output: `data/hurricane/tc_windfarm_m3_damage.parquet` + vendored curve (+ manifest)
- Finding: bimodal — bulk tiny (median ~0.3%), rare Cat-3 close passage ~11% of TIV.
