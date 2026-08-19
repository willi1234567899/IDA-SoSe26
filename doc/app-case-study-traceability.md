# App ↔ Case Study traceability (Group 38)

Goal: the Streamlit app presents the **same result story** as
`SoSe26_Case_Study_Group_38.ipynb` §4 *Evaluation and Result*, using only
`Data/SoSe26_Case_Study_finalData_Group_38.csv` from notebook §3.

## Mapping

| Case Study notebook | App tab | What must match |
|---------------------|---------|-----------------|
| §3 Creation of the final dataset | **Final dataset** | Same CSV, all columns/rows visible |
| §4 Recommendation (most popular vehicle) | **4.1 Recommendation** | Same rule: per K1–K7 max registrations → recommended config |
| §4 Yearly trends | **4.2 Yearly trends** | Same yearly counts / leaders by category |
| §4 Discussion + app screenshots | **4.3 Explore** + `Additional_files/` | Filters/map for stakeholder discussion; screenshots referenced in notebook |

## Shared decision rule

```text
for category in K1..K7:
    leading_component[category] = argmax_registrations(component)
recommended_vehicle = (leading_component[K1], …, leading_component[K7])
```

Optional weight column: `registrations` (default 1 per row).  
Documented in [`final-data-contract.md`](final-data-contract.md).

## Checklist for the group

1. Notebook §3 exports the CSV the app loads (relative path `Data/...`).
2. Notebook §4 computes the same K1–K7 leaders (numbers must match app tab 4.1).
3. Notebook §4 discusses yearly shifts using the same logic as app tab 4.2.
4. Screenshots of 4.1–4.3 + Final dataset go into `Additional_files/` and into notebook §4.
5. App runs with: `streamlit run SoSe26_Case_Study_App_Group_38.py`
