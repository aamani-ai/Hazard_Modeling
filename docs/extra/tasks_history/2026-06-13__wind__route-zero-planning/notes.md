# Notes — implementation, commands, verification, insights

## How the route-zero was built (two workflows)

**Workflow 1 — build** (`wind-route-zero`, 11 agents, ~26 min, ~1.13M tokens):
- *Research (4 parallel readers):* `Hazard_Data_Reference` (extracted to `/tmp/hdr.txt`); the `hazard_analysis`
  prior art (mag_sim, the worked example, wind_config); the wildfire kickoff template + voice; the
  principles/learnings/coupling definitions.
- *Draft (4 parallel authors):* layer-0 hazard-definition; the spine (README/intent/decisions/assumptions); the
  M0–M4 plans + done scaffold; the discussion docs.
- *Review (3 parallel lenses):* domain correctness, pedagogy, consistency/house-style.

**Workflow 2 — fix-up** (`wind-route-zero-fixups`, 9 agents): 8 per-file fixers (DD-WN renumber, notebook-fork
reconciliation, glosses) + 1 verifier. Result: **5/5 PASS**.

## Commands used (key ones)

```bash
# Extract the .docx reference (no python-docx dependency) — reuse this for any Google-Drive .docx:
.venv/bin/python - <<'PY'
import zipfile, re
xml = zipfile.ZipFile("docs/google_drive_docs/Hazard_Data_Reference.docx").read("word/document.xml").decode("utf-8","ignore")
out=[re.sub(r"<[^>]+>","",p).replace("&amp;","&").strip() for p in re.split(r"</w:p>", xml)]
open("/tmp/hdr.txt","w").write("\n".join(t for t in out if t))
PY

# Query the renewablesinfo boundary DB for wind sites (OSM schema: source=fuel, output=capacity-in-kW):
#   filter source~"wind", parse output→MW, shapely centroid → state; rank by capacity in the Great Plains box.
# (full snippet in the session transcript; Traverse OK + Shepherds Flat OR chosen.)

# Commit + push (route-zero):
git add docs/plans/convective_wind docs/extra/discussion/convective_wind
git commit -F - <<'EOF' ... EOF        # 5010a61
git push origin main                    # SSH alias github.com-work
```

## Verification (what we checked)

- **DD-WN cross-refs:** every `[DD-WN-N]` in the m-plans resolves to a real header in `decisions.md` whose
  *content* matches the in-context use. (After the fix-up — the build draft had a stale pre-final numbering.)
- **Links:** all relative links in the wind docs resolve on disk (independent bash check + the verify agent).
- **Notebook-fork consistency:** README / 00_intent / done / m-plans all agree — fork at M2 only; M3/M4 shared.
- **Pedagogy fixes landed:** the site-conditioned-vs-field-intensity contrast box (discussion/02), the F/s/A
  legend + derecho/μ_mean/λ glosses (00_hazard_definition), the EF5 "ceiling"→"truncation above the floor".
- **Secret scan** of the new docs before the public push: clean.

## Reference facts locked (the grounding, all traced to `Hazard_Data_Reference` unless noted)

- **Magnitude metric:** 3-second peak gust (mph) — the universal metric → fragility curve.
- **Strong-wind event threshold:** severe ≥ **58 mph (≈ 25.9 m/s)** (NWS; old repo stored 25.92).
- **EF scale (3-s gust, damage-inferred via 28 DI × 8 DOD):** EF0 65–85 / EF1 86–110 / EF2 111–135 / EF3
  136–165 / EF4 166–200 / EF5 **>200** mph (open-ended).
- **Physical bound L ≈ 113 m/s (~253 mph)** — *settled-framing / old-repo `HAZARD_LIMITS`, NOT the reference*;
  truncation above the open-ended EF5 floor; old repo had tornado L=145 m/s (Doppler max) — we adopt 113.
- **IEC 61400** Vref 50/42.5/37.5 m/s (class I/II/III); Ve50 ≈ 1.4·Vref ≈ 52–70 m/s — *settled-framing, NOT the
  reference* (the reference only mandates "account for survival wind speed + operational state").
- **Coupling = footprint:** narrow path → areal (tornado); broad swath → site-conditioned (strong wind, via the
  ASCE RP surface = pre-integrated); regional field → field-intensity (hurricane, deferred; Holland, x₀≈160 mph).
- **Data:** SPC SVRGIS (~70k tornado tracks 1950+; wind reports 1955+) · NOAA Storm Events · ASCE 7-22 maps
  (3-s gust at 33 ft Exp C; RC I 300-yr/II 700-yr/III 1,700-yr/IV 3,000-yr; Appendix F to ~10⁴–10⁶-yr) · Ch 32
  tornado maps (~EF2 cap) · USWTDB. **No public stochastic catalog** (Verisk/RMS proprietary). SPC is
  **population-biased** → bias-correct before fitting.

## Prior-art facts mined from `hazard_analysis/` (the old "value-farm" repo)

- `mag_sim`: per-hazard `HAZARD_CONFIG` (threshold μ) + `HAZARD_LIMITS` (bound L) — strong wind μ=25.92 m/s,
  L=113 m/s; bounded-GPD analytic solve `ξ=(μ_mean−μ)/(μ_mean−L)`, `σ=−ξ(L−μ)` on `[μ,L]`; anchored-logistic
  damage curves. **Reuse the solve; reject** their back-solving μ_mean from an NRI EAL target.
- `strong-wind-var-worked-example.md`: the old repo's **own** proof that Method 0 (expected-loss shortcut) vs
  Method 3 (compound-Poisson MC) differ ~**12×** at VaR₉₉ ($9M vs $109M) for strong wind, plus a ~175×
  PML/VaR invariant breach. This is the cardinal error our rebuild exists to escape (`DD-WN-13`).
- `config/subsystems/wind_config_default.csv`: turbine subsystem split (rotor/blades ~0.26, nacelle/drivetrain
  ~0.21, tower ~0.16, foundation ~0.12, substation ~0.09, electrical ~0.09, civil ~0.07) → the M3 blend.

## Key insights (for the next builder)

1. **The hazard-definition layer is real and load-bearing.** It only became *visible* with wind because hail
   (MESH) and wildfire (FSim) inherited the event definition from their data product. Classify every new peril
   by *how its data arrives* (learning-09) before reaching for catalog machinery.
2. **The ASCE RP surface is wind's FSim.** It hands you gust-by-return-period at the site — a pre-integrated EVT
   return-level curve. So strong-wind M1 is **profile-assembly**, not extraction; and strong-wind M2 reuses
   wildfire's site-conditioned machinery. Fastest path to a real number.
3. **Wind sub-perils span coupling buckets** — the cleanest demonstration yet of "standard interface, not
   standard physics": tornado=areal, strong wind=site-conditioned, hurricane=field-intensity, one shared engine.
4. **Two thresholds, far apart.** The meteorological event threshold (58 mph) counts events; the IEC survival
   speed (~52–70 m/s) is where damage starts. The curve is **anchored** so DR(58 mph)≈0 — most "severe wind"
   barely scratches a turbine.
5. **Adversarial review catches what a careful drafter misses** — here, a systematic stale cross-reference. Cheap
   insurance for docs a domain-newcomer will actually click through.
