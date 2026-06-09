# data/

Local working data for the pipeline — fetched source datasets, intermediate artifacts, and combined
outputs. Sits alongside `docs/`. **Gitignored by content** (parquet / grib / netcdf / …) — the folder
structure is tracked, the bulk data is not.

| Path | Holds |
|------|-------|
| `hail/` | Hail **M0** datasets per source — `hayhurst_hail_m0_noaa_50mi.parquet` (NOAA point events) now, MRMS footprints next — and (later) the reconciled set produced at the **M0→M1 catalog** step. |

> **Nothing here is a source of truth.** It's all re-derivable from the public APIs (Hydronos) / open data
> (AWS MRMS). Delete and re-run the notebooks to regenerate.
