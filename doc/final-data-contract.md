# Final dataset contract (App ↔ Case Study)

**File:** `Data/SoSe26_Case_Study_finalData_Group_38.csv`  
**Producer:** Case Study notebook §3  
**Consumer:** `SoSe26_Case_Study_App_Group_38.py` (only this file)

One row = yearly registration count for one OEM / vehicle type / category / component type.

## Required columns

| Column | Type | Meaning |
|--------|------|---------|
| `year` | int | Registration year |
| `oem` | str | OEM |
| `vehicle_type` | str | Vehicle type |
| `category` | str | `K1` … `K7` |
| `component_type` | str | Type code (e.g. `K1BE1`, `K2ST1`) |
| `n_registrations` | int | Number of registered vehicles |
| `label` | str | Human-readable type description |

Encoding: UTF-8; separator `,`.

## Decision rule (notebook §4 = app)

Overall winner in a category = `component_type` with the highest sum of `n_registrations` across all years. Ties are joint winners. Yearly charts use the same counts by `year`.

K4–K7 are mutually exclusive body types; they are not combined on one vehicle.

Place the CSV at the path above. Do **not** commit CSVs (`.gitignore`).
