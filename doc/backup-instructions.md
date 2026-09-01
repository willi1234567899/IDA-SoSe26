# Backup instructions — Group 38

How to keep and restore the project after ISIS submission.

## What to back up

| Item | Location | In git? |
|------|----------|---------|
| Submission zip | `IDA-project/SoSe26_Case_Study_Group_38.zip` | No |
| Source code + screenshots | `IDA-SoSe26/` repo | Yes (except CSV) |
| Final dataset | `IDA-SoSe26/Data/SoSe26_Case_Study_finalData_Group_38.csv` | **No** — copy separately |
| Defect cache | `IDA-SoSe26/local/defective_vehicles_after_reg.csv` | No (~38 MB) |
| tubCloud course data | `IDA SoSe26 - Data/` | No |
| ISIS upload confirmation | Screenshot / note | — |

**Git remote:** `https://github.com/willi1234567899/IDA-SoSe26.git`

## Recommended backup set (minimum)

1. `SoSe26_Case_Study_Group_38.zip` (ISIS submission copy)
2. `SoSe26_Case_Study_finalData_Group_38.csv` (Dropbox/Drive)
3. Push latest `IDA-SoSe26` to GitHub

## Restore the app only

```bash
unzip SoSe26_Case_Study_Group_38.zip
cd SoSe26_Case_Study_Group_38
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run SoSe26_Case_Study_App_Group_38.py --server.fileWatcherType none
```

## Restore full notebook reproduction

1. Clone `IDA-SoSe26` or unzip submission.
2. Copy final CSV into `Data/`.
3. Link or copy tubCloud folders into `Data/`:
   `Einzelteil`, `Fahrzeug`, `Geodaten`, `Komponente`, `Logistikverzug`, `Zulassungen`
4. Optional: copy `local/defective_vehicles_after_reg.csv` to skip long defect step.
5. `pip install -r requirements.txt` → Run All notebooks.

## Rebuild submission zip

```bash
cd IDA-SoSe26
bash scripts/build_submission_zip.sh
```
