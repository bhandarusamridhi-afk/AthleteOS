"""AthleteOS - Athlete dashboard view."""

from datetime import date

import plotly.graph_objects as go
import streamlit as st

import mock_data as md


def _readiness_gauge(score: int, label: str, color: str) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "", "font": {"size": 40}},
            title={"text": f"Readiness · {label}", "font": {"size": 16}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 55], "color": "#fee2e2"},
                    {"range": [55, 75], "color": "#fef3c7"},
                    {"range": [75, 100], "color": "#dcfce7"},
                ],
            },
        )
    )
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=10))
    return fig


def _line_chart(df, cols, title, ylabel):
    fig = go.Figure()
    for col, color in cols:
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df[col],
                mode="lines+markers",
                name=col.replace("_", " ").title(),
                line=dict(color=color, width=2),
                marker=dict(size=4),
            )
        )
    fig.update_layout(
        title=title,
        yaxis_title=ylabel,
        height=340,
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    return fig


def _log_form(name: str) -> None:
    """Manual entry form so athletes can log today's metrics."""
    with st.expander("Log today's check-in", expanded=False):
        with st.form("log_form", clear_on_submit=False):
            entry_date = st.date_input("Date", value=date.today())

            st.markdown("**Physical**")
            c1, c2, c3 = st.columns(3)
            training_load = c1.slider("Training load", 0, 100, 55)
            recovery = c2.slider("Recovery", 0, 100, 65)
            sleep_hours = c3.number_input("Sleep (hours)", 0.0, 14.0, 7.5, 0.1)
            c4, c5 = st.columns(2)
            resting_hr = c4.number_input("Resting HR (bpm)", 30, 120, 58)
            hrv = c5.number_input("HRV (ms)", 10, 200, 70)

            st.markdown("**Mental**")
            c6, c7 = st.columns(2)
            stress = c6.slider("Stress", 0, 100, 35)
            focus = c7.slider("Focus", 0, 100, 70)
            c8, c9 = st.columns(2)
            confidence = c8.slider("Confidence", 0, 100, 70)
            motivation = c9.slider("Motivation", 0, 100, 72)
            mood = st.slider("Overall mood (1-10)", 1, 10, 7)

            submitted = st.form_submit_button("Save check-in", use_container_width=True)
            if submitted:
                md.add_entry(
                    name,
                    {
                        "date": entry_date,
                        "training_load": training_load,
                        "recovery": recovery,
                        "resting_hr": resting_hr,
                        "sleep_hours": sleep_hours,
                        "hrv": hrv,
                        "stress": stress,
                        "focus": focus,
                        "confidence": confidence,
                        "motivation": motivation,
                        "mood": mood,
                    },
                )
                st.success("Check-in saved. Charts and readiness updated below.")
                st.rerun()


def render(name: str) -> None:
    meta = st.session_state.athlete_meta[name]
    df = md.get_athlete_df(name)
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest

    st.subheader(f"{name}")
    st.caption(f"{meta['sport']} · {meta['position']} · Age {meta['age']}")

    # Top row: readiness gauge + key metrics
    left, right = st.columns([1, 2])
    score = md.readiness_score(latest)
    label, color = md.readiness_label(score)
    with left:
        st.plotly_chart(_readiness_gauge(score, label, color), use_container_width=True)

    with right:
        st.markdown("**Today's snapshot**")
        m1, m2, m3 = st.columns(3)
        m1.metric("Recovery", f"{int(latest['recovery'])}", f"{int(latest['recovery'] - prev['recovery'])}")
        m2.metric("Training load", f"{int(latest['training_load'])}", f"{int(latest['training_load'] - prev['training_load'])}")
        m3.metric("Sleep", f"{latest['sleep_hours']}h", f"{latest['sleep_hours'] - prev['sleep_hours']:+.1f}")
        m4, m5, m6 = st.columns(3)
        m4.metric("Stress", f"{int(latest['stress'])}", f"{int(latest['stress'] - prev['stress'])}", delta_color="inverse")
        m5.metric("Focus", f"{int(latest['focus'])}", f"{int(latest['focus'] - prev['focus'])}")
        m6.metric("Motivation", f"{int(latest['motivation'])}", f"{int(latest['motivation'] - prev['motivation'])}")

    _log_form(name)

    st.divider()

    # Insights / alerts
    st.markdown("### Insights & alerts")
    insights = md.generate_insights(df, name)
    icons = {"alert": "🔴", "warning": "🟠", "positive": "🟢"}
    for ins in insights:
        text = f"**{ins['title']}** — {ins['message']}"
        if ins["level"] == "alert":
            st.error(text)
        elif ins["level"] == "warning":
            st.warning(text)
        else:
            st.success(text)

    st.divider()

    # Trend charts
    st.markdown("### Trends over the last 4 weeks")
    tab1, tab2 = st.tabs(["Physical", "Mental"])
    with tab1:
        st.plotly_chart(
            _line_chart(
                df,
                [("training_load", "#2563eb"), ("recovery", "#16a34a")],
                "Training load vs recovery",
                "Score (0-100)",
            ),
            use_container_width=True,
        )
        st.plotly_chart(
            _line_chart(
                df,
                [("sleep_hours", "#0891b2")],
                "Sleep duration",
                "Hours",
            ),
            use_container_width=True,
        )
    with tab2:
        st.plotly_chart(
            _line_chart(
                df,
                [("stress", "#dc2626"), ("focus", "#7c3aed")],
                "Stress vs focus",
                "Score (0-100)",
            ),
            use_container_width=True,
        )
        st.plotly_chart(
            _line_chart(
                df,
                [("confidence", "#ea580c"), ("motivation", "#16a34a")],
                "Confidence & motivation",
                "Score (0-100)",
            ),
            use_container_width=True,
        )
