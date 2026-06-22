# M4 — loss & metrics (hurricane × wind-farm)

Compound-Poisson MC at the shared λ (0.0116/yr) → **wind-only** EAL / VaR / PML / TVaR (% of TIV + $). Event-based
catalog feeds the MC directly (no RP bridge). **EAL 0.012% · PML250 0.42% · PML500 1.43% of TIV** (98.85% loss-free
years) — wind is small at Amazon (storms below IEC turbine survival; tail = rare Cat-3 close passage). The cell's
material hazard is **surge**; this leg is the compound join partner.

- Notebook: [`01_loss_metrics`](01_loss_metrics.ipynb)
- Outputs: `data/hurricane/tc_windfarm_m4_loss_metrics.parquet` + annual vectors + EP curve (+ manifest)
- Next (separate): finish flood-coastal × wind M4 — join `tc_windfarm_m3_damage.parquet` to the surge leg on `event_family_id`.

## Metric schema (house standard — parity with hail / wildfire / convective-wind)
The manifest carries **two twin blocks with identical keys**, the block name carrying the unit: **`metrics_usd`**
(dollars) and **`metrics_pct_of_tiv`** (% of TIV). Keys: `EAL` · `VaR95 (AEP-PML20)` · `VaR99 (AEP-PML100)` (this *is*
PML100) · `VaR99.6 (AEP-PML250)` · `PML500 (AEP-99.8)` · `TVaR99` · `OEP-PML100`. **AEP** = annual aggregate (sum of a
year's storms); **OEP** = the year's single largest storm (occurrence basis — `np.maximum.at` over the same MC draw, no
extra sampling). λ≪1 here, so OEP ≈ AEP (a year rarely carries >1 storm). Known-answer checks added: AEP ≥ OEP every
year, OEP-PML100 ≤ AEP-PML100, TVaR99 ≥ VaR99, twin-block monotone + unit-consistency.
