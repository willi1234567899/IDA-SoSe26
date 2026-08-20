"""
SoSe26 Case Study App – Group 38

Run from this folder (Anaconda / project env):

    python3 -m streamlit run SoSe26_Case_Study_App_Group_38.py

The app reads only:
    Data/SoSe26_Case_Study_finalData_Group_38.csv
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = Path("Data") / "SoSe26_Case_Study_finalData_Group_38.csv"
LOGO_PATH = Path("www") / "img" / "logo.svg"
CSS_PATH = Path("www") / "style.css"
FONT_REGULAR = Path("www") / "fonts" / "source-sans-3-latin-400-normal.woff2"
FONT_SEMIBOLD = Path("www") / "fonts" / "source-sans-3-latin-600-normal.woff2"

PLOTLY_BLUES = ["#2F5F7A", "#5BA4CF", "#8FCBE8", "#C5E4F3"]
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


def apply_design() -> None:
    font_css = _font_face(FONT_REGULAR, 400) + _font_face(FONT_SEMIBOLD, 600)
    extra = CSS_PATH.read_text(encoding="utf-8") if CSS_PATH.exists() else ""
    st.markdown(
        f"""
        <style>
        {font_css}
        html, body, [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"], .stMarkdown, .stMetric {{
            font-family: "Source Sans Pro", "Source Sans 3", Helvetica, Arial, sans-serif;
        }}
        [data-testid="stHeader"] {{ background: #E8F4FA; }}
        [data-testid="stSidebar"] {{ background: #E8F4FA; }}
        div[data-testid="stMetric"] {{
            background: #E8F4FA;
            border-left: 4px solid #5BA4CF;
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


def active_count_col(consider_defects: bool) -> str:
    return COUNT_CLEAN if consider_defects else COUNT_ALL


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
    sub = overall[overall["category"] == category].sort_values("n_count", ascending=False)
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
        color_discrete_sequence=PLOTLY_BLUES,
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
        color_discrete_sequence=PLOTLY_BLUES,
    )
    fig.update_layout(xaxis_tickangle=-35)
    return style_fig(fig)


def mark_series_span(fig, yearly: pd.DataFrame):
    """Mark first/last registration year when they fall inside the data span edges."""
    first = yearly.loc[yearly.groupby("series")["year"].idxmin()]
    started = first[first["year"] > DATA_START_YEAR]
    if not started.empty:
        fig.add_scatter(
            x=started["year"],
            y=started["n_count"],
            mode="markers",
            marker=SERIES_START_MARKER,
            name="series start (first registration after 2009)",
            legendgroup="series_start",
            hovertemplate=(
                "series start<br>year=%{x}<br>registrations=%{y:,}<extra></extra>"
            ),
        )

    last = yearly.loc[yearly.groupby("series")["year"].idxmax()]
    ended = last[last["year"] < DATA_END_YEAR]
    if not ended.empty:
        fig.add_scatter(
            x=ended["year"],
            y=ended["n_count"],
            mode="markers",
            marker=SERIES_END_MARKER,
            name="series end (last registration before 2016)",
            legendgroup="series_end",
            hovertemplate=(
                "series end<br>year=%{x}<br>registrations=%{y:,}<extra></extra>"
            ),
        )
    return fig


def plot_trends(df: pd.DataFrame, category: str, count_col: str):
    yearly = (
        df[df["category"] == category]
        .groupby(["year", "series"], as_index=False)[count_col]
        .sum()
        .rename(columns={count_col: "n_count"})
    )
    fig = px.line(
        yearly,
        x="year",
        y="n_count",
        color="series",
        markers=True,
        title=f"Yearly registrations - {category}",
        labels={
            "year": "Registration year",
            "n_count": "Registered vehicles",
            "series": "Component series",
        },
        color_discrete_sequence=PLOTLY_BLUES,
    )
    fig.update_layout(xaxis=dict(dtick=1))
    return style_fig(mark_series_span(fig, yearly))


def main() -> None:
    st.set_page_config(
        page_title="Most popular vehicle | IDA Group 38",
        layout="wide",
    )
    apply_design()
    df = get_data()

    header_l, header_r = st.columns([1, 5])
    with header_l:
        if LOGO_PATH.exists():
            svg = LOGO_PATH.read_text(encoding="utf-8")
            st.markdown(
                f'<div style="max-width:180px">{svg}</div>',
                unsafe_allow_html=True,
            )
    with header_r:
        st.markdown(
            """
            <div class="ida-hero">
              <h1>Most popular vehicle - component recommendation</h1>
              <p>Management briefing based on KBA registrations 2009-2016.
              Popularity is counted at <b>series</b> level
              (type + manufacturer + plant), e.g. K1BE1-104-1041.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    mode_col, total_col = st.columns([3, 1])
    with mode_col:
        mode = st.radio(
            "Analysis mode",
            options=["Without defects", "With defects"],
            index=0,
            horizontal=True,
            key="defect_mode",
            help=(
                "With defects: exclude vehicles marked defective themselves, or with a "
                "defective installed component or part (parts make their component "
                "defective too). Only defects after registration count."
            ),
        )
    consider_defects = mode.startswith("With")
    count_col = active_count_col(consider_defects)
    mode_tag = "clean" if consider_defects else "all"
    with total_col:
        st.metric(
            "Total (active mode)",
            f"{int(df[count_col].sum()):,}",
            help=f"Sum of `{count_col}` over the final table.",
        )

    if consider_defects:
        st.info(
            "Mode: **with defects** — ranking uses registrations of vehicles "
            "that are not defective (after-registration defects only)."
        )
    else:
        st.caption("Mode: **without defects** — all KBA registrations.")

    st.sidebar.header("Defectiveness rule")
    st.sidebar.write(f"**Active:** {mode}")
    st.sidebar.caption(
        "A vehicle is defective if the vehicle itself, an installed component, "
        "or an installed single part is marked defective. A defective part also "
        "makes its component defective. Only defects after registration are used."
    )

    overall = overall_counts(df, count_col)
    winners = winners_by_category(overall)

    tab_rec, tab_trend, tab_explore, tab_table = st.tabs(
        ["Recommendation", "Yearly trends", "Explore", "Full data"]
    )

    with tab_rec:
        st.subheader("Recommended component series (K1-K7)")
        st.caption(
            "Winner in each category = series with the most registered vehicles "
            "over the full period. Equal counts are shown as a joint win."
        )
        rec_cols = st.columns(7)
        for i, cat in enumerate(CATEGORIES):
            sub = winners[winners["category"] == cat]
            series_txt = " / ".join(sub["series"].tolist())
            n = int(sub["n_count"].iloc[0])
            rec_cols[i].metric(cat, series_txt, f"{n:,} vehicles")

        st.dataframe(
            winners[
                [
                    "category",
                    "series",
                    "component_type",
                    "manufacturer",
                    "plant",
                    "label",
                    "n_count",
                ]
            ].rename(columns={"n_count": "n_registrations"}),
            width="stretch",
            hide_index=True,
            key=f"rec_winners_table_{mode_tag}",
        )

        body = overall[overall["category"].isin(BODY_CATEGORIES)]
        best_body = body.loc[body["n_count"].idxmax()]
        k1 = winners[winners["category"] == "K1"]
        k2 = winners[winners["category"] == "K2"]
        k3 = winners[winners["category"] == "K3"]
        k1_txt = " or ".join(k1["series"].tolist())
        k2_txt = " or ".join(k2["series"].tolist())
        k3_txt = " or ".join(k3["series"].tolist())

        st.markdown("#### One car to build")
        st.info(
            f"**Body {best_body['series']}** ({best_body['label']}) is the "
            f"most registered platform. A feasible specification is: "
            f"engine **{k1_txt}**, seats **{k2_txt}**, "
            f"gearbox **{k3_txt}**, body **{best_body['series']}**. "
            "K4-K7 cannot be combined on one vehicle."
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
            "A stable winner every year is structural demand. "
            "A changing winner would be a fashion. "
            "A green ▲ marks first registration after 2009 (series start); "
            "a red × marks last registration before 2016 (series end). "
            "Both are proxies; the data has no production start/stop flag."
        )
        cat = st.selectbox("Category", CATEGORIES, index=0, key="trend_category")
        st.plotly_chart(
            plot_trends(df, cat, count_col),
            width="stretch",
            key=f"trend_lines_{cat}_{mode_tag}",
        )
        if cat in BODY_CATEGORIES:
            st.plotly_chart(
                plot_body_bars(overall),
                width="stretch",
                key=f"trend_bars_body_{cat}_{mode_tag}",
            )
        else:
            st.plotly_chart(
                plot_series_bars(overall, cat),
                width="stretch",
                key=f"trend_bars_{cat}_{mode_tag}",
            )

    with tab_explore:
        st.subheader("Filter the registration counts")
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
                ["category", "series", "component_type", "manufacturer", "plant", "label"],
                as_index=False,
            )[count_col]
            .sum()
            .rename(columns={count_col: "n_count"})
            .sort_values("n_count", ascending=False)
        )
        fig = px.bar(
            agg,
            x="series",
            y="n_count",
            color="category",
            title="Filtered registrations by component series",
            labels={
                "series": "Component series",
                "n_count": "Registered vehicles",
                "category": "Category",
            },
            color_discrete_sequence=PLOTLY_BLUES,
        )
        fig.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(
            style_fig(fig), width="stretch", key=f"explore_bars_{mode_tag}"
        )
        st.dataframe(
            agg.rename(columns={"n_count": "n_registrations"}),
            width="stretch",
            hide_index=True,
            key=f"explore_table_{mode_tag}",
        )

    with tab_table:
        st.subheader("Final dataset (all rows)")
        st.caption(
            f"Source: `{DATA_PATH}` · {len(df):,} rows. "
            "This is the only file the app reads. "
            "`n_registrations` = all vehicles; "
            "`n_registrations_clean` = excluding defective vehicles "
            "(after registration)."
        )
        st.dataframe(
            df, width="stretch", hide_index=True, key=f"full_table_{mode_tag}"
        )


if __name__ == "__main__":
    main()
