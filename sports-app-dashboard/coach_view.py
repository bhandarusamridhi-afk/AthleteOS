"""AthleteOS - Coach dashboard view."""

import plotly.graph_objects as go
import streamlit as st

import mock_data as md


def _status_color(label: str) -> str:
    return {"Optimal": "#16a34a", "Moderate": "#d97706", "At Risk": "#dc2626"}.get(
        label, "#6b7280"
    )


def _team_readiness_bar(summary) -> go.Figure:
    colors = [_status_color(s) for s in summary["Status"]]
    fig = go.Figure(
        go.Bar(
            x=summary["Readiness"],
            y=summary["Athlete"],
            orientation="h",
            marker_color=colors,
            text=summary["Readiness"],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Team readiness (lowest first)",
        xaxis=dict(range=[0, 100], title="Readiness score"),
        height=320,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def render() -> None:
    coach = md.COACH
    st.subheader(coach["name"])
    st.caption(f"{coach['team']} · Team overview")

    summary = md.team_summary()

    # Top KPI row
    at_risk = (summary["Status"] == "At Risk").sum()
    optimal = (summary["Status"] == "Optimal").sum()
    avg_ready = int(summary["Readiness"].mean())

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Athletes", len(summary))
    k2.metric("Avg readiness", avg_ready)
    k3.metric("Optimal", int(optimal))
    k4.metric("At risk", int(at_risk), delta_color="inverse")

    if at_risk:
        st.error(
            f"{at_risk} athlete(s) flagged **At Risk**. Review their cards below before "
            "setting today's training load."
        )

    st.divider()

    left, right = st.columns([3, 2])
    with left:
        st.plotly_chart(_team_readiness_bar(summary), use_container_width=True)
    with right:
        st.markdown("**Roster summary**")
        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Readiness": st.column_config.ProgressColumn(
                    "Readiness", min_value=0, max_value=100, format="%d"
                ),
            },
        )

    st.divider()

    # Per-athlete drilldown
    st.markdown("### Athlete detail")
    selected = st.selectbox("Select an athlete to inspect", summary["Athlete"].tolist())
    df = md.get_athlete_df(selected)
    latest = df.iloc[-1]
    score = md.readiness_score(latest)
    label, color = md.readiness_label(score)
    meta = st.session_state.athlete_meta[selected]

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        f"<div style='font-size:13px;color:#6b7280'>Readiness</div>"
        f"<div style='font-size:30px;font-weight:700;color:{color}'>{score}</div>"
        f"<div style='color:{color}'>{label}</div>",
        unsafe_allow_html=True,
    )
    c2.metric("Recovery", int(latest["recovery"]))
    c3.metric("Stress", int(latest["stress"]))
    c4.metric("Motivation", int(latest["motivation"]))

    st.caption(f"{meta['sport']} · {meta['position']} · Age {meta['age']}")

    # Combined physical + mental trend for the coach
    fig = go.Figure()
    for col, clr in [
        ("recovery", "#16a34a"),
        ("training_load", "#2563eb"),
        ("stress", "#dc2626"),
        ("motivation", "#ea580c"),
    ]:
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df[col],
                mode="lines",
                name=col.replace("_", " ").title(),
                line=dict(color=clr, width=2),
            )
        )
    fig.update_layout(
        title=f"{selected} · physical + mental trends",
        height=360,
        yaxis_title="Score (0-100)",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Insights for the selected athlete
    st.markdown("#### Recommended actions")
    for ins in md.generate_insights(df, selected):
        text = f"**{ins['title']}** — {ins['message']}"
        if ins["level"] == "alert":
            st.error(text)
        elif ins["level"] == "warning":
            st.warning(text)
        else:
            st.success(text)
