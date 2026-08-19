# App ↔ Case Study traceability (Group 38)

The Streamlit app presents the same result as
`SoSe26_Case_Study_Group_38.ipynb` §4, using only
`Data/SoSe26_Case_Study_finalData_Group_38.csv` from notebook §3.

## Mapping

| Case Study notebook | App tab | What must match |
|---------------------|---------|-----------------|
| §3 Creation of the final dataset | **Full data** | Same CSV, all rows |
| §4 Overall ranking / winners K1–K7 | **Recommendation** | Highest `n_registrations` per category; ties as joint winners |
| §4 Yearly line charts | **Yearly trends** | Same yearly counts by `component_type` |
| §4 Recommendation + screenshots | **Explore** + `Additional_files/` | OEM/year/category filters; screenshots in notebook §4 |

## Shared decision rule

```text
for category in K1..K7:
    winner[category] = argmax sum(n_registrations) over component_type
```

Feasible mix: one body from K4–K7 (not several), plus K1/K2/K3 winners.
