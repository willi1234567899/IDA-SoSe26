# Architecture (rough)

Two notebooks + one app, as required.

```text
original data (local / empty on submit)
        │
        ▼
General Tasks notebook  ──► answers + plots (own analyses)
        │
Case Study notebook
  1) import + EDA
  2) clean / tidy / features
  3) one final dataset
  4) analysis + recommendation (K1–K7)
        │
        ▼
final CSV  ──►  Web App (Dash and/or Streamlit)
        │
        ▼
results + screenshots in notebook / Additional_files
```

## Case study flow (from the PDF)

1. **Setup & import** – Jupyter notebook with group number + names; task interpretation; select/import relevant files; EDA  
2. **Data preparation** – clean (course methods), tidy data, features, **one final dataset**  
3. **App** – runs from submission folder on another PC; uses **only** that final dataset  
4. **App content** – stakeholder-useful views, interactivity (filters/maps/charts), table page with all final data  
5. **Document results** – step-by-step story, discuss charts, PEP 8, app screenshots in results  

## App design constraints

- main colour: **light blue**
- logo: own or Department of Quality Science
- font: **Source Sans Pro**
- target group: management / stakeholders for the case

## Important data rule

A vehicle is defective if an installed single part, component, or the vehicle itself is marked defective (same idea for components with defective parts). Production + defect info lives in the group production data; KBA registrations + geodata are also available.

## Reproducibility

- relative paths only  
- do **not** modify original data files  
- analysis must rerun when originals are dropped into the documented `Data` folder  
- suppress noisy warnings; no dead code  
