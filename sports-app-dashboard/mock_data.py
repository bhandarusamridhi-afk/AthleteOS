"""
AthleteOS - Mock data layer.

Generates deterministic, realistic sample data for a small team of athletes,
covering both physical performance metrics (training load, recovery, biometrics)
and mental performance indicators (stress, focus, confidence, motivation).

The data lives in Streamlit's session_state so that manual entries made during a
session persist until the page is reloaded. No external database is required,
which keeps deployment on Streamlit Community Cloud simple.
"""

from datetime import date, timedelta
import random

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Static roster definition
# ---------------------------------------------------------------------------

ATHLETES = [
    {"name": "Maya Thompson", "sport": "Sprint (100m)", "age": 22, "position": "Track"},
    {"name": "Diego Ramirez", "sport": "Football", "age": 25, "position": "Midfielder"},
    {"name": "Aiko Tanaka", "sport": "Swimming", "age": 19, "position": "Freestyle"},
    {"name": "Liam O'Connor", "sport": "Basketball", "age": 24, "position": "Guard"},
    {"name": "Sara Nilsson", "sport": "Distance Run", "age": 27, "position": "10k"},
]

COACH = {"name": "Coach Alex Carter", "team": "Apex Performance Squad"}

# Number of days of history to generate per athlete
HISTORY_DAYS = 28

# Metric definitions ---------------------------------------------------------
PHYSICAL_METRICS = ["training_load", "recovery", "resting_hr", "sleep_hours", "hrv"]
MENTAL_METRICS = ["stress", "focus", "confidence", "motivation", "mood"]


def _seed_for(name: str) -> int:
    """Stable per-athlete seed so data is consistent across reruns."""
    return abs(hash(name)) % (10 ** 6)


def _generate_history(athlete_name: str) -> pd.DataFrame:
    """Create a HISTORY_DAYS-long daily record for one athlete."""
    rng = random.Random(_seed_for(athlete_name))
    today = date.today()
    rows = []

    # Per-athlete baselines to create variety across the roster
    base_load = rng.randint(45, 70)
    base_recovery = rng.randint(55, 80)
    base_stress = rng.randint(25, 55)
    base_motivation = rng.randint(55, 85)

    for i in range(HISTORY_DAYS):
        day = today - timedelta(days=HISTORY_DAYS - 1 - i)
        # Gentle random walk around the baselines
        load = max(10, min(100, base_load + rng.randint(-15, 20)))
        recovery = max(20, min(100, base_recovery + rng.randint(-18, 15)))
        stress = max(5, min(100, base_stress + rng.randint(-12, 25)))
        focus = max(20, min(100, 100 - stress + rng.randint(-10, 15)))
        confidence = max(20, min(100, base_motivation + rng.randint(-15, 12)))
        motivation = max(20, min(100, base_motivation + rng.randint(-18, 12)))
        mood = max(1, min(10, round((focus + confidence + recovery) / 30)))

        rows.append(
            {
                "date": pd.Timestamp(day),
                # Physical
                "training_load": load,
                "recovery": recovery,
                "resting_hr": rng.randint(48, 68),
                "sleep_hours": round(rng.uniform(5.5, 8.8), 1),
                "hrv": rng.randint(45, 110),
                # Mental
                "stress": stress,
                "focus": focus,
                "confidence": confidence,
                "motivation": motivation,
                "mood": mood,
            }
        )

    return pd.DataFrame(rows)


def init_data() -> None:
    """Populate session_state with the full dataset once per session."""
    if "team_data" not in st.session_state:
        st.session_state.team_data = {
            a["name"]: _generate_history(a["name"]) for a in ATHLETES
        }
    if "athlete_meta" not in st.session_state:
        st.session_state.athlete_meta = {a["name"]: a for a in ATHLETES}


def get_athlete_df(name: str) -> pd.DataFrame:
    """Return a copy of one athlete's history, sorted by date."""
    init_data()
    return st.session_state.team_data[name].sort_values("date").reset_index(drop=True)


def add_entry(name: str, entry: dict) -> None:
    """Append (or replace) a daily entry for an athlete in session_state."""
    init_data()
    df = st.session_state.team_data[name]
    entry_date = pd.Timestamp(entry["date"])
    # Remove any existing row for that date so re-logging overwrites it
    df = df[df["date"] != entry_date]
    new_row = pd.DataFrame([entry])
    st.session_state.team_data[name] = (
        pd.concat([df, new_row], ignore_index=True)
        .sort_values("date")
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# Derived analytics
# ---------------------------------------------------------------------------

def readiness_score(latest: pd.Series) -> int:
    """
    Blend physical and mental signals into a single 0-100 readiness score.

    Physical contribution (60%): recovery, sleep, HRV, and inverse training load.
    Mental contribution (40%): focus, confidence, motivation, and inverse stress.
    """
    # Physical sub-score
    sleep_score = min(100, (latest["sleep_hours"] / 8.0) * 100)
    load_score = 100 - latest["training_load"]  # lower load -> fresher
    hrv_score = min(100, (latest["hrv"] / 110) * 100)
    physical = (
        latest["recovery"] * 0.4
        + sleep_score * 0.25
        + hrv_score * 0.2
        + load_score * 0.15
    )

    # Mental sub-score
    mental = (
        latest["focus"] * 0.3
        + latest["confidence"] * 0.25
        + latest["motivation"] * 0.25
        + (100 - latest["stress"]) * 0.2
    )

    score = physical * 0.6 + mental * 0.4
    return int(max(0, min(100, round(score))))


def readiness_label(score: int) -> tuple[str, str]:
    """Return (label, color) for a readiness score."""
    if score >= 75:
        return "Optimal", "#16a34a"
    if score >= 55:
        return "Moderate", "#d97706"
    return "At Risk", "#dc2626"


def generate_insights(df: pd.DataFrame, name: str) -> list[dict]:
    """
    Produce rule-based insights/alerts from recent trends.

    Each insight is a dict: {level, title, message}. Level is one of
    'alert', 'warning', 'positive'.
    """
    insights: list[dict] = []
    if df.empty:
        return insights

    latest = df.iloc[-1]
    recent = df.tail(7)

    # Overtraining: high sustained load + low recovery
    if recent["training_load"].mean() > 70 and latest["recovery"] < 50:
        insights.append(
            {
                "level": "alert",
                "title": "Overtraining risk",
                "message": (
                    f"{name} has averaged a high training load "
                    f"({recent['training_load'].mean():.0f}) with recovery dropping "
                    f"to {latest['recovery']:.0f}. Consider a deload or rest day."
                ),
            }
        )

    # Mental strain: rising stress + falling motivation
    if latest["stress"] > 65:
        insights.append(
            {
                "level": "alert",
                "title": "Elevated stress",
                "message": (
                    f"Stress is high at {latest['stress']:.0f}/100. Check in on mental "
                    "load, sleep, and life factors outside training."
                ),
            }
        )

    if latest["motivation"] < 45:
        insights.append(
            {
                "level": "warning",
                "title": "Low motivation",
                "message": (
                    f"Motivation has dropped to {latest['motivation']:.0f}/100 — a common "
                    "early sign of burnout. A goal-setting conversation may help."
                ),
            }
        )

    # Sleep debt
    if recent["sleep_hours"].mean() < 6.5:
        insights.append(
            {
                "level": "warning",
                "title": "Sleep debt",
                "message": (
                    f"Average sleep over the last 7 days is "
                    f"{recent['sleep_hours'].mean():.1f}h. Recovery and focus will suffer "
                    "below 7h."
                ),
            }
        )

    # Positive reinforcement
    if latest["recovery"] >= 75 and latest["focus"] >= 70 and latest["stress"] <= 40:
        insights.append(
            {
                "level": "positive",
                "title": "Peak readiness window",
                "message": (
                    "Strong recovery, sharp focus, and low stress — a great window for a "
                    "high-quality or high-intensity session."
                ),
            }
        )

    if not insights:
        insights.append(
            {
                "level": "positive",
                "title": "Balanced state",
                "message": "Physical and mental markers are within healthy ranges. Keep it up.",
            }
        )

    return insights


def team_summary() -> pd.DataFrame:
    """Build a roster-level summary table with the latest readiness per athlete."""
    init_data()
    rows = []
    for name, meta in st.session_state.athlete_meta.items():
        df = get_athlete_df(name)
        latest = df.iloc[-1]
        score = readiness_score(latest)
        label, _ = readiness_label(score)
        rows.append(
            {
                "Athlete": name,
                "Sport": meta["sport"],
                "Readiness": score,
                "Status": label,
                "Recovery": int(latest["recovery"]),
                "Stress": int(latest["stress"]),
                "Motivation": int(latest["motivation"]),
                "Sleep (h)": latest["sleep_hours"],
            }
        )
    return pd.DataFrame(rows).sort_values("Readiness").reset_index(drop=True)
