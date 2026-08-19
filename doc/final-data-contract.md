# Final dataset contract (App ↔ Case Study)

**File (required):** `Data/SoSe26_Case_Study_finalData_Group_38.csv`  
**Consumer:** `SoSe26_Case_Study_App_Group_38.py` (Streamlit) — loads **only** this file.  
**Producer:** Case Study notebook (Rolle B) — one tidy table after cleaning/merges.

One row = one registered vehicle (or one registration event) with its installed K1–K7 components.

## Required columns

| Column | Type | Meaning |
|--------|------|---------|
| `year` | int | Registration year (Zulassungsjahr) |
| `K1` | str | Component ID/type in category K1 |
| `K2` | str | Component ID/type in category K2 |
| `K3` | str | Component ID/type in category K3 |
| `K4` | str | Component ID/type in category K4 |
| `K5` | str | Component ID/type in category K5 |
| `K6` | str | Component ID/type in category K6 |
| `K7` | str | Component ID/type in category K7 |

Each row counts as **1 registration**. The app aggregates popularity by counting rows (no separate `registrations` column required). If Rolle B prefers a pre-aggregated table, add optional `registrations` (int ≥ 1); the app will use it as a weight when present.

## Optional columns (used when present)

| Column | Type | Meaning |
|--------|------|---------|
| `registrations` | int | Row weight (default 1) |
| `ort` | str | Registration place (filter / explore) |
| `plz` | str/int | Postal code |
| `lat` | float | Latitude (map if both lat/lon exist) |
| `lon` | float | Longitude |

## App behaviour (shared understanding)

- **Most popular vehicle** = for each of K1–K7, pick the component value with the highest registration weight, then present that K1–K7 combination as the recommendation.
- **Yearly trends** = popularity (counts) of components over `year`.
- Encoding: UTF-8; separator `,`.

## Filling the app

Place `Data/SoSe26_Case_Study_finalData_Group_38.csv` (from notebook §3).  
The app loads only that file; all tabs fill from it. Do **not** commit CSVs (`.gitignore`).
