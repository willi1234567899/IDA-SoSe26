"""
SoSe26 Case Study App – Group 38

Run from this folder (Anaconda / project env):

    streamlit run SoSe26_Case_Study_App_Group_38.py

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


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error(
            f"Final dataset not found at `{DATA_PATH}`. "
            "Run the case-study notebook first so this CSV is created."
        )
        st.stop()
    df = pd.read_csv(DATA_PATH)
    df["year"] = df["year"].astype(int)
    return df


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
    return pd.concat(rows, ignore_index=True)


def plot_category_bars(overall: pd.DataFrame, category: str, title: Optional[str] = None):
    sub = overall[overall["category"] == category]
    fig = px.bar(
        sub,
        x="component_type",
        y="n_registrations",
        color="label",
        title=title or f"Registered vehicles by component type — {category}",
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
        title=f"Yearly registrations — {category}",
        labels={
            "year": "Registration year",
            "n_registrations": "Registered vehicles",
            "component_type": "Component type",
        },
        color_discrete_sequence=PLOTLY_BLUES,
    )
    fig.update_layout(xaxis=dict(dtick=1))
    return style_fig(fig)


def main() -> None:
    st.set_page_config(
        page_title="Most popular vehicle | IDA Group 38",
        layout="wide",
    )
    apply_design()
    df = load_data()
    overall = overall_counts(df)
    winners = winners_by_category(overall)

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
              <h1>Most popular vehicle — component recommendation</h1>
              <p>Management briefing based on KBA registrations 2009–2016.
              Popularity is counted at <b>component type</b> (e.g. K1BE1),
              not at plant or serial number.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    tab_rec, tab_trend, tab_explore, tab_table = st.tabs(
        ["Recommendation", "Yearly trends", "Explore", "Full data"]
    )

    with tab_rec:
        st.subheader("Recommended component types (K1–K7)")
        st.caption(
            "Winner in each category = type with the most registered vehicles "
            "over the full period. Equal counts are shown as a joint win."
        )
        rec_cols = st.columns(7)
        for i, cat in enumerate(CATEGORIES):
            sub = winners[winners["category"] == cat]
            types = " / ".join(sub["component_type"].tolist())
            n = int(sub["n_registrations"].iloc[0])
            rec_cols[i].metric(cat, types, f"{n:,} vehicles")

        st.dataframe(winners, use_container_width=True, hide_index=True)

        body = overall[overall["category"].isin(BODY_CATEGORIES)]
        best_body = body.loc[body["n_registrations"].idxmax()]
        k1 = winners[winners["category"] == "K1"]
        k2 = winners[winners["category"] == "K2"].iloc[0]
        k3 = winners[winners["category"] == "K3"].iloc[0]
        k1_txt = " or ".join(k1["component_type"].tolist())

        st.markdown("#### One car to build")
        st.info(
            f"**Body {best_body['component_type']}** ({best_body['label']}) is the "
            f"most registered platform. A feasible specification is: "
            f"**{k1_txt}** engine, **{k2['component_type']}** seats "
            f"({k2['label']}), **{k3['component_type']}** gearbox "
            f"({k3['label']}), and **K4** body. "
            "K4–K7 cannot be combined on one vehicle."
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

    with tab_trend:
        st.subheader("Trends and fashions by year")
        st.caption(
            "A stable winner every year is structural demand. "
            "A changing winner would be a fashion."
        )
        cat = st.selectbox("Category", CATEGORIES, index=0)
        st.plotly_chart(plot_trends(df, cat), use_container_width=True)
        if cat in BODY_CATEGORIES:
            st.plotly_chart(plot_body_bars(overall), use_container_width=True)
        else:
            st.plotly_chart(plot_category_bars(overall, cat), use_container_width=True)

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

    with tab_table:
        st.subheader("Final dataset (all rows)")
        st.caption(
            f"Source: `{DATA_PATH}` · {len(df):,} rows. "
            "This is the only file the app reads."
        )
        st.dataframe(df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
