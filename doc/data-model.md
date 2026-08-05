# Data (rough)

Dataset categories (tubCloud / case study PDF):

| Folder / topic | German | Role |
|----------------|--------|------|
| Single parts | Einzelteil | parts + production / defect info |
| Components | Komponente | components K… + parts lists |
| Vehicles | Fahrzeug | vehicles + parts lists |
| Registrations | Zulassungen | KBA registrations |
| Geodata | Geodaten | geo for maps etc. |
| Logistics delay | Logistikverzug | used especially in General Tasks (K7) |

## ID pattern (example from PDF)

`1-201-2011-3` → designation / manufacturer / plant / sequence  
(e.g. component series from manufacturer `201`, plant `2011`)

Parts lists for components/vehicles follow naming like `Components_Name_Abbreviation`.

## Defect logic

Vehicle defective if **any** installed single part, component, or the vehicle is marked defective. Components inherit defects from defective parts the same way.

## Case study focus

Build **one final dataset** that lets us recommend popular **K1–K7** components from **registration** counts (overall + by year). App reads **only** that final CSV.

## General Tasks – named files (hints)

- `Komponente_K7.csv` + `Logistikverzug_K7.csv` → logistics delay distribution  
- parts **T16** in vehicles registered in **Adelshofen**  
- `Zulassungen_aller_Fahrzeuge` → attribute data types  
- `Fahrzeuge_OEM1_Typ11_Fehleranalyse` → linear model for mileage  
- body part `K5-112-1122-79` → hit-and-run / registration place (11.08.2010)

Inspect table structure before analysing. Choose what you need from the group database — don’t blindly load everything (size + RAM).
