# Folder structure

Aligned with **Submission Requirements**. **Group 38**.

```text
SoSe26_Case_Study_Group_38/
├── doc/                                      # planning only (optional in zip)
├── Additional_files/                         # app screenshots, extras
├── Data/                                     # originals empty on submit; final CSV here
│   └── SoSe26_Case_Study_finalData_Group_38.csv   # later
├── www/                                      # images, CSS, JS, fonts for the app
├── SoSe26_General_Tasks_Group_38.ipynb
├── SoSe26_General_Tasks_Group_38.html
├── SoSe26_Case_Study_Group_38.ipynb
├── SoSe26_Case_Study_Group_38.html
└── SoSe26_Case_Study_App_Group_38.py
```

Working copy folder is currently named `IDA-SoSe26` (rename to `SoSe26_Case_Study_Group_38` when zipping for submission). Placeholder notebooks, HTML exports, app, and empty final CSV are in place; content comes later.

Notes:

- On Windows the folder may show as `data` or `Data` — submission name is **`Data`**.
- Locally: unpack tubCloud originals into `Data/` (e.g. Einzelteil, Komponente, …). On submit: originals out, keep that area empty; only ship the final CSV (+ code/www/etc.).

## Case study notebook TOC (required flavour)

- Importing the data  
- Data preparation  
- Creation of the final dataset  
- Evaluation and Result  

## Pre-submission checklist

Deadline: **1 September 2026, 23:59** (ISIS). One zip per group.

### Notebooks & HTML

- [x] Participants listed (Case Study + General Tasks)
- [x] General Tasks `.ipynb` filled (tasks 1–6)
- [x] Re-export **General Tasks** `.html` (synced with participants; prefer one more export after a final **Run All**)
- [x] Case Study `.ipynb` has analysis + recommendation + Document results
- [x] Case Study Document results discusses findings and links app screenshots
- [x] Case Study `.html` replaced (no longer a placeholder; Plotly widgets may need a full **Run All** + re-export for interactive charts)

### App

- [x] Streamlit app runs on final CSV only (`SoSe26_Case_Study_App_Group_38.py`)
- [x] Design: light blue, Source Sans Pro, logo, filters, full-data table
- [x] Live smoke check: app loads on `http://127.0.0.1:8501` + CSV/syntax OK
- [ ] Optional: clean Anaconda/venv install from `requirements.txt` on a second machine
- [x] App screenshots in `Additional_files/` (`01`–`05`)
- [x] Screenshots referenced/embedded in Case Study Document results

### Data & zip packing

- [x] Final CSV present: `Data/SoSe26_Case_Study_finalData_Group_38.csv`
- [ ] Before zipping: remove original tubCloud data from `Data/` (keep folder empty except final CSV)
- [ ] Remove local-only extras from zip (`defective_vehicles_after_reg.csv`, symlinks to tubCloud, `__pycache__/`, `.DS_Store`, `.git/` if not wanted)
- [ ] Decide whether helper scripts (`defect_pipeline.py`, `rebuild_final_with_defects.py`) stay in the zip or stay local-only
- [ ] Rename folder to `SoSe26_Case_Study_Group_38/` for the archive
- [ ] Confirm relative paths only; zip opens and notebooks/app run on another PC
- [ ] Upload one zip to ISIS before the deadline (no success confirmation expected)

### Quick zip contents check

```text
SoSe26_Case_Study_Group_38/
├── Additional_files/          # screenshots
├── Data/
│   └── SoSe26_Case_Study_finalData_Group_38.csv
├── www/
├── SoSe26_General_Tasks_Group_38.ipynb
├── SoSe26_General_Tasks_Group_38.html
├── SoSe26_Case_Study_Group_38.ipynb
├── SoSe26_Case_Study_Group_38.html
├── SoSe26_Case_Study_App_Group_38.py
└── requirements.txt
```
