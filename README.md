# SoSe26_Case_Study_Group_38

IDA final project – Group **38**.

**Participants:** Mark Prymak, Pascal Diekmeier, Smilla Elisa Eichhorn, Willi Leonard Horn

Planning notes: [`doc/`](doc/README.md)  
Submission layout / naming: [`doc/folder-structure.md`](doc/folder-structure.md)

**Deadline:** 1 September 2026, 23:59

**Before upload:** see the [pre-submission checklist](doc/folder-structure.md#pre-submission-checklist).

Build the ISIS zip:

```bash
bash scripts/build_submission_zip.sh
```

Intermediate defect cache lives in `local/` (not submitted). tubCloud symlinks in `Data/` are for local development only.

## Run the case-study app

From this folder, after the notebook has written `Data/SoSe26_Case_Study_finalData_Group_38.csv`:

```text
streamlit run SoSe26_Case_Study_App_Group_38.py
```

The app reads only that CSV. Original tables stay under `Data/` (Fahrzeug, Zulassungen, …).
