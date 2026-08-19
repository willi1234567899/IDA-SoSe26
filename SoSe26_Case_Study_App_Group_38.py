from __future__ import annotations

import base64
import warnings
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "Data" / "SoSe26_Case_Study_finalData_Group_38.csv"
LOGO_PATH = ROOT / "www" / "img" / "logo.svg"
CSS_PATH = ROOT / "www" / "style.css"
FONT_REGULAR = ROOT / "www" / "fonts" / "source-sans-3-latin-400-normal.woff2"
FONT_SEMIBOLD = ROOT / "www" / "fonts" / "source-sans-3-latin-600-normal.woff2"

PLOTLY_BLUES = ["#2F5F7A", "#5BA4CF", "#8FCBE8", "#C5E4F3"]
CATEGORIES = ["K1", "K2", "K3", "K4", "K5", "K6", "K7"]
BODY_CATEGORIES = ["K4", "K5", "K6", "K7"]
REQUIRED_COLS = [
    "year",
    "oem",
    "vehicle_type",
    "category",
    "component_type",
    "n_registrations",
    "label",
]
EMPTY_WINNERS = pd.DataFrame(
    columns=["category", "component_type", "label", "n_registrations"]
)
EMPTY_FINAL = pd.DataFrame(columns=REQUIRED_COLS)


def _font_face(path: Path, weight: int) -> str:
    if not path.exists():
        return ""
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return (
        "@font-face {"
        'font-family: "Source Sans Pro";'
        "font-style: normal;"
        f"font-weight: {weight};"
        f"src: url(data:font/woff2;base64,{payload}) format('woff2');"
        "}"
    )


def apply_design() -> None:
    font_css = _font_face(FONT_REGULAR, 400) + _font_face(FONT_SEMIBOLD, 600)
    extra = CSS_PATH.read_text(encoding="utf-8") if CSS_PATH.is_file() else ""
    st.markdown(
        f"<style>{font_css}{extra}</style>",
        unsafe_allow_html=True,
    )


def load_final_data() -> pd.DataFrame | None:
    if not DATA_PATH.is_file():
        return None
    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    df.columns = df.columns.astype(str).str.strip()
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            "Final CSV is missing required columns: " + ", ".join(missing)
        )
    out = df.copy()
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out["n_registrations"] = pd.to_numeric(out["n_registrations"], errors="coerce")
    for col in ("oem", "vehicle_type", "category", "component_type", "label"):
        out[col] = out[col].astype("string").str.strip()
    out = out.dropna(subset=["year", "n_registrations", "category", "component_type"])
    if out.empty:
        raise ValueError("Final CSV has no usable rows after parsing.")
    out["year"] = out["year"].astype(int)
    out["n_registrations"] = out["n_registrations"].astype(int)
    return out


def overall_counts(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["category", "component_type", "label"], as_index=False)[
            "n_registrations"
        ]
        .sum()
        .sort_values(["category", "n_registrations"], ascending=[True, False])
    )


def winners_by_category(overall: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cat in CATEGORIES:
        sub = overall[overall["category"] == cat]
        if sub.empty:
            continue
        top_n = sub["n_registrations"].max()
        rows.append(sub[sub["n_registrations"] == top_n])
    if not rows:
        return EMPTY_WINNERS.copy()
    return pd.concat(rows, ignore_index=True)


def style_fig(fig):
    fig.update_layout(
        font_family="Source Sans Pro",
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend_title_text="",
        font_color="#1f2d3a",
        title_font_color="#1f2d3a",
    )
    fig.update_xaxes(title_font_color="#1f2d3a", tickfont_color="#1f2d3a", gridcolor="#eeeeee")
    fig.update_yaxes(title_font_color="#1f2d3a", tickfont_color="#1f2d3a", gridcolor="#eeeeee")
    return fig


def plot_category_bars(overall: pd.DataFrame, category: str):
    sub = overall[overall["category"] == category]
    fig = px.bar(
        sub,
        x="component_type",
        y="n_registrations",
        color="label",
        title=f"Registered vehicles by component type - {category}",
        labels={
            "component_type": "Component type",
            "n_registrations": "Registered vehicles",
            "label": "Description",
        },
        color_discrete_sequence=PLOTLY_BLUES,
    )
    return style_fig(fig)


def plot_body_bars(overall: pd.DataFrame):
    body = overall[overall["category"].isin(BODY_CATEGORIES)]
    fig = px.bar(
        body,
        x="component_type",
        y="n_registrations",
        color="label",
        title="Registered vehicles by body type (K4–K7)",
        labels={
            "component_type": "Body type",
            "n_registrations": "Registered vehicles",
            "label": "Description",
        },
        color_discrete_sequence=PLOTLY_BLUES,
    )
    return style_fig(fig)


def plot_trends(df: pd.DataFrame, category: str):
    yearly = (
        df[df["category"] == category]
        .groupby(["year", "component_type", "label"], as_index=False)["n_registrations"]
        .sum()
    )
    fig = px.line(
        yearly,
        x="year",
        y="n_registrations",
        color="component_type",
        markers=True,
        title=f"Yearly registrations - {category}",
        labels={
            "year": "Registration year",
            "n_registrations": "Registered vehicles",
            "component_type": "Component type",
        },
        color_discrete_sequence=PLOTLY_BLUES,
    )
    fig.update_layout(xaxis=dict(dtick=1))
    return style_fig(fig)


def recommendation_frame(df: pd.DataFrame | None) -> pd.DataFrame:
    rows = []
    winners = EMPTY_WINNERS
    if df is not None:
        winners = winners_by_category(overall_counts(df))
    for cat in CATEGORIES:
        sub = winners[winners["category"] == cat] if len(winners) else winners
        if sub is None or sub.empty:
            rows.append(
                {
                    "Category": cat,
                    "Component type": "-",
                    "Description": "-",
                    "Registered vehicles": "-",
                }
            )
            continue
        rows.append(
            {
                "Category": cat,
                "Component type": " / ".join(sub["component_type"].tolist()),
                "Description": " / ".join(sub["label"].astype(str).tolist()),
                "Registered vehicles": f"{int(sub['n_registrations'].iloc[0]):,}",
            }
        )
    return pd.DataFrame(rows)


def render_header() -> None:
    header_l, header_r = st.columns([1.1, 4.9])
    with header_l:
        if LOGO_PATH.is_file():
            svg = LOGO_PATH.read_text(encoding="utf-8")
            st.markdown(f'<div class="ida-logo">{svg}</div>', unsafe_allow_html=True)
    with header_r:
        st.markdown(
            """
            <div class="ida-hero">
              <h1>Most popular vehicle</h1>
              <p>Component recommendation from KBA registrations.
              Counts are by <b>component type</b> (e.g. K1BE1), not plant or serial number.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def tab_recommendation(df: pd.DataFrame | None) -> None:
    st.subheader("Recommended component types (K1-K7)")
    st.caption(
        "Winner in each category = type with the most registered vehicles "
        "over the full period. Equal counts are shown as a joint win."
    )
    rec = recommendation_frame(df)
    st.dataframe(rec, use_container_width=True, hide_index=True, height=308)

    if df is None:
        return

    overall = overall_counts(df)
    winners = winners_by_category(overall)
    body = overall[overall["category"].isin(BODY_CATEGORIES)]
    if body.empty or winners.empty:
        return
    best_body = body.loc[body["n_registrations"].idxmax()]
    k1 = winners[winners["category"] == "K1"]
    k2 = winners[winners["category"] == "K2"]
    k3 = winners[winners["category"] == "K3"]
    if k1.empty or k2.empty or k3.empty:
        return
    k2 = k2.iloc[0]
    k3 = k3.iloc[0]
    k1_txt = " or ".join(k1["component_type"].tolist())
    st.markdown("#### One car to build")
    st.write(
        f"**Body {best_body['component_type']}** ({best_body['label']}) is the "
        f"most registered platform. A feasible specification is: "
        f"**{k1_txt}** engine, **{k2['component_type']}** seats "
        f"({k2['label']}), **{k3['component_type']}** gearbox "
        f"({k3['label']}), and **{best_body['component_type']}** body. "
        "K4-K7 cannot be combined on one vehicle."
    )
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_category_bars(overall, "K1"), use_container_width=True)
    with c2:
        st.plotly_chart(plot_category_bars(overall, "K2"), use_container_width=True)
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(plot_category_bars(overall, "K3"), use_container_width=True)
    with c4:
        st.plotly_chart(plot_body_bars(overall), use_container_width=True)


def tab_trends(df: pd.DataFrame | None) -> None:
    st.subheader("Trends and fashions by year")
    st.caption(
        "A stable winner every year is structural demand. "
        "A changing winner would be a fashion."
    )
    if df is None:
        st.selectbox("Category", CATEGORIES, index=0, disabled=True)
        return
    cat = st.selectbox("Category", CATEGORIES, index=0)
    overall = overall_counts(df)
    st.plotly_chart(plot_trends(df, cat), use_container_width=True)
    if cat in BODY_CATEGORIES:
        st.plotly_chart(plot_body_bars(overall), use_container_width=True)
    else:
        st.plotly_chart(plot_category_bars(overall, cat), use_container_width=True)


def tab_explore(df: pd.DataFrame | None) -> None:
    st.subheader("Filter the registration counts")
    if df is None:
        st.slider("Years", 0, 1, (0, 1), disabled=True)
        st.multiselect("OEM", [], disabled=True)
        st.multiselect("Categories", CATEGORIES, default=["K1", "K2", "K3"], disabled=True)
        return
    years = sorted(int(y) for y in df["year"].unique())
    year_min, year_max = years[0], years[-1]
    if year_min == year_max:
        st.caption(f"Only one year in the data: **{year_min}**")
        y0, y1 = year_min, year_max
    else:
        y0, y1 = st.slider(
            "Years",
            min_value=year_min,
            max_value=year_max,
            value=(year_min, year_max),
        )
    oems = st.multiselect(
        "OEM",
        sorted(df["oem"].dropna().unique().tolist()),
        default=sorted(df["oem"].dropna().unique().tolist()),
    )
    cats = st.multiselect("Categories", CATEGORIES, default=["K1", "K2", "K3"])
    filtered = df[
        df["year"].between(y0, y1)
        & df["oem"].isin(oems)
        & df["category"].isin(cats)
    ]
    agg = (
        filtered.groupby(["category", "component_type", "label"], as_index=False)[
            "n_registrations"
        ]
        .sum()
        .sort_values("n_registrations", ascending=False)
    )
    fig = px.bar(
        agg,
        x="component_type",
        y="n_registrations",
        color="category",
        title="Filtered registrations by component type",
        labels={
            "component_type": "Component type",
            "n_registrations": "Registered vehicles",
            "category": "Category",
        },
        color_discrete_sequence=PLOTLY_BLUES,
    )
    st.plotly_chart(style_fig(fig), use_container_width=True)
    st.dataframe(agg, use_container_width=True, hide_index=True)


def tab_table(df: pd.DataFrame | None) -> None:
    st.subheader("Final dataset (all rows)")
    if df is None:
        st.caption(f"Source: `{DATA_PATH.relative_to(ROOT).as_posix()}`")
        blank = {c: "-" for c in REQUIRED_COLS}
        st.dataframe(pd.DataFrame([blank]), use_container_width=True, hide_index=True)
        return
    st.caption(
        f"Source: `{DATA_PATH.relative_to(ROOT).as_posix()}` · {len(df):,} rows. "
        "This is the only file the app reads."
    )
    st.dataframe(df, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(
        page_title="Most popular vehicle | IDA Group 38",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_design()
    render_header()

    st.sidebar.markdown("**Data source**")
    st.sidebar.caption("Data/SoSe26_Case_Study_finalData_Group_38.csv")

    df: pd.DataFrame | None = None
    try:
        df = load_final_data()
    except Exception as exc:
        st.error(f"Could not load final dataset: {exc}")
        df = None
    if df is not None:
        st.sidebar.write(f"{len(df):,} rows")
        st.sidebar.write(f"Years {int(df['year'].min())}–{int(df['year'].max())}")

    tab_rec, tab_trend, tab_explore_ui, tab_full = st.tabs(
        ["Recommendation", "Yearly trends", "Explore", "Full data"]
    )
    with tab_rec:
        tab_recommendation(df)
    with tab_trend:
        tab_trends(df)
    with tab_explore_ui:
        tab_explore(df)
    with tab_full:
        tab_table(df)


if __name__ == "__main__":
    main()
