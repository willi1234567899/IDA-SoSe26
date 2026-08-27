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
PLOTLY_COLORS = [
    "#2F5F7A",
    "#5BA4CF",
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
    "K1": "#2F5F7A",
    "K2": "#5BA4CF",
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


def active_count_col(exclude_defective: bool) -> str:
    return COUNT_CLEAN if exclude_defective else COUNT_ALL ##changed name

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

def build_series_kpis(    ##added 
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
        page_title="Most popular vehicle | IDA Group 38",
        layout="wide",
    )
    apply_design()
    df = get_data()


    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    header_l, header_r = st.columns([5, 1], vertical_alignment="top")

    with header_l:
        st.markdown(
            """
            <div class="ida-hero">
                <h1>Most popular vehicle - component recommendation</h1>
                <p>
                    Management briefing based on KBA registrations 2009-2016.
                    Popularity is counted at <b>series</b> level
                    (type + manufacturer + plant), e.g. K1BE1-104-1041.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with header_r:
        if LOGO_PATH.exists():
            st.image(
                str(LOGO_PATH),
                width=180,
            )


    # ---------------------------------------------------------
    # Registration basis
    # ---------------------------------------------------------

    settings_l, settings_r = st.columns([5, 1])

    with settings_l:
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
                "Exclude defective vehicles: remove vehicles classified as defective "
                "under the applied defect rule. Only defects occurring after "
                "registration are considered."
            ),
        )

        exclude_defective = mode == "Exclude defective vehicles"
        count_col = active_count_col(exclude_defective)
        mode_tag = "clean" if exclude_defective else "all"

        if exclude_defective:
            st.info(
                "**Defect filtering active:** vehicles classified as defective under "
                "the applied defect rule are excluded. Only defects occurring after "
                "registration are considered."
            )
        else:
            st.caption(
                "**All registrations:** no vehicles are excluded based on defect information."
            )
    # with total_col:
    #     st.metric(
    #         "Component observations", ##changed name
    #         f"{int(df[count_col].sum()):,}",
    #         help="Sum of registered component occurrences across engine, seats, "
    #         "gearbox and body. Each registered vehicle normally contributes "
    #         "four component observations.",
    #     )


    st.sidebar.header("Analysis settings") ##changed
    st.sidebar.write(f"**Registration basis:** {mode}")
    st.sidebar.caption(
        "A vehicle is classified as defective if the vehicle itself, an installed "
    "component, or an installed single part is marked defective. A defective "
    "single part also makes its component defective. Only defects occurring " ##changed
    "after registration are considered."
    )

    # ---------------------------------------------------------
    # Analysis period
    # ---------------------------------------------------------

    data_start_year = int(df["year"].min())
    data_end_year = int(df["year"].max())

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

    overall = overall_counts(
    analysis_df,
    count_col,
    )

    overall_full_period = overall_counts(
    df,
    count_col,
    )

    winners = winners_by_category(overall)

    series_kpis = build_series_kpis(
        df=analysis_df,
        count_col=count_col,

        # Important:
        # lifecycle always uses the complete dataset
        lifecycle_df=df,
    )

    # --------------------------------------------------------- added
    # Executive summary
    # ---------------------------------------------------------

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

    summary_cols = st.columns(5)

    with summary_cols[0]:
        st.metric(
            "Vehicle registrations",
            f"{vehicle_registrations:,}",
        )
        st.caption(
            f"Selected analysis period · {analysis_period_label}"
        )

    with summary_cols[1]:
        st.metric(
            "Top engine",
            series_names(engine_top),
        )
        st.caption(
            f"{engine_share:.1%} of K1 registrations"
        )

    with summary_cols[2]:
        st.metric(
            "Top seats",
            series_names(seats_top),
        )
        st.caption(
            f"{seats_share:.1%} of K2 registrations"
        )

    with summary_cols[3]:
        st.metric(
            "Top gearbox",
            series_names(gearbox_top),
        )
        st.caption(
            f"{gearbox_share:.1%} of K3 registrations"
        )

    with summary_cols[4]:
        st.metric(
            "Top body",
            series_names(body_top),
        )
        st.caption(
            f"{body_share:.1%} of all body registrations"
        ) ## added

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
            f"**Lifecycle check:** all 4 recommendations based on "
            f"**{analysis_period_label}** have at least one leading series "
            f"still observed in {latest_year}."
        )
    else:
        st.warning(
            f"**Lifecycle check:** only {current_slots} of 4 recommendations "
            f"based on **{analysis_period_label}** have a leading series still "
            f"observed in {latest_year}. Historical popularity may therefore "
            "include series no longer observed at the end of the dataset."
        )

    tab_rec, tab_trend, tab_explore, tab_table = st.tabs(
            ["Recommendation", "Yearly trends", "Explore", "Full data"]
        )

    with st.sidebar.expander("Glossary & methodology"):
        st.markdown(
        """
        **Registration volume**  
        Number of registered vehicles containing the respective component series.

        **Defect-filtered registrations**  
        Registrations remaining after vehicles classified as defective under the
        applied defect rule are excluded.

        **Category**  
        K1 = engine, K2 = seats, K3 = gearbox. K4–K7 represent the four
        body categories.                                                                    

        **Series**  
        Component series defined by component type, manufacturer and plant.

        **First observed registration**  
        First year in which a series appears in the available registration data.
        This does not necessarily represent its production start.

        **Last observed registration**  
        Last year in which a series appears in the available registration data.
        This does not necessarily represent its production end.
        """
        ) ## added

    with tab_rec:
        st.subheader("Top component recommendations")

        st.caption(
            "Series are ranked by registration volume using the selected registration basis. "
            "Market share refers to the respective recommendation pool. "
            "Ties are assigned the same rank."
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

        recommended_engine = series_names(
            engine_ranking[
                engine_ranking["display_rank"] == 1
            ]
        )

        recommended_seats = series_names(
            seats_ranking[
                seats_ranking["display_rank"] == 1
            ]
        )

        recommended_gearbox = series_names(
            gearbox_ranking[
                gearbox_ranking["display_rank"] == 1
            ]
        )

        recommended_body = series_names(
            body_ranking[
                body_ranking["display_rank"] == 1
            ]
        )
        # k1_txt = " or ".join(k1["series"].tolist())
        # k2_txt = " or ".join(k2["series"].tolist())
        # k3_txt = " or ".join(k3["series"].tolist())

        st.markdown("#### Popularity-based vehicle recommendation")

        st.info(
            f"Based on registrations in **{analysis_period_label}**, the individually "
            f"most popular component choices are engine **{recommended_engine}**, "
            f"seats **{recommended_seats}**, gearbox **{recommended_gearbox}**, "
            f"and body **{recommended_body}**. "
            "Components are selected independently based on registration volume. "
            "Compatibility of the combined specification is not validated."
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
            "A green ▲ marks the first observed registration of a "
            "series within the dataset; a red × marks its last observed registration. "
            "These markers do not necessarily represent actual production start or "
            "end dates."
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
                "Market share is calculated within the selected category for each year. "
                "This makes relative shifts visible even when the overall registration "
                "volume changes."
        )
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
            color_discrete_map=CATEGORY_COLORS,
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
