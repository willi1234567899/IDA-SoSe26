"""
Rebuild SoSe26_Case_Study_finalData_Group_38.csv with dual registration counts:
  n_registrations       = all registered vehicles
  n_registrations_clean = excluding vehicles defective under the course rule
                          (defects after registration only)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from defect_pipeline import (BOM_FILES, DATA_DIR, DEFECT_IDS_PATH,
    build_defective_vehicle_ids, load_defective_vehicle_ids)

FINAL_CSV = DATA_DIR / "SoSe26_Case_Study_finalData_Group_38.csv"

TYPE_LABEL = {
    "K1BE1": "Petrol engine (OEM1)",
    "K1BE2": "Petrol engine (OEM2)",
    "K1DI1": "Diesel engine (OEM1)",
    "K1DI2": "Diesel engine (OEM2)",
    "K2ST1": "Fabric seats (OEM1)",
    "K2ST2": "Fabric seats (OEM2)",
    "K2LE1": "Leather seats (OEM1)",
    "K2LE2": "Leather seats (OEM2)",
    "K3SG1": "Manual gearbox (OEM1)",
    "K3SG2": "Manual gearbox (OEM2)",
    "K3AG1": "Automatic gearbox (OEM1)",
    "K3AG2": "Automatic gearbox (OEM2)",
    "K4": "Body (OEM1 Typ11)",
    "K5": "Body (OEM1 Typ12)",
    "K6": "Body (OEM2 Typ21)",
    "K7": "Body (OEM2 Typ22)"
}

BOM_META = [("Fahrzeug/Bestandteile_Fahrzeuge_OEM1_Typ11.csv", "OEM1", "Typ11"),
    ("Fahrzeug/Bestandteile_Fahrzeuge_OEM1_Typ12.csv", "OEM1", "Typ12"),
    ("Fahrzeug/Bestandteile_Fahrzeuge_OEM2_Typ21.csv", "OEM2", "Typ21"),
    ("Fahrzeug/Bestandteile_Fahrzeuge_OEM2_Typ22.csv", "OEM2", "Typ22")]

SLOTS = [("ID_Motor", "K1"),("ID_Sitze", "K2"),("ID_Schaltung", "K3"),("ID_Karosserie", "body")]

def parse_component_id(series: pd.Series) -> pd.DataFrame:
    parts = series.astype(str).str.split("-", n=3, expand=True)
    out = pd.DataFrame(
        {
            "component_type": parts[0],
            "manufacturer": parts[1],
            "plant": parts[2],
        }
    )
    out["series"] = out["component_type"] + "-" + out["manufacturer"] + "-" + out["plant"]
    return out

def rebuild_final_csv(defective: set[str] | None = None) -> pd.DataFrame:
    if defective is None:
        if DEFECT_IDS_PATH.exists():
            defective = load_defective_vehicle_ids()
        else:
            defective = build_defective_vehicle_ids(save=True)
    print(f"Using {len(defective):,} defective vehicle IDs", flush=True)

    zul_path = DATA_DIR / "Zulassungen" / "Zulassungen_alle_Fahrzeuge.csv"
    with open(zul_path, "rb") as f:
        head = f.read(200).decode("utf-8", errors="replace")
    sep = ";" if head.count(";") > head.count(",") else ","
    zul = pd.read_csv(zul_path, sep=sep, usecols=["IDNummer", "Zulassung"], dtype={"IDNummer": str})
    zul["year"] = pd.to_datetime(zul["Zulassung"], errors="coerce").dt.year
    zul = zul.dropna(subset=["year"])
    zul["year"] = zul["year"].astype(int)
    zul_slim = zul[["IDNummer", "year"]]

    agg_parts = []
    for rel, oem, vtype in BOM_META:
        bom_one = pd.read_csv(
            DATA_DIR / rel,
            sep=";",
            usecols=["ID_Fahrzeug", "ID_Karosserie", "ID_Schaltung", "ID_Sitze", "ID_Motor"],
            dtype=str,
        )
        m = bom_one.merge(zul_slim, left_on="ID_Fahrzeug", right_on="IDNummer", how="inner")
        m["is_clean"] = ~m["ID_Fahrzeug"].isin(defective)
        for col, default_cat in SLOTS:
            parsed = parse_component_id(m[col])
            out = pd.DataFrame(
                {
                    "year": m["year"].values,
                    "oem": oem,
                    "vehicle_type": vtype,
                    "component_type": parsed["component_type"].values,
                    "manufacturer": parsed["manufacturer"].values,
                    "plant": parsed["plant"].values,
                    "series": parsed["series"].values,
                    "is_clean": m["is_clean"].values,
                }
            )
            out["category"] = out["component_type"] if default_cat == "body" else default_cat
            g = (
                out.groupby(
                    [
                        "year",
                        "oem",
                        "vehicle_type",
                        "category",
                        "component_type",
                        "manufacturer",
                        "plant",
                        "series",
                    ],
                    as_index=False,
                )
                .agg(
                    n_registrations=("series", "size"),
                    n_registrations_clean=("is_clean", "sum"),
                )
            )
            agg_parts.append(g)
        print(f"{oem} {vtype}: {len(m):,} vehicles", flush=True)

    final = pd.concat(agg_parts, ignore_index=True)
    final = final.groupby(
        [
            "year",
            "oem",
            "vehicle_type",
            "category",
            "component_type",
            "manufacturer",
            "plant",
            "series"
        ],
        as_index=False,).agg(
        n_registrations=("n_registrations", "sum"),
        n_registrations_clean=("n_registrations_clean", "sum"))
    final["n_registrations_clean"] = final["n_registrations_clean"].astype(int)
    final["label"] = final["component_type"].map(TYPE_LABEL)
    unknown = final[final["label"].isna()]
    if not unknown.empty:
        raise ValueError(f"Unlabelled types: {unknown['component_type'].unique()}")

    final.to_csv(FINAL_CSV, index=False)
    print(f"Wrote {FINAL_CSV} ({len(final)} rows)", flush=True)
    return final

if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--rebuild-defects", action="store_true", help="recompute defective vehicle IDs")
    args = p.parse_args()
    if args.rebuild_defects or not DEFECT_IDS_PATH.exists():
        build_defective_vehicle_ids(save=True)
    rebuild_final_csv()