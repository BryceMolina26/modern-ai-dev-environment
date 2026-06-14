"""Executive SEO Expert Recommendations Dashboard — portfolio Streamlit app."""

from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent / "data.csv"
HIGH_CONSENSUS_LEVELS = {"Universal Consensus", "Strong Consensus"}
AGREEMENT_LEVELS = HIGH_CONSENSUS_LEVELS
DISAGREEMENT_LEVELS = {"Mixed (Expert Disagreement)", "Individual Expert View"}

CONSENSUS_RANK = {
    "Universal Consensus": 1,
    "Strong Consensus": 2,
    "Mixed (Expert Disagreement)": 3,
    "Individual Expert View": 4,
}

EXEC_PALETTE = {
    "navy": "#1e3a5f",
    "navy_light": "#2d4a6f",
    "gold": "#c9a227",
    "gold_light": "#e8c547",
    "slate": "#475569",
    "slate_light": "#64748b",
    "surface": "#f8fafc",
    "border": "#e2e8f0",
    "text": "#0f172a",
    "success": "#059669",
    "warning": "#d97706",
    "danger": "#dc2626",
}

COLOR_SEQUENCE = [
    EXEC_PALETTE["navy"],
    EXEC_PALETTE["gold"],
    "#2563eb",
    EXEC_PALETTE["success"],
    EXEC_PALETTE["warning"],
    EXEC_PALETTE["danger"],
    EXEC_PALETTE["slate_light"],
]

CHART_LAYOUT = dict(
    template="plotly_white",
    margin=dict(l=48, r=24, t=56, b=48),
    height=420,
    font=dict(family="Inter, Segoe UI, sans-serif", size=13, color=EXEC_PALETTE["text"]),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["Expert"] = df["Expert"].astype(str).str.strip()
    df["Category"] = df["Category"].astype(str).str.strip()
    df["Topic"] = df["Topic"].astype(str).str.strip()
    df["Recommendation"] = df["Recommendation"].astype(str).str.strip()
    df["Consensus_Level"] = df["Consensus_Level"].astype(str).str.strip()
    return df


def apply_filters(
    df: pd.DataFrame,
    experts: list[str],
    categories: list[str],
    consensus_levels: list[str],
) -> pd.DataFrame:
    filtered = df.copy()
    if experts:
        filtered = filtered[filtered["Expert"].isin(experts)]
    if categories:
        filtered = filtered[filtered["Category"].isin(categories)]
    if consensus_levels:
        filtered = filtered[filtered["Consensus_Level"].isin(consensus_levels)]
    return filtered


def apply_search(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query.strip():
        return df
    mask = df.apply(
        lambda row: row.astype(str).str.contains(query, case=False, regex=False).any(),
        axis=1,
    )
    return df[mask]


def compute_kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    high_consensus = df["Consensus_Level"].isin(HIGH_CONSENSUS_LEVELS).sum()
    return {
        "experts": df["Expert"].nunique(),
        "recommendations": total,
        "categories": df["Category"].nunique(),
        "topics": df["Topic"].nunique(),
        "high_consensus": high_consensus,
        "consensus_rate": (high_consensus / total * 100) if total else 0.0,
    }


def generate_executive_insights(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []

    category_counts = df.groupby("Category").size()
    expert_counts = df.groupby("Expert").size()
    kpis = compute_kpis(df)

    category_agreement = (
        df.assign(_agree=df["Consensus_Level"].isin(HIGH_CONSENSUS_LEVELS))
        .groupby("Category")["_agree"]
        .mean()
        .sort_values(ascending=False)
    )
    strongest_cat = category_agreement.index[0]
    strongest_pct = category_agreement.iloc[0] * 100

    return [
        {
            "icon": "📂",
            "title": "Most Discussed Category",
            "value": category_counts.idxmax(),
            "detail": f"{category_counts.max():,} recommendations across the filtered dataset.",
        },
        {
            "icon": "👤",
            "title": "Top Contributor",
            "value": expert_counts.idxmax(),
            "detail": f"{expert_counts.max():,} recommendations — highest expert output in view.",
        },
        {
            "icon": "🤝",
            "title": "Consensus Rate",
            "value": f"{kpis['consensus_rate']:.0f}%",
            "detail": f"{kpis['high_consensus']:,} of {kpis['recommendations']:,} rows show Universal or Strong Consensus.",
        },
        {
            "icon": "🏷️",
            "title": "Unique Topics",
            "value": f"{kpis['topics']:,}",
            "detail": "Distinct strategic topics represented after applying filters.",
        },
        {
            "icon": "✅",
            "title": "Strongest Agreement",
            "value": strongest_cat,
            "detail": f"{strongest_pct:.0f}% agreement rate — highest category consensus in view.",
        },
    ]


def build_expert_comparison(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Expert", as_index=False)
        .agg(
            Recommendations=("Expert", "size"),
            Categories=("Category", "nunique"),
            Topics=("Topic", "nunique"),
            High_Consensus=("Consensus_Level", lambda s: s.isin(HIGH_CONSENSUS_LEVELS).sum()),
        )
        .assign(
            High_Consensus_Pct=lambda d: (
                d["High_Consensus"] / d["Recommendations"] * 100
            ).round(1),
        )
        .sort_values("Recommendations", ascending=False)
        .reset_index(drop=True)
    )


def build_top_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    ranked = df.copy()
    ranked["_rank"] = ranked["Consensus_Level"].map(CONSENSUS_RANK).fillna(99)
    ranked = ranked.sort_values(["_rank", "Category", "Expert"]).drop(columns="_rank")
    return ranked[["Recommendation", "Expert", "Category", "Consensus_Level"]].reset_index(drop=True)


def build_expert_heatmap(df: pd.DataFrame) -> go.Figure:
    pivot = (
        df.groupby(["Expert", "Category"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )
    pivot = pivot.reindex(
        sorted(pivot.index),
        columns=sorted(pivot.columns),
    )

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[
                [0.0, EXEC_PALETTE["surface"]],
                [0.25, "#cbd5e1"],
                [0.5, "#64748b"],
                [0.75, EXEC_PALETTE["navy_light"]],
                [1.0, EXEC_PALETTE["navy"]],
            ],
            hovertemplate="Expert: %{y}<br>Category: %{x}<br>Recommendations: %{z}<extra></extra>",
            colorbar=dict(title="Count"),
        )
    )
    fig.update_layout(
        title=dict(
            text="Expert × Category Recommendation Matrix",
            font=dict(size=16, color=EXEC_PALETTE["navy"]),
        ),
        xaxis=dict(title="Category", tickangle=-35),
        yaxis=dict(title="Expert"),
        **CHART_LAYOUT,
    )
    return fig


def build_consensus_donut(df: pd.DataFrame) -> go.Figure:
    consensus_counts = (
        df.groupby("Consensus_Level", as_index=False)
        .size()
        .rename(columns={"size": "Recommendations"})
        .sort_values("Recommendations", ascending=False)
    )
    fig = px.pie(
        consensus_counts,
        names="Consensus_Level",
        values="Recommendations",
        title="Consensus Level Distribution",
        color_discrete_sequence=COLOR_SEQUENCE,
        hole=0.55,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        title_font=dict(size=16, color=EXEC_PALETTE["navy"]),
        **CHART_LAYOUT,
    )
    return fig


def build_agreement_chart(df: pd.DataFrame) -> go.Figure:
    agreement_count = df["Consensus_Level"].isin(AGREEMENT_LEVELS).sum()
    disagreement_count = df["Consensus_Level"].isin(DISAGREEMENT_LEVELS).sum()
    other_count = len(df) - agreement_count - disagreement_count

    labels, values, colors = [], [], []
    if agreement_count:
        labels.append("Agreement")
        values.append(agreement_count)
        colors.append(EXEC_PALETTE["success"])
    if disagreement_count:
        labels.append("Disagreement")
        values.append(disagreement_count)
        colors.append(EXEC_PALETTE["danger"])
    if other_count:
        labels.append("Other")
        values.append(other_count)
        colors.append(EXEC_PALETTE["slate_light"])

    fig = go.Figure(
        data=[
            go.Bar(
                x=labels,
                y=values,
                marker_color=colors,
                text=values,
                textposition="outside",
                hovertemplate="%{x}: %{y} recommendations<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text="Agreement vs Disagreement",
            font=dict(size=16, color=EXEC_PALETTE["navy"]),
        ),
        yaxis=dict(title="Recommendations"),
        xaxis=dict(title=""),
        showlegend=False,
        **CHART_LAYOUT,
    )
    return fig


def build_topic_chart(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    topic_counts = (
        df.groupby("Topic", as_index=False)
        .size()
        .rename(columns={"size": "Recommendations"})
        .sort_values("Recommendations", ascending=False)
        .head(top_n)
        .sort_values("Recommendations", ascending=True)
    )
    fig = px.bar(
        topic_counts,
        x="Recommendations",
        y="Topic",
        orientation="h",
        color="Recommendations",
        color_continuous_scale=[
            [0, EXEC_PALETTE["navy_light"]],
            [0.5, EXEC_PALETTE["navy"]],
            [1, EXEC_PALETTE["gold"]],
        ],
        title=f"Top {top_n} Most Discussed Topics",
        labels={"Recommendations": "Count", "Topic": "Topic"},
    )
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        title_font=dict(size=16, color=EXEC_PALETTE["navy"]),
        **CHART_LAYOUT,
    )
    return fig


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def inject_executive_styles() -> None:
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

            html, body, [class*="css"] {{
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}

            .block-container {{
                padding-top: 2rem;
                padding-bottom: 3rem;
                max-width: 1400px;
            }}

            h1 {{
                color: {EXEC_PALETTE["navy"]};
                font-weight: 700;
                font-size: 2.25rem;
                letter-spacing: -0.02em;
                margin-bottom: 0.35rem;
            }}

            h2, h3 {{
                color: {EXEC_PALETTE["navy"]};
                font-weight: 600;
                letter-spacing: -0.01em;
            }}

            .dashboard-subtitle {{
                color: {EXEC_PALETTE["slate_light"]};
                font-size: 1.05rem;
                line-height: 1.6;
                margin-bottom: 2rem;
            }}

            .section-header {{
                color: {EXEC_PALETTE["navy"]};
                font-size: 1.35rem;
                font-weight: 600;
                margin: 2rem 0 1.25rem;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid {EXEC_PALETTE["gold"]};
            }}

            div[data-testid="stMetric"] {{
                background: linear-gradient(145deg, #ffffff 0%, {EXEC_PALETTE["surface"]} 100%);
                border: 1px solid {EXEC_PALETTE["border"]};
                border-left: 4px solid {EXEC_PALETTE["gold"]};
                border-radius: 14px;
                padding: 1.25rem 1.5rem;
                box-shadow: 0 1px 3px rgba(30, 58, 95, 0.06);
            }}

            div[data-testid="stMetricLabel"] {{
                font-size: 0.8rem;
                color: {EXEC_PALETTE["slate"]};
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }}

            div[data-testid="stMetricValue"] {{
                font-size: 2rem;
                color: {EXEC_PALETTE["navy"]};
                font-weight: 700;
            }}

            .kpi-icon {{
                font-size: 1.5rem;
                margin-bottom: 0.35rem;
            }}

            .insight-card {{
                background: linear-gradient(145deg, #ffffff 0%, {EXEC_PALETTE["surface"]} 100%);
                border: 1px solid {EXEC_PALETTE["border"]};
                border-radius: 14px;
                padding: 1.35rem 1.5rem;
                height: 100%;
                box-shadow: 0 2px 8px rgba(30, 58, 95, 0.05);
                transition: box-shadow 0.2s ease;
            }}

            .insight-card:hover {{
                box-shadow: 0 4px 16px rgba(30, 58, 95, 0.1);
            }}

            .insight-icon {{
                font-size: 1.75rem;
                margin-bottom: 0.65rem;
            }}

            .insight-title {{
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: {EXEC_PALETTE["slate_light"]};
                margin-bottom: 0.4rem;
            }}

            .insight-value {{
                font-size: 1.15rem;
                font-weight: 700;
                color: {EXEC_PALETTE["navy"]};
                line-height: 1.35;
                margin-bottom: 0.5rem;
            }}

            .insight-detail {{
                font-size: 0.82rem;
                color: {EXEC_PALETTE["slate"]};
                line-height: 1.5;
            }}

            .download-panel {{
                background: linear-gradient(135deg, {EXEC_PALETTE["navy"]} 0%, {EXEC_PALETTE["navy_light"]} 100%);
                border-radius: 16px;
                padding: 2rem 2.25rem;
                color: #ffffff;
                margin-top: 1rem;
            }}

            .download-panel h3 {{
                color: #ffffff !important;
                margin: 0 0 0.5rem;
                font-size: 1.25rem;
            }}

            .download-panel p {{
                color: rgba(255, 255, 255, 0.85);
                font-size: 0.95rem;
                margin: 0 0 1.25rem;
                line-height: 1.55;
            }}

            .dashboard-footer {{
                margin-top: 4rem;
                padding: 2rem 0 1rem;
                border-top: 1px solid {EXEC_PALETTE["border"]};
                text-align: center;
            }}

            .footer-title {{
                font-size: 0.95rem;
                font-weight: 600;
                color: {EXEC_PALETTE["navy"]};
                margin-bottom: 0.35rem;
            }}

            .footer-credit {{
                font-size: 0.85rem;
                color: {EXEC_PALETTE["slate_light"]};
            }}

            div[data-testid="stTabs"] button {{
                font-weight: 600;
                font-size: 0.95rem;
            }}

            div[data-testid="stTabs"] [aria-selected="true"] {{
                color: {EXEC_PALETTE["navy"]} !important;
                border-bottom-color: {EXEC_PALETTE["gold"]} !important;
            }}

            [data-testid="stSidebar"] {{
                background: linear-gradient(180deg, {EXEC_PALETTE["surface"]} 0%, #ffffff 100%);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_row(kpis: dict) -> None:
    cards = [
        ("👥", "Experts", f"{kpis['experts']:,}", "Practitioners in the filtered selection."),
        ("📋", "Recommendations", f"{kpis['recommendations']:,}", "Total expert recommendations in view."),
        ("📊", "Categories", f"{kpis['categories']:,}", "Strategic areas covered."),
        ("🤝", "Consensus Rate", f"{kpis['consensus_rate']:.0f}%", "Share with Universal or Strong Consensus."),
    ]
    cols = st.columns(4)
    for col, (icon, label, value, help_text) in zip(cols, cards):
        with col:
            st.markdown(f'<div class="kpi-icon">{icon}</div>', unsafe_allow_html=True)
            st.metric(label=label, value=value, help=help_text)


def render_executive_insights(insights: list[dict]) -> None:
    st.markdown('<p class="section-header">Executive Insights</p>', unsafe_allow_html=True)
    cols = st.columns(len(insights))
    for col, insight in zip(cols, insights):
        with col:
            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="insight-icon">{insight["icon"]}</div>
                    <div class="insight-title">{insight["title"]}</div>
                    <div class="insight-value">{insight["value"]}</div>
                    <div class="insight-detail">{insight["detail"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_top_recommendations_table(df: pd.DataFrame) -> None:
    st.markdown('<p class="section-header">Top Recommendations</p>', unsafe_allow_html=True)
    search_query = st.text_input(
        "Search recommendations",
        placeholder="Filter by recommendation, expert, category, or consensus level…",
        key="top_recs_search",
    )
    top_recs = build_top_recommendations(df)
    display_df = apply_search(top_recs, search_query)
    st.caption(f"{len(display_df):,} recommendation(s) — ranked by consensus strength")
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Recommendation": st.column_config.TextColumn("Recommendation", width="large"),
            "Expert": st.column_config.TextColumn("Expert", width="small"),
            "Category": st.column_config.TextColumn("Category", width="small"),
            "Consensus_Level": st.column_config.TextColumn("Consensus Level", width="medium"),
        },
    )


def render_overview_tab(filtered: pd.DataFrame, kpis: dict) -> None:
    render_kpi_row(kpis)
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    render_executive_insights(generate_executive_insights(filtered))
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    render_top_recommendations_table(filtered)


def render_expert_analysis_tab(filtered: pd.DataFrame) -> None:
    st.markdown('<p class="section-header">Expert Performance</p>', unsafe_allow_html=True)

    chart_left, chart_right = st.columns(2)

    expert_counts = (
        filtered.groupby("Expert", as_index=False)
        .size()
        .rename(columns={"size": "Recommendations"})
        .sort_values("Recommendations", ascending=True)
    )
    fig_experts = px.bar(
        expert_counts,
        x="Recommendations",
        y="Expert",
        orientation="h",
        color="Recommendations",
        color_continuous_scale=[
            [0, EXEC_PALETTE["navy_light"]],
            [1, EXEC_PALETTE["navy"]],
        ],
        title="Recommendations by Expert",
    )
    fig_experts.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        title_font=dict(size=16, color=EXEC_PALETTE["navy"]),
        **CHART_LAYOUT,
    )
    chart_left.plotly_chart(fig_experts, use_container_width=True)

    category_counts = (
        filtered.groupby("Category", as_index=False)
        .size()
        .rename(columns={"size": "Recommendations"})
        .sort_values("Recommendations", ascending=False)
    )
    fig_categories = px.bar(
        category_counts,
        x="Category",
        y="Recommendations",
        color="Recommendations",
        color_continuous_scale=[
            [0, EXEC_PALETTE["gold_light"]],
            [1, EXEC_PALETTE["gold"]],
        ],
        title="Recommendations by Category",
    )
    fig_categories.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        title_font=dict(size=16, color=EXEC_PALETTE["navy"]),
        **CHART_LAYOUT,
    )
    fig_categories.update_xaxes(tickangle=-35)
    chart_right.plotly_chart(fig_categories, use_container_width=True)

    st.markdown('<p class="section-header">Expert Comparison Matrix</p>', unsafe_allow_html=True)
    st.plotly_chart(build_expert_heatmap(filtered), use_container_width=True)

    st.markdown('<p class="section-header">Expert Summary</p>', unsafe_allow_html=True)
    expert_comparison = build_expert_comparison(filtered)
    st.dataframe(
        expert_comparison,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Expert": st.column_config.TextColumn("Expert", width="medium"),
            "Recommendations": st.column_config.NumberColumn("Recommendations", format="%d"),
            "Categories": st.column_config.NumberColumn("Categories", format="%d"),
            "Topics": st.column_config.NumberColumn("Topics", format="%d"),
            "High_Consensus": st.column_config.NumberColumn("High Consensus", format="%d"),
            "High_Consensus_Pct": st.column_config.NumberColumn("Agreement %", format="%.1f%%"),
        },
    )


def render_consensus_tab(filtered: pd.DataFrame) -> None:
    st.markdown('<p class="section-header">Consensus Analysis</p>', unsafe_allow_html=True)
    chart_left, chart_right = st.columns(2)
    chart_left.plotly_chart(build_consensus_donut(filtered), use_container_width=True)
    chart_right.plotly_chart(build_agreement_chart(filtered), use_container_width=True)

    st.markdown('<p class="section-header">Consensus Breakdown</p>', unsafe_allow_html=True)
    breakdown = (
        filtered.groupby("Consensus_Level", as_index=False)
        .size()
        .rename(columns={"size": "Count"})
        .assign(
            Share=lambda d: (d["Count"] / d["Count"].sum() * 100).round(1),
        )
        .sort_values("Count", ascending=False)
    )
    st.dataframe(
        breakdown,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Consensus_Level": st.column_config.TextColumn("Consensus Level"),
            "Count": st.column_config.NumberColumn("Recommendations", format="%d"),
            "Share": st.column_config.NumberColumn("Share of Total", format="%.1f%%"),
        },
    )


def render_data_explorer_tab(filtered: pd.DataFrame, df: pd.DataFrame) -> None:
    st.markdown('<p class="section-header">Topic Explorer</p>', unsafe_allow_html=True)
    st.plotly_chart(build_topic_chart(filtered, top_n=15), use_container_width=True)

    st.markdown('<p class="section-header">Full Dataset</p>', unsafe_allow_html=True)
    search_query = st.text_input(
        "Search all fields",
        placeholder="Filter by expert, category, topic, recommendation, or consensus…",
        key="explorer_search",
    )
    table_df = apply_search(filtered, search_query)
    st.caption(f"{len(table_df):,} of {len(filtered):,} row(s) displayed")
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Expert": st.column_config.TextColumn("Expert", width="small"),
            "Category": st.column_config.TextColumn("Category", width="small"),
            "Topic": st.column_config.TextColumn("Topic", width="medium"),
            "Recommendation": st.column_config.TextColumn("Recommendation", width="large"),
            "Consensus_Level": st.column_config.TextColumn("Consensus Level", width="medium"),
        },
    )

    st.markdown('<p class="section-header">Download Center</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="download-panel">
            <h3>Export Filtered Data</h3>
            <p>
                Download the complete filtered dataset as CSV for offline analysis,
                executive reporting, or integration with your BI tools.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    dl_col1, dl_col2, dl_col3 = st.columns([1, 1, 2])
    with dl_col1:
        st.download_button(
            label="⬇ Download Filtered CSV",
            data=to_csv_bytes(filtered),
            file_name="seo_recommendations_filtered.csv",
            mime="text/csv",
            use_container_width=True,
            help="All rows matching sidebar filters.",
        )
    with dl_col2:
        st.download_button(
            label="⬇ Download Table View",
            data=to_csv_bytes(table_df),
            file_name="seo_recommendations_export.csv",
            mime="text/csv",
            use_container_width=True,
            help="Rows currently shown in the table (filters + search).",
        )
    with dl_col3:
        st.download_button(
            label="⬇ Download Full Dataset",
            data=to_csv_bytes(df),
            file_name="seo_recommendations_full.csv",
            mime="text/csv",
            use_container_width=True,
            help="Complete unfiltered dataset.",
        )


def render_footer() -> None:
    st.markdown(
        """
        <div class="dashboard-footer">
            <div class="footer-title">AI-Powered SEO Research Dashboard</div>
            <div class="footer-credit">Created by Bryce Molina</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Executive SEO Analytics Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_executive_styles()
    df = load_data()

    st.title("Executive SEO Analytics Dashboard")
    st.markdown(
        '<p class="dashboard-subtitle">'
        "Strategic intelligence on AI-powered SEO recommendations — synthesized from "
        "leading practitioners for executive decision-making."
        "</p>",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Filters")
        expert_options = sorted(df["Expert"].unique())
        category_options = sorted(df["Category"].unique())
        consensus_options = sorted(df["Consensus_Level"].unique())

        selected_experts = st.multiselect(
            "Expert",
            options=expert_options,
            default=expert_options,
        )
        selected_categories = st.multiselect(
            "Category",
            options=category_options,
            default=category_options,
        )
        selected_consensus = st.multiselect(
            "Consensus Level",
            options=consensus_options,
            default=consensus_options,
        )

        st.divider()
        filtered_preview = apply_filters(
            df, selected_experts, selected_categories, selected_consensus
        )
        st.caption(f"Showing {len(filtered_preview):,} of {len(df):,} recommendations")

    filtered = apply_filters(
        df,
        selected_experts,
        selected_categories,
        selected_consensus,
    )

    if filtered.empty:
        st.warning(
            "No recommendations match the current filters. Adjust your selections to continue."
        )
        render_footer()
        return

    kpis = compute_kpis(filtered)

    tab_overview, tab_expert, tab_consensus, tab_explorer = st.tabs(
        ["Overview", "Expert Analysis", "Consensus Analysis", "Data Explorer"]
    )

    with tab_overview:
        render_overview_tab(filtered, kpis)

    with tab_expert:
        render_expert_analysis_tab(filtered)

    with tab_consensus:
        render_consensus_tab(filtered)

    with tab_explorer:
        render_data_explorer_tab(filtered, df)

    render_footer()


if __name__ == "__main__":
    main()
