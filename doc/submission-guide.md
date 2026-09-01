# Submission guide — Group 38

Where everything goes in the ISIS zip and what examiners need.

## Zip root

`SoSe26_Case_Study_Group_38/`

## Required files

| Path | Role |
|------|------|
| `SoSe26_General_Tasks_Group_38.ipynb` / `.html` | General tasks (25 pts) |
| `SoSe26_Case_Study_Group_38.ipynb` / `.html` | Analysis + Document results |
| `SoSe26_Case_Study_App_Group_38.py` | Streamlit dashboard |
| `Data/SoSe26_Case_Study_finalData_Group_38.csv` | **Only** file in `Data/` |
| `defect_pipeline.py` | Notebook: defect vehicle IDs |
| `rebuild_final_with_defects.py` | Notebook: rebuild final CSV |
| `requirements.txt` | Dependencies |
| `.streamlit/config.toml` | Theme |

## `Additional_files/`

Per Submission Requirements: *“Screenshots of app and other files that do not
fit other cases.”*

| File | Purpose |
|------|---------|
| `01`–`05_*.png` | App screenshots (embedded in Case Study notebook) |
| `Dashboard_User_Guide.md` | How to use the dashboard, KPIs, features |

**Not in zip:** `doc/` (local planning notes only).

## `www/`

Static assets for the app: `style.css`, `fonts/`, `img/` (logo).

## What examiners run

1. Place tubCloud data under `Data/` (folders they provide).
2. Open HTML notebooks or Run All `.ipynb` to reproduce analysis.
3. Run the app with **only** the final CSV (no raw data needed for the app).

## Build zip

```bash
bash scripts/build_submission_zip.sh
```

Output: `../SoSe26_Case_Study_Group_38.zip`
