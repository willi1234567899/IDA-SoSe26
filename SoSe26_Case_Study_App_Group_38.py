from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "Data" / "SoSe26_Case_Study_finalData_Group_38.csv"
CSS_PATH = ROOT / "www" / "styles.css"
LOGO_PATH = ROOT / "www" / "logo.svg"

K_COLS = [f"K{i}" for i in range(1, 8)]
REQUIRED_COLS = ["year", *K_COLS]
BLUE = "#7eb6d4"
BLUE_DARK = "#3d7ea3"

EMPTY_RECOMMENDATION = pd.DataFrame(
    {
        "Category": K_COLS,
        "Leading component": ["—"] * 7,
        "Registrations": ["—"] * 7,
        "Share (%)": ["—"] * 7,
    }
)
EMPTY_YEARLY_LEADERS = pd.DataFrame(
    columns=["Year", "Leading component", "Registrations"]
)
EMPTY_FINAL_DATA = pd.DataFrame(
    columns=["year", *K_COLS, "registrations", "ort", "plz", "lat", "lon"]
)

PLOTLY_LAYOUT = dict(
    font=dict(family="Source Sans 3, Source Sans Pro, sans-serif", size=13, color="#1a1a1a"),
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    colorway=[BLUE_DARK, BLUE, "#a8d0e4", "#5a9fbf", "#c5e2ef"],
    margin=dict(l=64, r=24, t=56, b=48),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color="#1a1a1a")),
    title=dict(font=dict(size=15, color="#1a1a1a")),
    xaxis=dict(
        title_font=dict(color="#1a1a1a"),
        tickfont=dict(color="#1a1a1a"),
        gridcolor="#eeeeee",
        zeroline=False,
    ),
    yaxis=dict(
        title_font=dict(color="#1a1a1a"),
        tickfont=dict(color="#1a1a1a"),
        gridcolor="#eeeeee",
        zeroline=False,
        automargin=True,
    ),
)


def inject_styles() -> None:
    if CSS_PATH.is_file():
        css = CSS_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_final_data(path_str: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path_str, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path_str, encoding="utf-8-sig")

    df.columns = df.columns.astype(str).str.strip()
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(
            "Final CSV is missing required columns: "
            + ", ".join(missing)
            + ". See doc/final-data-contract.md."
        )

    out = df.copy()
    out["year"] = pd.to_numeric(out["year"], errors="coerce")

    for col in K_COLS:
        out[col] = (
            out[col]
            .astype("string")
            .str.strip()
            .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "<NA>": pd.NA})
        )

    if "registrations" in out.columns:
        out["registrations"] = (
            pd.to_numeric(out["registrations"], errors="coerce").fillna(1).clip(lower=1)
        )
    else:
        out["registrations"] = 1.0
    out["registrations"] = out["registrations"].astype(float)

    if "ort" in out.columns:
        out["ort"] = (
            out["ort"]
            .astype("string")
            .str.strip()
            .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
        )

    for geo in ("lat", "lon"):
        if geo in out.columns:
            out[geo] = pd.to_numeric(out[geo], errors="coerce")

    out = out.dropna(subset=["year"])
    if out.empty:
        raise ValueError(
            "Final CSV has no usable rows after parsing `year`. "
            "Check that year values are numeric."
        )

    out["year"] = out["year"].astype(int)
    return out


def weighted_mode(series: pd.Series, weights: pd.Series) -> tuple[str, float]:
    tmp = pd.DataFrame({"v": series, "w": weights}).dropna(subset=["v"])
    if tmp.empty:
        return "—", 0.0
    ranked = (
        tmp.groupby("v", as_index=False)["w"]
        .sum()
        .sort_values(["w", "v"], ascending=[False, True])
    )
    top = ranked.iloc[0]
    return str(top["v"]), float(top["w"])


def recommend_vehicle(df: pd.DataFrame) -> pd.DataFrame:
    total = float(df["registrations"].sum())
    rows = []
    for col in K_COLS:
        value, weight = weighted_mode(df[col], df["registrations"])
        share = (weight / total * 100.0) if total > 0 else 0.0
        rows.append(
            {
                "category": col,
                "component": value,
                "registrations": int(weight),
                "share_pct": round(share, 1),
            }
        )
    return pd.DataFrame(rows)


def count_exact_configuration(df: pd.DataFrame, rec: pd.DataFrame) -> int:
    mask = pd.Series(True, index=df.index)
    for row in rec.itertuples():
        if row.component == "—":
            return 0
        mask &= df[row.category] == row.component
    return int(df.loc[mask, "registrations"].sum())


def category_year_counts(df: pd.DataFrame, category: str) -> pd.DataFrame:
    tmp = df.dropna(subset=[category])
    if tmp.empty:
        return pd.DataFrame(columns=["year", "component", "count"])
    return (
        tmp.groupby(["year", category], as_index=False)["registrations"]
        .sum()
        .rename(columns={category: "component", "registrations": "count"})
    )


def yearly_leaders(df: pd.DataFrame, category: str) -> pd.DataFrame:
    counts = category_year_counts(df, category)
    if counts.empty:
        return pd.DataFrame(columns=["year", "component", "count"])
    idx = counts.groupby("year")["count"].idxmax()
    return counts.loc[idx].sort_values("year").reset_index(drop=True)


def render_header() -> None:
    c1, c2 = st.columns([0.55, 5.45])
    with c1:
        if LOGO_PATH.is_file():
            st.image(str(LOGO_PATH), width=40)
    with c2:
        st.markdown(
            """
            <div class="site-header" style="border:0;margin:0;padding:0.15rem 0 0 0;">
              <div>
                <h1>Most popular vehicle</h1>
                <p>Group 38 · Case Study result for management (components K1–K7)</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        '<hr style="border:none;border-top:2px solid #7eb6d4;margin:0.35rem 0 1.25rem 0;" />',
        unsafe_allow_html=True,
    )


def show_chart(fig) -> None:
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def empty_bar_chart() -> None:
    fig = px.bar(
        pd.DataFrame({"category": K_COLS, "registrations": [None] * 7}),
        x="category",
        y="registrations",
        labels={"registrations": "Registrations", "category": "Category"},
        title="Leading component per category (K1–K7)",
        category_orders={"category": K_COLS},
    )
    fig.update_traces(marker_color=BLUE_DARK)
    fig.update_yaxes(range=[0, 1], automargin=True)
    fig.update_layout(margin=dict(l=64, r=24, t=64, b=48), height=380)
    show_chart(fig)


def empty_line_chart() -> None:
    fig = px.line(
        pd.DataFrame({"year": pd.Series(dtype=int), "count": pd.Series(dtype=float), "component": pd.Series(dtype=str)}),
        x="year",
        y="count",
        color="component",
        labels={"count": "Registrations", "year": "Year", "component": "Component"},
        title="Yearly registrations by component",
    )
    fig.update_layout(height=380)
    show_chart(fig)


def tab_result(df: pd.DataFrame | None) -> None:
    st.subheader("4.1 Overall recommendation")
    st.write(
        "Case-study question: Which vehicle configuration is most popular? "
        "For each category **K1–K7**, take the component with the "
        "**highest registration weight** in the final dataset. "
        "Those seven leaders form the recommended vehicle."
    )

    if df is None:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Registrations analysed", "—")
        m2.metric("Period", "—")
        m3.metric("Exact config matches", "—")
        m4.metric("Registration places", "—")

        st.write("**Recommended most popular vehicle (K1–K7 leaders)**")
        st.dataframe(EMPTY_RECOMMENDATION, use_container_width=True, hide_index=True)
        empty_bar_chart()
        return

    rec = recommend_vehicle(df)
    total = int(df["registrations"].sum())
    years = f"{int(df['year'].min())}–{int(df['year'].max())}"
    exact = count_exact_configuration(df, rec)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Registrations analysed", f"{total:,}")
    m2.metric("Period", years)
    m3.metric("Exact config matches", f"{exact:,}")
    if "ort" in df.columns:
        m4.metric("Registration places", int(df["ort"].nunique(dropna=True)))
    else:
        m4.metric("Registration places", "—")

    st.write("**Recommended most popular vehicle (K1–K7 leaders)**")
    st.caption("Identical decision rule to Case Study notebook §4.1.")
    st.dataframe(
        rec.rename(
            columns={
                "category": "Category",
                "component": "Leading component",
                "registrations": "Registrations",
                "share_pct": "Share (%)",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.info(
        "Interpretation: combine the seven leading components to the recommended vehicle. "
        "Exact-config matches = how often that full combination appears in the data."
    )

    fig = px.bar(
        rec,
        x="category",
        y="registrations",
        custom_data=["component", "share_pct"],
        labels={"registrations": "Registrations", "category": "Category"},
        title="Case Study result – leading component per category (K1–K7)",
        category_orders={"category": K_COLS},
    )
    fig.update_traces(
        marker_color=BLUE_DARK,
        texttemplate="%{y}",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "Category %{x}<br>Component %{customdata[0]}"
            "<br>Registrations %{y}<br>Share %{customdata[1]}%<extra></extra>"
        ),
    )
    ymax = float(rec["registrations"].max()) if len(rec) else 1.0
    fig.update_yaxes(range=[0, ymax * 1.18], automargin=True)
    fig.update_layout(margin=dict(l=64, r=24, t=64, b=48), height=380)
    show_chart(fig)


def tab_trends(df: pd.DataFrame | None) -> None:
    st.subheader("4.2 Yearly popularity trends")
    st.write(
        "Case-study requirement: analyse popularity **over time**. "
        "Per category, show registration leaders by year and discuss shifts "
        "(notebook §4.2 ↔ this tab)."
    )

    if df is None:
        st.selectbox("Component category (K1–K7)", K_COLS, index=0, disabled=True)
        st.write("**Yearly leader**")
        st.dataframe(EMPTY_YEARLY_LEADERS, use_container_width=True, hide_index=True)
        empty_line_chart()
        return

    years = sorted(int(y) for y in df["year"].dropna().unique())
    if not years:
        st.warning("No year values available for trends.")
        return

    year_min, year_max = years[0], years[-1]
    c1, c2 = st.columns([2, 1])
    with c1:
        if year_min == year_max:
            st.caption(f"Only one year in the data: **{year_min}**")
            year_range = (year_min, year_max)
        else:
            year_range = st.slider(
                "Year range",
                min_value=year_min,
                max_value=year_max,
                value=(year_min, year_max),
            )
    with c2:
        category = st.selectbox("Component category (K1–K7)", K_COLS, index=0)

    filtered = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
    counts = category_year_counts(filtered, category)
    if counts.empty:
        st.warning("No component data for the selected filters.")
        return

    leaders = yearly_leaders(filtered, category)
    st.write(f"**Yearly leader in {category}**")
    st.dataframe(
        leaders.rename(
            columns={
                "year": "Year",
                "component": "Leading component",
                "count": "Registrations",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    top_n = (
        counts.groupby("component")["count"]
        .sum()
        .sort_values(ascending=False)
        .head(6)
        .index
    )
    plot_df = counts[counts["component"].isin(top_n)].sort_values(["component", "year"])

    fig = px.line(
        plot_df,
        x="year",
        y="count",
        color="component",
        markers=True,
        labels={"count": "Registrations", "year": "Year", "component": "Component"},
        title=f"Yearly registrations – {category} (top components)",
    )
    fig.update_xaxes(dtick=1)
    show_chart(fig)

    overall = recommend_vehicle(df)
    overall_comp = overall.loc[overall["category"] == category, "component"].iloc[0]
    last_year_comp = leaders.iloc[-1]["component"] if len(leaders) else "—"
    if last_year_comp == overall_comp:
        st.success(
            f"In {category}, overall leader **{overall_comp}** "
            f"also leads in the latest year of the selected range."
        )
    else:
        st.warning(
            f"In {category}, overall leader **{overall_comp}** vs latest year "
            f"**{last_year_comp}** — discuss this shift in notebook §4.2."
        )


def tab_explore(df: pd.DataFrame | None) -> None:
    st.subheader("4.3 Stakeholder exploration")
    st.write(
        "Interactive checks on the **same final dataset**. "
        "Use for management discussion and screenshots (`Additional_files/` / notebook §4.3)."
    )

    if df is None:
        c1, c2 = st.columns(2)
        with c1:
            st.multiselect("Registration years", [], disabled=True)
            st.selectbox("Focus category", K_COLS, index=0, disabled=True)
        with c2:
            st.multiselect("Components in category", [], disabled=True)
            st.multiselect("Registration places (ort)", [], disabled=True)
        empty_bar_chart()
        return

    years = sorted(int(y) for y in df["year"].dropna().unique().tolist())
    c1, c2 = st.columns(2)
    with c1:
        sel_years = st.multiselect("Registration years", years, default=years)
        category = st.selectbox("Focus category", K_COLS, index=0, key="explore_cat")
    with c2:
        components = sorted(
            v for v in df[category].dropna().astype(str).unique().tolist()
        )
        sel_components = st.multiselect(
            f"Components in {category}",
            components,
            default=components[: min(5, len(components))],
            key=f"explore_components_{category}",
        )
        sel_places: list[str] = []
        if "ort" in df.columns:
            places = sorted(
                v for v in df["ort"].dropna().astype(str).unique().tolist()
            )
            sel_places = st.multiselect("Registration places (ort)", places, default=[])

    if not sel_years:
        st.warning("Select at least one year.")
        return
    if not sel_components:
        st.warning("Select at least one component.")
        return

    filtered = df[df["year"].isin(sel_years)]
    filtered = filtered[filtered[category].isin(sel_components)]
    if sel_places:
        filtered = filtered[filtered["ort"].isin(sel_places)]

    st.caption(
        f"Filtered view: {len(filtered):,} rows · "
        f"{int(filtered['registrations'].sum()):,} registrations"
    )
    if filtered.empty:
        st.warning("No rows match the current filters.")
        return

    overall = recommend_vehicle(df)
    leader = overall.loc[overall["category"] == category, "component"].iloc[0]
    leader_regs = int(
        filtered.loc[filtered[category] == leader, "registrations"].sum()
    )
    st.write(
        f"Under current filters, overall leader in **{category}** (**{leader}**) "
        f"→ **{leader_regs:,}** registrations."
    )

    share = (
        filtered.groupby(category, as_index=False)["registrations"]
        .sum()
        .rename(columns={category: "component", "registrations": "count"})
        .sort_values("count", ascending=False)
    )
    fig = px.bar(
        share,
        x="component",
        y="count",
        labels={"count": "Registrations", "component": "Component"},
        title=f"Filtered registrations by {category}",
    )
    fig.update_traces(marker_color=BLUE)
    show_chart(fig)

    if {"lat", "lon"}.issubset(filtered.columns):
        map_df = filtered.dropna(subset=["lat", "lon"]).copy()
        map_df = map_df[
            map_df["lat"].between(-90, 90) & map_df["lon"].between(-180, 180)
        ]
        if not map_df.empty:
            st.write("**Geographic distribution** (if geodata is in the final CSV)")
            st.map(
                map_df.rename(columns={"lat": "latitude", "lon": "longitude"})[
                    ["latitude", "longitude"]
                ]
            )


def tab_table(df: pd.DataFrame | None) -> None:
    st.subheader("3 → Final dataset used by the app")
    st.write(
        "One tidy table from Case Study notebook §3: "
        "`Data/SoSe26_Case_Study_finalData_Group_38.csv`. "
        "Required columns: `year`, `K1`…`K7`. Optional: `registrations`, `ort`, `plz`, `lat`, `lon`."
    )

    if df is None:
        st.dataframe(EMPTY_FINAL_DATA, use_container_width=True, hide_index=True)
        return

    st.caption("Full final dataset — source of all charts above.")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        label="Download final dataset (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="SoSe26_Case_Study_finalData_Group_38_view.csv",
        mime="text/csv",
    )


def main() -> None:
    st.set_page_config(
        page_title="IDA Case Study – Group 38",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_styles()
    render_header()

    st.sidebar.markdown("**Case Study link**")
    st.sidebar.caption("Notebook §3 → final CSV")
    st.sidebar.caption("Notebook §4 → tabs 4.1–4.3")
    st.sidebar.caption("doc/final-data-contract.md")
    st.sidebar.caption("doc/app-case-study-traceability.md")

    df: pd.DataFrame | None = None
    if DATA_PATH.is_file():
        try:
            df = load_final_data(str(DATA_PATH))
            st.sidebar.write(f"{len(df):,} rows")
            st.sidebar.write(f"Years {int(df['year'].min())}–{int(df['year'].max())}")
        except Exception as exc:
            st.error(f"Could not load final dataset: {exc}")
            df = None
    st.sidebar.caption("Data/SoSe26_Case_Study_finalData_Group_38.csv")

    tab_o, tab_t, tab_e, tab_d = st.tabs(
        [
            "4.1 Recommendation",
            "4.2 Yearly trends",
            "4.3 Explore",
            "Final dataset",
        ]
    )
    with tab_o:
        tab_result(df)
    with tab_t:
        tab_trends(df)
    with tab_e:
        tab_explore(df)
    with tab_d:
        tab_table(df)

    st.markdown(
        '<p class="footer-note">IDA SoSe26 · Group 38</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
