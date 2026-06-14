"""SEO Expert Recommendations Dashboard — portfolio Streamlit app."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent / "data.csv"
HIGH_CONSENSUS_LEVELS = {"Universal Consensus", "Strong Consensus"}

CHART_LAYOUT = dict(
    template="plotly_white",
    margin=dict(l=40, r=20, t=50, b=40),
    height=380,
    font=dict(family="Inter, Segoe UI, sans-serif", size=12),
)

COLOR_SEQUENCE = [
    "#2563eb",
    "#7c3aed",
    "#0891b2",
    "#059669",
    "#d97706",
    "#dc2626",
    "#64748b",
]


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


def render_kpi_card(label: str, value: str | int, help_text: str) -> None:
    st.metric(label=label, value=value, help=help_text)


def main() -> None:
    st.set_page_config(
        page_title="SEO Expert Recommendations Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
            .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
            div[data-testid="stMetric"] {
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 1rem 1.25rem;
            }
            div[data-testid="stMetricLabel"] { font-size: 0.85rem; color: #475569; }
            div[data-testid="stMetricValue"] { font-size: 1.75rem; color: #0f172a; }
            h1 { color: #0f172a; font-weight: 700; margin-bottom: 0.25rem; }
            .dashboard-subtitle { color: #64748b; font-size: 1rem; margin-bottom: 1.5rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    df = load_data()

    st.title("SEO Expert Recommendations Dashboard")
    st.markdown(
        '<p class="dashboard-subtitle">'
        "Interactive analysis of AI-powered SEO recommendations synthesized from leading practitioners."
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
        st.caption(f"Showing {len(apply_filters(df, selected_experts, selected_categories, selected_consensus)):,} of {len(df):,} recommendations")

    filtered = apply_filters(
        df,
        selected_experts,
        selected_categories,
        selected_consensus,
    )

    if filtered.empty:
        st.warning("No recommendations match the current filters. Adjust your selections to continue.")
        return

    total_experts = filtered["Expert"].nunique()
    total_recommendations = len(filtered)
    total_categories = filtered["Category"].nunique()
    high_consensus = filtered["Consensus_Level"].isin(HIGH_CONSENSUS_LEVELS).sum()
    high_consensus_pct = (high_consensus / total_recommendations * 100) if total_recommendations else 0

    st.subheader("Key Metrics")
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        render_kpi_card("Total Experts", f"{total_experts:,}", "Distinct experts in the filtered dataset.")
    with kpi_cols[1]:
        render_kpi_card("Total Recommendations", f"{total_recommendations:,}", "Recommendations matching active filters.")
    with kpi_cols[2]:
        render_kpi_card("Total Categories", f"{total_categories:,}", "Distinct recommendation categories.")
    with kpi_cols[3]:
        render_kpi_card(
            "High Consensus Recommendations",
            f"{high_consensus:,}",
            f"Universal or Strong consensus ({high_consensus_pct:.0f}% of filtered rows).",
        )

    st.divider()
    st.subheader("Visual Analysis")

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
        color_continuous_scale="Blues",
        title="Recommendations by Expert",
        labels={"Recommendations": "Count", "Expert": "Expert"},
    )
    fig_experts.update_layout(showlegend=False, coloraxis_showscale=False, **CHART_LAYOUT)
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
        color_continuous_scale="Purples",
        title="Recommendations by Category",
        labels={"Recommendations": "Count", "Category": "Category"},
    )
    fig_categories.update_layout(showlegend=False, coloraxis_showscale=False, **CHART_LAYOUT)
    fig_categories.update_xaxes(tickangle=-35)
    chart_right.plotly_chart(fig_categories, use_container_width=True)

    consensus_counts = (
        filtered.groupby("Consensus_Level", as_index=False)
        .size()
        .rename(columns={"size": "Recommendations"})
        .sort_values("Recommendations", ascending=False)
    )
    fig_consensus = px.pie(
        consensus_counts,
        names="Consensus_Level",
        values="Recommendations",
        title="Consensus Level Distribution",
        color_discrete_sequence=COLOR_SEQUENCE,
        hole=0.45,
    )
    fig_consensus.update_traces(textposition="inside", textinfo="percent+label")
    fig_consensus.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig_consensus, use_container_width=True)

    st.divider()
    st.subheader("Recommendations Explorer")

    search_query = st.text_input(
        "Search recommendations",
        placeholder="Search by expert, category, topic, recommendation, or consensus level…",
    )

    table_df = filtered.copy()
    if search_query.strip():
        mask = table_df.apply(
            lambda row: row.astype(str).str.contains(search_query, case=False, regex=False).any(),
            axis=1,
        )
        table_df = table_df[mask]

    st.caption(f"{len(table_df):,} row(s) displayed")

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


if __name__ == "__main__":
    main()
