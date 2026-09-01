"""
Build vehicles defective under the course rule (after registration only).

A vehicle is defective if the vehicle, an installed component, or an installed
single part is marked defective. Components inherit defective parts.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

DATA_DIR = Path("Data")
LOCAL_DIR = Path("local")  # intermediate outputs — not submitted in Data/
DEFECT_IDS_PATH = LOCAL_DIR / "defective_vehicles_after_reg.csv"

BOM_FILES = [
    "Fahrzeug/Bestandteile_Fahrzeuge_OEM1_Typ11.csv",
    "Fahrzeug/Bestandteile_Fahrzeuge_OEM1_Typ12.csv",
    "Fahrzeug/Bestandteile_Fahrzeuge_OEM2_Typ21.csv",
    "Fahrzeug/Bestandteile_Fahrzeuge_OEM2_Typ22.csv",
]

VEHICLE_FILES = [
    "Fahrzeug/Fahrzeuge_OEM1_Typ11.csv",
    "Fahrzeug/Fahrzeuge_OEM1_Typ12.csv",
    "Fahrzeug/Fahrzeuge_OEM2_Typ21.csv",
    "Fahrzeug/Fahrzeuge_OEM2_Typ22.csv",
]

COMPONENT_FILES = [
    ("Komponente/Komponente_K1BE1.csv", "ID_Motor"),
    ("Komponente/Komponente_K1BE2.csv", "ID_Motor"),
    ("Komponente/Komponente_K1DI1.csv", "ID_Motor"),
    ("Komponente/Komponente_K1DI2.txt", "ID_Motor"),
    ("Komponente/Komponente_K2LE1.txt", "ID_Sitze"),
    ("Komponente/Komponente_K2LE2.txt", "ID_Sitze"),
    ("Komponente/Komponente_K2ST1.txt", "ID_Sitze"),
    ("Komponente/Komponente_K2ST2.csv", "ID_Sitze"),
    ("Komponente/Komponente_K3AG1.csv", "ID_Schaltung"),
    ("Komponente/Komponente_K3AG2.txt", "ID_Schaltung"),
    ("Komponente/Komponente_K3SG1.csv", "ID_Schaltung"),
    ("Komponente/Komponente_K3SG2.csv", "ID_Schaltung"),
    ("Komponente/Komponente_K4.csv", "ID_Karosserie"),
    ("Komponente/Komponente_K5.csv", "ID_Karosserie"),
    ("Komponente/Komponente_K6.csv", "ID_Karosserie"),
    ("Komponente/Komponente_K7.txt", "ID_Karosserie"),
]

BESTANDTEILE_KOMPONENTE = [
    ("Komponente/Bestandteile_Komponente_K1BE1.csv", "ID_K1BE1"),
    ("Komponente/Bestandteile_Komponente_K1BE2.csv", "ID_K1BE2"),
    ("Komponente/Bestandteile_Komponente_K1DI1.csv", "ID_K1DI1"),
    ("Komponente/Bestandteile_Komponente_K1DI2.csv", "ID_K1DI2"),
    ("Komponente/Bestandteile_Komponente_K2LE1.csv", "ID_K2LE1"),
    ("Komponente/Bestandteile_Komponente_K2LE2.csv", "ID_K2LE2"),
    ("Komponente/Bestandteile_Komponente_K2ST1.csv", "ID_K2ST1"),
    ("Komponente/Bestandteile_Komponente_K2ST2.csv", "ID_K2ST2"),
    ("Komponente/Bestandteile_Komponente_K3AG1.csv", "ID_K3AG1"),
    ("Komponente/Bestandteile_Komponente_K3AG2.csv", "ID_K3AG2"),
    ("Komponente/Bestandteile_Komponente_K3SG1.csv", "ID_K3SG1"),
    ("Komponente/Bestandteile_Komponente_K3SG2.csv", "ID_K3SG2"),
    ("Komponente/Bestandteile_Komponente_K4.csv", "ID_K4"),
    ("Komponente/Bestandteile_Komponente_K5.csv", "ID_K5"),
    ("Komponente/Bestandteile_Komponente_K6.csv", "ID_K6"),
    ("Komponente/Bestandteile_Komponente_K7.csv", "ID_K7"),
]


def _sep_from_head(head: str) -> str:
    if " | | " in head:
        return " | | "
    if "II" in head[:300] and head.count("II") >= 5:
        return "II"
    # double-space delimited fields (Einzelteil_T02/T24/T31/T36, …)
    if '  "ID_' in head or head.startswith('"X1"  "') or 'X1"  "ID_' in head:
        return "  "
    if head.count("|") >= 4 and head.count(",") <= 1 and " | | " not in head:
        return "|"
    if head.count("\t") >= 4 and "\\" in head[:200]:
        # tab used as row sep with backslash fields (handled separately)
        return '\\"'
    if head.count("\t") >= 4:
        return "\t"
    if head.count('\\"') >= 3 or (head.count("\\") >= 8 and "," not in head[:100]):
        return '\\"'
    if head.count(";") >= head.count(","):
        return ";"
    return ","


def _normalize_text(text: str, field_sep: str) -> str:
    # unify uncommon row separators (BEL \x07, BS \x08, VT, FF, CR)
    for rs in ("\x0b", "\x0c", "\r", "\x07", "\x08"):
        text = text.replace(rs, "\n")

    # some exports use tab as the only row separator (no newlines)
    if "\n" not in text and "\t" in text:
        text = text.replace("\t", "\n")

    if field_sep == " | | ":
        text = text.replace(" | | ", ",")
        if "\t" in text:
            text = text.replace("\t", "\n")
        # records glued with a space before the next row index: ...NA "2",661,...
        text = re.sub(r' "(\d+)",', r'\n"\1",', text)
        text = re.sub(r'""(\d+)",', r'"\n"\1",', text)
    elif field_sep == "  ":
        # double-space fields; tabs often separate rows
        if "\t" in text:
            text = text.replace("\t", "\n")
        text = text.replace("  ", ",")
        text = re.sub(r' "(\d+)",', r'\n"\1",', text)
    elif field_sep == "\t":
        text = re.sub(r'""(\d+)"\t', r'"\n"\1"\t', text)
        text = re.sub(r'([^\t\n"])"(\d+)"\t', r'\1\n"\2"\t', text)
    elif field_sep == "|":
        text = re.sub(r'""(\d+)"\|', r'"\n"\1"|', text)
        text = re.sub(r'([^\|\n"])"(\d+)"\|', r'\1\n"\2"|', text)
    elif field_sep == "II":
        text = text.replace("II", ",")
        if "\n" not in text:
            text = re.sub(r' "(\d+)",', r'\n"\1",', text)
            text = re.sub(r'""(\d+)",', r'"\n"\1",', text)
            text = re.sub(r'NA"(\d+)",', r'NA\n"\1",', text)
    elif field_sep == '\\"':
        # field separator is a single backslash between quoted/unquoted fields
        if "\t" in text:
            text = text.replace("\t", "\n")
        text = text.replace("\\", ",")
        # rows glued with no newline; next row starts as "X1",rownum,
        text = re.sub(r'""(\d+)",', r'"\n"\1",', text)
        text = re.sub(r'([^,\n])("\d+",\d+,)', r'\1\n\2', text)
    elif field_sep == "|":
        pass  # already single-char
    elif field_sep == "\t":
        pass
    else:
        pass

    return text


def _stream_normalize_to_temp(path: Path, field_sep: str) -> Path:
    """Convert exotic separators to a temp CSV without holding the whole file in RAM."""
    import tempfile

    tmp = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".csv", delete=False
    )
    tmp_path = Path(tmp.name)
    buf = ""
    bytes_in = 0
    with open(path, "r", encoding="utf-8", errors="replace") as src, tmp:
        while True:
            chunk = src.read(4_000_000)
            if not chunk:
                break
            bytes_in += len(chunk)
            buf += chunk
            for rs in ("\x0b", "\x0c", "\r", "\x07", "\x08"):
                buf = buf.replace(rs, "\n")
            if field_sep == " | | ":
                buf = buf.replace(" | | ", ",")
                # some pipepipe files still use tab as the row separator (e.g. T16)
                if "\t" in buf:
                    buf = buf.replace("\t", "\n")
                buf = re.sub(r' "(\d+)",', r'\n"\1",', buf)
                buf = re.sub(r'""(\d+)",', r'"\n"\1",', buf)
            elif field_sep == "  ":
                if "\t" in buf:
                    buf = buf.replace("\t", "\n")
                buf = buf.replace("  ", ",")
                buf = re.sub(r' "(\d+)",', r'\n"\1",', buf)
            elif field_sep == "\t":
                # tabs are fields; rows glued without newlines.
                # forms seen: ...1970""2"\t  and  ...NA"2"\t
                buf = re.sub(r'""(\d+)"\t', r'"\n"\1"\t', buf)
                buf = re.sub(r'([^\t\n"])"(\d+)"\t', r'\1\n"\2"\t', buf)
            elif field_sep == "|":
                # pipes are fields; glue rows if needed
                buf = re.sub(r'""(\d+)"\|', r'"\n"\1"|', buf)
                buf = re.sub(r'([^\|\n"])"(\d+)"\|', r'\1\n"\2"|', buf)
                if "\r" in buf:
                    buf = buf.replace("\r", "\n")
            elif field_sep == "II":
                buf = buf.replace("II", ",")
                buf = re.sub(r' "(\d+)",', r'\n"\1",', buf)
                buf = re.sub(r'""(\d+)",', r'"\n"\1",', buf)
                buf = re.sub(r'NA"(\d+)",', r'NA\n"\1",', buf)
            elif field_sep == '\\"':
                if "\t" in buf:
                    buf = buf.replace("\t", "\n")
                buf = buf.replace("\\", ",")
                # rows glued; next row starts as "X1",rownum, (after header ""1",)
                buf = re.sub(r'""(\d+)",', r'"\n"\1",', buf)
                buf = re.sub(r'([^,\n])("\d+",\d+,)', r'\1\n\2', buf)
            elif "\n" not in buf and "\t" in buf:
                buf = buf.replace("\t", "\n")

            if "\n" in buf:
                ready, buf = buf.rsplit("\n", 1)
                # backslash exports often have an unnamed R index after X1;
                # pad the header so it matches the 16 data fields.
                if field_sep == '\\"' and not getattr(tmp, "_hdr_padded", False):
                    if ready.startswith('"X1",') and '","ID_' in ready[:80]:
                        ready = ready.replace('"X1",', '"X1","rn",', 1)
                        tmp._hdr_padded = True
                tmp.write(ready)
                tmp.write("\n")
            # Never flush mid-row (that created mega-lines). If still huge, force a
            # last-resort split on quoted row index + int + quoted id.
            if len(buf) > 2_000_000:
                buf = re.sub(
                    r'([^,\n])"(\d+)",(\d+),"',
                    r'\1\n"\2",\3,"',
                    buf,
                )
                if "\n" in buf:
                    ready, buf = buf.rsplit("\n", 1)
                    tmp.write(ready)
                    tmp.write("\n")
            if bytes_in % 80_000_000 < 4_000_000:
                print(f"    … streamed {bytes_in / 1e6:.0f} MB", flush=True)
        if buf:
            tmp.write(buf)
            if not buf.endswith("\n"):
                tmp.write("\n")
    print(f"    … normalize done ({bytes_in / 1e6:.0f} MB)", flush=True)
    return tmp_path


def _read_raw(path: Path) -> pd.DataFrame:
    """Read mixed-delimiter production tables into a DataFrame."""
    path = Path(path)
    with open(path, "rb") as f:
        head = f.read(20000).decode("utf-8", errors="replace")
    field_sep = _sep_from_head(head)

    if field_sep in {",", ";"} and ("\n" in head or "\r" in head):
        df = pd.read_csv(path, sep=field_sep, low_memory=False)
    else:
        parse_sep = "," if field_sep in {" | | ", "  ", "II", '\\"'} else field_sep
        tmp_path = _stream_normalize_to_temp(path, field_sep)
        try:
            df = pd.read_csv(tmp_path, sep=parse_sep, low_memory=False)
        finally:
            tmp_path.unlink(missing_ok=True)

    df.columns = [str(c).strip().strip('"') for c in df.columns]
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df = df.dropna(axis=1, how="all")
    return df


def _tidy_fault(df: pd.DataFrame) -> pd.DataFrame:
    cols = list(df.columns)

    id_plain = [
        c
        for c in cols
        if c.startswith("ID_") and not c.endswith((".x", ".y"))
    ]
    if id_plain:
        # prefer component/part id over odd extras
        id_plain = sorted(id_plain, key=len)
        id_s = df[id_plain[0]]
    else:
        id_x = next((c for c in cols if c.startswith("ID_") and c.endswith(".x")), None)
        id_y = next((c for c in cols if c.startswith("ID_") and c.endswith(".y")), None)
        if id_x is None and id_y is None:
            raise ValueError(f"No ID_* column among {cols[:25]}")
        id_s = df[id_x] if id_x else df[id_y]
        if id_x and id_y:
            id_s = id_s.fillna(df[id_y])

    if "Fehlerhaft" in df.columns:
        fh = df["Fehlerhaft"]
    else:
        fx = df["Fehlerhaft.x"] if "Fehlerhaft.x" in df.columns else None
        fy = df["Fehlerhaft.y"] if "Fehlerhaft.y" in df.columns else None
        if fx is not None and fy is not None:
            fh = (
                pd.to_numeric(fx, errors="coerce").fillna(0).ne(0)
                | pd.to_numeric(fy, errors="coerce").fillna(0).ne(0)
            ).astype(int)
        elif fx is not None:
            fh = fx
        elif fy is not None:
            fh = fy
        else:
            raise ValueError(f"No Fehlerhaft among {cols[:25]}")

    if "Fehlerhaft_Datum" in df.columns:
        fd = df["Fehlerhaft_Datum"]
    elif "Fehlerhaft_Datum.x" in df.columns or "Fehlerhaft_Datum.y" in df.columns:
        fdx = df["Fehlerhaft_Datum.x"] if "Fehlerhaft_Datum.x" in df.columns else None
        fdy = df["Fehlerhaft_Datum.y"] if "Fehlerhaft_Datum.y" in df.columns else None
        if fdx is not None and fdy is not None:
            fd = fdx.fillna(fdy)
        else:
            fd = fdx if fdx is not None else fdy
    else:
        fd = pd.Series(pd.NaT, index=df.index)

    out = pd.DataFrame(
        {
            "id": id_s.astype(str),
            "fehlerhaft": pd.to_numeric(fh, errors="coerce").fillna(0).astype(int),
            "defect_date": pd.to_datetime(fd, errors="coerce"),
        }
    )
    return out


def load_defective_units(path: Path) -> pd.DataFrame:
    """Load only defective units; chunk large plain CSVs."""
    print(f"  reading {path.name} ({path.stat().st_size / 1e6:.0f} MB)", flush=True)
    path = Path(path)
    size_mb = path.stat().st_size / 1e6
    with open(path, "rb") as f:
        head = f.read(20000).decode("utf-8", errors="replace")
    field_sep = _sep_from_head(head)

    if size_mb >= 80 and field_sep in {",", ";"} and ("\n" in head or "\r" in head):
        chunks = []
        for chunk in pd.read_csv(path, sep=field_sep, chunksize=250_000, low_memory=False):
            tidy = _tidy_fault(chunk)
            bad = tidy.loc[
                tidy["fehlerhaft"] == 1, ["id", "defect_date"]
            ].dropna(subset=["defect_date"])
            if not bad.empty:
                chunks.append(bad)
        out = (
            pd.concat(chunks, ignore_index=True)
            if chunks
            else pd.DataFrame(columns=["id", "defect_date"])
        )
        print(f"    defective: {len(out):,}", flush=True)
        return out

    # exotic formats: stream-normalize, then filter defective in chunks from temp
    if field_sep not in {",", ";"} or not ("\n" in head or "\r" in head):
        parse_sep = "," if field_sep in {" | | ", "  ", "II", '\\"'} else field_sep
        tmp_path = _stream_normalize_to_temp(path, field_sep)
        try:
            chunks = []
            for chunk in pd.read_csv(
                tmp_path, sep=parse_sep, chunksize=250_000, low_memory=False
            ):
                chunk.columns = [str(c).strip().strip('"') for c in chunk.columns]
                tidy = _tidy_fault(chunk)
                bad = tidy.loc[
                    tidy["fehlerhaft"] == 1, ["id", "defect_date"]
                ].dropna(subset=["defect_date"])
                if not bad.empty:
                    chunks.append(bad)
            out = (
                pd.concat(chunks, ignore_index=True)
                if chunks
                else pd.DataFrame(columns=["id", "defect_date"])
            )
            print(f"    defective: {len(out):,}", flush=True)
            return out
        finally:
            tmp_path.unlink(missing_ok=True)

    raw = _read_raw(path)
    tidy = _tidy_fault(raw)
    bad = tidy.loc[tidy["fehlerhaft"] == 1, ["id", "defect_date"]].dropna(subset=["defect_date"])
    print(f"    defective: {len(bad):,}", flush=True)
    del raw, tidy
    return bad


def load_registrations() -> pd.DataFrame:
    path = DATA_DIR / "Zulassungen" / "Zulassungen_alle_Fahrzeuge.csv"
    with open(path, "rb") as f:
        head = f.read(200).decode("utf-8", errors="replace")
    sep = ";" if head.count(";") > head.count(",") else ","
    zul = pd.read_csv(path, sep=sep, usecols=["IDNummer", "Zulassung"], dtype={"IDNummer": str})
    zul["reg_date"] = pd.to_datetime(zul["Zulassung"], errors="coerce")
    zul = zul.dropna(subset=["reg_date"])
    return zul.rename(columns={"IDNummer": "ID_Fahrzeug"})[["ID_Fahrzeug", "reg_date"]]


def load_bom_slot_maps() -> dict[str, pd.DataFrame]:
    """One vehicle->component map per BOM slot (~3.2M rows each)."""
    slots = {
        "ID_Motor": [],
        "ID_Sitze": [],
        "ID_Schaltung": [],
        "ID_Karosserie": [],
    }
    for rel in BOM_FILES:
        df = pd.read_csv(
            DATA_DIR / rel,
            sep=";",
            usecols=["ID_Fahrzeug", "ID_Motor", "ID_Sitze", "ID_Schaltung", "ID_Karosserie"],
            dtype=str,
        )
        for col in slots:
            slots[col].append(
                df[["ID_Fahrzeug", col]].rename(columns={col: "component_id"})
            )
        print(f"  BOM {Path(rel).name}: {len(df):,}", flush=True)
    out = {}
    for col, frames in slots.items():
        m = pd.concat(frames, ignore_index=True)
        print(f"  slot {col}: {len(m):,}", flush=True)
        out[col] = m
    return out


def _mark_from_units(
    defective: set[str],
    units: pd.DataFrame,
    id_map: pd.DataFrame,
    reg: pd.DataFrame,
    map_key: str,
) -> int:
    """Add vehicles whose linked unit has defect_date > reg_date."""
    if units.empty:
        return 0
    before = len(defective)
    keys = units["id"].unique()
    sub_map = id_map[id_map[map_key].isin(keys)]
    if sub_map.empty:
        return 0
    m = units.merge(sub_map, left_on="id", right_on=map_key, how="inner")
    m = m.merge(reg, on="ID_Fahrzeug", how="inner")
    hit = m.loc[m["defect_date"] > m["reg_date"], "ID_Fahrzeug"]
    defective.update(map(str, hit))
    return len(defective) - before


def _read_bestandteile(path: Path) -> pd.DataFrame:
    with open(path, "rb") as f:
        head = f.read(500).decode("utf-8", errors="replace")
    sep = ";" if head.count(";") >= head.count(",") else ","
    df = pd.read_csv(path, sep=sep, dtype=str)
    df.columns = [str(c).strip().strip('"') for c in df.columns]
    return df


def build_defective_vehicle_ids(save: bool = True) -> set[str]:
    print("1) registrations", flush=True)
    reg = load_registrations()
    print(f"   {len(reg):,}", flush=True)

    defective: set[str] = set()

    print("2) vehicle-level defects (after registration)", flush=True)
    for rel in VEHICLE_FILES:
        units = load_defective_units(DATA_DIR / rel)
        m = units.merge(reg, left_on="id", right_on="ID_Fahrzeug", how="inner")
        hit = m.loc[m["defect_date"] > m["reg_date"], "ID_Fahrzeug"]
        defective.update(map(str, hit))
    print(f"   cumulative: {len(defective):,}", flush=True)

    print("3) component maps from vehicle BOM (per slot)", flush=True)
    slot_maps = load_bom_slot_maps()

    print("4) component-level defects (after registration)", flush=True)
    for rel, slot in COMPONENT_FILES:
        path = DATA_DIR / rel
        if not path.exists():
            print(f"   MISSING {path}")
            continue
        units = load_defective_units(path)
        added = _mark_from_units(
            defective, units, slot_maps[slot], reg, "component_id"
        )
        print(f"   {path.name}: +{added:,} -> {len(defective):,}", flush=True)

    print("5) Einzelteil defects -> components -> vehicles", flush=True)
    part_files = {}
    for p in sorted((DATA_DIR / "Einzelteil").glob("Einzelteil_T*")):
        m = re.search(r"T(\d+)", p.stem)
        if m:
            part_files[int(m.group(1))] = p
    print(f"   part files available: {sorted(part_files)}", flush=True)

    defective_parts: dict[int, pd.DataFrame] = {}

    def parts_for(num: int) -> pd.DataFrame:
        if num not in defective_parts:
            if num not in part_files:
                defective_parts[num] = pd.DataFrame(columns=["id", "defect_date"])
            else:
                defective_parts[num] = load_defective_units(part_files[num])
        return defective_parts[num]

    def slot_for_comp_col(comp_col: str) -> str:
        name = comp_col.replace("ID_", "")
        if name.startswith("K1"):
            return "ID_Motor"
        if name.startswith("K2"):
            return "ID_Sitze"
        if name.startswith("K3"):
            return "ID_Schaltung"
        return "ID_Karosserie"

    for rel, comp_col in BESTANDTEILE_KOMPONENTE:
        path = DATA_DIR / rel
        if not path.exists():
            print(f"   MISSING {path}")
            continue
        b = _read_bestandteile(path)
        if comp_col not in b.columns:
            print(f"   skip {path.name}: no {comp_col}")
            continue
        slot = slot_for_comp_col(comp_col)
        part_cols = [c for c in b.columns if re.fullmatch(r"ID_T\d+", c)]
        print(f"   {path.name}: parts {part_cols} -> {slot}", flush=True)
        for pc in part_cols:
            num = int(re.search(r"T(\d+)", pc).group(1))
            units = parts_for(num)
            if units.empty:
                continue
            link = b[[pc, comp_col]].dropna()
            link.columns = ["part_id", "component_id"]
            link["part_id"] = link["part_id"].astype(str)
            link["component_id"] = link["component_id"].astype(str)
            keys = units["id"].unique()
            link = link[link["part_id"].isin(keys)]
            if link.empty:
                continue
            u = units.merge(link, left_on="id", right_on="part_id", how="inner")
            inherited = u[["component_id", "defect_date"]].rename(
                columns={"component_id": "id"}
            )
            added = _mark_from_units(
                defective, inherited, slot_maps[slot], reg, "component_id"
            )
            print(f"     {pc}: +{added:,} -> {len(defective):,}", flush=True)

    print(f"DONE: {len(defective):,} defective vehicles (after registration)", flush=True)
    if save:
        LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        pd.Series(sorted(defective), name="ID_Fahrzeug").to_csv(DEFECT_IDS_PATH, index=False)
        print(f"wrote {DEFECT_IDS_PATH}", flush=True)
    return defective


def load_defective_vehicle_ids() -> set[str]:
    if DEFECT_IDS_PATH.exists():
        return set(pd.read_csv(DEFECT_IDS_PATH, dtype=str)["ID_Fahrzeug"].astype(str))
    return build_defective_vehicle_ids(save=True)


if __name__ == "__main__":
    build_defective_vehicle_ids(save=True)
