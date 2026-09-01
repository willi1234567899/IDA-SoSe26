"""
SoSe26 Case Study App – Group 38

Participants: Mark Prymak, Pascal Diekmeier, Smilla Elisa Eichhorn,
Willi Leonard Horn

Run from this folder (Anaconda / project env):

    python3 -m streamlit run SoSe26_Case_Study_App_Group_38.py

The app reads only:
    Data/SoSe26_Case_Study_finalData_Group_38.csv
"""

from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw, ImageFont

DATA_PATH = Path("Data") / "SoSe26_Case_Study_finalData_Group_38.csv"
LOGO_PATH = Path("www") / "img" / "company-logo.png"
FALLBACK_LOGO_PATH = Path("www") / "img" / "logo.svg"
CSS_PATH = Path("www") / "style.css"
COMPANY_NAME = "Vektor Motors"
LOGO_WIDTH_HEADER = 120
FONT_REGULAR = Path("www") / "fonts" / "source-sans-3-latin-400-normal.woff2"
FONT_SEMIBOLD = Path("www") / "fonts" / "source-sans-3-latin-600-normal.woff2"

# Brand tokens (keep in sync with www/style.css :root)
BRAND_BLUE = "#5BA4CF"
BRAND_BLUE_DARK = "#2F5F7A"
BRAND_BLUE_SOFT = "#E8F4FA"
BRAND_BLUE_LINE = "#C5DCEB"
BRAND_TEXT = "#1F2D3A"
BRAND_MUTED = "#4A6A7A"
BRAND_WARN = "#8A4B16"


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    value = color.lstrip("#")
    return tuple(int(value[i: i + 2], 16) for i in (0, 2, 4))


PLOTLY_BLUES = [BRAND_BLUE_DARK, BRAND_BLUE, "#8FCBE8", "#C5E4F3"]
PLOTLY_COLORS = [
    BRAND_BLUE_DARK,
    BRAND_BLUE,
    "#1F7A8C",
    "#6C8EBF",
    "#8A7FB8",
    "#4F8F6F",
    "#A07A5F",
    "#7A6F9B",
    "#5796A5",
    "#8FA6B3",
]

CATEGORY_COLORS = {
    "K1": BRAND_BLUE_DARK,
    "K2": BRAND_BLUE,
    "K3": "#1F7A8C",
    "K4": "#6C8EBF",
    "K5": "#8A7FB8",
    "K6": "#4F8F6F",
    "K7": "#A07A5F",
}
CATEGORIES = ["K1", "K2", "K3", "K4", "K5", "K6", "K7"]
BODY_CATEGORIES = ["K4", "K5", "K6", "K7"]
# data span is 2009-2016; no explicit production start/stop flags exist, so
# "series start" = first year with registrations > 2009
# "series end" = last year with registrations < 2016
DATA_START_YEAR = 2009
DATA_END_YEAR = 2016
SERIES_START_MARKER = dict(
    symbol="triangle-up",
    size=12,
    color="#1F7A4D",
    line=dict(width=1, color="#1F7A4D"),
)
SERIES_END_MARKER = dict(
    symbol="x",
    size=14,
    color="#C0392B",
    line=dict(width=2, color="#C0392B"),
)

COUNT_ALL = "n_registrations"
COUNT_CLEAN = "n_registrations_clean"

FINAL_DATA_COLUMN_LABELS = {
    "year": "Year",
    "oem": "OEM",
    "vehicle_type": "Vehicle type",
    "category": "Category",
    "component_type": "Component type",
    "manufacturer": "Manufacturer",
    "plant": "Plant",
    "series": "Series",
    "n_registrations": "Registrations",
    "n_registrations_clean": "Registrations (defect-filtered)",
    "label": "Description",
}


@st.cache_data
def load_data(data_mtime: float) -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error(
            f"Final dataset not found at `{DATA_PATH}`. "
            "Run the case-study notebook first so this CSV is created."
        )
        st.stop()
    df = pd.read_csv(DATA_PATH)
    df["year"] = df["year"].astype(int)
    for col in ["manufacturer", "plant"]:
        if col in df.columns:
            df[col] = df[col].astype(str)
    if COUNT_CLEAN not in df.columns:
        df[COUNT_CLEAN] = df[COUNT_ALL]
    return df


def get_data() -> pd.DataFrame:
    """Load final CSV, busting cache when the file changes on disk."""
    mtime = DATA_PATH.stat().st_mtime if DATA_PATH.exists() else 0.0
    return load_data(mtime)


def _font_face(path: Path, weight: int) -> str:
    if not path.exists():
        return ""
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"""
    @font-face {{
      font-family: "Source Sans Pro";
      font-style: normal;
      font-weight: {weight};
      src: url(data:font/woff2;base64,{payload}) format("woff2");
    }}
    """


def _image_data_uri(path: Path) -> str:
    mime_by_suffix = {
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }
    mime = mime_by_suffix.get(path.suffix.lower(), "application/octet-stream")
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{payload}"


def render_sidebar_branding(logo_file: Path) -> None:
    logo_markup = ""
    if logo_file.exists():
        logo_markup = (
            f'<img src="{_image_data_uri(logo_file)}" '
            f'alt="{COMPANY_NAME}" class="ida-sidebar-logo" />'
        )

    st.markdown(
        f"""
        <div class="ida-sidebar-branding">
            <div class="ida-sidebar-logo-wrap">
                {logo_markup}
            </div>
            <p class="ida-sidebar-brand">{COMPANY_NAME}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(logo_file: Path) -> None:
    logo_markup = ""
    if logo_file.exists():
        logo_markup = (
            f'<img src="{_image_data_uri(logo_file)}" '
            f'alt="{COMPANY_NAME}" class="ida-page-header__logo" '
            f'style="width: {LOGO_WIDTH_HEADER}px;" />'
        )

    st.markdown(
        f"""
        <header class="ida-page-header">
            {logo_markup}
            <div class="ida-page-header__text">
                <p class="ida-page-header__company">{COMPANY_NAME}</p>
                <h1 class="ida-page-header__title">
                    Vehicle Popularity Analysis Dashboard
                </h1>
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_settings_summary(
    registration_basis: str,
    period_mode: str,
    analysis_period_label: str,
) -> None:
    st.sidebar.header("Current analysis settings")
    st.sidebar.markdown(
        f"""
**Registration basis:** {registration_basis}
**Analysis period:** {period_mode}
**Years in analysis:** {analysis_period_label}
"""
    )
    st.sidebar.divider()


def apply_design() -> None:
    font_css = _font_face(FONT_REGULAR, 400) + _font_face(FONT_SEMIBOLD, 600)
    extra = CSS_PATH.read_text(encoding="utf-8") if CSS_PATH.exists() else ""
    st.markdown(
        f"""
        <style>
        {font_css}
        html, body, [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"], .stMarkdown, .stMetric {{
            font-family: "Source Sans Pro", "Source Sans 3",
                Helvetica, Arial, sans-serif;
        }}
        [data-testid="stHeader"] {{ background: {BRAND_BLUE_SOFT}; }}
        [data-testid="stSidebar"] {{ background: {BRAND_BLUE_SOFT}; }}
        div[data-testid="stMetric"] {{
            background: {BRAND_BLUE_SOFT};
            border-left: 4px solid {BRAND_BLUE};
            padding: 0.6rem 0.8rem;
        }}
        {extra}
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_fig(fig):
    fig.update_layout(
        font_family="Source Sans Pro",
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend_title_text="",
    )
    return fig


def active_count_col(exclude_defective: bool) -> str:
    return COUNT_CLEAN if exclude_defective else COUNT_ALL


def methodology_text(
    analysis_period_label: str,
    registration_basis: str,
) -> str:
    return f"""
**Popularity metric**
We count how many **registered vehicles** contain each component **series**
(type + manufacturer + plant), summed over the selected analysis period
(**{analysis_period_label}**) and registration basis (**{registration_basis}**).

**Four recommendation pools (not seven separate winners)**
| Pool | Categories | Rule |
|------|------------|------|
| Engine | K1 only | Highest registration volume within K1 |
| Seats | K2 only | Highest registration volume within K2 |
| Gearbox | K3 only | Highest registration volume within K3 |
| Body | **K4 + K5 + K6 + K7 together** | Top volume across all body series |

K4–K7 are different **body categories**, but a vehicle needs **one body choice**.
Therefore we compare every body series from K4–K7 in a **single ranking**
and recommend the overall body leader — not one winner per K4, K5, K6, and K7.

**Most popular vehicle** = top engine + top seats + top gearbox + top body
(four independent choices by registration volume).

**Ties**
If two or more series share the highest count in a pool, all are shown as
co-leaders (same rank).

**Trends tab**
Yearly charts always use the **full dataset period** so long-term fashions
remain visible. Rankings above respect the analysis-period filter selected above.

**Not validated**
We do not check whether the four recommended components can be built together
on one real vehicle.
"""


def with_count(df: pd.DataFrame, count_col: str) -> pd.DataFrame:
    """Normalize the active metric to column name n_count for plotting."""
    out = df.copy()
    out["n_count"] = out[count_col]
    return out


def overall_counts(df: pd.DataFrame, count_col: str) -> pd.DataFrame:
    return (
        df.groupby(
            ["category", "component_type", "manufacturer", "plant", "series", "label"],
            as_index=False,
        )[count_col]
        .sum()
        .rename(columns={count_col: "n_count"})
        .sort_values(["category", "n_count"], ascending=[True, False])
    )


def build_series_kpis(
    df: pd.DataFrame,
    count_col: str,
    lifecycle_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Build one KPI table per component series.

    Metrics:
    - registration volume
    - defect-filtered registration volume
    - affected vehicle rate
    - category market share
    - category rank
    - first / last observed registration year
    - whether the series is observed in the latest dataset year
    - lead of the category winner over second place
    """

    if lifecycle_df is None:
        lifecycle_df = df

    group_cols = [
        "category",
        "component_type",
        "manufacturer",
        "plant",
        "series",
        "label",
    ]

    # ---------------------------------------------------------
    # 1. Aggregate registrations per component series
    # ---------------------------------------------------------
    kpis = (
        df.groupby(group_cols, as_index=False)
        .agg(
            n_registrations=(COUNT_ALL, "sum"),
            n_registrations_clean=(COUNT_CLEAN, "sum"),
        )
    )

    # Active metric depends on selected registration basis
    kpis["n_count"] = kpis[count_col]

    # ---------------------------------------------------------
    # 2. Affected vehicle rate
    # ---------------------------------------------------------
    kpis["n_affected"] = (
        kpis["n_registrations"]
        - kpis["n_registrations_clean"]
    )

    denominator = kpis["n_registrations"].replace(0, pd.NA)

    kpis["affected_vehicle_rate"] = (
        kpis["n_affected"] / denominator
    ).astype(float)

    # ---------------------------------------------------------
    # 3. Market share within category
    # ---------------------------------------------------------
    kpis["category_total"] = (
        kpis.groupby("category")["n_count"]
        .transform("sum")
    )

    kpis["market_share"] = (
        kpis["n_count"]
        / kpis["category_total"].replace(0, pd.NA)
    ).astype(float)

    # ---------------------------------------------------------
    # 4. Rank within category
    #
    # method="min":
    # 1, 1, 3 in case of a tie
    # ---------------------------------------------------------
    kpis["rank"] = (
        kpis.groupby("category")["n_count"]
        .rank(
            method="min",
            ascending=False,
        )
        .astype("Int64")
    )

    # Identify tied positions
    kpis["is_tied"] = (
        kpis.groupby(
            ["category", "n_count"]
        )["series"]
        .transform("size")
        .gt(1)
    )

    # ---------------------------------------------------------
    # 5. Lifecycle
    #
    # Always use ALL registrations here.
    # Defect filtering must not make a series appear discontinued.
    # ---------------------------------------------------------
    lifecycle = (
        lifecycle_df[
            lifecycle_df[COUNT_ALL] > 0
        ]
        .groupby(
            ["category", "series"],
            as_index=False,
        )
        .agg(
            first_observed_year=("year", "min"),
            last_observed_year=("year", "max"),
        )
    )

    latest_year = int(lifecycle_df["year"].max())

    lifecycle["observed_in_latest_year"] = (
        lifecycle["last_observed_year"] == latest_year
    )

    kpis = kpis.merge(
        lifecycle,
        on=["category", "series"],
        how="left",
    )

    kpis["latest_data_year"] = latest_year

    # ---------------------------------------------------------
    # 6. Winner gap vs. second place
    # ---------------------------------------------------------
    leader_stats = []

    for category, sub in kpis.groupby("category"):
        values = (
            sub["n_count"]
            .sort_values(ascending=False)
            .reset_index(drop=True)
        )

        top_1 = values.iloc[0]

        if len(values) > 1:
            top_2 = values.iloc[1]

            gap_abs = top_1 - top_2

            gap_pct = (
                gap_abs / top_2
                if top_2 != 0
                else pd.NA
            )

            category_total = sub["n_count"].sum()

            # Difference in category market share
            gap_pp = (
                gap_abs / category_total
                if category_total != 0
                else pd.NA
            )

        else:
            top_2 = pd.NA
            gap_abs = pd.NA
            gap_pct = pd.NA
            gap_pp = pd.NA

        leader_stats.append(
            {
                "category": category,
                "leader_count": top_1,
                "second_count": top_2,
                "lead_vs_second_abs": gap_abs,
                "lead_vs_second_pct": gap_pct,
                "lead_vs_second_pp": gap_pp,
            }
        )

    leader_stats = pd.DataFrame(leader_stats)

    kpis = kpis.merge(
        leader_stats,
        on="category",
        how="left",
    )

    # ---------------------------------------------------------
    # 7. Final sorting
    # ---------------------------------------------------------
    return (
        kpis.sort_values(
            ["category", "n_count", "series"],
            ascending=[True, False, True],
        )
        .reset_index(drop=True)
    )


def top_series_rows(
    kpis: pd.DataFrame,
    categories: str | list[str],
) -> pd.DataFrame:
    """Return all series tied for the highest active registration volume."""

    if isinstance(categories, str):
        categories = [categories]

    sub = kpis[kpis["category"].isin(categories)].copy()

    if sub.empty:
        return sub

    top_count = sub["n_count"].max()

    return (
        sub[sub["n_count"] == top_count]
        .sort_values(["category", "series"])
        .reset_index(drop=True)
    )


def series_names(rows: pd.DataFrame) -> str:
    """Format one or multiple tied series for display."""

    if rows.empty:
        return "No data"

    return " / ".join(rows["series"].tolist())


def build_recommendation_export(
    analysis_period_label: str,
    registration_basis: str,
    vehicle_registrations: int,
    engine_top: pd.DataFrame,
    seats_top: pd.DataFrame,
    gearbox_top: pd.DataFrame,
    body_top: pd.DataFrame,
    engine_share: float,
    seats_share: float,
    gearbox_share: float,
    body_share: float,
) -> pd.DataFrame:
    """One export row per leading series (ties become multiple rows)."""

    def slot_rows(
        slot: str,
        rows: pd.DataFrame,
        share: float,
        share_label: str,
    ) -> list[dict]:
        if rows.empty:
            return [
                {
                    "slot": slot,
                    "series": "No data",
                    "market_share": share,
                    "share_basis": share_label,
                    "analysis_period": analysis_period_label,
                    "registration_basis": registration_basis,
                    "vehicle_registrations": vehicle_registrations,
                }
            ]

        out = []
        for _, row in rows.iterrows():
            out.append(
                {
                    "slot": slot,
                    "series": row["series"],
                    "market_share": share,
                    "share_basis": share_label,
                    "analysis_period": analysis_period_label,
                    "registration_basis": registration_basis,
                    "vehicle_registrations": vehicle_registrations,
                }
            )
        return out

    records: list[dict] = []
    records.extend(slot_rows("Engine · K1", engine_top, engine_share, "K1"))
    records.extend(slot_rows("Seats · K2", seats_top, seats_share, "K2"))
    records.extend(slot_rows("Gearbox · K3", gearbox_top, gearbox_share, "K3"))
    records.extend(
        slot_rows("Body · K4–K7", body_top, body_share, "K4–K7 body pool")
    )
    return pd.DataFrame.from_records(records)


def dataframe_to_excel_bytes(df: pd.DataFrame,
                             sheet_name: str = "Recommendation") -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return buffer.getvalue()


def _load_export_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Return a TrueType font for JPEG export, with sensible fallbacks."""
    if bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "DejaVuSans-Bold.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "DejaVuSans.ttf",
        ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def recommendation_to_jpeg_bytes(
    analysis_period_label: str,
    registration_basis: str,
    exclude_defective: bool,
    slots: list[tuple[str, str, str]],
    vehicle_registrations: int,
) -> bytes:
    """Render a stakeholder-friendly JPEG of the recommended vehicle card."""

    width = 1400
    padding = 36
    accent = _hex_to_rgb(BRAND_BLUE)
    soft = _hex_to_rgb(BRAND_BLUE_SOFT)
    dark = _hex_to_rgb(BRAND_BLUE_DARK)
    muted = _hex_to_rgb(BRAND_MUTED)
    warn = _hex_to_rgb(BRAND_WARN)
    white = (255, 255, 255)
    divider_rgb = _hex_to_rgb(BRAND_BLUE_LINE)

    title_font = _load_export_font(42, bold=True)
    meta_font = _load_export_font(22)
    label_font = _load_export_font(18, bold=True)
    series_font = _load_export_font(24, bold=True)
    share_font = _load_export_font(18)
    footer_label_font = _load_export_font(20, bold=True)
    footer_value_font = _load_export_font(34, bold=True)

    # Probe height with a temporary image.
    probe = Image.new("RGB", (width, 100), white)
    probe_draw = ImageDraw.Draw(probe)

    content_width = width - 2 * padding - 10
    slot_gap = 24
    slot_width = (content_width - 3 * slot_gap) // 4
    slot_heights = []
    for label, series, share in slots:
        wrapped = _wrap_text(probe_draw, series, series_font, slot_width - 8)
        slot_heights.append(28 + 8 + len(wrapped) * 30 + 8 + 24)

    filter_extra = 36 if exclude_defective else 0
    body_top = padding + 56 + 34 + filter_extra
    slots_height = max(slot_heights) if slot_heights else 80
    height = body_top + slots_height + 28 + 70 + padding

    img = Image.new("RGB", (width, height), white)
    draw = ImageDraw.Draw(img)

    # Card background + left accent.
    draw.rectangle((0, 0, width, height), fill=soft)
    draw.rectangle((0, 0, 10, height), fill=accent)

    x = padding + 10
    y = padding
    draw.text((x, y), "Recommended vehicle", font=title_font, fill=dark)
    y += 56
    draw.text(
        (x, y),
        f"Analysis period · {analysis_period_label} · {registration_basis}",
        font=meta_font,
        fill=muted,
    )
    y += 34
    if exclude_defective:
        draw.text(
            (x, y),
            "Defect filter active — rankings exclude defective vehicles.",
            font=meta_font,
            fill=warn,
        )
        y += 36

    for i, (label, series, share) in enumerate(slots):
        sx = x + i * (slot_width + slot_gap)
        sy = y
        draw.text((sx, sy), label.upper(), font=label_font, fill=muted)
        sy += 28
        for text_line in _wrap_text(draw, series, series_font, slot_width - 8):
            draw.text((sx, sy), text_line, font=series_font, fill=dark)
            sy += 30
        draw.text((sx, sy + 4), share, font=share_font, fill=muted)

    y = body_top + slots_height + 18
    draw.line((x, y, width - padding, y), fill=divider_rgb, width=2)
    y += 18
    draw.text((x, y + 8), "Vehicle registrations", font=footer_label_font, fill=muted)
    value_x = x + int(draw.textlength("Vehicle registrations",
                      font=footer_label_font)) + 18
    draw.text((value_x, y), f"{vehicle_registrations:,}",
              font=footer_value_font, fill=dark)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=92, optimize=True)
    return buffer.getvalue()


def render_recommendation_hero(
    analysis_period_label: str,
    registration_basis: str,
    exclude_defective: bool,
    engine_top: pd.DataFrame,
    seats_top: pd.DataFrame,
    gearbox_top: pd.DataFrame,
    body_top: pd.DataFrame,
    engine_share: float,
    seats_share: float,
    gearbox_share: float,
    body_share: float,
    vehicle_registrations: int,
) -> None:
    slots = [
        (
            "Engine · K1",
            series_names(engine_top),
            f"{engine_share:.1%} of K1 registrations",
        ),
        (
            "Seats · K2",
            series_names(seats_top),
            f"{seats_share:.1%} of K2 registrations",
        ),
        (
            "Gearbox · K3",
            series_names(gearbox_top),
            f"{gearbox_share:.1%} of K3 registrations",
        ),
        (
            "Body · K4–K7",
            series_names(body_top),
            f"{body_share:.1%} of K4–K7 body pool",
        ),
    ]

    slot_html = "".join(
        (
            '<div class="slot">'
            f'<p class="slot-label">{label}</p>'
            f'<p class="slot-series">{series}</p>'
            f'<p class="slot-share">{share}</p>'
            "</div>"
        )
        for label, series, share in slots
    )

    filter_html = ""
    if exclude_defective:
        filter_html = (
            '<p class="rec-filter">'
            "Defect filter active — rankings exclude defective vehicles. "
            "Details: see Glossary."
            "</p>"
        )

    hero_height = 248 if exclude_defective else 218

    # Render as an HTML component so Streamlit markdown cannot break nested tags.
    components.html(
        f"""
        <style>
          html, body {{
            margin: 0;
            padding: 0;
          }}
          .rec-hero {{
            background: {BRAND_BLUE_SOFT};
            border-left: 4px solid {BRAND_BLUE};
            box-sizing: border-box;
            color: {BRAND_TEXT};
            font-family: "Source Sans Pro", "Source Sans 3",
                Helvetica, Arial, sans-serif;
            padding: 1rem 1.15rem 1rem;
          }}
          .rec-title {{
            color: {BRAND_BLUE_DARK};
            font-size: 1.4rem;
            font-weight: 600;
            line-height: 1.2;
            margin: 0 0 0.2rem;
          }}
          .rec-period {{
            color: {BRAND_MUTED};
            font-size: 0.9rem;
            margin: 0 0 0.45rem;
          }}
          .rec-filter {{
            color: {BRAND_WARN};
            font-size: 0.88rem;
            font-weight: 600;
            margin: 0 0 0.85rem;
          }}
          .rec-slots {{
            display: grid;
            gap: 0.85rem 1.25rem;
            grid-template-columns: repeat(4, minmax(0, 1fr));
          }}
          .slot-label {{
            color: {BRAND_MUTED};
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            margin: 0 0 0.2rem;
            text-transform: uppercase;
          }}
          .slot-series {{
            color: {BRAND_BLUE_DARK};
            font-size: 1rem;
            font-weight: 600;
            line-height: 1.35;
            margin: 0 0 0.2rem;
            overflow-wrap: anywhere;
            word-break: break-word;
          }}
          .slot-share {{
            color: {BRAND_MUTED};
            font-size: 0.85rem;
            margin: 0;
          }}
          .rec-divider {{
            border: 0;
            border-top: 1px solid {BRAND_BLUE_LINE};
            margin: 1rem 0 0.85rem;
          }}
          .rec-regs {{
            align-items: baseline;
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem 0.85rem;
          }}
          .rec-regs-label {{
            color: {BRAND_MUTED};
            font-size: 0.85rem;
            font-weight: 600;
            margin: 0;
          }}
          .rec-regs-value {{
            color: {BRAND_BLUE_DARK};
            font-size: 1.35rem;
            font-weight: 600;
            margin: 0;
          }}
          @media (max-width: 900px) {{
            .rec-slots {{
              grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
          }}
        </style>
        <div class="rec-hero">
          <p class="rec-title">Recommended vehicle</p>
          <p class="rec-period">
            Analysis period · {analysis_period_label}
            · {registration_basis}
          </p>
          {filter_html}
          <div class="rec-slots">{slot_html}</div>
          <hr class="rec-divider" />
          <div class="rec-regs">
            <p class="rec-regs-label">Vehicle registrations</p>
            <p class="rec-regs-value">{vehicle_registrations:,}</p>
          </div>
        </div>
        """,
        height=hero_height,
        scrolling=False,
    )

    export_df = build_recommendation_export(
        analysis_period_label=analysis_period_label,
        registration_basis=registration_basis,
        vehicle_registrations=vehicle_registrations,
        engine_top=engine_top,
        seats_top=seats_top,
        gearbox_top=gearbox_top,
        body_top=body_top,
        engine_share=engine_share,
        seats_share=seats_share,
        gearbox_share=gearbox_share,
        body_share=body_share,
    )

    jpeg_bytes = recommendation_to_jpeg_bytes(
        analysis_period_label=analysis_period_label,
        registration_basis=registration_basis,
        exclude_defective=exclude_defective,
        slots=slots,
        vehicle_registrations=vehicle_registrations,
    )

    period_slug = (
        analysis_period_label.replace("–", "-").replace(" ", "")
    )
    mode_slug = "exclude-defective" if exclude_defective else "all-registrations"
    base_name = f"recommended_vehicle_{period_slug}_{mode_slug}"

    st.markdown('<div class="ida-export-row">', unsafe_allow_html=True)
    excel_col, jpeg_col = st.columns(2)
    with excel_col:
        st.download_button(
            label="Export Excel",
            data=dataframe_to_excel_bytes(export_df),
            file_name=f"{base_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help=(
                "Download the recommended vehicle slots and settings "
                "as an Excel file."
            ),
            key=f"export_recommendation_xlsx_{mode_slug}_{period_slug}",
            type="primary",
            icon=":material/table:",
            width="stretch",
        )
    with jpeg_col:
        st.download_button(
            label="Export JPEG",
            data=jpeg_bytes,
            file_name=f"{base_name}.jpg",
            mime="image/jpeg",
            help="Download a JPEG image of the recommended vehicle card.",
            key=f"export_recommendation_jpeg_{mode_slug}_{period_slug}",
            type="primary",
            icon=":material/image:",
            width="stretch",
        )
    st.markdown("</div>", unsafe_allow_html=True)


def build_ranking(
    kpis: pd.DataFrame,
    categories: str | list[str],
) -> pd.DataFrame:
    """
    Build a ranking for one category or a combined category group.

    For K4-K7 this allows one overall body ranking.
    """

    if isinstance(categories, str):
        categories = [categories]

    ranking = kpis[
        kpis["category"].isin(categories)
    ].copy()

    if ranking.empty:
        return ranking

    # Recalculate rank within the selected ranking pool.
    ranking["display_rank"] = (
        ranking["n_count"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )

    total = ranking["n_count"].sum()

    ranking["display_share"] = (
        ranking["n_count"] / total
        if total > 0
        else 0.0
    )

    ranking["lifecycle"] = ranking.apply(
        lambda row:
            f"Observed in {int(row['latest_data_year'])}"
            if row["observed_in_latest_year"]
            else f"Last observed {int(row['last_observed_year'])}",
        axis=1,
    )

    return (
        ranking.sort_values(
            ["n_count", "series"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )


def top_five_ranking(ranking: pd.DataFrame) -> pd.DataFrame:
    """
    Return the top five ranks.

    Ties are preserved, so more than five rows may be shown
    if multiple series share rank 5.
    """

    if ranking.empty:
        return ranking

    return ranking[
        ranking["display_rank"] <= 5
    ].copy()


def ranking_lead_stats(ranking: pd.DataFrame) -> dict:
    """Calculate the leader's gap to the second row in the ranking."""

    if ranking.empty:
        return {
            "lead_abs": None,
            "lead_pct": None,
            "lead_pp": None,
        }

    values = (
        ranking["n_count"]
        .sort_values(ascending=False)
        .reset_index(drop=True)
    )

    if len(values) < 2:
        return {
            "lead_abs": None,
            "lead_pct": None,
            "lead_pp": None,
        }

    top_1 = values.iloc[0]
    top_2 = values.iloc[1]

    gap_abs = top_1 - top_2

    gap_pct = (
        gap_abs / top_2
        if top_2 != 0
        else None
    )

    total = ranking["n_count"].sum()

    gap_pp = (
        gap_abs / total
        if total != 0
        else None
    )

    return {
        "lead_abs": int(gap_abs),
        "lead_pct": gap_pct,
        "lead_pp": gap_pp,
    }


def winners_by_category(overall: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cat in CATEGORIES:
        sub = overall[overall["category"] == cat]
        if sub.empty:
            continue
        top_n = sub["n_count"].max()
        rows.append(sub[sub["n_count"] == top_n])
    return pd.concat(rows, ignore_index=True)


def plot_series_bars(overall: pd.DataFrame, category: str, title: Optional[str] = None):
    sub = overall[overall["category"] == category].sort_values(
        "n_count", ascending=False)
    fig = px.bar(
        sub,
        x="series",
        y="n_count",
        color="label",
        title=title or f"Registered vehicles by series - {category}",
        labels={
            "series": "Component series",
            "n_count": "Registered vehicles",
            "label": "Type",
        },
        color_discrete_sequence=PLOTLY_COLORS,
    )
    fig.update_layout(xaxis_tickangle=-35)
    return style_fig(fig)


def plot_body_bars(overall: pd.DataFrame):
    body = overall[overall["category"].isin(BODY_CATEGORIES)]
    fig = px.bar(
        body,
        x="series",
        y="n_count",
        color="category",
        title="Registered vehicles by body series (K4-K7)",
        labels={
            "series": "Body series",
            "n_count": "Registered vehicles",
            "category": "Category",
        },
        color_discrete_map=CATEGORY_COLORS,
    )
    fig.update_layout(xaxis_tickangle=-35)
    return style_fig(fig)


def mark_series_span(
    fig,
    yearly: pd.DataFrame,
    y_col: str = "n_count",
):
    """
    Mark first and last observed registration of each series.

    The marker position follows the currently displayed metric:
    registration volume or market share.
    """

    # ---------------------------------------------------------
    # First observed registration
    # ---------------------------------------------------------
    first = yearly.loc[
        yearly.groupby("series")["year"].idxmin()
    ]

    started = first[
        first["year"] > DATA_START_YEAR
    ]

    if not started.empty:

        if y_col == "market_share":
            start_hover = (
                "first observed registration"
                "<br>year=%{x}"
                "<br>market share=%{y:.1%}"
                "<extra></extra>"
            )
        else:
            start_hover = (
                "first observed registration"
                "<br>year=%{x}"
                "<br>registrations=%{y:,}"
                "<extra></extra>"
            )

        fig.add_scatter(
            x=started["year"],
            y=started[y_col],
            mode="markers",
            marker=SERIES_START_MARKER,
            name="first observed registration",
            legendgroup="series_start",
            hovertemplate=start_hover,
        )

    # ---------------------------------------------------------
    # Last observed registration
    # ---------------------------------------------------------
    last = yearly.loc[
        yearly.groupby("series")["year"].idxmax()
    ]

    ended = last[
        last["year"] < DATA_END_YEAR
    ]

    if not ended.empty:

        if y_col == "market_share":
            end_hover = (
                "last observed registration"
                "<br>year=%{x}"
                "<br>market share=%{y:.1%}"
                "<extra></extra>"
            )
        else:
            end_hover = (
                "last observed registration"
                "<br>year=%{x}"
                "<br>registrations=%{y:,}"
                "<extra></extra>"
            )

        fig.add_scatter(
            x=ended["year"],
            y=ended[y_col],
            mode="markers",
            marker=SERIES_END_MARKER,
            name="last observed registration",
            legendgroup="series_end",
            hovertemplate=end_hover,
        )

    return fig


def plot_trends(
    df: pd.DataFrame,
    category: str,
    count_col: str,
    metric: str = "Registration volume",
):
    """
    Plot yearly development by component series.

    metric:
    - Registration volume
    - Category market share
    """

    yearly = (
        df[df["category"] == category]
        .groupby(
            ["year", "series"],
            as_index=False,
        )[count_col]
        .sum()
        .rename(
            columns={
                count_col: "n_count"
            }
        )
    )

    # ---------------------------------------------------------
    # Market share within category and year
    # ---------------------------------------------------------
    yearly["category_total"] = (
        yearly.groupby("year")["n_count"]
        .transform("sum")
    )

    denominator = yearly["category_total"].where(
        yearly["category_total"] != 0
    )

    yearly["market_share"] = (
        yearly["n_count"] / denominator
    )

    # ---------------------------------------------------------
    # Select display metric
    # ---------------------------------------------------------
    if metric == "Category market share":

        y_col = "market_share"

        title = (
            f"Yearly category market share - {category}"
        )

        labels = {
            "year": "Registration year",
            "market_share": "Category market share",
            "series": "Component series",
        }

    else:

        y_col = "n_count"

        title = (
            f"Yearly registrations - {category}"
        )

        labels = {
            "year": "Registration year",
            "n_count": "Registered vehicles",
            "series": "Component series",
        }

    # ---------------------------------------------------------
    # Plot
    # ---------------------------------------------------------
    fig = px.line(
        yearly,
        x="year",
        y=y_col,
        color="series",
        markers=True,
        title=title,
        labels=labels,
        color_discrete_sequence=PLOTLY_COLORS,
    )

    fig.update_layout(
        xaxis=dict(dtick=1)
    )

    # Percentage formatting
    if metric == "Category market share":

        fig.update_yaxes(
            tickformat=".1%"
        )

        fig.update_traces(
            hovertemplate=(
                "year=%{x}"
                "<br>market share=%{y:.1%}"
                "<extra>%{fullData.name}</extra>"
            )
        )

    else:

        fig.update_traces(
            hovertemplate=(
                "year=%{x}"
                "<br>registrations=%{y:,}"
                "<extra>%{fullData.name}</extra>"
            )
        )

    return style_fig(
        mark_series_span(
            fig,
            yearly,
            y_col=y_col,
        )
    )


def main() -> None:
    st.set_page_config(
        page_title="Vehicle Popularity Analysis Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_design()
    df = get_data()

    logo_file = LOGO_PATH if LOGO_PATH.exists() else FALLBACK_LOGO_PATH

    with st.sidebar:
        render_sidebar_branding(logo_file)
        st.divider()

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    render_page_header(logo_file)

    st.info(
        "Use the button :material/keyboard_double_arrow_right: in the top left corner "
        "to open the sidebar. Use it for analysis settings, calculation methodology, "
        "and glossary."
    )

    # ---------------------------------------------------------
    # Registration basis + analysis period (side by side)
    # ---------------------------------------------------------

    data_start_year = int(df["year"].min())
    data_end_year = int(df["year"].max())

    filt_l, filt_div, filt_r = st.columns([1, 0.04, 1], gap="medium")

    with filt_l:
        mode = st.radio(
            "Registration basis",
            options=[
                "All registrations",
                "Exclude defective vehicles",
            ],
            index=0,
            horizontal=True,
            key="defect_mode",
            help=(
                "All registrations: use all registered vehicles. "
                "Exclude defective vehicles: remove vehicles classified as defective. "
                "Full definition of defectiveness: see Glossary in the sidebar."
            ),
        )

    with filt_div:
        st.markdown(
            '<div class="ida-filter-divider" aria-hidden="true"></div>',
            unsafe_allow_html=True,
        )

    with filt_r:
        period_mode = st.radio(
            "Analysis period",
            options=[
                "Full period",
                "Latest year",
                "Custom period",
            ],
            index=0,
            horizontal=True,
            key="analysis_period_mode",
            help=(
                "Full period: analyse all available registration years. "
                "Latest year: analyse only the most recent year in the dataset. "
                "Custom period: select a specific year range."
            ),
        )

    exclude_defective = mode == "Exclude defective vehicles"
    count_col = active_count_col(exclude_defective)
    mode_tag = "clean" if exclude_defective else "all"

    if period_mode == "Full period":
        analysis_start_year = data_start_year
        analysis_end_year = data_end_year

    elif period_mode == "Latest year":
        analysis_start_year = data_end_year
        analysis_end_year = data_end_year

    else:
        analysis_start_year, analysis_end_year = st.slider(
            "Select years",
            min_value=data_start_year,
            max_value=data_end_year,
            value=(data_start_year, data_end_year),
            step=1,
            key="analysis_year_range",
        )

    # IMPORTANT:
    # This must be OUTSIDE the if / elif / else block
    analysis_df = df[
        df["year"].between(
            analysis_start_year,
            analysis_end_year,
        )
    ].copy()

    # Label for display
    if analysis_start_year == analysis_end_year:
        analysis_period_label = str(analysis_start_year)
    else:
        analysis_period_label = (
            f"{analysis_start_year}–{analysis_end_year}"
        )

    render_sidebar_settings_summary(mode, period_mode, analysis_period_label)

    with st.sidebar.expander("How we calculate popularity and the recommendation"):
        st.markdown(methodology_text(analysis_period_label, mode))

    with st.sidebar.expander("Glossary"):
        st.markdown(
            """
**Series**
Component type + manufacturer + plant (e.g. K1BE1-104-1041).

**Registration volume**
Number of registered vehicles containing that series.

**Defective vehicle**
A vehicle is classified as defective if the vehicle itself, an installed
component, or an installed single part is marked defective. A defective
single part also makes its component defective. Only defects occurring
after registration are considered. Pre-registration defects are treated
as production issues and ignored for this registration-based analysis.

**Defect-filtered registrations**
Registration counts after excluding defective vehicles
(see *Defective vehicle*).

**First / last observed registration**
First or last year a series appears in the data — not necessarily production start/end.

**Lifecycle check**
For each of the four recommended slots (engine, seats, gearbox, body), we check
whether at least one leading series from the selected analysis period still has
registrations in the latest year of the full dataset. If a leader is no longer
observed there, the recommendation may reflect a historically popular series
that is no longer present at the end of the data.

**Export recommendation**
Below the Recommended vehicle card you can download the current result:
- **Excel** — table of recommended slots (series, market share, analysis period,
  registration basis, vehicle registrations). Tied leaders appear as separate rows.
- **JPEG** — image of the Recommended vehicle card for slides or reports.
"""
        )

    overall = overall_counts(
        analysis_df,
        count_col,
    )

    overall_full_period = overall_counts(
        df,
        count_col,
    )

    series_kpis = build_series_kpis(
        df=analysis_df,
        count_col=count_col,

        # Important:
        # lifecycle always uses the complete dataset
        lifecycle_df=df,
    )

    # Executive summary

    engine_top = top_series_rows(series_kpis, "K1")
    seats_top = top_series_rows(series_kpis, "K2")
    gearbox_top = top_series_rows(series_kpis, "K3")
    body_top = top_series_rows(series_kpis, BODY_CATEGORIES)

    latest_year = int(series_kpis["latest_data_year"].max())

    # Each vehicle has exactly one engine.
    # Therefore the total K1 volume equals the number of vehicles
    # in the currently selected registration basis.
    vehicle_registrations = int(
        series_kpis.loc[
            series_kpis["category"] == "K1",
            "n_count",
        ].sum()
    )

    def category_share(rows: pd.DataFrame) -> float:
        if rows.empty:
            return 0.0

        return float(rows.iloc[0]["market_share"])

    engine_share = category_share(engine_top)
    seats_share = category_share(seats_top)
    gearbox_share = category_share(gearbox_top)

    body_pool = series_kpis[
        series_kpis["category"].isin(BODY_CATEGORIES)
    ]

    body_total = body_pool["n_count"].sum()

    if not body_top.empty and body_total > 0:
        body_share = (
            body_top.iloc[0]["n_count"]
            / body_total
        )
    else:
        body_share = 0.0

    st.subheader("Executive summary")

    render_recommendation_hero(
        analysis_period_label=analysis_period_label,
        registration_basis=mode,
        exclude_defective=exclude_defective,
        engine_top=engine_top,
        seats_top=seats_top,
        gearbox_top=gearbox_top,
        body_top=body_top,
        engine_share=engine_share,
        seats_share=seats_share,
        gearbox_share=gearbox_share,
        body_share=body_share,
        vehicle_registrations=vehicle_registrations,
    )

    engine_ranking = build_ranking(series_kpis, "K1")
    seats_ranking = build_ranking(series_kpis, "K2")
    gearbox_ranking = build_ranking(series_kpis, "K3")
    body_ranking = build_ranking(series_kpis, BODY_CATEGORIES)

    engine_top5 = top_five_ranking(engine_ranking)
    seats_top5 = top_five_ranking(seats_ranking)
    gearbox_top5 = top_five_ranking(gearbox_ranking)
    body_top5 = top_five_ranking(body_ranking)

    recommendation_slots = [
        engine_top,
        seats_top,
        gearbox_top,
        body_top,
    ]

    current_slots = sum(
        (
            not rows.empty
            and rows["observed_in_latest_year"].any()
        )
        for rows in recommendation_slots
    )

    if current_slots == 4:
        st.success(
            f"**Lifecycle check:** all four recommendation slots (K1, K2, K3, "
            f"body pool K4–K7) based on **{analysis_period_label}** have at least "
            f"one leading series still observed in {latest_year}. "
            "Details: see Glossary."
        )
    else:
        st.warning(
            f"**Lifecycle check:** only {current_slots} of four recommendation "
            f"slots (K1, K2, K3, body pool K4–K7) based on **{analysis_period_label}** "
            f"have a leading series still observed in {latest_year}. "
            "Historical popularity may include series no longer observed "
            "at the end of the dataset. "
            "Details: see Glossary.")

    tab_rec, tab_trend, tab_explore, tab_table = st.tabs(
        ["Recommendation", "Yearly trends", "Explore", "Full data"]
    )

    with tab_rec:
        st.subheader("Top component recommendations")
        st.caption(
            "This page shows the ranking detail behind the recommended vehicle: "
            "leaders and runners-up by registration volume for engine, seats, "
            "gearbox, and body. Use the category tabs for tables and KPIs; the "
            "charts below compare series within each pool."
        )

        rank_engine, rank_seats, rank_gearbox, rank_body = st.tabs(
            [
                "Engine · K1",
                "Seats · K2",
                "Gearbox · K3",
                "Body · K4–K7",
            ]
        )

        with rank_engine:
            stats = ranking_lead_stats(engine_ranking)

            top_rows = engine_ranking[
                engine_ranking["display_rank"] == 1
            ]

            m1, m2, m3 = st.columns(3)

            with m1:
                st.metric(
                    "Leader",
                    series_names(top_rows),
                )

            with m2:
                if stats["lead_pp"] is not None:
                    st.metric(
                        "Lead vs #2",
                        f"{stats['lead_pp'] * 100:.1f} pp",
                    )

            with m3:
                if not top_rows.empty:
                    st.metric(
                        "Leader market share",
                        f"{top_rows.iloc[0]['display_share']:.1%}",
                    )

            engine_display = engine_top5[
                [
                    "display_rank",
                    "series",
                    "label",
                    "n_count",
                    "display_share",
                    "affected_vehicle_rate",
                    "lifecycle",
                ]
            ].copy()

            engine_display.columns = [
                "Rank",
                "Series",
                "Type",
                "Registrations",
                "Market share",
                "Affected vehicle rate",
                "Lifecycle",
            ]

            engine_display["Market share"] = (
                engine_display["Market share"]
                .map(lambda x: f"{x:.1%}")
            )

            engine_display["Affected vehicle rate"] = (
                engine_display["Affected vehicle rate"]
                .map(lambda x: f"{x:.1%}")
            )

            st.dataframe(
                engine_display,
                width="stretch",
                hide_index=True,
            )

        with rank_seats:
            stats = ranking_lead_stats(seats_ranking)

            top_rows = seats_ranking[
                seats_ranking["display_rank"] == 1
            ]

            m1, m2, m3 = st.columns(3)

            with m1:
                st.metric(
                    "Leader",
                    series_names(top_rows),
                )

            with m2:
                if stats["lead_pp"] is not None:
                    st.metric(
                        "Lead vs #2",
                        f"{stats['lead_pp'] * 100:.1f} pp",
                    )

            with m3:
                if not top_rows.empty:
                    st.metric(
                        "Leader market share",
                        f"{top_rows.iloc[0]['display_share']:.1%}",
                    )

            seats_display = seats_top5[
                [
                    "display_rank",
                    "series",
                    "label",
                    "n_count",
                    "display_share",
                    "affected_vehicle_rate",
                    "lifecycle",
                ]
            ].copy()

            seats_display.columns = [
                "Rank",
                "Series",
                "Type",
                "Registrations",
                "Market share",
                "Affected vehicle rate",
                "Lifecycle",
            ]

            seats_display["Market share"] = (
                seats_display["Market share"]
                .map(lambda x: f"{x:.1%}")
            )

            seats_display["Affected vehicle rate"] = (
                seats_display["Affected vehicle rate"]
                .map(lambda x: f"{x:.1%}")
            )

            st.dataframe(
                seats_display,
                width="stretch",
                hide_index=True,
            )

        with rank_gearbox:
            stats = ranking_lead_stats(gearbox_ranking)

            top_rows = gearbox_ranking[
                gearbox_ranking["display_rank"] == 1
            ]

            m1, m2, m3 = st.columns(3)

            with m1:
                st.metric(
                    "Leader",
                    series_names(top_rows),
                )

            with m2:
                if stats["lead_pp"] is not None:
                    st.metric(
                        "Lead vs #2",
                        f"{stats['lead_pp'] * 100:.1f} pp",
                    )

            with m3:
                if not top_rows.empty:
                    st.metric(
                        "Leader market share",
                        f"{top_rows.iloc[0]['display_share']:.1%}",
                    )

            gearbox_display = gearbox_top5[
                [
                    "display_rank",
                    "series",
                    "label",
                    "n_count",
                    "display_share",
                    "affected_vehicle_rate",
                    "lifecycle",
                ]
            ].copy()

            gearbox_display.columns = [
                "Rank",
                "Series",
                "Type",
                "Registrations",
                "Market share",
                "Affected vehicle rate",
                "Lifecycle",
            ]

            gearbox_display["Market share"] = (
                gearbox_display["Market share"]
                .map(lambda x: f"{x:.1%}")
            )

            gearbox_display["Affected vehicle rate"] = (
                gearbox_display["Affected vehicle rate"]
                .map(lambda x: f"{x:.1%}")
            )

            st.dataframe(
                gearbox_display,
                width="stretch",
                hide_index=True,
            )

        with rank_body:
            stats = ranking_lead_stats(body_ranking)

            top_rows = body_ranking[
                body_ranking["display_rank"] == 1
            ]

            m1, m2, m3 = st.columns(3)

            with m1:
                st.metric(
                    "Leader",
                    series_names(top_rows),
                )

            with m2:
                if stats["lead_pp"] is not None:
                    st.metric(
                        "Lead vs #2",
                        f"{stats['lead_pp'] * 100:.1f} pp",
                    )

            with m3:
                if not top_rows.empty:
                    st.metric(
                        "Leader market share",
                        f"{top_rows.iloc[0]['display_share']:.1%}",
                    )

            body_display = body_top5[
                [
                    "display_rank",
                    "series",
                    "label",
                    "n_count",
                    "display_share",
                    "affected_vehicle_rate",
                    "lifecycle",
                ]
            ].copy()

            body_display.columns = [
                "Rank",
                "Series",
                "Type",
                "Registrations",
                "Market share",
                "Affected vehicle rate",
                "Lifecycle",
            ]

            body_display["Market share"] = (
                body_display["Market share"]
                .map(lambda x: f"{x:.1%}")
            )

            body_display["Affected vehicle rate"] = (
                body_display["Affected vehicle rate"]
                .map(lambda x: f"{x:.1%}")
            )

            st.dataframe(
                body_display,
                width="stretch",
                hide_index=True,
            )

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(
                plot_series_bars(overall, "K1"),
                width="stretch",
                key=f"rec_bars_k1_{mode_tag}",
            )
        with c2:
            st.plotly_chart(
                plot_series_bars(overall, "K2"),
                width="stretch",
                key=f"rec_bars_k2_{mode_tag}",
            )
        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(
                plot_series_bars(overall, "K3"),
                width="stretch",
                key=f"rec_bars_k3_{mode_tag}",
            )
        with c4:
            st.plotly_chart(
                plot_body_bars(overall),
                width="stretch",
                key=f"rec_bars_body_{mode_tag}",
            )

    with tab_trend:
        st.subheader("Trends and fashions by year")
        st.caption(
            "Trends use the **full registration period** (not the analysis-period "
            "filter above). A stable yearly winner suggests structural demand; a "
            "changing winner suggests fashion. Green ▲ = first observed registration; "
            "red × = last observed registration (not necessarily production dates)."
        )
        trend_metric = st.radio(
            "Display metric",
            options=[
                "Registration volume",
                "Category market share",
            ],
            index=0,
            horizontal=True,
            key="trend_metric",
            help=(
                "Registration volume shows absolute yearly registrations. "
                "Category market share shows each series' share of all registrations "
                "within the selected category and year."
            ),
        )
        cat = st.selectbox("Category", CATEGORIES, index=0, key="trend_category")
        st.plotly_chart(
            plot_trends(
                df,
                cat,
                count_col,
                trend_metric,
            ),
            width="stretch",
            key=f"trend_lines_{cat}_{mode_tag}_{trend_metric}",
        )
        if trend_metric == "Category market share":
            st.caption(
                "Market share is calculated within the selected category "
                "for each year. "
                "This makes relative shifts visible even when the overall registration "
                "volume changes.")
        if cat in BODY_CATEGORIES:
            st.plotly_chart(
                plot_body_bars(overall_full_period),
                width="stretch",
                key=f"trend_bars_body_{cat}_{mode_tag}",
            )
        else:
            st.plotly_chart(
                plot_series_bars(overall_full_period, cat),
                width="stretch",
                key=f"trend_bars_{cat}_{mode_tag}",
            )

    with tab_explore:
        st.subheader("Filter the registration counts")
        st.caption(
            "Explore the underlying registration data with your own filters. "
            "Choose years, OEMs, and categories to rebuild the bar chart and table. "
            "Counts follow the current Registration basis selected above "
            "(all registrations or exclude defective vehicles)."
        )
        years = sorted(df["year"].unique().tolist())
        y0, y1 = st.slider(
            "Years",
            min_value=min(years),
            max_value=max(years),
            value=(min(years), max(years)),
        )
        oems = st.multiselect(
            "OEM",
            sorted(df["oem"].unique()),
            default=sorted(df["oem"].unique()),
        )
        cats = st.multiselect("Categories", CATEGORIES, default=["K1", "K2", "K3"])
        filtered = df[
            df["year"].between(y0, y1)
            & df["oem"].isin(oems)
            & df["category"].isin(cats)
        ]
        agg = (
            filtered.groupby(
                [
                    "category",
                    "series",
                    "component_type",
                    "manufacturer",
                    "plant",
                    "label"],
                as_index=False,
            )[count_col] .sum() .rename(
                columns={
                    count_col: "n_count"}) .sort_values(
                        "n_count",
                ascending=False))
        registrations_label = (
            "Registrations (defect-filtered)"
            if exclude_defective
            else "Registrations"
        )
        fig = px.bar(
            agg,
            x="series",
            y="n_count",
            color="category",
            title="Filtered registrations by component series",
            labels={
                "series": "Component series",
                "n_count": registrations_label,
                "category": "Category",
            },
            color_discrete_map=CATEGORY_COLORS,
        )
        fig.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(
            style_fig(fig), width="stretch", key=f"explore_bars_{mode_tag}"
        )

        explore_display = agg.rename(
            columns={
                "category": "Category",
                "series": "Series",
                "component_type": "Component type",
                "manufacturer": "Manufacturer",
                "plant": "Plant",
                "label": "Description",
                "n_count": registrations_label,
            }
        )
        st.dataframe(
            explore_display,
            width="stretch",
            hide_index=True,
            key=f"explore_table_{mode_tag}",
        )

    with tab_table:
        st.subheader("Final dataset (all rows)")
        st.caption(
            "Audit view of the complete final dataset used by this app "
            f"(`{DATA_PATH}` · {len(df):,} rows). "
            "Every chart and recommendation above is built only from these rows. "
            "**Registrations** = all registered vehicles; "
            "**Registrations (defect-filtered)** = excluding defective vehicles "
            "(after registration — see Glossary)."
        )

        full_display = df.rename(
            columns={
                col: FINAL_DATA_COLUMN_LABELS.get(col, col)
                for col in df.columns
            }
        )

        st.download_button(
            label="Export Excel",
            data=dataframe_to_excel_bytes(full_display, sheet_name="Final data"),
            file_name="SoSe26_Case_Study_finalData_Group_38.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download the full final dataset with readable column names as Excel.",
            key=f"export_full_data_{mode_tag}",
            type="primary",
            icon=":material/table:",
            width="stretch",
        )

        st.dataframe(
            full_display,
            width="stretch",
            hide_index=True,
            key=f"full_table_{mode_tag}",
        )


if __name__ == "__main__":
    main()
