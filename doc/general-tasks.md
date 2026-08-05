# General Tasks (25 points)

Separate notebook + HTML export. Explain steps; support with visualizations. Run all cells before saving. Must run on current Anaconda.

## 1. Logistics delay for component K7 (8 points)

Use `Komponente_K7.csv` (Produktionsdatum) and `Logistikverzug_K7.csv` (Wareneingang).  
Assume goods are issued **one day after** production date. Build a “Logistics delay” dataset.

| Part | Points | Ask |
|------|--------|-----|
| a | 2 | How is the delay distributed? Justify with goodness-of-fit tests |
| b | 2 | Mean delay in **working days** (exclude weekends); interpret |
| c | 2 | Histogram + density with **plotly**; explain bin size |
| d | 2 | Describe a **decision tree** process to classify K7 defective (`Fehlerhaft`); use viz |

## 2. Separate files / DB structure (2 points)

Why store data in separate files ( ≥4 benefits)? What is that typical DB structure called?

## 3. Parts T16 in Adelshofen (3 points)

How many parts **T16** ended up in vehicles registered in **Adelshofen**?

## 4. Registration table attributes (2 points)

Data types of attributes in `Zulassungen_aller_Fahrzeuge` — table in Markdown + short description of the types.

## 5. Linear model for mileage (5 points)

From `Fahrzeuge_OEM1_Typ11_Fehleranalyse`: linear model mileage vs suitable variables; recommendations for OEM1.

## 6. Hit-and-run (5 points)

Date **11.08.2010**. Find where the vehicle with body part **`K5-112-1122-79`** was registered.
